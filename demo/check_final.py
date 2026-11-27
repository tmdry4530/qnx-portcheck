#!/usr/bin/env python3
"""Pre-submission checks for the rendered demo: placeholders, subtitle/burn-in agreement, frame-exact video."""
import argparse
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "demo" / "scenes.json"
FINAL_SRT = "qnx-portcheck-demo.srt"
FINAL_MP4 = "qnx-portcheck-demo.mp4"
EVAL_TOKEN = "[EVAL_NUMBERS]"

PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9_]{2,}\]|\b(?:TODO|TBD|FIXME|XXX)\b|(?i:placeholder)")
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[PX^_][^\x1b]*\x1b\\|\x1b[@-Z\\-_]")
CUE_RE = re.compile(r"(\d+)\n(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})\n(.*)", re.S)


def find_placeholders(text):
    """Return every placeholder-like token in text, in order of appearance."""
    return PLACEHOLDER_RE.findall(text)


def cast_text(path):
    """Concatenate the output ("o") payloads of an asciinema v2 cast and strip ANSI escapes."""
    chunks = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        event = json.loads(line)
        if len(event) >= 3 and event[1] == "o":
            chunks.append(event[2])
    return ANSI_RE.sub("", "".join(chunks))


def parse_srt_ms(text):
    """Parse SRT into [(start_ms, end_ms, text)]; raises ValueError on a malformed block."""
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()):
        if not block:
            continue
        match = CUE_RE.fullmatch(block)
        if not match:
            raise ValueError(f"malformed SRT block: {block[:60]!r}")
        g = [int(x) for x in match.groups()[1:9]]
        start = ((g[0] * 60 + g[1]) * 60 + g[2]) * 1000 + g[3]
        end = ((g[4] * 60 + g[5]) * 60 + g[6]) * 1000 + g[7]
        cues.append((start, end, match.group(10)))
    return cues


def read_scenes_tsv(render_dir):
    """Return [(scene_id, duration_ms)] from subs/scenes.tsv."""
    rows = (Path(render_dir) / "subs" / "scenes.tsv").read_text(encoding="utf-8").splitlines()
    scenes = []
    for row in rows[1:]:
        if row.strip():
            fields = row.split("\t")
            scenes.append((fields[0], int(Decimal(fields[3]) * 1000)))
    return scenes


def _scan(path, text, errors):
    for token in find_placeholders(text):
        errors.append(f"{path}: placeholder token {token!r}")


def check_render(render_dir):
    """Scan every rendered text that is visible in the video. Returns (errors, files_scanned)."""
    render = Path(render_dir)
    errors, scanned = [], 0
    status_path = render / "subs" / "eval_status.txt"
    status = status_path.read_text(encoding="utf-8").strip() if status_path.exists() else "missing"
    if status != "filled":
        errors.append(f"{status_path}: eval status is {status!r}, expected 'filled'")
    for path in sorted((render / "cards").glob("*.txt")) + sorted((render / "subs").glob("*.srt")):
        _scan(path, path.read_text(encoding="utf-8"), errors)
        scanned += 1
    for path in sorted((render / "casts").glob("*.cast")):
        try:
            text = cast_text(path)
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{path}: unreadable cast: {exc}")
        else:
            _scan(path, text, errors)
        scanned += 1
    if scanned == 0:
        errors.append(f"{render}: no rendered cards, subtitles, or casts found")
    return errors, scanned


def check_srt_matches_burn_in(render_dir):
    """Assert subs/demo.srt equals the per-scene SRTs burned in by record.sh, offset by scene start."""
    subs = Path(render_dir) / "subs"
    errors, expected, offset = [], [], 0
    try:
        for scene_id, duration_ms in read_scenes_tsv(render_dir):
            expected.extend((a + offset, b + offset, t) for a, b, t in parse_srt_ms((subs / f"{scene_id}.srt").read_text(encoding="utf-8")))
            offset += duration_ms
        actual = parse_srt_ms((subs / "demo.srt").read_text(encoding="utf-8"))
    except (OSError, ValueError, IndexError) as exc:
        return [f"{subs}: cannot compare subtitles: {exc}"]
    if len(actual) != len(expected):
        errors.append(f"{subs / 'demo.srt'}: {len(actual)} cues, burned-in scenes have {len(expected)}")
    for index, (got, want) in enumerate(zip(actual, expected), 1):
        if got != want:
            errors.append(f"{subs / 'demo.srt'}: cue {index} is {got!r}, burned-in is {want!r}")
    return errors


def check_final_dir(render_dir, final_dir):
    """Final SRT must be byte-identical to render/subs/demo.srt and placeholder-free."""
    final_srt = Path(final_dir) / FINAL_SRT
    source = Path(render_dir) / "subs" / "demo.srt"
    if not final_srt.exists():
        return [f"{final_srt}: missing"]
    errors = []
    data = final_srt.read_bytes()
    if data != source.read_bytes():
        errors.append(f"{final_srt}: differs from {source}")
    _scan(final_srt, data.decode("utf-8"), errors)
    return errors


def check_video_frames(mp4_path, expected_seconds, fps=30):
    """Decode-count the first video stream; it must hold exactly round(expected_seconds*fps) frames at fps/1."""
    command = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
               "-show_entries", "stream=nb_read_frames,r_frame_rate", "-of", "json", str(mp4_path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return [f"{mp4_path}: ffprobe not found; cannot verify frame count"]
    if result.returncode != 0:
        return [f"{mp4_path}: ffprobe failed ({result.returncode}): {result.stderr.strip()}"]
    try:
        stream = json.loads(result.stdout)["streams"][0]
        frames = int(stream["nb_read_frames"])
        rate = stream["r_frame_rate"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        return [f"{mp4_path}: unexpected ffprobe output: {exc!r}"]
    errors = []
    want_frames = round(expected_seconds * fps)
    if frames != want_frames:
        errors.append(f"{mp4_path}: {frames} video frames ({frames / fps:.3f}s), expected {want_frames} ({expected_seconds:g}s at {fps} fps)")
    if rate != f"{fps}/1":
        errors.append(f"{mp4_path}: r_frame_rate {rate}, expected {fps}/1")
    return errors


def check_final_video(render_dir, final_dir):
    """If the final mp4 exists, it must be frame-exact to scenes.tsv and outlast the final SRT."""
    final_mp4 = Path(final_dir) / FINAL_MP4
    if not final_mp4.exists():
        return []
    try:
        expected_seconds = sum(ms for _, ms in read_scenes_tsv(render_dir)) / 1000
    except (OSError, ValueError, IndexError) as exc:
        return [f"{final_mp4}: cannot read scene durations: {exc}"]
    errors = check_video_frames(final_mp4, expected_seconds)
    final_srt = Path(final_dir) / FINAL_SRT
    try:
        cues = parse_srt_ms(final_srt.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return errors + [f"{final_srt}: cannot read cues: {exc}"]
    if cues and cues[-1][1] > round(expected_seconds * 1000):
        errors.append(f"{final_srt}: last cue ends at {cues[-1][1] / 1000:.3f}s, after the {expected_seconds:g}s video")
    return errors


def check_scene_sources(scenes_path=SCENES):
    """Only [EVAL_NUMBERS] in scene 05 card_text/narration may carry a placeholder in scenes.json."""
    errors = []

    def walk(value, scene_id, field):
        if isinstance(value, str):
            for token in find_placeholders(value):
                if not (token == EVAL_TOKEN and scene_id == "05" and field in ("card_text", "narration")):
                    errors.append(f"{scenes_path}: scene {scene_id} {field}: placeholder token {token!r}")
        elif isinstance(value, list):
            for item in value:
                walk(item, scene_id, field)
        elif isinstance(value, dict):
            for key, item in value.items():
                walk(item, scene_id, key)

    for scene in json.loads(Path(scenes_path).read_text(encoding="utf-8")):
        for key, value in scene.items():
            walk(value, scene.get("id", "?"), key)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", required=True, help="render directory produced by demo/record.sh")
    parser.add_argument("--final-dir", help=f"submission directory containing {FINAL_SRT} (and {FINAL_MP4}, if built)")
    args = parser.parse_args(argv)
    errors = check_scene_sources()
    render_errors, scanned = check_render(args.render)
    errors += render_errors + check_srt_matches_burn_in(args.render)
    if args.final_dir:
        errors += check_final_dir(args.render, args.final_dir) + check_final_video(args.render, args.final_dir)
        scanned += 1
    try:
        cues = len(parse_srt_ms((Path(args.render) / "subs" / "demo.srt").read_text(encoding="utf-8")))
        total = sum(ms for _, ms in read_scenes_tsv(args.render)) / 1000
        print(f"cues: {cues}; total duration: {total:g}s; files scanned: {scanned}")
    except (OSError, ValueError, IndexError) as exc:
        errors.append(f"summary unavailable: {exc}")
    if errors:
        print("placeholder check: FAIL", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("placeholder check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

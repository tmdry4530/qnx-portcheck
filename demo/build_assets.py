#!/usr/bin/env python3
"""Build deterministic script and subtitle assets from scenes.json."""
import argparse
from datetime import date, datetime
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "demo" / "scenes.json"
SCRIPT = ROOT / "demo" / "script.md"
HONESTY = "We did not run this on a QNX target; compared its findings against qnx-ports patches; triage aid, not an oracle."


def load_scenes():
    return json.loads(SCENES.read_text(encoding="utf-8"))


METRICS = ("recall_source", "recall_source_nontest", "recall_build", "precision", "precision_in_patched_files")
METRIC_CLAUSE = r"source-site recall ([0-9]+\.[0-9]{3}) \(([0-9]+)/([0-9]+)\), non-test source-site recall ([0-9]+\.[0-9]{3}) \(([0-9]+)/([0-9]+)\), build-site recall ([0-9]+\.[0-9]{3}) \(([0-9]+)/([0-9]+)\), precision ([0-9]+\.[0-9]{3}) \(([0-9]+)/([0-9]+)\), precision in patched files ([0-9]+\.[0-9]{3}) \(([0-9]+)/([0-9]+)\)\."
SPLIT_RES = {
    "tune": re.compile(r"^Split tune \(micro, ([0-9]+) projects\): " + METRIC_CLAUSE + r"$", re.M),
    "holdout": re.compile(r"^Split holdout \(seen during tuning\) \(micro, ([0-9]+) projects\): " + METRIC_CLAUSE + r"$", re.M),
    "fresh": re.compile(r"^Split fresh \(micro, ([0-9]+) projects\): " + METRIC_CLAUSE + r"$", re.M),
}


def load_eval(path) -> tuple[dict | None, str]:
    path = Path(path)
    if not path.is_absolute(): path = ROOT / path
    try: content = path.read_text(encoding="utf-8")
    except FileNotFoundError: return None, "missing"
    except (OSError, UnicodeError) as exc: return None, f"unreadable: {exc}"
    fields = {}
    patterns = {"label": r"^- Label: (.*)$", "projects": r"^- Projects: ([0-9]+)$", "scanner": r"^- Scanner: (.*)$", "scanner_commit": r"^- Scanner source commit: ([0-9a-fA-F]+)$", "date": r"^- Date \(KST\): (.+)$"}
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.M)
        if not match: return None, f"missing or malformed {key} metadata"
        fields[key] = int(match.group(1)) if key == "projects" else match.group(1)
    try:
        date.fromisoformat(fields["date"][:10])
        if len(fields["date"]) > 10: datetime.fromisoformat(fields["date"])
    except ValueError: return None, "malformed date metadata"
    if re.search(r"^> \*\*FAKE", content, re.M) or any("fake" in fields[k].lower() for k in ("label", "scanner")):
        return None, "FAKE run rejected"
    if not fields["scanner"].startswith("qnx-portcheck"): return None, "scanner is not qnx-portcheck"
    result = dict(fields)
    for split in ("fresh", "tune", "holdout"):
        match = SPLIT_RES[split].search(content)
        if not match: return None, f"missing or malformed Split {split if split != 'holdout' else 'holdout (seen during tuning)'} line"
        prefix = "" if split == "fresh" else split + "_"
        result[prefix + "projects"] = int(match.group(1))
        for i, key in enumerate(METRICS):
            value, numerator, denominator = match.group(i * 3 + 2, i * 3 + 3, i * 3 + 4)
            result[prefix + key], result[prefix + f"{key}_num"], result[prefix + f"{key}_den"] = value, int(numerator), int(denominator)
    return result, ""


def apply_eval(scene, ev) -> dict:
    import copy
    result = copy.deepcopy(scene)
    if ev is None: return result
    values = dict(ev, scanner_commit_short=ev["scanner_commit"][:7], date_short=ev["date"][:10])
    result["narration"] = [sentence for text in result["narration"] for sentence in ([t.format(**values) for t in result.get("eval_narration", [])] if "[EVAL_NUMBERS]" in text else [text])]
    headline = result["eval_card_text"].format(**values)
    secondary = result["eval_card_secondary"].format(**values)
    result["card_text"] = headline + "\n" + secondary + "\n" + "\n".join(line for line in result["card_text"].splitlines() if "[EVAL_NUMBERS]" not in line)
    return result


def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


def render_script(scenes=None):
    scenes = load_scenes() if scenes is None else scenes
    total = sum(s["duration"] for s in scenes)
    narration = [sentence for s in scenes for sentence in s["narration"]]
    words = word_count(" ".join(narration))
    lines = ["# qnx-portcheck demo narration", "", f"Total duration: {total:g} seconds", f"Narration: {words} words; estimated read time at 150 wpm: {words / 150 * 60:.1f} seconds", "", f"Honesty statement: {HONESTY}", ""]
    for s in scenes:
        lines.extend([f"## {s['id']} — {s['title']}", "", f"Duration: {s['duration']:g} seconds", "", "On-screen commands:", "", "```sh"])
        lines.extend(s["commands"] or ["(none)"])
        lines.extend(["```", "", "Narration:", "", " ".join(s["narration"]), ""])
        if s["id"] == "05":
            lines.extend(["At render time, [EVAL_NUMBERS] is replaced from eval/RESULTS.md (see demo/README.md); if missing or not a real qnx-portcheck run, the placeholder stays.", "", "Evaluation narration templates:", "", *[f"- {item}" for item in s["eval_narration"]], ""])
        if s["requires"]:
            lines.extend([f"Guard: requires {', '.join(s['requires'])}; otherwise this scene is a placeholder.", ""])
    return "\n".join(lines).rstrip() + "\n"


def _sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]


def make_cues(sentences, duration):
    if isinstance(sentences, str):
        sentences = _sentences(sentences)
    if not sentences:
        return []
    start, end = 0.3, max(0.3, float(duration) - 0.3)
    usable = end - start
    weights = [max(1, word_count(s)) for s in sentences]
    total = sum(weights)
    # Allocate proportional slots, expanding short slots to 1.2s when feasible.
    if usable >= 1.2 * len(sentences):
        weights = [max(w / total * usable, 1.2) for w in weights]
        scale = usable / sum(weights)
        lengths = [w * scale for w in weights]
    else:
        lengths = [usable * w / total for w in weights]
    cues, cursor = [], start
    for sentence, length in zip(sentences, lengths):
        nxt = min(end, cursor + length)
        cues.append((cursor, nxt, sentence))
        cursor = nxt
    if cues:
        a, _, t = cues[-1]
        cues[-1] = (a, end, t)
    return cues


def _timestamp(seconds):
    ms = round(max(0, seconds) * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_srt(cues):
    return "\n\n".join(f"{i}\n{_timestamp(a)} --> {_timestamp(b)}\n{text}" for i, (a, b, text) in enumerate(cues, 1)) + ("\n" if cues else "")


def parse_srt(text):
    def sec(stamp):
        h, m, rest = stamp.split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    parsed = []
    for block in re.split(r"\n\s*\n", text.strip()):
        match = re.match(r"\d+\s*\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*)", block, re.S)
        if match:
            parsed.append((sec(match.group(1)), sec(match.group(2)), match.group(3)))
    return parsed


def build_subs(out_dir, scenes=None, eval_path=None):
    scenes = load_scenes() if scenes is None else scenes
    eval_path = eval_path or os.environ.get("EVAL_RESULTS", "eval/RESULTS.md")
    ev, reason = load_eval(eval_path)
    scenes = [apply_eval(scene, ev) if scene["id"] == "05" else scene for scene in scenes]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    offset, combined = 0.0, []
    rows = ["id\tslug\tkind\tduration\trequires"]
    for scene in scenes:
        cues = make_cues(scene["narration"], scene["duration"])
        (out / f"{scene['id']}.srt").write_text(format_srt(cues), encoding="utf-8")
        combined.extend((a + offset, b + offset, t) for a, b, t in cues)
        rows.append("\t".join([scene["id"], scene["slug"], scene["kind"], str(scene["duration"]), ",".join(scene["requires"])]))
        offset += scene["duration"]
    (out / "demo.srt").write_text(format_srt(combined), encoding="utf-8")
    (out / "scenes.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (out / "eval_status.txt").write_text("filled\n" if ev is not None else f"placeholder: {reason}\n", encoding="utf-8")
    if ev is None: print(f"WARNING: eval numbers not filled ({reason}); keeping [EVAL_NUMBERS] placeholder", file=sys.stderr)


def card_text(scene_id, out_file, eval_path=None):
    scene = next(s for s in load_scenes() if s["id"] == scene_id)
    ev, reason = None, ""
    if scene_id == "05":
        eval_path = eval_path or os.environ.get("EVAL_RESULTS", "eval/RESULTS.md")
        ev, reason = load_eval(eval_path)
        scene = apply_eval(scene, ev)
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    output = Path(out_file)
    output.write_text(scene["card_text"], encoding="utf-8")
    if scene_id == "05":
        if ev is not None:
            values = dict(ev, scanner_commit_short=ev["scanner_commit"][:7], date_short=ev["date"][:10])
            headline = scene["eval_card_text"].format(**values)
            remaining = "\n".join(line for line in next(s for s in load_scenes() if s["id"] == "05")["card_text"].splitlines() if "[EVAL_NUMBERS]" not in line)
            secondary = scene["eval_card_secondary"].format(**values) + "\n" + remaining
        else:
            headline, secondary = scene["card_text"], ""
            secondary = "\n".join(line for line in scene["card_text"].splitlines() if "[EVAL_NUMBERS]" not in line)
        output.with_name(output.stem + "-headline" + output.suffix).write_text(headline, encoding="utf-8")
        output.with_name(output.stem + "-secondary" + output.suffix).write_text(secondary, encoding="utf-8")
    if scene_id == "05" and ev is None: print(f"WARNING: eval numbers not filled ({reason}); keeping [EVAL_NUMBERS] placeholder", file=sys.stderr)


def check():
    scenes = load_scenes()
    errors = []
    if [s["id"] for s in scenes] != [f"{i:02d}" for i in range(len(scenes))]: errors.append("scene ids must be unique and ordered 00..06")
    total = sum(s["duration"] for s in scenes)
    if total >= 180: errors.append("total duration must be under 180 seconds")
    for s in scenes:
        words = word_count(" ".join(s["narration"]))
        if words / 150 * 60 > s["duration"] - 1: errors.append(f"scene {s['id']} narration exceeds duration budget")
    scene05 = next(s for s in scenes if s["id"] == "05")
    worst = {"label":"x", "projects":999, "tune_projects":999, "holdout_projects":999, "scanner":"qnx-portcheck", "scanner_commit":"abcdef0", "date":"2026-12-31", **{item: value for prefix in ("", "tune_", "holdout_") for key in METRICS for item, value in ((prefix+key,"0.000"),(prefix+key+"_num",999),(prefix+key+"_den",999))}}
    if word_count(" ".join(apply_eval(scene05, worst)["narration"])) / 150 * 60 > scene05["duration"] - 1: errors.append("scene 05 rendered eval narration exceeds duration budget")
    words = word_count(" ".join(x for s in scenes for x in s["narration"]))
    if words / 150 * 60 >= 180: errors.append("total narration estimate must be under 3 minutes")
    if not any(HONESTY in " ".join(s["narration"]) for s in scenes): errors.append("honesty sentence missing from narration")
    if not any(HONESTY in s["card_text"] for s in scenes if s["id"] == "06"): errors.append("honesty sentence missing from closing card")
    if not SCRIPT.exists() or SCRIPT.read_text(encoding="utf-8") != render_script(scenes): errors.append("demo/script.md is out of date; run build_assets.py script")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"scene checks passed: {len(scenes)} scenes, {total:g}s, {words} narration words")
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("script")
    p = sub.add_parser("subs"); p.add_argument("--out", required=True); p.add_argument("--eval")
    p = sub.add_parser("card-text"); p.add_argument("--scene", required=True); p.add_argument("--out", required=True); p.add_argument("--eval")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "script":
        SCRIPT.parent.mkdir(parents=True, exist_ok=True); SCRIPT.write_text(render_script(), encoding="utf-8"); return 0
    if args.command == "subs": build_subs(args.out, eval_path=args.eval); return 0
    if args.command == "card-text": card_text(args.scene, args.out, args.eval); return 0
    return check()

if __name__ == "__main__":
    raise SystemExit(main())

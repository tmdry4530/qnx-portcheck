#!/usr/bin/env python3
"""Build deterministic script and subtitle assets from scenes.json."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "demo" / "scenes.json"
SCRIPT = ROOT / "demo" / "script.md"
HONESTY = "We did not run this on a QNX target; we validated it against qnx-ports patches."


def load_scenes():
    return json.loads(SCENES.read_text(encoding="utf-8"))


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


def build_subs(out_dir, scenes=None):
    scenes = load_scenes() if scenes is None else scenes
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


def check():
    scenes = load_scenes()
    errors = []
    if [s["id"] for s in scenes] != [f"{i:02d}" for i in range(len(scenes))]: errors.append("scene ids must be unique and ordered 00..06")
    total = sum(s["duration"] for s in scenes)
    if total >= 180: errors.append("total duration must be under 180 seconds")
    for s in scenes:
        words = word_count(" ".join(s["narration"]))
        if words / 150 * 60 > s["duration"] - 1: errors.append(f"scene {s['id']} narration exceeds duration budget")
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
    p = sub.add_parser("subs"); p.add_argument("--out", required=True)
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "script":
        SCRIPT.parent.mkdir(parents=True, exist_ok=True); SCRIPT.write_text(render_script(), encoding="utf-8"); return 0
    if args.command == "subs": build_subs(args.out); return 0
    return check()

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
# Build the final silent submission video and its SRT from a full demo/record.sh run.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
# FINAL_DIR and DEMO_OUT may be absolute; relative values (env or default) resolve against REPO_ROOT, not the cwd.
FINAL_DIR="${FINAL_DIR:-demo/out/final}"
if [[ "$FINAL_DIR" != /* ]]; then FINAL_DIR="${REPO_ROOT%/}/$FINAL_DIR"; fi
OUT="${DEMO_OUT:-demo/render}"
if [[ "$OUT" != /* ]]; then OUT="${REPO_ROOT%/}/$OUT"; fi
FINAL_MP4="$FINAL_DIR/qnx-portcheck-demo.mp4"
FINAL_SRT="$FINAL_DIR/qnx-portcheck-demo.srt"
MIN_FREE_KB=$((3 * 1024 * 1024))

fail() {
    printf 'build_final: %s\n' "$1" >&2
    exit 1
}

if [[ -n "${SCENES+x}" ]]; then
    fail "SCENES is set ('${SCENES}'); the final build needs every scene. Unset SCENES and retry."
fi

disk_path="$(dirname "$FINAL_DIR")"
while [[ ! -d "$disk_path" ]]; do disk_path="$(dirname "$disk_path")"; done
free_kb="$(df -Pk "$disk_path" | awk 'NR == 2 { print $4 }')"
if [[ -z "$free_kb" ]] || ((free_kb < MIN_FREE_KB)); then
    fail "only ${free_kb:-unknown} KiB free on $disk_path; need at least 3 GiB"
fi

DEMO_OUT="$OUT" bash demo/record.sh

eval_status="$(cat "$OUT/subs/eval_status.txt")"
if [[ "$eval_status" != filled ]]; then
    fail "eval numbers not filled ($eval_status); fix eval/RESULTS.md before building the final video"
fi

for scene_id in 01 02; do
    scene_mode="$(awk -F '\t' -v id="$scene_id" '$1 == id { print $2 }' "$OUT/manifest.txt")"
    if [[ "$scene_mode" != recorded ]]; then
        fail "scene $scene_id mode is '${scene_mode:-missing}' in $OUT/manifest.txt; expected 'recorded'"
    fi
done
if grep -q $'\tplaceholder\t' "$OUT/manifest.txt"; then
    fail "$OUT/manifest.txt lists placeholder scenes"
fi

python3 demo/check_final.py --render "$OUT" || fail "render checks failed"

mkdir -p "$FINAL_DIR"
nice -n 10 ffmpeg -nostdin -y -v error -i "$OUT/demo-burned.mp4" -map 0:v:0 -c:v copy -an -movflags +faststart "$FINAL_MP4"
cp -- "$OUT/subs/demo.srt" "$FINAL_SRT"

python3 demo/check_final.py --render "$OUT" --final-dir "$FINAL_DIR" || fail "final directory checks failed"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,codec_name,width,height -of json "$FINAL_MP4"
printf 'Final video: %s\nFinal subtitles: %s\n' "$FINAL_MP4" "$FINAL_SRT"

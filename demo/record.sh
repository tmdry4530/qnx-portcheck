#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
OUT="${DEMO_OUT:-demo/out}"
if [[ "$OUT" != /* ]]; then OUT="${REPO_ROOT%/}/$OUT"; fi
ASCIINEMA_BIN="${ASCIINEMA:-$(command -v asciinema || true)}"
if [[ -z "$ASCIINEMA_BIN" ]]; then ASCIINEMA_BIN=/workspace/qnxref/venv/bin/asciinema; fi
AGG_BIN="${AGG:-$(command -v agg || true)}"
if [[ -z "$AGG_BIN" ]]; then AGG_BIN=/home/box/bin/agg; fi

for tool in "$ASCIINEMA_BIN" "$AGG_BIN" ffmpeg ffprobe python3; do
    if ! command -v "$tool" >/dev/null 2>&1 && [[ ! -x "$tool" ]]; then
        printf 'Required tool missing: %s\n' "$tool" >&2
        exit 1
    fi
done
"$ASCIINEMA_BIN" --version
"$AGG_BIN" --version
ffmpeg -version | head -n 1
ffprobe -version | head -n 1
python3 --version

python3 demo/build_assets.py check
python3 demo/build_assets.py subs --out "$OUT/subs"
mkdir -p "$OUT/casts" "$OUT/gifs" "$OUT/raw" "$OUT/cards" "$OUT/clips"
: > "$OUT/manifest.txt"
eval_status="$(cat "$OUT/subs/eval_status.txt")"
printf 'eval\t%s\n' "$eval_status" >> "$OUT/manifest.txt"

while IFS=$'\t' read -r scene_id slug kind duration requires <&3; do
    [[ "$scene_id" == id ]] && continue
    if [[ -n "${SCENES:-}" && ! " $SCENES " =~  $scene_id  ]]; then continue; fi
    mode=recorded
    if [[ "$kind" == card ]]; then mode=card
    elif [[ ",$requires," == *,scan-cli,* ]] && ! PYTHONPATH=src python3 -c 'import qnx_portcheck.cli' >/dev/null 2>&1; then mode=placeholder
    fi
    card_path="$OUT/cards/$scene_id.txt"
    if [[ "$mode" != recorded ]]; then
        if [[ "$mode" == card ]]; then
            python3 demo/build_assets.py card-text --scene "$scene_id" --out "$card_path"
        else
        python3 - "$scene_id" "$mode" "$card_path" <<'PY'
import json, sys, textwrap
from pathlib import Path
scenes = json.loads(Path('demo/scenes.json').read_text(encoding='utf-8'))
scene = next(item for item in scenes if item['id'] == sys.argv[1])
mode = sys.argv[2]
text = scene['card_text']
if mode == 'placeholder':
    text = 'PLACEHOLDER: scan CLI not merged yet\n' + '\n'.join(scene['commands'])
text = '\n'.join(textwrap.fill(line, width=60) for line in text.split('\n'))
Path(sys.argv[3]).write_text(text, encoding='utf-8')
PY
        fi
        title_file="$OUT/cards/$scene_id-title.txt"
        python3 - "$scene_id" "$title_file" <<'PY'
import json, sys, textwrap
from pathlib import Path
scene = next(x for x in json.loads(Path('demo/scenes.json').read_text()) if x['id'] == sys.argv[1])
Path(sys.argv[2]).write_text(textwrap.fill(scene['title'], width=48), encoding='utf-8')
PY
        if [[ "$scene_id" == 05 ]]; then
            headline_file="$OUT/cards/$scene_id-headline.txt"
            secondary_file="$OUT/cards/$scene_id-secondary.txt"
            body_filter="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile='$headline_file':fontcolor=white:fontsize=28:line_spacing=9:x=80:y=175:y_align=0:fix_bounds=1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile='$secondary_file':fontcolor=white:fontsize=18:line_spacing=7:x=80:y=430:y_align=0:fix_bounds=1"
        else
            body_filter="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile='$card_path':fontcolor=white:fontsize=25:line_spacing=12:x=80:y=220:y_align=0:fix_bounds=1"
        fi
        ffmpeg -nostdin -y -v error -f lavfi -i "color=c=0x1e1e1e:s=1280x720:r=30:d=$duration" \
            -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile='$title_file':fontcolor=white:fontsize=38:x=80:y=100,$body_filter" \
            -an -c:v libx264 -pix_fmt yuv420p "$OUT/raw/$scene_id.mp4"
    else
        export TERM=xterm-256color
        "$ASCIINEMA_BIN" rec --overwrite -q -i 2 --cols 100 --rows 28 -c "bash demo/scenes/$scene_id-$slug.sh" "$OUT/casts/$scene_id.cast"
        "$AGG_BIN" --font-family "DejaVu Sans Mono" --font-size 20 --theme monokai --idle-time-limit 2 "$OUT/casts/$scene_id.cast" "$OUT/gifs/$scene_id.gif"
        ffmpeg -nostdin -y -v error -i "$OUT/gifs/$scene_id.gif" -vf "scale=1280:590:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:4:color=0x1e1e1e,fps=30" -an -c:v libx264 -pix_fmt yuv420p "$OUT/raw/$scene_id.mp4"
    fi
    raw_duration="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/raw/$scene_id.mp4")"
    if python3 - "$raw_duration" "$duration" <<'PY'
import sys
raise SystemExit(0 if float(sys.argv[1]) > float(sys.argv[2]) else 1)
PY
    then
        printf 'Warning: scene %s exceeded %ss; speeding it up to fit.\n' "$scene_id" "$duration" >&2
        speed_filter="setpts=$(python3 -c "print(float('$duration')/float('$raw_duration'))")*PTS"
        fit_filter="$speed_filter,trim=duration=$duration,setpts=PTS-STARTPTS"
    else
        fit_filter="tpad=stop_mode=clone:stop_duration=$duration,trim=duration=$duration,setpts=PTS-STARTPTS"
    fi
    ffmpeg -nostdin -y -v error -i "$OUT/raw/$scene_id.mp4" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
        -vf "$fit_filter,subtitles='$OUT/subs/$scene_id.srt':force_style='FontName=DejaVu Sans,FontSize=16,Outline=1,MarginV=8'" \
        -t "$duration" -map 0:v:0 -map 1:a:0 -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -ac 2 -shortest "$OUT/clips/$scene_id.mp4"
    printf '%s\t%s\t%s\n' "$scene_id" "$mode" "$duration" >> "$OUT/manifest.txt"
done 3< "$OUT/subs/scenes.tsv"

if [[ -n "${SCENES:-}" ]]; then
    printf 'SCENES subset requested; concatenating only selected clips.\n'
fi
concat_file="$OUT/concat.txt"
: > "$concat_file"
while IFS=$'\t' read -r scene_id slug kind duration requires; do
    [[ "$scene_id" == id ]] && continue
    if [[ -n "${SCENES:-}" && ! " $SCENES " =~  $scene_id  ]]; then continue; fi
    printf "file '%s'\n" "$OUT/clips/$scene_id.mp4" >> "$concat_file"
done < "$OUT/subs/scenes.tsv"
ffmpeg -nostdin -y -v error -f concat -safe 0 -i "$concat_file" -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -ac 2 "$OUT/demo-burned.mp4"
ffmpeg -nostdin -y -v error -i "$OUT/demo-burned.mp4" -i "$OUT/subs/demo.srt" -map 0:v:0 -map 0:a:0 -map 1:0 -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng "$OUT/demo.mp4"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,codec_name,width,height -of json "$OUT/demo.mp4"

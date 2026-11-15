#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
OUT="${DEMO_OUT:-demo/out}"
ENGINE="${TTS_ENGINE:-auto}"
if [[ "${1:-}" == --synthesize ]]; then
    adapter="$2"; text="$3"; output="$4"
    case "$adapter" in
        tts_espeak_ng) espeak-ng -w "$output" "$text" ;;
        tts_espeak) espeak -w "$output" "$text" ;;
        tts_piper) piper --model "${PIPER_MODEL:?PIPER_MODEL is required for piper}" --output_file "$output" <<< "$text" ;;
        tts_festival) printf '%s\n' "$text" | text2wave -o "$output" ;;
        tts_pico2wave) pico2wave -w "$output" -l en-US "$text" ;;
        *) exit 2 ;;
    esac
    exit 0
fi

command_exists() { command -v "$1" >/dev/null 2>&1; }
tts_espeak_ng() { espeak-ng -w "$2" "$1"; }
tts_espeak() { espeak -w "$2" "$1"; }
tts_piper() {
    if [[ -z "${PIPER_MODEL:-}" ]]; then printf '%s\n' 'PIPER_MODEL is required for piper.' >&2; return 1; fi
    piper --model "$PIPER_MODEL" --output_file "$2" <<< "$1"
}
tts_festival() { printf '%s\n' "$1" | text2wave -o "$2"; }
tts_pico2wave() { pico2wave -w "$2" -l en-US "$1"; }

if [[ "$ENGINE" == auto ]]; then
    if command_exists espeak-ng; then ENGINE=espeak-ng
    elif command_exists espeak; then ENGINE=espeak
    elif command_exists piper; then ENGINE=piper
    elif command_exists text2wave; then ENGINE=festival
    elif command_exists pico2wave; then ENGINE=pico2wave
    else ENGINE=none
    fi
fi
if [[ "$ENGINE" == none ]]; then
    printf 'No local TTS engine found; subtitles-only video is %s/demo.mp4\n' "$OUT"
    exit 0
fi

mkdir -p "$OUT/tts"
python3 - "$ENGINE" "$OUT" <<'PY'
import json, subprocess, sys
from pathlib import Path
engine, out = sys.argv[1:]
scenes = json.loads(Path('demo/scenes.json').read_text(encoding='utf-8'))
funcs = {'espeak-ng':'tts_espeak_ng', 'espeak':'tts_espeak', 'piper':'tts_piper', 'festival':'tts_festival', 'pico2wave':'tts_pico2wave'}
script = Path('demo/tts.sh').resolve()
for scene in scenes:
    narration = ' '.join(scene['narration'])
    output = Path(out) / 'tts' / f"{scene['id']}.wav"
    subprocess.run(['bash', str(script), '--synthesize', funcs[engine], narration, str(output)], check=True)
PY

python3 - "$OUT" <<'PY'
import json, subprocess, sys
from pathlib import Path
out = Path(sys.argv[1])
scenes = json.loads(Path('demo/scenes.json').read_text(encoding='utf-8'))
inputs, filters, offset = [], [], 0.0
for scene in scenes:
    wav = out / 'tts' / f"{scene['id']}.wav"
    duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(wav)], text=True))
    if duration > scene['duration']:
        print(f"Warning: narration for scene {scene['id']} is {duration:.2f}s, longer than {scene['duration']}s.", file=sys.stderr)
    inputs.extend(['-i', str(wav)])
    delay = round(offset * 1000)
    filters.append(f"[{len(filters)}:a]adelay={delay}|{delay}[a{len(filters)}]")
    offset += scene['duration']
labels = ''.join(f"[a{i}]" for i in range(len(filters)))
filters.append(f"{labels}amix=inputs={len(scenes)}:normalize=0,apad=whole_dur={offset}[narration]")
subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',';'.join(filters),'-map','[narration]','-c:a','aac',str(out/'narration.m4a')],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(out/'demo.mp4'),'-i',str(out/'narration.m4a'),'-map','0:v:0','-map','1:a:0','-map','0:s?','-c:v','copy','-c:a','aac','-c:s','copy',str(out/'demo-voiced.mp4')],check=True)
PY

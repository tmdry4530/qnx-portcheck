# Reproducible demo video

Run `bash demo/record.sh` from any directory to create the terminal/card clips, burned subtitles, and `demo/render/demo.mp4`. Run `bash demo/tts.sh` separately to add narration when a supported local engine is available. The `demo/render/` directory is used because workspace hydrate skips directories named `out/`.

Requirements are Python 3 (stdlib only for demo scripts), asciinema 2.4.0, agg 1.9.0, ffmpeg/ffprobe 7.1 with libass, and the DejaVu fonts named in the project brief. Shellcheck is used for the requested script check. The pipeline never installs software or accesses the network.

Video renders natively at 1920×1080. Terminal footage (agg font size 30) is scaled into a 1920×885 area at the top of each frame, leaving a bottom band for burned subtitles. Card scenes use the same subtitle style. Every ffmpeg call runs under `nice -n 10`. Set `DEMO_SHOW_EXIT=1` when running a scene to display every command's exit status; a success note can be supplied as `show_cmd 'command' 'note'`.

The CLI is merged: install the package and run the `qnx-portcheck` entry point, or from a checkout use `PYTHONPATH=src python3 -m qnx_portcheck` (equivalently `python3 -m qnx_portcheck.cli`). Subcommands are `scan PATH [--format text|json|sarif] [--out OUT] [--fail-on error|warning|never]`, `scaffold PATH [--name NAME] [--out OUT] [--build-system cmake|meson|autotools|make] [--force] [--dry-run]`, and `lint-buildfile FILE... [--format text|json]`; `--version` prints the version. The demo scenes run these real commands through the `qnx-portcheck` shell function in `scenes/lib.sh`, which puts the repository `src/` on `PYTHONPATH` and calls `python3 -m qnx_portcheck.cli`; if the CLI is not importable, it falls back to the scaffold/lint modules and `record.sh` renders scan scenes 01 and 02 as placeholder cards. `[EVAL_NUMBERS]` in scene 05 is replaced at render time with the numbers from `eval/RESULTS.md` (see below).

This is a host-side tool. No QNX SDP was used and no QNX target was run. Suggestions are grounded in QNX 8.0 documentation; generated build files are drafts that need review. We did not run this on a QNX target; compared its findings against qnx-ports patches; triage aid, not an oracle.

## Evaluation numbers contract

At render time, `demo/build_assets.py subs` and `card-text` read `eval/RESULTS.md`; `EVAL_RESULTS` overrides that path (relative paths are resolved from the repository root). The representative headline is the `Split fresh (micro, N projects): ...` line, with source-site recall, non-test source-site recall, build-site recall, precision, and precision in patched files in that order. Each metric has three decimal places and integer numerator/denominator pairs. The fresh split project count supplies `{projects}`.

Well-formed `Split tune (micro, N projects): ...` and `Split holdout (seen during tuning) (micro, N projects): ...` lines are also required and shown smaller on the evaluation card. The card says `holdout was seen during tuning`. Holdout is not the headline because it was seen during tuning. `Overall (micro)` may be present, but it is not the representative number.

Metadata bullets `Label`, `Projects`, `Scanner`, `Scanner source commit`, and `Date (KST)` are required. The run is rejected if its label or scanner contains `fake` (case-insensitive), any line starts with `> **FAKE`, or the scanner does not start with `qnx-portcheck`. Missing, malformed, or no-data (`—`) split results leave `[EVAL_NUMBERS]` in narration and card and print a warning to stderr. `subs` writes `eval_status.txt` as `filled` or `placeholder: <reason>`; the recording manifest includes that status. Decimal values are emitted exactly as written in the results file.
No voice, face, or music is included by default. Local text-to-speech is optional and isolated in `tts.sh`.

## Final submission build

`bash demo/build_final.sh` runs a full `demo/record.sh` (it refuses when `SCENES` is set) and writes the silent submission files to `FINAL_DIR` (default `demo/out/final`, repo-relative and ignored by git; override with an absolute path such as `FINAL_DIR=/path/to/submission`, while a relative `FINAL_DIR` resolves against the repository root, not the current directory; `DEMO_OUT` selects the render directory as in `record.sh`):

- `qnx-portcheck-demo.mp4`: the burned-in video stream copied from `demo-burned.mp4`, no audio stream, `+faststart`.
- `qnx-portcheck-demo.srt`: byte-identical copy of `subs/demo.srt`.

It aborts before recording if less than 3 GiB is free near `FINAL_DIR`, and afterwards unless `subs/eval_status.txt` is `filled`, scenes 01 and 02 are `recorded` in `manifest.txt`, and `python3 demo/check_final.py --render <render dir>` passes. `check_final.py` fails on placeholder tokens (`[ALL_CAPS]`, `TODO`, `TBD`, `FIXME`, `XXX`, `placeholder`) in rendered cards, subtitles, and recorded terminal output; on any placeholder in `scenes.json` other than `[EVAL_NUMBERS]` in scene 05; and when `subs/demo.srt` differs, to the millisecond, from the per-scene subtitles burned into the clips. With `--final-dir` it also verifies the submitted SRT and checks the final video frame-exact: `ffprobe -count_frames` must report exactly 30 × (sum of `subs/scenes.tsv` durations) frames at `r_frame_rate` 30/1, and the last SRT cue must end no later than the video. `record.sh` joins the clips with ffmpeg's concat filter rather than the concat demuxer, which drops a frame at every clip boundary. The script ends by printing ffprobe duration, codec, and size of the final mp4.


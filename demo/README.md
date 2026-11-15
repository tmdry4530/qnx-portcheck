# Reproducible demo video

Run `bash demo/record.sh` from any directory to create the terminal/card clips, burned subtitles, and `demo/out/demo.mp4`. Run `bash demo/tts.sh` separately to add narration when a supported local engine is available.

Requirements are Python 3 (stdlib only for demo scripts), asciinema 2.4.0, agg 1.9.0, ffmpeg/ffprobe 7.1 with libass, and the DejaVu fonts named in the project brief. Shellcheck is used for the requested script check. The pipeline never installs software or accesses the network.

Terminal footage is scaled into a 1280×590 area at the top of each 1280×720 frame, leaving a bottom band for burned subtitles. Card scenes use the same subtitle style. Set `DEMO_SHOW_EXIT=1` when running a scene to display every command's exit status; a success note can be supplied as `show_cmd 'command' 'note'`.

Until `qnx_portcheck.cli` is merged, scan scenes 01 and 02 render explicit placeholders listing the intended commands. `[EVAL_NUMBERS]` remains a placeholder until actual evaluation results are recorded in `eval/RESULTS.md`.

This is a host-side tool. No QNX SDP was used and no QNX target was run. Suggestions are grounded in QNX 8.0 documentation; generated build files are drafts that need review. We did not run this on a QNX target; compared its findings against qnx-ports patches; triage aid, not an oracle.

## Evaluation numbers contract

At render time, `demo/build_assets.py subs` and `card-text` read `eval/RESULTS.md`; `EVAL_RESULTS` overrides that path (relative paths are resolved from the repository root). The representative headline is the `Split fresh (micro, N projects): ...` line, with source-site recall, non-test source-site recall, build-site recall, precision, and precision in patched files in that order. Each metric has three decimal places and integer numerator/denominator pairs. The fresh split project count supplies `{projects}`.

Well-formed `Split tune (micro, N projects): ...` and `Split holdout (seen during tuning) (micro, N projects): ...` lines are also required and shown smaller on the evaluation card. The card says `holdout was seen during tuning`. Holdout is not the headline because it was seen during tuning. `Overall (micro)` may be present, but it is not the representative number.

Metadata bullets `Label`, `Projects`, `Scanner`, `Scanner source commit`, and `Date (KST)` are required. The run is rejected if its label or scanner contains `fake` (case-insensitive), any line starts with `> **FAKE`, or the scanner does not start with `qnx-portcheck`. Missing, malformed, or no-data (`—`) split results leave `[EVAL_NUMBERS]` in narration and card and print a warning to stderr. `subs` writes `eval_status.txt` as `filled` or `placeholder: <reason>`; the recording manifest includes that status. Decimal values are emitted exactly as written in the results file.
No voice, face, or music is included by default. Local text-to-speech is optional and isolated in `tts.sh`.

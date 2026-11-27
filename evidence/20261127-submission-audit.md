# Submission text and checklist audit

Date (KST, Asia/Seoul): 2026-11-27 17:43

Branch: `dev3/submission-audit`

Integration onto local main: `git merge --ff-only main`. The audit branch was still at `228920f` with uncommitted submission edits; local main `7b649f6` is a descendant of `228920f`, so the fast-forward succeeded. No rebase, no force-push, and no push to origin.

- Local main at integration: `7b649f6025be6bb327144a5bcd422d7456bfe98a` (`7b649f6`, final demo build)
- Documentation-fix commit: `fa6333ec64d10e7fb355d4caaf65db1a57394040` (`fa6333e`)
- This evidence file is added in the following commit on the same branch (branch tip after that commit).

## Test suite

Command (repository root, after `pip install -e '.[test]'`):

```bash
python -m pytest -q tests eval/tests
```

Result, run on the documentation-fix tree (`fa6333e`, parent `7b649f6`):

- 188 tests collected (`132` under `tests/`, including `30` in `tests/test_demo_final.py`; `56` in `eval/tests/`)
- **183 passed, 6 skipped**, exit 0, about 2.5 s
- No failures or errors

Skipped (optional dependencies, not failures):

- `tests/test_action.py`: PyYAML not installed (the tool runtime is standard-library only)
- `tests/test_scaffold.py`: four tests skipped because `QNX_BUILD_FILES` is unset (optional upstream source comparison)
- `eval/tests/test_eval.py`: one test skipped because PyYAML is unavailable

A JUnit export also lists one extra skipped module stub from `pytest.importorskip("yaml")` in `tests/test_action.py`. That stub is not a collected test and is not included in the 188/183/6 figures.

Default `pytest -q` (via `testpaths = ["tests"]` in `pyproject.toml`) collects only the 132 tests under `tests/`. The figures above are the full suite, including the evaluation harness.

## Secret scan

Tool: gitleaks 8.21.2

- `gitleaks detect` (git history): 50 commits scanned, **no leaks found**
- `gitleaks detect --no-git` (working tree): **no leaks found**

## Public URL checks

`curl -L` on 2026-11-27 (KST). All returned HTTP 200.

| URL | HTTP status |
|---|---|
| https://github.com/tmdry4530/qnx-portcheck | 200 (public; unauthenticated `git ls-remote` HEAD was `228920f` at check time, before local main moved to `7b649f6`) |
| https://github.com/tmdry4530/qnx-portcheck.git | 200 (redirects to the repo page) |
| https://github.com/tmdry4530/qnx-portcheck/blob/main/docs/tutorial-port-linux-daemon-to-qnx8.md | 200 (checklist item 15) |
| https://github.com/qnx-ports | 200 |
| https://github.com/qnx-ports/build-files | 200 |
| https://qnx.devpost.com/rules | 200 |
| https://qnx.devpost.com/ | 200 |
| https://qnx.software/en/developers/get-started/qnx-everywhere | 200 |
| https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html | 200 |
| https://www.qnx.com/developers/docs/ | 200 |

Unauthenticated GitHub API for `tmdry4530/qnx-portcheck`: `visibility=public`, license SPDX `Apache-2.0`, empty description, homepage, and topics, matching the checklist About-section note.

## Claims that matched (not changed)

- 25 scan rules in `ALL_RULES`, with a positive and a negative fixture for each
- Evaluation headline numbers in `eval/RESULTS.md` and README: fresh 15-project source-site recall 0.079 (23/292), precision 0.033 (48/1448), precision in patched files 0.191 (48/251), build-site recall 0.009 (17/1864); SDL 1790 of 1864 fresh build sites; tune 0.157 (18/115) on 17 projects; seen-during-tuning 0.284 (56/197) on 16 projects
- Performance rounding: 28 s / 1124 s (28.0 / 1123.7) and 4.2 s / 724 s (4.19 / 724.17) from `eval/perf/README.md`
- Scanner source commit `5118669`; first commit `b068fe8` at 2026-11-15 11:57 KST; scaffold pin `79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5`; eclipse-score fixture `f9156c2…`; Apache-2.0 license
- Commands, paths, exit codes, SARIF 2.1.0, host-only wording (no target run, no SDP build), and official-rules date conversions (ET/EST to KST)
- Local demo file `qnx-submission/qnx-portcheck-demo.mp4`: 161.000 s, 1920×1080, 30 fps, 4830 frames, H.264, no audio stream, sibling `.srt` present. Scene durations in `demo/scenes.json` sum to 161 s.

## Fixed items (before → after)

1. `submission/devpost-en.md` video line: `[VIDEO_URL] (YouTube, public, under 3 minutes)` → `TODO [VIDEO_URL] (YouTube, public, under 3 minutes). Local silent 1920×1080 file is 161 seconds at \`qnx-submission/qnx-portcheck-demo.mp4\`.` The YouTube URL stays a TODO.
2. `submission/devpost-en.md` pytest count: `90 tests, plus 41 for the evaluation harness` → `132 tests, plus 56 for the evaluation harness` (inventory on `7b649f6`).
3. `submission/checklist.md` item 1: `see 20261115-expansion.md` → `see the internal expansion plan dated 2026-11-15, not in this repository` (that file is not in the repo).
4. `submission/checklist.md` item 10: status `placeholder — [VIDEO_URL] still needs filling` → `done (text); video link still TODO`. Requirement 10 is the text description, which is complete; the video URL is item 12.
5. `submission/checklist.md` item 12: `Draft at demo/render/demo.mp4` → final silent 1920×1080 file is 161 seconds at `qnx-submission/qnx-portcheck-demo.mp4`; status now also says the YouTube URL is still TODO. No absolute machine paths added.
6. `submission/checklist.md` item 18: harness SHA `7df6c14` → `8ce088a`, matching `eval/RESULTS.md` after the path-sanitizing reuse run (scanner remains `5118669`; metric numbers were unchanged).

## Remaining manual items

These were not done, by design (no Devpost, upload, or public-settings changes):

- Item 1: user/COO Join on Devpost (existing account; no new sign-up)
- Item 2: entrant confirms age, residency, and conflicts
- Item 5: select category **Developer Tooling & Host Tools** on the form
- Item 12: public YouTube upload and fill `TODO [VIDEO_URL]` after code freeze / QA (local file is ready)
- Item 14: keep the repo public and the license unchanged through 2027-01-30 KST
- Item 15: bonus tutorial form field (the document and public URL exist; its own status box still says the scan step and any target run were not verified)
- Item 19: submit on Devpost before 2026-12-16 04:00 KST
- Item 20: tax forms only if winning

Item 8 remains `partial` (host tool; not built with the SDP or run on a target). That is consistent with the honesty statement.

Note (not changed in this audit): `demo/README.md` and `demo/build_final.sh` on `7b649f6` still document a default `FINAL_DIR` with an absolute machine path. Submission copy uses only the portable `qnx-submission/qnx-portcheck-demo.mp4` location.

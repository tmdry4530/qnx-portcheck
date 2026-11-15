# qnx-portcheck demo narration

Total duration: 152 seconds
Narration: 200 words; estimated read time at 150 wpm: 80.0 seconds

Honesty statement: We did not run this on a QNX target; we validated it against qnx-ports patches.

## 00 — qnx-portcheck

Duration: 8 seconds

On-screen commands:

```sh
(none)
```

Narration:

A host-side portability review for Linux projects targeting QNX 8.0.

## 01 — Scan the Linux daemon

Duration: 28 seconds

On-screen commands:

```sh
qnx-portcheck scan examples/linux-daemon --format text
```

Narration:

We scan the epoll and inotify Linux daemon from the repository. Findings are suggestions grounded in QNX 8.0 documentation; review them in project context.

Guard: requires scan-cli; otherwise this scene is a placeholder.

## 02 — Machine-readable reports

Duration: 24 seconds

On-screen commands:

```sh
qnx-portcheck scan examples/linux-daemon --format json
qnx-portcheck scan examples/linux-daemon --format sarif --out /tmp/qnx-demo/demo.sarif
python3 -m json.tool /tmp/qnx-demo/demo.sarif | head -20
```

Narration:

The same scan can emit JSON for tools and SARIF for code review. The bundled CI action in action/action.yml can upload SARIF to code scanning when permissions allow.

Guard: requires scan-cli; otherwise this scene is a placeholder.

## 03 — Generate draft build files

Duration: 30 seconds

On-screen commands:

```sh
cp -a examples/linux-daemon /tmp/qnx-demo/linux-daemon
qnx-portcheck scaffold /tmp/qnx-demo/linux-daemon --dry-run
qnx-portcheck scaffold /tmp/qnx-demo/linux-daemon
ls /tmp/qnx-demo/linux-daemon/qnx/build
head -6 /tmp/qnx-demo/linux-daemon/qnx/build/common.mk
```

Narration:

Scaffolding previews and writes draft build files in a temporary project copy. Each file carries a provenance header citing the exact qnx-ports build-files commit it follows. Generated files still need review and were not built with an SDP.

## 04 — Check mkifs buildfiles

Duration: 24 seconds

On-screen commands:

```sh
qnx-portcheck lint-buildfile examples/linux-daemon/qnx/filewatchd.build
qnx-portcheck lint-buildfile tests/fixtures/buildfiles/bad/multiple.build
```

Narration:

The clean example passes the host-side buildfile check. The intentionally bad fixture reports an error and exits with status one. Each rule links to the QNX 8.0 mkifs documentation.

## 05 — Evaluation

Duration: 24 seconds

On-screen commands:

```sh
(none)
```

Narration:

[EVAL_NUMBERS] Recall and precision against qnx-ports patches across at least fifteen projects belong here, filled from eval/RESULTS.md. We did not run this on a QNX target; we validated it against qnx-ports patches. This is a host tool; no QNX SDP was used. Suggestions follow QNX 8.0 documentation, and generated build files are drafts.

## 06 — Learn more

Duration: 14 seconds

On-screen commands:

```sh
(none)
```

Narration:

Read the repository tutorial for sources, caveats, and next steps.

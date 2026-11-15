# Devpost submission copy: qnx-portcheck (English)

Category: **Developer Tooling & Host Tools**
Bonus: **Best Codelab / Tutorial** ([docs/tutorial-port-linux-daemon-to-qnx8.md](../docs/tutorial-port-linux-daemon-to-qnx8.md))
Repository: https://github.com/tmdry4530/qnx-portcheck (must be public before submission)
Video: [VIDEO_URL] (YouTube, public, under 3 minutes)

---

## Inspiration

QNX 8.0 is now free for non-commercial use, and the [qnx-ports](https://github.com/qnx-ports) organization shows how
much open-source software people want to run on it. Every one of those ports starts the same way: someone reads
a Linux codebase line by line, looking for epoll, inotify, `/proc` files, `__linux__`-only branches and Linux link
flags, then works out what QNX 8.0 offers instead. That first pass is slow, repetitive and easy to get wrong.
We wanted a tool that does it in seconds and links every suggestion to the QNX documentation it relies on.

## What it does

qnx-portcheck is a host-side command-line tool (Python 3.10+, standard library only) for porting Linux C/C++
projects to QNX OS 8.0:

- **`qnx-portcheck scan <path>`** finds Linux-only constructs in C/C++ sources and in CMake, Make and Meson files,
  using 17 rules: epoll, inotify, eventfd, timerfd, signalfd, prctl, `sys/sysinfo.h`, sendfile, splice, accept4,
  pipe2, raw `syscall()`/`SYS_*`, `<linux/*.h>` headers, `/proc` paths, `__linux__`-only `#if` branches,
  `-lpthread`/`-ldl`/`-lrt`, and other Linux-only libraries. Each finding has a severity, a confidence level, a
  suggestion and a link to the QNX 8.0 documentation page supporting it. When no QNX 8.0 page supports a
  replacement, the tool says `manual review` and gives no link, instead of guessing. Output is text, JSON
  or SARIF 2.1.0, and `--fail-on error|warning|never` makes it usable as a CI gate (exit codes 0/1/2).
- **`qnx-portcheck scaffold <project>`** generates draft `qnx/build/` files (recursive Makefile, `common.mk`,
  `nto-aarch64-le` and `nto-x86_64-o` variants, plus a CMake toolchain file or Meson cross file) following the
  qnx-ports build-files layout at a pinned commit. It detects CMake, Meson, Autotools or plain Make.
- **`qnx-portcheck lint-buildfile <file>`** checks QNX `mkifs` buildfile syntax, with each check tied to the
  QNX 8.0 mkifs reference.
- A **GitHub Action** (`action/action.yml`) runs the scan on pull requests and uploads SARIF to GitHub code scanning.

Some of what the tool reports surprised us. QNX 8.0 *does* document `inotify_init()` (in libfsnotify, with the
`fsevmgr` service), `pipe2()` (in libc, with `O_CLOEXEC`/`O_NONBLOCK` only) and `accept4()` (in the io-sock stack).
qnx-portcheck reports these as `note` findings with the exact link flag or service needed, not as false "unsupported" errors.

## How QNX is used (evidence for reviewers)

qnx-portcheck is a host tool whose output is specifically meant for building software for QNX 8.0:

- `src/qnx_portcheck/rules/io_multiplex.py`: epoll, inotify, eventfd, timerfd and signalfd rules, mapping to
  QNX 8.0 `ionotify()`, `poll()`, libfsnotify, `timer_create()` and `sigwaitinfo()`.
- `src/qnx_portcheck/rules/linux_apis.py`: prctl to `pthread_setname_np()`, `accept4()` via io-sock and `libsocket.so`,
  `pipe2()` flag limits, and `__linux__` branches to the qcc `__QNX__` macro (value 800 for QNX 8.0) (`_ifdef`).
- `src/qnx_portcheck/rules/procfs.py`: `/proc` paths compared with the QNX procnto `/proc` layout
  (for example `/proc/self/exe` vs `/proc/<pid>/exefile`).
- `src/qnx_portcheck/rules/buildfiles.py`: `-lpthread`/`-ldl`/`-lrt`, which QNX 8.0 provides in libc (`_detect_standard`).
- `docs/rule-sources.md`: the URL, fetch time and a one-line quote for every QNX 8.0 page the rules cite, and the
  list of APIs (sendfile, splice, sysinfo, etc.) that QNX 8.0 docs don't cover, which are therefore `manual review`.
- `src/qnx_portcheck/scaffold.py` (`plan_scaffold`): qnx-ports-style `qnx/build/` generation for the `nto-aarch64-le`
  and `nto-x86_64-o` variants; provenance in `docs/scaffold-sources.md`.
- `src/qnx_portcheck/lint_buildfile.py` (`lint_text`): mkifs buildfile checks; rules in `docs/buildfile-lint-rules.md`.
- `examples/linux-daemon/`: a Linux epoll + inotify daemon and its `poll()` port, used in the tutorial.

**qnx-portcheck was not run on a QNX target. It was validated by comparing its findings against the changes made
by real qnx-ports patches.** We also did not build the generated scaffolds with the QNX SDP.

## How we built it

- Python 3.10+, standard library only (argparse, dataclasses, re, json), packaged with setuptools.
- A single-pass C/C++ lexer (`src/qnx_portcheck/lexer.py`) produces a comment-free view and a view with literals
  blanked, keeping line and column numbers. It handles escapes, raw strings (`R"x(...)x"`), encoding prefixes and
  C++14 digit separators. Rules match on these views, so commented-out code and text inside strings don't
  trigger findings. The `/proc` rule deliberately looks only at string literals.
- Each rule is a small object (`src/qnx_portcheck/rules/base.py`: `Rule`, `Hit`, `include_and_calls`) with an id,
  severity, confidence, suggestion, doc URL and detector, so adding a rule doesn't touch the scanner.
- Reports: text, a stable JSON schema (`CONTRACT.md`) used by our evaluation scripts, and SARIF 2.1.0 (`src/qnx_portcheck/report.py`).
- Documentation-first rules: we fetched each QNX 8.0 documentation page with curl and recorded the evidence
  before writing a suggestion. Pages that returned 404 (for example per-function pages for epoll, eventfd,
  sendfile and prctl) were recorded too.
- pytest suite (52 tests): a positive and a negative fixture for every rule, with an expected marker on every line
  that should produce a finding; lexer edge cases; JSON and SARIF structure; CLI exit codes; scaffold, lint and action tests.
- The code was written with OpenAI Codex CLI from written specifications, then reviewed and tested by the team.

## Challenges we ran into

- **No QNX SDP on our machines.** We chose a host-side tool and are explicit about what it hasn't done:
  no target runs and no SDP builds.
- **The documentation didn't say what we expected.** We assumed inotify, pipe2 and accept4 would be "unsupported".
  QNX 8.0 documents all three, so their severity dropped to `note`. epoll, eventfd, timerfd and signalfd have no
  C Library Reference pages; libepoll, libeventfd, libtimerfd and libsignalfd appear only as Wayland-on-Screen
  dependencies. The suggestions say exactly that, without claiming general availability.
- **False positives from lexing.** Code review found that a `//` or `/*` inside a string literal could hide real
  code from the scanner. We rewrote the lexer as one state machine and added regression tests.
- **Keeping the JSON schema stable** while the rules changed, because the evaluation scripts depend on it.

## Accomplishments that we're proud of

- 17 scan rules, each tied either to a fetched QNX 8.0 documentation page or to an explicit `manual review`, with no invented APIs.
- Three commands (scan, scaffold, lint-buildfile) plus a GitHub Action with SARIF upload, all in one installable package with no runtime dependencies.
- An evaluation against real qnx-ports patches: [EVAL_NUMBERS]
- A step-by-step tutorial that ports an epoll + inotify daemon and labels every step that couldn't be verified on a target.

## What we learned

- QNX 8.0 covers more of the Linux/BSD API surface than we assumed (inotify via fsevmgr, pipe2, accept4 via io-sock),
  so a good porting tool has to say "available, but link this and run that", not just "unsupported".
- QNX's native notification model (`ionotify()` with sigevents, which `select()` and `poll()` are built on) is the
  documented counterpart of epoll.
- QNX documents `/proc` as a debugging interface rather than a production monitoring API, which changes how code that reads `/proc` should be ported.

## What's next

- More rules, each added only after a QNX 8.0 page confirms the replacement.
- Run `scan`, `scaffold` and the generated `qnx/build/` files against a real QNX SDP 8.0 / QEMU setup, and publish the results.
- Wider evaluation across more qnx-ports projects, and automatic fix-it suggestions where the replacement is mechanical (for example, dropping `-lpthread` for QNX builds).

## Built with

Python, argparse, pytest, setuptools, SARIF 2.1.0, GitHub Actions, GitHub code scanning, CMake/Make/Meson (as scan
and scaffold inputs), QNX SDP 8.0 documentation, qnx-ports/build-files, OpenAI Codex CLI

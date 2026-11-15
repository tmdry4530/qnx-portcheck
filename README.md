# qnx-portcheck

**A host-side porting assistant for moving Linux C/C++ code to QNX OS 8.0.**

qnx-portcheck is a pure-Python (3.10+, standard library only) tool that runs on your development host.
It has been tested on Linux only. It has three commands:

| Command | What it does |
|---|---|
| `scan` | Finds Linux-only constructs in C/C++ sources and build files (epoll, inotify, eventfd, timerfd, signalfd, prctl, `sys/sysinfo.h`, `/proc` paths, `__linux__`-only branches, `-ldl`/`-lrt`/`-lpthread` and more). Each finding comes with a replacement suggestion and a link to the QNX 8.0 documentation page that supports it. If no QNX 8.0 page supports a replacement, the finding says `manual review` and has no link. Output: text, JSON or SARIF 2.1.0. |
| `scaffold` | Generates draft `qnx/build/` files (recursive `Makefile`, `common.mk`, `nto-aarch64-le/` and `nto-x86_64-o/` Makefiles, plus a CMake toolchain file or Meson cross file) in the style of [qnx-ports/build-files](https://github.com/qnx-ports/build-files) at commit `79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5`. Detects CMake, Meson, Autotools or plain Make. |
| `lint-buildfile` | Static syntax checks for QNX `mkifs` buildfiles (attributes, inline files, comments, quoting), each check tied to the QNX 8.0 mkifs reference. |

> **Scope and honesty statement.** qnx-portcheck targets **QNX OS 8.0** (QNX SDP 8.0). It is a **host tool**:
> it was developed and tested on Linux and **has not been run on a real QNX target or QEMU image**, and the
> generated build files have **not** been built with the QNX SDP (the SDP was not available to the authors).
> Rule suggestions cite only QNX 8.0 documentation pages that were actually fetched; see
> [docs/rule-sources.md](docs/rule-sources.md). The scan rules are evaluated by comparing findings with
> the changes real [qnx-ports](https://github.com/qnx-ports) patches made (see [Evaluation](#evaluation)).

## Requirements

- Python **>= 3.10** (from `pyproject.toml`). The runtime uses only the Python standard library.
- `pytest >= 7` for the test suite (`pip install -e '.[test]'`).
- QNX version targeted: **8.0**. Target for findings and scaffolds: QNX OS 8.0 on `aarch64le` / `x86_64`
  (the scaffold variants). The tool itself never executes anything on a QNX target and does not need the QNX SDP.
  Building the scaffolded `qnx/build/` files needs a QNX SDP 8.0 environment (`qcc` toolchain), which this project did not use.

## Install

```bash
git clone https://github.com/tmdry4530/qnx-portcheck.git
cd qnx-portcheck
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[test]'
qnx-portcheck --version        # qnx-portcheck 0.1.0
pytest -q
```

## Usage

### scan

```bash
qnx-portcheck scan <path> [--format text|json|sarif] [--out FILE] [--fail-on error|warning|never]
```

- `<path>`: a directory (scanned recursively, hidden directories skipped) or a single file.
- Files scanned: C/C++ `.c .cc .cpp .cxx .h .hh .hpp .hxx`; build files `CMakeLists.txt`, `*.cmake`,
  `Makefile`/`makefile`/`GNUmakefile`, `*.mk`, `meson.build`.
- Comments are ignored, and string literal contents are ignored by every rule except the `/proc` path rule,
  which looks only at string literals. Member and namespace-qualified calls (`obj.splice()`, `std::list::splice`)
  don't match.
- `--format`: `text` (default), `json` (schema in [CONTRACT.md](CONTRACT.md)), or `sarif` (SARIF 2.1.0, for GitHub code scanning).
- `--out FILE`: write the report to a file instead of stdout.

Exit codes:

| Code | Meaning |
|---|---|
| 0 | No finding at or above the `--fail-on` threshold |
| 1 | At least one finding at or above the threshold |
| 2 | Usage error (bad arguments or path not found) |

`--fail-on error` (default) counts only `error` findings; `--fail-on warning` counts `error` and `warning`;
`--fail-on never` always exits 0 unless there is a usage error.

Example (the epoll + inotify daemon used in the tutorial):

```text
$ qnx-portcheck scan examples/linux-daemon --fail-on never
src/filewatchd.c:6:1: warning [LNX-EPOLL] Linux epoll header <sys/epoll.h>
    suggestion: QNX 8.0 documents ionotify() as corresponding to Linux epoll(); poll()/select() are also available. ...
    doc: https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html
...
11 finding(s): 0 error, 5 warning, 6 note in 3 file(s) scanned
```

JSON finding fields: `rule_id`, `severity` (`error|warning|note`), `file` (relative to `root`, POSIX), `line`, `col`,
`message`, `suggestion`, `doc_url` (QNX 8.0 doc URL or `null`), `confidence` (`high|medium|manual-review`).

### scaffold

```bash
qnx-portcheck scaffold <project-root> [--name NAME] [--out DIR] [--build-system cmake|meson|autotools|make] [--force] [--dry-run]
```

Writes to `<project-root>/qnx/build/` by default. Existing files are skipped unless `--force` is given; `--dry-run`
only prints what would be created. Each generated file has a provenance header naming the upstream qnx-ports file
it follows (see [docs/scaffold-sources.md](docs/scaffold-sources.md)). Exit code 0 on success, 2 if the build system can't be detected.
The printed build hint (`QNX_PROJECT_ROOT="$(pwd)" make -C qnx/build install`) requires a QNX SDP environment and
is not executed by the tool.

### lint-buildfile

```bash
qnx-portcheck lint-buildfile <file> [<file> ...] [--format text|json]
```

Exit code 1 if any `error` diagnostic is found, 0 otherwise, 2 if a file can't be read. Rules and their
QNX 8.0 mkifs documentation anchors are in [docs/buildfile-lint-rules.md](docs/buildfile-lint-rules.md).
This is a static syntax aid, not a full mkifs parser, and it was not checked against the real `mkifs` binary.

## GitHub Action

A composite action in [`action/`](action/) installs qnx-portcheck, runs `scan --format sarif` and uploads the
SARIF file to GitHub code scanning with `github/codeql-action/upload-sarif@v4`.

```yaml
permissions:
  contents: read
  security-events: write
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: tmdry4530/qnx-portcheck/action@main
        with:
          path: "."
```

Inputs: `path` (default `.`), `sarif-file` (default `qnx-portcheck.sarif`), `python-version` (default `3.12`),
`upload` (default `true`), `category` (default `qnx-portcheck`). Output: `sarif-file`. A full workflow is in
[examples/workflows/qnx-portcheck.yml](examples/workflows/qnx-portcheck.yml); see [action/README.md](action/README.md)
for fork pull requests (no write token: set `upload: "false"`). Pin the action to a commit SHA for production use.

## Scan rules

"Verified" means the suggestion and `doc_url` come from a QNX 8.0 documentation page fetched on 2026-11-15
(URL, fetch time and quote in [docs/rule-sources.md](docs/rule-sources.md)). "Manual review" means no QNX 8.0
page confirmed a replacement, so the suggestion is `manual review` and `doc_url` is `null`.

| Rule | Severity | Detects | QNX 8.0 doc basis | Status |
|---|---|---|---|---|
| LNX-EPOLL | warning | `<sys/epoll.h>`, `epoll_create/create1/ctl/wait/pwait/pwait2()` | `ionotify()` "corresponds to the Linux epoll() function"; `poll()`. No epoll page in the C Library Reference | verified |
| LNX-INOTIFY | note | `<sys/inotify.h>`, `inotify_init/init1/add_watch()` | Available in libfsnotify (`-l fsnotify`); needs `fsevmgr` | verified |
| LNX-EVENTFD | warning | `<sys/eventfd.h>`, `eventfd()`, `eventfd_read/write()` | libeventfd listed only for Wayland on Screen (`screen.notify_fd` package) | verified |
| LNX-TIMERFD | warning | `<sys/timerfd.h>`, `timerfd_create/settime/gettime()` | `timer_create()` + `timer_settime()` in libc | verified |
| LNX-SIGNALFD | warning | `<sys/signalfd.h>`, `signalfd()` | `sigwaitinfo()` / `sigtimedwait()` in libc | verified |
| LNX-PRCTL | error | `<sys/prctl.h>`, `prctl()` | `pthread_setname_np()` for `PR_SET_NAME`; other options manual review | verified |
| LNX-SYSINFO | error | `<sys/sysinfo.h>`, `sysinfo()`, `get_nprocs*()`, `get_(av)phys_pages()` | none found | manual review |
| LNX-SENDFILE | error | `<sys/sendfile.h>`, `sendfile()` | none found | manual review |
| LNX-SPLICE | error | `splice()`, `vmsplice()` | none found | manual review |
| LNX-ACCEPT4 | note | `accept4()` | Listed in io-sock Networking APIs; link `libsocket.so` | verified |
| LNX-PIPE2 | note (warning with `O_DIRECT`) | `pipe2()` | In libc; only `O_CLOEXEC` and `O_NONBLOCK` | verified |
| LNX-SYSCALL | error | `<sys/syscall.h>`, `syscall()`, `SYS_*` / `__NR_*` | none found | manual review |
| LNX-LINUX-HEADER | error | `#include <linux/...>` | none found | manual review |
| LNX-PROCFS | warning | String literals starting with `/proc` | QNX `/proc` layout differs (`/proc/<pid>/exefile` etc.) and is meant for debugging | verified |
| LNX-LINUX-IFDEF | warning | `#if/#ifdef/#elif` on `__linux__`, `__linux`, `__gnu_linux__`, `linux`, unless the same condition also tests `__QNX__`/`__QNXNTO__` | qcc defines `__QNX__` (800 for 8.0); `__QNXNTO__` deprecated | verified |
| LNX-LINK-FLAGS | warning | `-lpthread`, `-ldl`, `-lrt`; CMake `target_link_libraries(... pthread dl rt ${CMAKE_DL_LIBS})`; Meson `find_library`/`dependency` | `pthread_create()`, `dlopen()`, `clock_gettime()` are in libc | verified |
| LNX-LINK-FLAGS-OTHER | warning | `-lsystemd`, `-ludev`, `-lcap`, `-laio`, `-lnuma`, `-lutil` | none found | manual review |
| PORT-OS-IFDEF | note | `#if/#ifdef/#elif` on BSD/macOS/Solaris/AIX/HP-UX/Haiku/Cygwin macros with no `__QNX__`/`__QNXNTO__` | qcc defines `__QNX__` | verified |
| PORT-QNXNTO | note | conditional tests `__QNXNTO__` but not `__QNX__` | `__QNXNTO__` deprecated (manifests) | verified |
| PORT-MINMAX | warning | file includes `<sys/param.h>`, uses `MIN()`/`MAX()`, defines neither; reported at the last `#include` before the first use | none (`<sys/param.h>` is not POSIX) | manual review |
| PORT-MINMAX-DEFINE | warning | `#define min(`/`#define max(` not under `#ifndef min`/`max` | QNX `<stdlib.h>` defines `min()`/`max()` | verified |
| PORT-SA-RESTART | warning | `SA_RESTART` used in a file that never tests or defines it | QNX `struct sigaction` has no `SA_RESTART` flag | verified |
| PORT-TIMEVAL | note | header file uses `struct timeval` but includes neither `<sys/time.h>` nor `<sys/select.h>` | POSIX `<sys/time.h>` (no QNX page) | manual review |
| BLD-CMAKE-PLATFORM | warning | CMake `if`/`elseif` testing APPLE, LINUX, BSD, CYGWIN, ANDROID, IOS or `CMAKE_(HOST_)SYSTEM_NAME` in a chain that never names QNX | QNX porting guide: CMake conditionals on `CMAKE_SYSTEM_NAME` need extending for QNX | verified |
| BLD-AUTOCONF-HOST | warning | each OS label of a `case $host…`/`AS_CASE([$host_os]…)` dispatch in configure.ac/project .m4 files that has no `qnx`/`nto` label | QNX configure hooks use `nto*` targets | verified |

## Evaluation

[EVAL_NUMBERS]

The scan rules are evaluated against open-source projects that the [qnx-ports](https://github.com/qnx-ports)
organization has already ported: scan the upstream base commit, then compare findings with the files and lines
the qnx-ports patch changed. Results, scripts and raw outputs will be in `eval/`. Only numbers from actual runs are reported.

## Tutorial

[Port a Linux epoll + inotify daemon to QNX 8.0 with qnx-portcheck](docs/tutorial-port-linux-daemon-to-qnx8.md),
with example sources in [examples/linux-daemon/](examples/linux-daemon/).

## Development

```bash
pip install -e '.[test]'
pytest -q
```

Internal interfaces (CLI, JSON schema, exit codes) are defined in [CONTRACT.md](CONTRACT.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).

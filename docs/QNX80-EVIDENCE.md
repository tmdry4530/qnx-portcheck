# QNX 8.0 evidence for qnx-portcheck

This document supports submission checklist item #8. qnx-portcheck is a host-side Python tool (`scan`, `scaffold`, `lint-buildfile`) that analyses Linux projects and emits QNX 8.0-oriented findings, draft recursive-make scaffolding, and mkifs buildfile lint diagnostics. Line numbers refer to commit `1bf6e52`.

## Status

This is a host tool. It runs on the developer's Linux, macOS, or Windows machine, not on QNX. We have not installed or used the QNX Software Development Platform (SDP), compiled anything with `qcc` or `q++`, or run the real `mkifs` binary. We have not built the generated scaffold with the SDP or run anything on a QNX target or QEMU. `scaffold` and `lint-buildfile` are static generators/checkers and have not been validated against real `mkifs` or `qcc`.

Every documentation URL in the tables below is under `https://www.qnx.com/developers/docs/8.0/` and returned HTTP 200 to `curl -L` on 2026-11-16 11:31–11:32 KST (Asia/Seoul). URLs that failed or live outside `/docs/8.0/` are not used as evidence links; see the verification log.

## 1. Scan rules that cite QNX 8.0 documentation

Rules live under `src/qnx_portcheck/rules/`. Each rule may set `Rule.doc_url` (and sometimes a per-hit `doc_url`). Findings are emitted by the scanner; SARIF `helpUri` is copied from `rule.doc_url` in `src/qnx_portcheck/report.py:70-71`.

| Rule ID | QNX 8.0-specific behavior | File and lines | QNX 8.0 documentation |
|---|---|---|---|
| LNX-EPOLL | Flags Linux epoll headers/APIs. Suggests `ionotify()` as QNX's documented correspondence to Linux epoll; `poll()` and `select()` are also available. No epoll page is in the 8.0 C Library Reference; libepoll is mentioned only on the Screen/Wayland page. | `src/qnx_portcheck/rules/io_multiplex.py:26-35` (URL at 34) | [ionotify](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html); [poll](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/poll.html); [select](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/select.html); [Screen/Wayland](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.screen/topic/manual/cscreen_wayland.html) |
| LNX-INOTIFY | Flags inotify use. QNX 8.0 provides `inotify_init()` and `inotify_add_watch()` in libfsnotify; link with `-l fsnotify`; `fsevmgr` must be running. | `io_multiplex.py:36-43` (URL at 42) | [inotify_init](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_init.html); [inotify_add_watch](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_add_watch.html); [fsevmgr](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/f/fsevmgr.html) |
| LNX-EVENTFD | `eventfd` is not in the QNX 8.0 C Library Reference; libeventfd is listed only in the Screen/Wayland page. Otherwise suggests `pipe()`/`pipe2()` with `poll()`. | `io_multiplex.py:44-51` (URL at 50) | [Screen/Wayland](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.screen/topic/manual/cscreen_wayland.html); [pipe](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pipe.html) |
| LNX-TIMERFD | `timerfd` is not in the 8.0 C Library Reference (libtimerfd appears only on the Screen/Wayland page). The documented libc alternative is `timer_create()` with a sigevent, armed using `timer_settime()`. | `io_multiplex.py:52-60` (URL at 59) | [timer_create](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/timer_create.html); [Screen/Wayland](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.screen/topic/manual/cscreen_wayland.html) |
| LNX-SIGNALFD | `signalfd` is not in the 8.0 C Library Reference (libsignalfd appears only on the Screen/Wayland page). Documented libc alternatives are `sigwaitinfo()` and `sigtimedwait()`. | `io_multiplex.py:61-67` (URL at 66) | [sigwaitinfo](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/sigwaitinfo.html); [Screen/Wayland](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.screen/topic/manual/cscreen_wayland.html) |
| LNX-PRCTL | `prctl()` is not in the QNX 8.0 C Library Reference. For `PR_SET_NAME`, suggests `pthread_setname_np()`; other options need manual review. | `src/qnx_portcheck/rules/linux_apis.py:77-83` (URL at 81) | [pthread_setname_np](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_setname_np.html) |
| LNX-ACCEPT4 | `accept4()` is provided by the QNX 8.0 io-sock stack with FreeBSD semantics. io-sock apps link against `libsocket.so` (`-l socket`); there is no `libsocket.a`. | `linux_apis.py:93-100` (URL at 98) | [io-sock socket API](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html); [migration guide](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html) |
| LNX-PIPE2 | `pipe2()` is in QNX 8.0 libc but supports only `O_CLOEXEC` and `O_NONBLOCK`. | `linux_apis.py:101-107` (URL at 105) | [pipe2](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pipe2.html) |
| LNX-LINUX-IFDEF | Flags Linux-only preprocessor conditions. Suggests adding a QNX branch: qcc defines `__QNX__` (800 for QNX 8.0); `__QNXNTO__` is deprecated. | `linux_apis.py:110-118` (URL at 116) | [Neutrino-specific definitions](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/devel_Neutrino_specific.html); [manifests](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/manifests.html) |
| LNX-PROCFS | Flags Linux `/proc` paths. QNX 8.0 procnto has a different layout (`/proc/<pid>/as`, `cmdline`, `ctl`, `exefile`; `/proc/self/` is the caller's address space). Linux `/proc/self/exe` does not exist; procnto exposes `/proc/<pid>/exefile`. | `src/qnx_portcheck/rules/procfs.py:9-21, 37-38` (URL at 21) | [process filesystem](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/process_proc_filesystem.html); [procnto](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/p/procnto.html) |
| LNX-LINK-FLAGS | Flags `-lpthread`, `-ldl`, `-lrt` and CMake/Meson equivalents. QNX 8.0 documents `pthread_create()`, `dlopen()`, and `clock_gettime()` in libc, which qcc usually links automatically. | `src/qnx_portcheck/rules/buildfiles.py:9-12` (URLS), `79-84` (per-hit URL), `93-99` (rule; default URL is pthread_create) | [pthread_create](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_create.html); [dlopen](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/dlopen.html); [clock_gettime](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/clock_gettime.html) |
| PORT-OS-IFDEF | Flags a non-Linux Unix branch without a QNX case. qcc defines `__QNX__` (800 for QNX 8.0). | `src/qnx_portcheck/rules/platform.py:87-89` | [Neutrino-specific definitions](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/devel_Neutrino_specific.html) |
| PORT-QNXNTO | Flags `__QNXNTO__` without `__QNX__`. QNX 8.0 lists `__QNXNTO__` as deprecated; qcc defines `__QNX__` (800 for QNX 8.0). | `platform.py:87-90` | [manifests](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/manifests.html) |
| PORT-MINMAX-DEFINE | Flags `#define min()`/`max()` clashes with QNX 8.0 `<stdlib.h>` macros (C only). | `platform.py:87, 92` | [max](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/max.html); [min](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/min.html) |
| PORT-SA-RESTART | Flags `SA_RESTART`, which is not a documented QNX 8.0 sigaction flag. Documented flags are `SA_NOCLDSTOP`, `SA_NOCLDWAIT`, `SA_NODEFER`, `SA_ONSTACK`, `SA_RESETHAND`, and `SA_SIGINFO`. | `platform.py:87, 93` | [sigaction structure](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/sigaction_struct.html) |
| BLD-AUTOCONF-HOST | Flags an autoconf host/target OS case without a QNX / `*-nto-qnx*` arm; suggestion includes `aarch64-unknown-nto-qnx8.0.0`. | `src/qnx_portcheck/rules/build_platform.py:105-106` (DOC2, RULES) | [preconfigure hook](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_hook_preconfigure.html); [GNU configure](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_GNU_configure.html) |
| BLD-CMAKE-PLATFORM | Flags a CMake platform condition without a QNX case. | `build_platform.py:104-106` | No URL: the in-code URL is outside `/docs/8.0/`; no QNX 8.0 CMake page returning 200 was found after probing candidate paths. |

## 2. Scaffold: QNX 8.0 recursive-make layout

`src/qnx_portcheck/scaffold.py` uses a pattern recorded as qnx-ports/build-files at `79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5`; see also `docs/scaffold-sources.md`. The default output directory is `qnx/build` (line 204). Its provenance header (lines 48-53) marks every generated file as a draft and says it was not built or run on a QNX target by qnx-portcheck. The CLI hint (line 235) says the install command requires a QNX SDP environment and is not executed by this tool.

| Scaffold detail | Implementation evidence | QNX 8.0 documentation and limits |
|---|---|---|
| Squashed OS-CPU-VARIANT directories | `plan_scaffold` emits `nto-aarch64-le/Makefile` and `nto-x86_64-o/Makefile` (`scaffold.py:209-210`). | [addvariant](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/a/addvariant.html) describes squashing levels and gives `addvariant -i OS/CPU/VARIANT nto x86_64 o`, creating `nto-x86_64-o`. [Collapse convention](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_COLLAPSE.html) says unnecessary OS/CPU/VARIANT levels can be collapsed by joining names with dashes. The official aarch64 example uses `addvariant nto aarch64 o.le` (directory `nto-aarch64-o.le`); this scaffold follows qnx-ports/build-files spelling `nto-aarch64-le`, not that exact example. |
| Recursing top Makefile | Generated top Makefile body at line 207 contains `LIST=OS` and the QRECURSE/`recurse.mk` include idiom. | [addvariant](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/a/addvariant.html); [recursive structure](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_STRUCTURE.html); [make conventions](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent.html). The addvariant squashed-directory example uses `LIST=OS CPU VARIANT`; this scaffold follows qnx-ports/build-files `ports/cJSON/Makefile` and emits `LIST=OS`. |
| `common.mk` and variant makefiles | `common.mk` lines 56-72 uses `ifndef QCONFIG`, `QCONFIG=qconfig.mk`, includes `$(QCONFIG)` and `$(MKFILES_ROOT)/qmacros.mk`, then includes `$(MKFILES_ROOT)/qtargets.mk`. Variant Makefiles at lines 209-210 contain only `include ../common.mk`. | [qconfig.mk](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_qconfig.mk.html) shows the `QCONFIG`/`qtargets.mk` pattern; [USEMAC](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_USEMAC.html) names qconfig.mk, qrules.mk, and qtargets.mk as standard includes; [SPEC](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_SPEC.html) and [STRUCTURE](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_STRUCTURE.html) describe bottom-level variant makefiles. A dedicated qmacros.mk page returned 404 and is not linked. |
| qcc / q++ and `-Vgcc_*` targets | Autotools/make `common.mk` and the CMake toolchain set the compiler to qcc/q++ with `-Vgcc_$(OS)$(CPUVARDIR)` or `-V${QNX_GCC_VERSION}gcc_nto${CMAKE_SYSTEM_PROCESSOR}` (`scaffold.py:103-104, 171-172, 185-186`; CMake also 112-113). | [qcc](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html) documents `qcc -Vgcc_ntox86_64` and `qcc -Vgcc_ntoaarch64le`, and says qcc automatically links some default libraries including libc. [qconfig.mk](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_qconfig.mk.html) documents CPUVARDIR as CPUDIR plus a variant suffix (for example, aarch64le or x86_64). |
| `-D_QNX_SOURCE` | `common.mk` sets `CFLAGS += -D_QNX_SOURCE` (line 70); Meson cross-file sets `c_args`/`cpp_args` to `-D_QNX_SOURCE` (lines 157-158). | [qcc](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html) says to use `-D` to define `_QNX_SOURCE` when declarations from headers are needed; gnu* `-std` variants define it automatically. |
| CMake toolchain | Sets `CMAKE_SYSTEM_NAME QNX`, `QNX TRUE`, and C/C++ compilers to `$QNX_HOST/usr/bin/qcc` and `q++` (lines 93-104). | [qcc](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html) documents the compiler. No QNX 8.0 CMake documentation page returning 200 was found, so the CMake setup has no verified 8.0-specific page. |

## 3. mkifs buildfile lint (BF-* rules)

`src/qnx_portcheck/lint_buildfile.py` is a static syntax checker for mkifs buildfiles. The mkifs URL is set at line 11; `_diag` at lines 25-27 appends `#mkifs__Buildfiles` or `#mkifs__Attributes`. These anchors were present in the 8.0 page HTML on 2026-11-16. The BOOL/VALUE closed-world attribute sets are at lines 12-13. Human-readable grounding is in `docs/buildfile-lint-rules.md:1-18`, which cites the same page and states the checker has not been validated against the real mkifs binary.

| Rule ID | Severity | Check | Implementation line | Anchor |
|---|---|---|---:|---|
| BF-ATTR-UNTERMINATED | error | Attribute `[` has no closing `]` | 131 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-ATTR-MULTIPLE-GROUPS | error | More than one bracket group before a file spec | 138 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-ATTR-EQUALS-SPACING | error | Whitespace around attribute `=` | 141 | [Attributes](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Attributes). The code tags this diagnostic as `Attributes`; the lint-rules prose cites Buildfiles for the no-spaces sentence. |
| BF-ATTR-UNKNOWN | warning | Attribute name is outside the documented BOOL/VALUE lists (lines 12-13) | 147 | [Attributes](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Attributes) |
| BF-ATTR-KIND | error | Boolean/value attribute used in the opposite form; `compress` may be either | 148-151 | [Attributes](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Attributes) |
| BF-COMMENT-SPACE | warning | `#` glued to a command; a separating space is needed | 116 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-INLINE-OPEN-CONTENT | error | Content after `{` on the opening line | 164 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-INLINE-CLOSE-CONTENT | error | Content before `}` on the closing line | 105 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-INLINE-UNCLOSED | error | Inline file not closed before EOF | 181 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-INLINE-STRAY-CLOSE | error | `}` outside an inline file | 124 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-FILE-QUOTE | error | Unbalanced filename double quote | 175 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |
| BF-PATH-BACKSLASH | note | Backslash used as a path separator; recommends `/` | 178 | [Buildfiles](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html#mkifs__Buildfiles) |

This is a static syntax aid, not a full mkifs parser. It has not been validated against real mkifs or the SDP.

## 4. Action and tutorial (host-side, 8.0-oriented)

The GitHub composite action `action/action.yml` runs `qnx-portcheck scan` on the CI host and may upload SARIF (lines 37-60). `action/README.md:3` says it runs the host-side tool and never runs anything on a QNX target. SARIF `helpUri` carries the 8.0 rule `doc_url` (`report.py:70-71`). This is host automation around the documented scanner, not a target run; see the scan-rule table above.

`docs/tutorial-port-linux-daemon-to-qnx8.md` walks through scanning, scaffolding, and linting a Linux epoll+inotify daemon for QNX 8.0. It cites verified `ionotify.html`, `poll.html`, `select.html`, `inotify_init.html`, `inotify_add_watch.html`, `fsevmgr.html`, and `mkifs.html` pages. `epoll_create.html` returned 404 (tutorial line 93) and is not used as a link. The tutorial records “NOT VERIFIED: no QNX SDP was available to the authors” (line 140) and “NOT VERIFIED ON A QNX TARGET” (line 144). The scaffold step (lines 113-129) names `nto-aarch64-le` and `nto-x86_64-o`. The lint step (lines 152-155) runs `lint-buildfile` on `examples/linux-daemon/qnx/filewatchd.build`, an illustrative mkifs snippet containing `fsevmgr`, `libfsnotify.so.1`, and `[perms=0755] /usr/bin/filewatchd=filewatchd`. The tutorial was not executed on SDP or a target.

## 5. Rules without a QNX 8.0 `doc_url`

These scanner rules have `doc_url = null` or suggest manual review; no URL is supplied here:

- LNX-SYSINFO, LNX-SENDFILE, LNX-SPLICE, LNX-SYSCALL, and LNX-LINUX-HEADER (`linux_apis.py:84-92, 108-109`).
- LNX-LINK-FLAGS-OTHER (`buildfiles.py:100-101`).
- PORT-MINMAX and PORT-TIMEVAL (`platform.py:91, 94`). `PORT-TIMEVAL`'s DOC entry is a POSIX page, not under `/docs/8.0/`.
- BLD-CMAKE-PLATFORM is covered above: its in-code URL is outside `/docs/8.0/` and no verified QNX 8.0 CMake page was found.

## URL verification log

URLs were checked with `curl -sS -L` (follow redirects); status is final after redirects. No redirects were observed (`num_redirects=0` in an earlier pass the same morning). The date column is KST.

| URL | Final HTTP status | Date (KST) |
|---|---:|---|
| `https://www.qnx.com/developers/docs/8.0/` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/clock_gettime.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/dlopen.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_add_watch.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_init.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/max.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/min.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/manifests.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pipe.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pipe2.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/poll.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_create.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_setname_np.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/select.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/sigaction_struct.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/sigwaitinfo.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/timer_create.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/devel_Neutrino_specific.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_COLLAPSE.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_GNU_configure.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_SPEC.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_STRUCTURE.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_USEMAC.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_hook_preconfigure.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_qconfig.mk.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_qtargets.mk.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/process_proc_filesystem.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/a/addvariant.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/f/fsevmgr.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/p/procnto.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html` | 200 | 2026-11-16 11:31–11:32 |
| `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.screen/topic/manual/cscreen_wayland.html` | 200 | 2026-11-16 11:31–11:32 |

The following were checked in the same window and are not used as evidence links:

- 404: `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/epoll_create.html` (also recorded in `docs/tutorial-port-linux-daemon-to-qnx8.md:93`; LNX-EPOLL cites `ionotify.html` instead).
- 404: `https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_qmacros.mk.html` (probed as a possible qmacros.mk page).
- 200 but outside `/docs/8.0/`: `https://www.qnx.com/developers/docs/qnxeverywhere/`, `https://www.qnx.com/developers/docs/qnxeverywhere/com.qnx.doc.qpg/topic/port_CMake.html`, and `https://www.qnx.com/developers/docs/qnxeverywhere/com.qnx.doc.qpg/topic/port_Source_code.html`. These are not linked as QNX 8.0 evidence.

Other candidate 8.0 paths were probed earlier the same morning (CMake pages, `_QNX_SOURCE` topic paths, and guessed `make_convent_*` names) and returned 404; they are not listed as evidence links.

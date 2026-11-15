# Rule tuning on dev1/tune (2026-11-15 KST)

> **Status:** the 16 projects labelled `holdout` by the harness split below were read during tuning and are now
> classified as **seen during tuning**. They are not a holdout. A fresh holdout of unseen projects is being measured
> separately; its results are not here yet. Where this file says "holdout" it means the harness's split name.

Scanner commits: `85a5ca9` (perf, findings unchanged, evidence in `perf/`), `5118669` (rules).
Measurement: `PATH=<venv>/bin:$PATH python eval/run_eval.py --work-dir <checkouts>` (window ±3, merge gap 3),
same 33 pinned projects and patches as the 0.1.0 baseline. Tune-only iterations used `--split tune`.

## Split and what was looked at (read this first)

The split is the harness's `--split` (main `0b9b4a1`, METHOD.md "Tune / holdout split"): names sorted, index 0, 2, 4…
are **tune** (17), index 1, 3, 5… are **holdout** (16).

- tune: asio, aws-c-common, c-ares, chrony, fribidi, gnutls, iperf3, libevent, libusb, libwebsockets, libyaml, lua,
  nghttp2, open-amp, re2, strongswan, unbound
- holdout: avahi, aws-c-io, check, dlt-daemon, glog, googletest, jansson, libmetal, libuv, libxml2, lldpd, mosquitto,
  ntpsec, pistache, s2n-tls, tinyxml2

**Contamination disclosure.** Before this split was published I had been told to use the *other* parity (1-based even
positions = tuning), which is exactly today's holdout set. Under that instruction I read the full QNX patches
(`*.qnx.diff`) of all 16 of today's holdout projects and the EPOLL/TIMERFD findings in their result JSON, and drafted
rule ideas from them (s2n-tls MIN/MAX, pistache/aws-c-io BSD/Apple `#if`s, s2n-tls `if(APPLE)`, lldpd host-OS list,
mosquitto/pistache/libuv/dlt-daemon/aws-c-io epoll/timerfd placement). After the split changed I:

- kept only rules that have tune-side evidence or that the Engineering Lead asked for explicitly, and re-based
  each rule's evidence on tune cases and official docs;
- dropped two drafted rules whose only motivation was holdout patches: a Meson `host_machine.system()` rule
  (pistache) and a build-probe rule for Linux-only headers (mosquitto), and dropped the "report the end of a CMake
  if/elseif chain" variant (aws-c-io);
- did not open holdout patches or holdout result JSON again; holdout per-rule numbers below come from
  `summary.json` `aggregate.by_split`.

These 16 projects are therefore **not a generalisation check** (now classified as seen during tuning), especially PORT-MINMAX (designed after seeing
s2n-tls; the tune split has no MIN/MAX site at all) and PORT-OS-IFDEF.

## Rules added or changed

| rule | tune evidence (patch sites) | doc / basis |
|---|---|---|
| PORT-OS-IFDEF | asio multicast.cpp `|| defined(__OpenBSD__)` list and `#if defined(__hpux)`; strongswan pfkey `__FreeBSD__` branches | QNX: qcc defines `__QNX__` |
| PORT-QNXNTO | c-ares ares.h `defined(__QNXNTO__)` → `__QNX__`; gnutls/libusb use `__QNXNTO__` | QNX manifests: `__QNXNTO__` deprecated |
| PORT-MINMAX | none on tune (asked for by EL; s2n-tls is holdout) | POSIX has no `<sys/param.h>`; doc_url null, manual review |
| PORT-MINMAX-DEFINE | strongswan utils/align.h wraps `max`/`min` in `#ifndef` | QNX `<stdlib.h>` defines `min()`/`max()` |
| PORT-SA-RESTART | asio socket_types.hpp `ASIO_OS_DEF_SA_RESTART`, libevent signal.c, chrony configure (not scanned) | QNX `struct sigaction` lists no SA_RESTART |
| PORT-TIMEVAL | unbound (4 headers), iperf3 timer.h, nghttp2 util.h, libusb examples add `<sys/time.h>` | POSIX `<sys/time.h>`; doc_url null. Restricted to headers after tune run: all files 121 findings / 6 TP, headers 31 / 4 |
| BLD-CMAKE-PLATFORM | aws-c-common `if (UNIX AND NOT APPLE AND NOT ${CMAKE_SYSTEM_NAME} MATCHES FreeBSD|OpenBSD)` | QNX porting guide (CMake page) |
| BLD-AUTOCONF-HOST | libusb configure.ac `case $host in` gains `*-qnx* | *-nto*` | QNX build-hooks `nto*` targets. After the first tune run `aclocal.m4` and third-party macro files (acx_, lib-, gettext…) were excluded: 275 → 59 findings, TP unchanged (4) |
| Linux-only guard | (precision) | qcc never defines `__linux__`; LNX-LINUX-IFDEF on the guard stays |
| build-probe guard | all 27 tune EPOLL/TIMERFD findings (see below) | code compiled only if the project's probe succeeds |

## Why LNX-EPOLL (72) and LNX-TIMERFD (31) had 0 TP

Tune split, baseline 0.1.0 results: 27 of the 103 findings (c-ares 6 EPOLL, libevent 12 EPOLL + 3 TIMERFD,
libusb 5 TIMERFD, asio 1 TIMERFD).

- **Not a matching-window problem.** None of the 27 is in a file the port touched at all, so no window size would
  match them.
- **The patches fix a different place: the build configuration.** Every one of the 27 sits inside a branch enabled
  by a configure/CMake probe: c-ares `#ifdef HAVE_SYS_EPOLL_H` (CMake `CHECK_INCLUDE_FILES(sys/epoll.h …)`),
  libevent `epoll.c` wrapped in `#ifdef EVENT__HAVE_EPOLL` and `#ifdef EVENT__HAVE_SYS_TIMERFD_H`, libusb
  `#ifdef USBI_TIMERFD_AVAILABLE` (configure `AC_CHECK_HEADER([sys/timerfd.h] …)`), asio
  `#if defined(ASIO_HAS_TIMERFD)`. On QNX the probe fails (or the port turns it off), the code is compiled out,
  and the port changes nothing there. When a port does need a change, it is in the build files or in the
  dispatch code that picks the backend.
- Fix: findings of these facility rules are dropped inside such probe branches (and inside `__linux__`-only
  branches). Tune: LNX-EPOLL 18 → 4, LNX-TIMERFD 9 → 0, LNX-EVENTFD 7 → 0, with no TP lost (there were none).

## Before / after (micro)

Baseline: `0b9b4a1` RESULTS.md (scanner 0.1.0, source 511aa2e). After: this branch, scanner `5118669`.

| split | metric | before | after |
|---|---|---|---|
| tune (17) | source-site recall | 0.052 (6/115) | 0.157 (18/115) |
| tune | non-test source recall | 0.060 (6/100) | 0.150 (15/100) |
| tune | build-site recall | 0.000 (0/48) | 0.083 (4/48) |
| tune | precision | 0.026 (10/384) | 0.035 (27/761) |
| tune | precision in patched files | 0.286 (10/35) | 0.206 (27/131) |
| seen during tuning (16; harness split `holdout`) | source-site recall | 0.051 (10/197) | 0.284 (56/197) |
| seen during tuning | non-test source recall | 0.057 (9/158) | 0.260 (41/158) |
| seen during tuning | build-site recall | 0.000 (0/58) | 0.035 (2/58) |
| seen during tuning | precision | 0.017 (10/591) | 0.056 (61/1089) |
| seen during tuning | precision in patched files | 0.102 (10/98) | 0.218 (61/280) |
| all (33) | source-site recall | 0.051 (16/312) | 0.237 (74/312) |
| all | non-test source recall | 0.058 (15/258) | 0.217 (56/258) |
| all | build-site recall | 0.000 (0/106) | 0.057 (6/106) |
| all | precision | 0.021 (20/975) | 0.048 (88/1850) |
| all | precision in patched files | 0.150 (20/133) | 0.214 (88/411) |

Gains on the 16 seen-during-tuning projects by rule (from `summary.json` by_split, split `holdout`): PORT-MINMAX 23 sites (s2n-tls), PORT-OS-IFDEF 23 sites,
LNX-LINUX-IFDEF 7, BLD-CMAKE-PLATFORM 2. Sites can be hit by more than one rule, so these overlap.

## Limits

- Precision stays low (3.5% tune). PORT-OS-IFDEF is the noisiest rule (tune 247 findings, 4 TP); it was not narrowed
  further because on tune no structural filter separated TPs from FPs without being fitted to 4 examples.
- Build recall is still low: most tune build changes are install/test plumbing (`if(QNX) install(...)`), library
  lists (`-lsocket`) or compiler flags, which no "Linux-only construct" rule can predict.
- Handwritten `configure` scripts (chrony) and waf `wscript` are not scanned.
- The ±3-line matching window still decides placement-sensitive rules (PORT-MINMAX, PORT-TIMEVAL report the last
  `#include` before the first use, where a fix is usually inserted).

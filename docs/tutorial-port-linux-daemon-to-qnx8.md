# Port a Linux epoll + inotify daemon to QNX 8.0 with qnx-portcheck

> **Verification status (2026-11)**
>
> Checked: qnx-portcheck scaffold and lint-buildfile ran on a Linux host on 2026-11-15 against this example; both daemon variants compile on Linux (gcc, -Wall -Wextra -Werror); QNX facts come from QNX 8.0 documentation fetched 2026-11-15.
>
> Not checked: the scan step output (scan was not run when this tutorial was written); no QNX SDP build, no target run, and whether an inotify file descriptor is pollable on QNX.

## What you'll build

A small C daemon, `filewatchd`, watches one directory and prints filesystem event masks and names. The Linux version waits on an inotify descriptor and a signal self-pipe with epoll. The port variant uses `poll()` for those two descriptors. The example intentionally keeps inotify so the tutorial can focus on the wait mechanism and the QNX filesystem event manager requirements.

## Prerequisites

- Python >= 3.10 on a Linux, macOS, or Windows host for qnx-portcheck.
- A C compiler and CMake for the Linux example.
- A QNX SDP 8.0 installation is needed only for the build step. An SDP was **not available to the authors**.

## Step 1: the Linux daemon

The original is [src/filewatchd.c](../examples/linux-daemon/src/filewatchd.c). It initializes inotify, watches a directory, creates an epoll instance, and adds both the inotify descriptor and a self-pipe read end:

```c
notify_fd = inotify_init1(IN_CLOEXEC);
inotify_add_watch(notify_fd, argv[1], IN_CREATE | IN_DELETE | IN_MODIFY |
                  IN_MOVED_FROM | IN_MOVED_TO);
epoll_fd = epoll_create1(EPOLL_CLOEXEC);
epoll_ctl(epoll_fd, EPOLL_CTL_ADD, notify_fd, &event);
epoll_ctl(epoll_fd, EPOLL_CTL_ADD, pipefd[0], &event);
while (running) {
    int count = epoll_wait(epoll_fd, ready, 8, -1);
    /* drain the signal pipe or read and log inotify events */
}
```

A SIGINT or SIGTERM handler writes one byte to the self-pipe. The main loop handles shutdown and closes its descriptors.

## Step 2: scan the example

From the repository root:

```sh
qnx-portcheck scan examples/linux-daemon --format text
qnx-portcheck scan examples/linux-daemon --format sarif --out qnx-portcheck.sarif
```

Findings depend on the installed rule set and tool version; this tutorial does not claim a particular scan result. The following is **illustrative, not real output**. It shows the JSON schema shape from `CONTRACT.md`; `LNX-EPOLL` is an example rule id from that contract, not a claim about a scan of this sample.

The scan subcommand was developed in parallel and was not run for this tutorial.

```json
{"tool":"qnx-portcheck","version":"x.y.z","root":"<abs path>","findings":[{"rule_id":"LNX-EPOLL","severity":"error|warning|note","file":"<path relative to root, posix>","line":123,"col":5,"message":"...","suggestion":"...","doc_url":"https://www.qnx.com/developers/docs/8.0/... or null","confidence":"high|medium|manual-review"}]}
```

### Rule IDs beyond epoll and inotify

The sample daemon mostly triggers the `LNX-*` API rules, but a real project can also show the rule IDs below.
Descriptions follow `src/qnx_portcheck/rules/` and the evidence in [rule-sources.md](rule-sources.md).
"Manual review" in the last column is the rule's `confidence`: the finding needs a human decision. For
`PORT-MINMAX` and `PORT-TIMEVAL` no QNX documentation page confirms a replacement, so their suggestion is just
`manual review` and `doc_url` is `null`; the other manual-review rules link the QNX page their suggestion is based on.

| Rule ID | Severity | What it reports | Basis | Confidence |
|---|---|---|---|---|
| `PORT-OS-IFDEF` | note | an `#if`/`#ifdef`/`#elif` that tests BSD, macOS, Solaris, AIX, HP-UX, Haiku or Cygwin macros (`__APPLE__`, `__FreeBSD__`, `__OpenBSD__`, `__sun`, `__hpux`, ...) and never `__QNX__`/`__QNXNTO__` | qcc defines `__QNX__` | manual review |
| `PORT-QNXNTO` | note | a conditional that tests `__QNXNTO__` but not `__QNX__` | QNX 8.0 manifests list `__QNXNTO__` as deprecated | high |
| `PORT-MINMAX` | warning | a file that includes `<sys/param.h>` and uses `MIN()`/`MAX()` without defining them; reported at the last `#include` before the first use | `<sys/param.h>` is not a POSIX header | manual review (no doc_url) |
| `PORT-MINMAX-DEFINE` | warning | `#define min(` or `#define max(` that is not inside `#ifndef min`/`#ifndef max` | QNX 8.0 `<stdlib.h>` already defines `min()`/`max()` macros (C only) | high |
| `PORT-SA-RESTART` | warning | uses of `SA_RESTART` in a file that never tests or defines it | the QNX 8.0 `struct sigaction` flags do not include `SA_RESTART` | high |
| `PORT-TIMEVAL` | note | a header file that uses `struct timeval` but includes neither `<sys/time.h>` nor `<sys/select.h>` | POSIX defines `struct timeval` in `<sys/time.h>` | manual review (no doc_url) |
| `BLD-CMAKE-PLATFORM` | warning | a CMake `if()`/`elseif()` that tests `APPLE`, `LINUX`, `BSD`, `CYGWIN`, `ANDROID`, `IOS` or `CMAKE_SYSTEM_NAME`/`CMAKE_HOST_SYSTEM_NAME`, in an if/elseif chain that never names QNX | the QNX porting guide says CMake conditionals on `CMAKE_SYSTEM_NAME` need to be extended for QNX | manual review |
| `BLD-AUTOCONF-HOST` | warning | each OS label (`*-linux*`, `darwin*`, `*-netbsd*`, ...) of a `case $host...` or `AS_CASE([$host_os], ...)` dispatch that has no `qnx`/`nto` label | QNX configure hooks select `nto*` targets | manual review |

Scan scope and guards:

- Besides C/C++ sources, CMake, Make and Meson files, the scan reads `configure.ac`, `configure.in` and the
  project's own `*.m4` files. It skips generated or third-party macro files (`aclocal.m4`, `libtool.m4`, `pkg.m4`,
  and names starting with `lt`, `ax_`, `acx_`, `pkg`, `lib-`, `gl_`, `gettext`, `iconv`, `nls`, `po.m4`,
  `progtest`, `intl`). `dnl` comments are ignored. Generated `configure` scripts are not scanned.
- Linux API findings (epoll, eventfd, timerfd, signalfd, inotify, prctl, sysinfo, sendfile, splice, syscall,
  accept4, pipe2, `<linux/*.h>`, `/proc`) are not reported inside a branch that only compiles when `__linux__`,
  `__linux`, `linux` or `__gnu_linux__` is defined, because qcc does not define them. The guard line itself is
  still reported as `LNX-LINUX-IFDEF`.
- epoll, eventfd, timerfd, signalfd and inotify findings are not reported inside a branch whose condition requires
  a build-probe macro naming that facility, such as `#ifdef HAVE_SYS_EPOLL_H` or `#if defined(EVENT__HAVE_EPOLL)`.
  That code compiles only when the project's configure or CMake check finds the facility, so the place to look is
  the build configuration.

## Step 3: understand the QNX alternatives

The QNX 8.0 C Library Reference documents `poll()` and `ppoll()` for multiplexing descriptors, with the header `<sys/poll.h>`. It also has a `select()` reference. QNX documents `ionotify()` as the resource-manager notification API: “This function corresponds to the Linux epoll() function and BSD's kqueue().” The docs explain that QNX `ionotify()`, `select()`, and `poll()` implementations use the same IO_NOTIFY message, and that a server supporting one will generally support the others. `ionotify()` can combine descriptor input with QNX messaging, provided the application registers the event with `MsgRegisterEvent()` for the descriptor passed to `ionotify()`; `poll()` suits multiple descriptors such as sockets, pipes, and serial ports. See the [ionotify reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html), [poll reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/poll.html), and [select reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/select.html).

The QNX 8.0 C Library Reference page at the [epoll_create URL](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/e/epoll_create.html) returned HTTP 404 when checked on 2026-11-15; we did not find epoll in that reference. The separate [qnx-ports epoll library](https://github.com/qnx-ports/epoll) is another option to evaluate; its [build files](https://github.com/qnx-ports/build-files/tree/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/epoll) are published separately. We did not build or test that port.

## Step 4: apply the port

The example selects `src/filewatchd_poll.c` when `FILEWATCHD_USE_POLL` is enabled. Its wait set is straightforward:

```c
#include <sys/poll.h>
/* ... */
fds[0].fd = notify_fd; fds[0].events = POLLIN;
fds[1].fd = pipefd[0]; fds[1].events = POLLIN;
int count = poll(fds, 2, -1);
```

The `<sys/poll.h>` include follows the [QNX poll reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/poll.html). QNX provides inotify declarations in `<sys/inotify.h>` through `libfsnotify`; when linking with qcc use `-l fsnotify`. The QNX docs say inotify opens `/dev/fsnotify`, which `fsevmgr` creates and owns. The calls fail if the process lacks read permission for `/dev/fsnotify` or if `fsevmgr` isn't running; the documentation lists ENOSYS specifically for the case where `fsevmgr` isn't running. See [inotify_init()/inotify_init1()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_init.html) and [inotify_add_watch()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_add_watch.html).

The documentation does **not** confirm whether an inotify descriptor can be passed to `poll()` or `select()` on QNX. Treat that as a target verification item. If it is not supported, a fallback is a dedicated thread doing blocking `read()` on the inotify descriptor and forwarding events to the main loop.

QNX's inotify documentation classifies the API as Linux and warns that implementations differ. The init page lists io-blk.so-based and devf-ram-based filesystems; the add_watch page says only io-blk.so-based filesystems currently support it. Preserve that discrepancy when deciding which target filesystems to validate.

## Step 5: generate QNX build scaffolding

Run the host tool:

```sh
qnx-portcheck scaffold examples/linux-daemon
```

For this CMake project, the generator writes exactly these five files under `examples/linux-daemon/qnx/build/`:

- `Makefile`
- `common.mk`
- `nto-aarch64-le/Makefile`
- `nto-x86_64-o/Makefile`
- `qnx.nto.toolchain.cmake`

Each generated file has a provenance header naming qnx-portcheck, marking the result as a draft not built or run on a QNX target, and recording its pattern source from `qnx-ports/build-files` at commit `79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5` plus the detected build system. Review generated scaffolding before use.

## Step 6: build with the SDP

With a QNX SDP 8.0 environment available, the documented intended commands are:

```sh
source <sdp>/qnxsdp-env.sh
QNX_PROJECT_ROOT="$(pwd)/examples/linux-daemon" make -C examples/linux-daemon/qnx/build install
```

**NOT VERIFIED: no QNX SDP was available to the authors.** The command and generated scaffold have not been validated with the SDP.

## Step 7: run on a target

**NOT VERIFIED ON A QNX TARGET.** Start `fsevmgr` before filesystem resource managers that should provide event notifications. Ensure `libfsnotify.so` is on `LD_LIBRARY_PATH`. The [fsevmgr reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/f/fsevmgr.html) documents its role and options. A minimal illustrative mkifs snippet is saved as [filewatchd.build](../examples/linux-daemon/qnx/filewatchd.build):

```text
fsevmgr
libfsnotify.so.1
[perms=0755] /usr/bin/filewatchd=filewatchd
```

The [mkifs reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html) describes `[attributes] file_specification`, `target_path=host_path`, and `perms=`. Adapt paths and startup ordering for the image. Check the saved file directly with:

```sh
qnx-portcheck lint-buildfile examples/linux-daemon/qnx/filewatchd.build
```

This command reported no diagnostics on the Linux host on 2026-11-15. The host-side lint does not validate runtime behavior or prove the image will boot.

## Step 8: run in CI

Copy [the example workflow](../examples/workflows/qnx-portcheck.yml) to `.github/workflows/`. It checks out the repository and runs the composite action. SARIF upload needs `security-events: write`; GitHub does not grant write tokens to fork pull requests, so use `upload: "false"` and upload an artifact if needed. The action runs on the CI host and never runs the daemon on a QNX target.

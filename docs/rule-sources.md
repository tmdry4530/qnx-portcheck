# Rule sources (QNX 8.0 documentation evidence)

Every `doc_url` and every suggestion in `src/qnx_portcheck/rules/` is backed by a public QNX SDP 8.0
documentation page that was fetched with `curl` (HTTP 200) from the box on 2026-11-15 between 12:00 and 12:01 KST.
Quotes are copied from the fetched page body. Rules whose alternative could not be confirmed in QNX 8.0 docs
use `suggestion = "manual review"` and `doc_url = null`.

Base: `https://www.qnx.com/developers/docs/8.0/`

## Verified pages

| Rule(s) | URL | Fetched (KST) | Quote (one line) |
|---|---|---|---|
| LNX-EPOLL | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html | 2026-11-15 12:00 | "This function corresponds to the Linux epoll() function and BSD's kqueue()." |
| LNX-EPOLL | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/poll.html | 2026-11-15 12:00 | "The poll() function provides applications with a mechanism for multiplexing input/output over a set of file descriptors." |
| LNX-EPOLL, LNX-EVENTFD, LNX-TIMERFD, LNX-SIGNALFD | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.screen/topic/manual/cscreen_wayland.html | 2026-11-15 12:01 | "To use Wayland on Screen, you need to link the following libraries: libepoll libtimerfd libsignalfd libeventfd ... You can find these libraries in the com.qnx.${baselineId}.target.screen.notify_fd package." |
| LNX-INOTIFY | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_init.html | 2026-11-15 12:00 | "Library: libfsnotify Use the -l fsnotify option to qcc to link against this library." |
| LNX-INOTIFY | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/inotify_add_watch.html | 2026-11-15 12:00 | "inotify_add_watch() Add or update a watch for filesystem events associated with a path" |
| LNX-EVENTFD | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pipe.html | 2026-11-15 12:00 | "Library: libc Use the -l c option to qcc to link against this library." |
| LNX-TIMERFD | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/t/timer_create.html | 2026-11-15 12:00 | "Create a timer ... int timer_create( clockid_t clock_id , struct sigevent * evp , timer_t * timerid );" (Library: libc) |
| LNX-SIGNALFD | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/sigwaitinfo.html | 2026-11-15 12:00 | "Wait for a pending signal and retrieve its information" (Library: libc) |
| LNX-PRCTL | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_setname_np.html | 2026-11-15 12:00 | "Name a thread Synopsis: #include <pthread.h> int pthread_setname_np(pthread_t tid , const char* newname );" |
| LNX-PROCFS | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/process_proc_filesystem.html | 2026-11-15 12:01 | "The /proc filesystem does not have full filesystem functionality, so you should not use it in production systems to control or monitor the behavior of processes and threads." |
| LNX-PROCFS | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/p/procnto.html | 2026-11-15 12:01 | "/proc/self/ The address space for yourself (i.e., for the process that's making the query)." |
| LNX-PROCFS (/proc/self/exe) | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/process_proc_filesystem.html | 2026-11-15 12:01 | "exefile The path of the executable file used to run the process." |
| LNX-LINUX-IFDEF | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/devel_Neutrino_specific.html | 2026-11-15 12:01 | "The qcc utility defines the __QNX__ preprocessor symbol (or manifest constant) to allow you to specify QNX OS-specific code." |
| LNX-LINUX-IFDEF | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/manifests.html | 2026-11-15 12:01 | "__QNXNTO__ N/A Deprecated. The target is the QNX Neutrino RTOS." |
| LNX-LINK-FLAGS (-lpthread) | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_create.html | 2026-11-15 12:01 | "Library: libc Use the -l c option to qcc to link against this library. This library is usually included automatically." |
| LNX-LINK-FLAGS (-ldl) | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/dlopen.html | 2026-11-15 12:00 | "Library: libc Use the -l c option to qcc to link against this library. This library is usually included automatically." |
| LNX-LINK-FLAGS (-lrt) | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/clock_gettime.html | 2026-11-15 12:00 | "Library: libc Use the -l c option to qcc to link against this library. This library is usually included automatically." |
| LNX-ACCEPT4 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.io_sock/topic/socket_api.html | 2026-11-15 12:01 | "The io-sock networking stack supports all the routines that application programmers would expect, including (but not limited to) the functions listed below ... accept() accept4() bind() ..." |
| LNX-ACCEPT4 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.qnxsdp.migration/topic/migrate_app.html | 2026-11-15 12:01 | "There is no io-sock version of the libsocket.a static library. Instead, your io-sock applications should link against the libsocket.so shared library." |
| LNX-PIPE2 | https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pipe2.html | 2026-11-15 12:00 | "flags Bitwise combination of two supported flags: O_CLOEXEC ... O_NONBLOCK" (Library: libc) |

## Not verifiable in QNX 8.0 docs (manual review, doc_url = null)

Checked on 2026-11-15 12:00-12:01 KST: the per-function URLs below returned HTTP 404, and the names do not
appear in the C Library Reference table of contents (1,479 topic links collected from the A-Z index pages)
nor in the io-sock Networking APIs list.

| Rule | Checked URL (404) | Result |
|---|---|---|
| LNX-SENDFILE | .../com.qnx.doc.neutrino.lib_ref/topic/s/sendfile.html | not documented -> manual review |
| LNX-SPLICE | .../com.qnx.doc.neutrino.lib_ref/topic/s/splice.html | not documented -> manual review |
| LNX-SYSINFO | .../com.qnx.doc.neutrino.lib_ref/topic/s/sysinfo.html | not documented -> manual review (sysconf() page lists no processor-count or memory-size name) |
| LNX-SYSCALL | (no QNX 8.0 page for Linux `syscall()` / `SYS_*` numbers found) | manual review |
| LNX-LINUX-HEADER | (Linux kernel UAPI headers `<linux/*.h>` are not part of QNX docs) | manual review |
| LNX-LINK-FLAGS-OTHER (-lsystemd, -ludev, -lcap, -laio, -lnuma, -lutil) | (no QNX 8.0 library pages found) | manual review |
| LNX-PRCTL (options other than PR_SET_NAME) | .../com.qnx.doc.neutrino.lib_ref/topic/p/prctl.html | 404 -> only PR_SET_NAME has a documented replacement |
| LNX-EPOLL/EVENTFD/TIMERFD/SIGNALFD per-function pages | .../e/epoll_create.html, .../e/eventfd.html, .../t/timerfd_create.html, .../s/signalfd.html | 404: these libraries are mentioned only on the Screen/Wayland page, so findings are `warning`/`medium` |

## Notes
- `inotify`, `pipe2()` and `accept4()` ARE documented for QNX 8.0, so those rules are `note` severity (link/setup differences), not errors.
- The Wayland page documents libepoll/libeventfd/libtimerfd/libsignalfd only as dependencies for Wayland on Screen; the tool says so instead of claiming general availability.

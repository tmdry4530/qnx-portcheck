"""I/O multiplexing and Linux event descriptor rules."""
from __future__ import annotations

from .base import Rule, include_and_calls

DOCS_BASE = "https://www.qnx.com/developers/docs/8.0/"


def _rule(
    rule_id: str,
    label: str,
    header: str,
    calls: str,
    suggestion: str,
    doc: str,
    severity: str = "warning",
    confidence: str = "high",
) -> Rule:
    """Build a rule for an include and a list of calls."""
    url = DOCS_BASE + doc
    detector = include_and_calls((header,), tuple(calls.split()), label.lower())
    return Rule(rule_id, severity, confidence, "c", label, suggestion, url, detector)


RULES = [
    _rule(
        "LNX-EPOLL", "epoll", "sys/epoll.h",
        "epoll_create epoll_create1 epoll_ctl epoll_wait epoll_pwait epoll_pwait2",
        "QNX 8.0 documents ionotify() as corresponding to Linux epoll(); "
        "poll()/select() are also available. No epoll page exists in the QNX 8.0 "
        "C Library Reference. A libepoll is listed in the "
        "com.qnx.<baselineId>.target.screen.notify_fd package (documented for "
        "Wayland on Screen); verify it is in your SDP before relying on it.",
        "com.qnx.doc.neutrino.lib_ref/topic/i/ionotify.html",
    ),
    _rule(
        "LNX-INOTIFY", "inotify", "sys/inotify.h",
        "inotify_init inotify_init1 inotify_add_watch",
        "inotify_init()/inotify_add_watch() exist in QNX 8.0 in libfsnotify: "
        "link with -l fsnotify; the fsevmgr filesystem event manager service "
        "must be running (FSNOTIFY_PREFIX must match).",
        "com.qnx.doc.neutrino.lib_ref/topic/i/inotify_init.html", "note",
    ),
    _rule(
        "LNX-EVENTFD", "eventfd", "sys/eventfd.h",
        "eventfd eventfd_read eventfd_write",
        "eventfd is not in the QNX 8.0 C Library Reference; libeventfd is "
        "listed only in the screen.notify_fd package (Wayland on Screen). "
        "Otherwise replace with a pipe()/pipe2() wake-up fd watched by poll().",
        "com.qnx.doc.screen/topic/manual/cscreen_wayland.html", confidence="medium",
    ),
    _rule(
        "LNX-TIMERFD", "timerfd", "sys/timerfd.h",
        "timerfd_create timerfd_settime timerfd_gettime",
        "timerfd is not in the QNX 8.0 C Library Reference (libtimerfd is "
        "listed only in the screen.notify_fd package for Wayland on Screen). "
        "Documented libc alternative: timer_create() with a struct sigevent, "
        "armed with timer_settime().",
        "com.qnx.doc.neutrino.lib_ref/topic/t/timer_create.html", confidence="medium",
    ),
    _rule(
        "LNX-SIGNALFD", "signalfd", "sys/signalfd.h", "signalfd",
        "signalfd is not in the QNX 8.0 C Library Reference (libsignalfd is "
        "listed only in the screen.notify_fd package for Wayland on Screen). "
        "Documented libc alternatives: sigwaitinfo()/sigtimedwait() on a dedicated thread.",
        "com.qnx.doc.neutrino.lib_ref/topic/s/sigwaitinfo.html", confidence="medium",
    ),
]

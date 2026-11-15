"""Linux API, header, and conditional compilation rules."""
from __future__ import annotations

import re
from typing import Iterable
from .base import Hit, Rule, SourceContext, include_and_calls

D = "https://www.qnx.com/developers/docs/8.0/"
def _api(rule_id: str, title: str, suggestion: str, doc: str | None,
         header: str = "", calls: str = "", severity: str = "error",
         confidence: str = "manual-review") -> Rule:
    url = D + doc if doc else None
    detector = include_and_calls((header,) if header else (), tuple(calls.split()), title.lower(), suggestion, url)
    return Rule(rule_id, severity, confidence, "c", title, suggestion, url, detector)

def _linux_header(context: SourceContext) -> Iterable[Hit]:
    for match in re.finditer(r'^\s*#\s*include\s*[<"](linux/[^>"]+)[>"]', context.comments, re.M):
        line = context.comments.count("\n", 0, match.start()) + 1
        col = match.start() - context.comments.rfind("\n", 0, match.start())
        yield Hit(line, col, f"Linux kernel header <{match.group(1)}>")

def _ifdef(context: SourceContext) -> Iterable[Hit]:
    for line_no, line in enumerate(context.comments.splitlines(), 1):
        if not re.match(r'^\s*#\s*(?:if|ifdef|ifndef|elif|elifdef|elifndef)\b', line):
            continue
        if re.search(r'__QNX(?:NTO)?__', line):
            continue
        if re.search(r'__linux__|__linux\b|__gnu_linux__|defined\s*(?:\(\s*linux\s*\)|linux\b)|#\s*ifdef\s+linux\b', line):
            yield Hit(line_no, 1, "Linux-only preprocessor condition")

RULES = [
    _api("LNX-PRCTL", "prctl", "prctl() is not in the QNX 8.0 C Library Reference. For PR_SET_NAME use pthread_setname_np(); other prctl options: manual review.", "com.qnx.doc.neutrino.lib_ref/topic/p/pthread_setname_np.html", "sys/prctl.h", "prctl", confidence="medium"),
    _api("LNX-SYSINFO", "sysinfo", "manual review", None, "sys/sysinfo.h", "sysinfo get_nprocs get_nprocs_conf get_phys_pages get_avphys_pages"),
    _api("LNX-SENDFILE", "sendfile", "manual review", None, "sys/sendfile.h", "sendfile"),
    _api("LNX-SPLICE", "splice", "manual review", None, calls="splice vmsplice"),
    _api("LNX-SYSCALL", "syscall", "manual review", None, "sys/syscall.h", "syscall"),
    _api("LNX-ACCEPT4", "accept4", "accept4() is provided by the QNX 8.0 io-sock stack (FreeBSD semantics; see FreeBSD accept(2)). io-sock applications link against libsocket.so (-l socket); there is no libsocket.a.", "com.qnx.doc.neutrino.io_sock/topic/socket_api.html", calls="accept4", severity="note", confidence="high"),
    _api("LNX-PIPE2", "pipe2", "pipe2() is in QNX 8.0 libc but supports only O_CLOEXEC and O_NONBLOCK flags; check that no other flags (e.g. O_DIRECT) are passed.", "com.qnx.doc.neutrino.lib_ref/topic/p/pipe2.html", calls="pipe2", severity="note", confidence="high"),
    Rule("LNX-LINUX-HEADER", "error", "manual-review", "c", "Linux kernel header", "manual review", None, _linux_header),
    Rule("LNX-LINUX-IFDEF", "warning", "high", "c", "Linux-only preprocessor condition", "This branch is Linux-only. qcc defines __QNX__ (value 800 for QNX 8.0; e.g. #if defined(__QNX__) && __QNX__ >= 800); add a QNX branch. __QNXNTO__ is deprecated.", D + "com.qnx.doc.neutrino.prog/topic/devel_Neutrino_specific.html", _ifdef),
]

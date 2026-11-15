"""QNX and Unix portability checks for C and C++ sources."""
from __future__ import annotations
import re
from typing import Iterable
from qnx_portcheck.lexer import position
from .base import Hit, Rule, SourceContext
from .linux_apis import LINUX_IFDEF_RE

DIRECTIVE = re.compile(r'^\s*#\s*(if|ifdef|ifndef|elif|elifdef|elifndef)\b')
UNIX = re.compile(r'\b(__APPLE__|__MACH__|__FreeBSD__|__NetBSD__|__OpenBSD__|__DragonFly__|__FreeBSD_kernel__|__sun__?|__HAIKU__|_AIX|__hpux|__CYGWIN__)\b')
INCLUDE = re.compile(r'^\s*#\s*include\b', re.M)

def _directives(text: str):
    lines = text.splitlines(); i = 0
    while i < len(lines):
        start = i; chunk = lines[i]
        while chunk.rstrip().endswith('\\') and i + 1 < len(lines):
            i += 1; chunk = chunk.rstrip()[:-1] + ' ' + lines[i]
        if DIRECTIVE.match(chunk): yield start + 1, chunk
        i += 1

def _use_include_line(context: SourceContext, line: int) -> int:
    last = line
    for m in INCLUDE.finditer(context.comments):
        n, _ = position(context.comments, m.start())
        if n < line: last = n
        else: break
    return last

def _os_ifdef(c):
    for line, text in _directives(c.comments):
        m = UNIX.search(text)
        if m and not re.search(r'\b(?:__QNX__|__QNXNTO__)\b', text) and not re.search(LINUX_IFDEF_RE, text):
            yield Hit(line, 1, f"Platform branch for {m.group(1)} has no __QNX__ case")

def _qnxnto(c):
    for line, text in _directives(c.comments):
        if re.search(r'\b__QNXNTO__\b', text) and not re.search(r'\b__QNX__\b', text):
            yield Hit(line, 1, "__QNXNTO__ tested without __QNX__")

def _minmax(c):
    if 'sys/param.h' not in c.comments or re.search(r'^\s*#\s*(?:define|undef)\s+(?:MIN|MAX)\b', c.comments, re.M): return
    if not re.search(r'^\s*#\s*include\s*[<"]sys/param\.h[>"]', c.comments, re.M): return
    for no, line in enumerate(c.code.splitlines(), 1):
        if DIRECTIVE.match(line): continue
        m = re.search(r'(?<![\w.>:])(MIN|MAX)\s*\(', line)
        if m:
            loc = _use_include_line(c, no)
            yield Hit(loc, 1, f"MIN()/MAX() used (first at line {no}) but not defined in this file; <sys/param.h> is not a POSIX header and its MIN/MAX macros are a BSD/glibc extension")
            return

def _minmax_define(c):
    stack=[]
    for no, line in enumerate(c.comments.splitlines(),1):
        m=re.match(r'^\s*#\s*(if|ifdef|ifndef|elif|else|endif|define)\b\s*(.*)',line)
        if not m: continue
        op,arg=m.group(1),m.group(2).strip()
        if op in ('if','ifdef','ifndef'):
            guarded = (op=='ifndef' and arg.split()[0] in ('min','max') if arg else False) or bool(re.search(r'!\s*defined\s*(?:\(\s*)?(min|max)\b',arg))
            name = arg.split()[0] if op=='ifndef' and arg else re.search(r'!\s*defined\s*(?:\(\s*)?(min|max)',arg).group(1) if re.search(r'!\s*defined\s*(?:\(\s*)?(min|max)',arg) else None
            stack.append((name,guarded))
        elif op=='endif' and stack: stack.pop()
        elif op=='define':
            d=re.match(r'(min|max)\s*\(',arg)
            if d and not any(g and n==d.group(1) for n,g in stack): yield Hit(no,1,f"Defines {d.group(1)}() which QNX <stdlib.h> already defines as a macro")

def _sa_restart(c):
    directives=list(_directives(c.comments))
    if any(re.search(r'\b(?:ifdef|ifndef)\s+SA_RESTART\b|\bdefined\s*(?:\(\s*)?SA_RESTART\b|#\s*define\s+SA_RESTART\b',t) for _,t in directives): return
    for no,line in enumerate(c.code.splitlines(),1):
        dm=re.match(r'^\s*#\s*(\w+)\b(.*)',line)
        if dm and (dm.group(1) in ('if','ifdef','ifndef','elif','elifdef','elifndef','undef') or (dm.group(1)=='define' and re.match(r'\s*SA_RESTART\b',dm.group(2)))): continue
        for m in re.finditer(r'\bSA_RESTART\b',line): yield Hit(no,m.start()+1,"SA_RESTART used")

HEADER_SUFFIXES = (".h", ".hh", ".hpp", ".hxx")

def _timeval(c):
    # Headers only: a header is included from many contexts and should be self-contained; .c files
    # usually get struct timeval through a project config header.
    if not c.path.endswith(HEADER_SUFFIXES): return
    if re.search(r'^\s*#\s*include\s*[<"](?:sys/time|sys/select)\.h[>"]',c.comments,re.M): return
    for no,line in enumerate(c.code.splitlines(),1):
        if DIRECTIVE.match(line): continue
        if re.search(r'\bstruct\s+timeval\b',line):
            yield Hit(_use_include_line(c,no),1,f"struct timeval used (first at line {no}) without including <sys/time.h>"); return

DOC={"os":"https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/devel_Neutrino_specific.html","qnxnto":"https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/manifests.html","minmax_define":"https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/max.html","sa":"https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/sigaction_struct.html","timeval":"https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/sys_time.h.html"}
RULES=[
 Rule("PORT-OS-IFDEF","note","manual-review","c","Non-Linux Unix branch without QNX","This conditional selects code for other Unix-like systems (BSD/macOS/Solaris/AIX/HP-UX) but never for QNX. qcc defines __QNX__ (800 for QNX 8.0); check whether QNX should take this branch (add `|| defined(__QNX__)`) or the other one (add `&& !defined(__QNX__)`).",DOC['os'],_os_ifdef),
 Rule("PORT-QNXNTO","note","high","c","Deprecated __QNXNTO__ test","QNX 8.0 lists __QNXNTO__ as deprecated; qcc defines __QNX__ (800 for QNX 8.0). Test __QNX__ (optionally keep __QNXNTO__ for older releases).",DOC['qnxnto'],_qnxnto),
 Rule("PORT-MINMAX","warning","manual-review","c","MIN()/MAX() from <sys/param.h>","manual review",None,_minmax),
 Rule("PORT-MINMAX-DEFINE","warning","high","c","min()/max() macro clashes with QNX <stdlib.h>","QNX 8.0 <stdlib.h> defines min() and max() macros (C only); wrap this definition in #ifndef <name> or rename it.",DOC['minmax_define'],_minmax_define),
 Rule("PORT-SA-RESTART","warning","high","c","SA_RESTART is not a QNX sigaction flag","The QNX 8.0 struct sigaction documents sa_flags SA_NOCLDSTOP, SA_NOCLDWAIT, SA_NODEFER, SA_ONSTACK, SA_RESETHAND and SA_SIGINFO only; there is no SA_RESTART. Guard it (#ifdef SA_RESTART) and handle EINTR.",DOC['sa'],_sa_restart),
 Rule("PORT-TIMEVAL","note","manual-review","c","struct timeval without <sys/time.h>","manual review",None,_timeval),
]

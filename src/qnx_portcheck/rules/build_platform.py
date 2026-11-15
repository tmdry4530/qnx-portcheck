"""Platform dispatch checks in CMake and GNU autoconf inputs."""
from __future__ import annotations
import re
from typing import Iterable
from qnx_portcheck.lexer import position
from .base import Hit, Rule, SourceContext
from .buildfiles import _without_comments

PLATFORM = re.compile(r'\b(?:APPLE|LINUX|BSD|CYGWIN|ANDROID|IOS|CMAKE_SYSTEM_NAME|CMAKE_HOST_SYSTEM_NAME)\b')
OS_GLOB = re.compile(r'(?i)(?:linux|uclinux|android|darwin|freebsd|kfreebsd|netbsd|openbsd|dragonfly|solaris|sunos|cygwin|mingw|msys|haiku|aix|hpux|gnu)')

def _cmake_text(c): return _without_comments(c.raw)
def _cmake(c):
    text = _cmake_text(c)
    commands = []
    pattern = re.compile(r"\b(if|elseif)\s*\(", re.I)
    for match in pattern.finditer(text):
        depth = 1
        cursor = match.end()
        quoted = False
        while cursor < len(text) and depth:
            if text[cursor] == '"':
                quoted = not quoted
            elif not quoted and text[cursor] == '(':
                depth += 1
            elif not quoted and text[cursor] == ')':
                depth -= 1
            cursor += 1
        commands.append((match.group(1).lower(), match.start(), match.end(),
                         text[match.end():cursor - 1], cursor))

    # Associate each condition with the innermost CMake if/endif chain.
    events = [(cmd[1], "command", cmd) for cmd in commands]
    events.extend((m.start(), "endif", None)
                  for m in re.finditer(r"\bendif\s*\(", text, re.I))
    events.sort(key=lambda event: event[0])
    stack = []
    chains = []
    for _, kind, cmd in events:
        if kind == "endif":
            if stack:
                stack.pop()
        elif cmd[0] == "if":
            chain = [cmd]
            chains.append(chain)
            stack.append(chain)
        elif stack:
            stack[-1].append(cmd)

    for chain in chains:
        qnx_case = any(re.search(r"\bQNX\b", command[3], re.I)
                       for command in chain)
        if qnx_case:
            continue
        for command in chain:
            if not PLATFORM.search(command[3]):
                continue
            collapsed = " ".join(command[3].split())
            if len(collapsed) > 60:
                collapsed = collapsed[:57] + "..."
            line, _ = position(text, command[1])
            yield Hit(line, 1, f"CMake platform condition `{collapsed}` has no QNX case")

def _autoconf_text(c):
    text=_without_comments(c.raw); chars=list(text)
    for m in re.finditer(r'(?im)(?<!\S)dnl\b[^\n]*',text):
        for i in range(m.start(),m.end()): chars[i]=' '
    return ''.join(chars)

def _autoconf(c):
    text=_autoconf_text(c)
    # Shell case blocks and AS_CASE calls are balanced through esac / brackets and parens.
    blocks=[]
    for m in re.finditer(r'(?i)\bcase\s+([^\s]+)\s+in\b',text):
        if not re.search(r'host|target|build_os',m.group(1),re.I): continue
        end=re.search(r'\besac\b',text[m.end():],re.I)
        if end: blocks.append((m.end(),m.end()+end.start(),False))
    for m in re.finditer(r'\bAS_CASE\s*\(',text,re.I):
        if not re.search(r'host|target|build_os',text[m.end():m.end()+100],re.I): continue
        depth=1; i=m.end(); bracket=0
        while i<len(text) and depth:
            if text[i]=='[': bracket+=1
            elif text[i]==']': bracket=max(0,bracket-1)
            elif not bracket and text[i]=='(': depth+=1
            elif not bracket and text[i]==')': depth-=1
            i+=1
        blocks.append((m.end(),i-1,True))
    for start,end,as_case in blocks:
        segment=text[start:end]
        if re.search(r'(?i)(?:qnx|\bnto\b)',segment): continue
        if as_case:
            for label in re.finditer(r'\[([^\]]+)\]',segment):
                pattern=label.group(1).strip()
                if OS_GLOB.search(pattern):
                    line,_=position(text,start+label.start(1)); yield Hit(line,1,f"Host OS case `{pattern[:40]}` in a dispatch with no nto-qnx* case")
        else:
            offset=0
            for line in segment.splitlines(True):
                m=re.match(r'\s*([^\n)]*)\)',line)
                if m and OS_GLOB.search(m.group(1)):
                    pattern=m.group(1).strip(); no,_=position(text,start+offset); yield Hit(no,1,f"Host OS case `{pattern[:40]}` in a dispatch with no nto-qnx* case")
                offset+=len(line)

DOC1='https://www.qnx.com/developers/docs/qnxeverywhere/com.qnx.doc.qpg/topic/port_CMake.html'
DOC2='https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/make_convent_hook_preconfigure.html'
RULES=[Rule('BLD-CMAKE-PLATFORM','warning','manual-review','build','CMake platform condition without QNX','This branch selects sources, flags or libraries per platform but never names QNX. QNX toolchain files set CMAKE_SYSTEM_NAME to QNX (and often QNX TRUE), and QNX notes that CMake conditionals checking CMAKE_SYSTEM_NAME need to be extended for QNX; decide whether QNX belongs in this condition (e.g. add `AND NOT CMAKE_SYSTEM_NAME STREQUAL "QNX"` or an elseif branch).',DOC1,_cmake),Rule('BLD-AUTOCONF-HOST','warning','manual-review','build','autoconf host OS case without QNX','GNU configure names QNX targets *-nto-qnx* (e.g. aarch64-unknown-nto-qnx8.0.0); add a *-nto-qnx* case next to these or confirm the default branch is right for QNX.',DOC2,_autoconf)]

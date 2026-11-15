"""Link library detectors for common build systems."""
from __future__ import annotations

import re
from typing import Iterable
from .base import Hit, Rule, SourceContext

D = "https://www.qnx.com/developers/docs/8.0/"
URLS = {"pthread": D + "com.qnx.doc.neutrino.lib_ref/topic/p/pthread_create.html",
        "dl": D + "com.qnx.doc.neutrino.lib_ref/topic/d/dlopen.html",
        "rt": D + "com.qnx.doc.neutrino.lib_ref/topic/c/clock_gettime.html"}
FUNCTIONS = {"pthread": "pthread_create", "dl": "dlopen", "rt": "clock_gettime"}

def _without_comments(text: str) -> str:
    """Blank hash comments while retaining quoted strings and line positions."""
    chars = list(text)
    index = 0
    while index < len(text):
        if text.startswith("#[", index):
            match = re.match(r'#\[(=*)\[', text[index:])
            if match:
                terminator = "]" + match.group(1) + "]"
                end = text.find(terminator, index + match.end())
                end = len(text) if end < 0 else end + len(terminator)
                for pos in range(index, end):
                    if chars[pos] != "\n":
                        chars[pos] = " "
                index = end
                continue
        if text[index] in "'\"":
            quote = text[index]
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == quote:
                    index += 1
                    break
                index += 1
            continue
        if text[index] == "#":
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            for pos in range(index, end):
                chars[pos] = " "
            index = end
            continue
        index += 1
    return "".join(chars)

def _position(text: str, offset: int) -> tuple[int, int]:
    return text.count("\n", 0, offset) + 1, offset - text.rfind("\n", 0, offset)

def detect_link(context: SourceContext) -> Iterable[Hit]:
    """Find all documented and manual-review link library references."""
    text = _without_comments(context.raw)
    for match in re.finditer(r"(?<![\w-])-l(dl|rt|pthread)(?![\w-])", text):
        yield _hit(match, text, "-l" + match.group(1))
    for match in re.finditer(r"(?<![\w-])-l(systemd|udev|cap|aio|numa|util)(?![\w-])", text):
        line, col = _position(text, match.start())
        yield Hit(line, col, f"Linux-specific link library '-l{match.group(1)}'")
    if context.path.endswith("CMakeLists.txt") or context.path.endswith(".cmake"):
        for call in re.finditer(r"\b(?:target_link_libraries|link_libraries)\s*\(", text, re.I):
            depth, cursor = 1, call.end()
            while cursor < len(text) and depth:
                if text[cursor] == "(": depth += 1
                elif text[cursor] == ")": depth -= 1
                cursor += 1
            segment = text[call.end():cursor - 1]
            pattern = r"\$\{CMAKE_DL_LIBS\}|(?<![\w/\"'])\b(dl|rt|pthread)\b(?![\w/\"'])"
            for match in re.finditer(pattern, segment):
                lib = "dl" if match.group(0) == "${CMAKE_DL_LIBS}" else match.group(1)
                yield _hit(match, text, lib, call.end() + match.start())
    if context.path.endswith("meson.build"):
        pattern = r"\b(?:find_library\s*\(\s*|dependency\s*\(\s*)['\"](dl|rt|pthread)['\"]"
        for match in re.finditer(pattern, text):
            yield _hit(match, text, match.group(1), match.start(1))

def _hit(match: re.Match, text: str, lib: str, offset: int | None = None) -> Hit:
    line, col = _position(text, match.start() if offset is None else offset)
    library_name = lib[2:] if lib.startswith("-l") else lib
    message = f"Linux link library '{lib}'"
    suggestion = (
        f"On QNX 8.0 {FUNCTIONS[library_name]}() is documented in libc, "
        f"which qcc usually links automatically; drop or guard lib{library_name} "
        "for QNX builds."
    )
    return Hit(line, col, message, suggestion=suggestion, doc_url=URLS[library_name])

def detect_standard(context: SourceContext) -> Iterable[Hit]:
    """Yield documented libc library hits only."""
    yield from (hit for hit in detect_link(context) if hit.doc_url is not None)

def detect_other(context: SourceContext) -> Iterable[Hit]:
    """Yield libraries requiring manual review only."""
    yield from (hit for hit in detect_link(context) if hit.doc_url is None
                and hit.message.startswith("Linux-specific"))

RULES = [
    Rule("LNX-LINK-FLAGS", "warning", "high", "build", "Linux link library", "manual review", None, detect_standard),
    Rule("LNX-LINK-FLAGS-OTHER", "warning", "manual-review", "build", "Linux-specific link library", "manual review", None, detect_other),
]

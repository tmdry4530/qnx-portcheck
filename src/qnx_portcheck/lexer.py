"""C/C++ lexical views with comments and literal contents blanked in place."""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import re

RAW_PREFIX = re.compile(r'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')
NORMAL_PREFIX = re.compile(r"(?:u8|u|U|L)?([\"'])")
_LITERAL_START = frozenset("uULR\"'")
_line_cache: tuple[str, list[int]] | None = None


@dataclass(frozen=True)
class StringLiteral:
    """A string literal and its opening quote position."""

    line: int
    col: int
    text: str


def line_starts(text: str) -> list[int]:
    """Return the offset of the first character of every line."""
    global _line_cache
    cached = _line_cache
    if cached is not None and cached[0] is text:
        return cached[1]
    starts = [0]
    find = text.find
    newline = find("\n")
    while newline >= 0:
        starts.append(newline + 1)
        newline = find("\n", newline + 1)
    _line_cache = (text, starts)
    return starts


def position(text: str, offset: int) -> tuple[int, int]:
    """Convert an offset to a 1-based line and column."""
    starts = line_starts(text)
    line = bisect_right(starts, offset)
    return line, offset - starts[line - 1] + 1


def lex(text: str) -> tuple[str, list[tuple[int, int, str]], str]:
    """Return code view, string literals, and a comment-stripped view."""
    comments = list(text)
    code = list(text)
    strings: list[tuple[int, int, str]] = []
    index = 0
    size = len(text)
    state = "code"
    quote = ""
    literal_start = 0
    content_start = 0
    raw_end = ""
    raw_quote_offset = 0
    escaped = False

    def blank(target: list[str], start: int, end: int) -> None:
        for offset in range(start, end):
            if text[offset] != "\n":
                target[offset] = " "

    while index < size:
        if state == "code":
            if text[index] in _LITERAL_START:
                raw = RAW_PREFIX.match(text, index)
                normal = NORMAL_PREFIX.match(text, index)
            else:
                raw = normal = None
            if raw and (index == 0 or not (text[index - 1].isalnum() or text[index - 1] == "_")):
                literal_start = index
                content_start = raw.end()
                raw_end = ")" + raw.group(1) + '"'
                raw_quote_offset = raw.end() - len(raw.group(1)) - 2
                quote = '"'
                state = "raw_string"
                index = content_start
                continue
            if normal and (index == 0 or not (text[index - 1].isalnum() or text[index - 1] == "_")):
                literal_start = index
                quote = normal.group(1)
                content_start = normal.end()
                state = "string" if quote == '"' else "char"
                escaped = False
                index = content_start
                continue
            if text.startswith("//", index):
                blank(comments, index, index + 2)
                blank(code, index, index + 2)
                state = "line_comment"
                index += 2
                continue
            if text.startswith("/*", index):
                blank(comments, index, index + 2)
                blank(code, index, index + 2)
                state = "block_comment"
                index += 2
                continue
            index += 1
            continue
        if state == "line_comment":
            if text[index] == "\\" and index + 1 < size and text[index + 1] == "\n":
                blank(comments, index, index + 1)
                blank(code, index, index + 1)
                index += 1
            elif text[index] == "\n":
                state = "code"
            else:
                blank(comments, index, index + 1)
                blank(code, index, index + 1)
            index += 1
            continue
        if state == "block_comment":
            if text.startswith("*/", index):
                blank(comments, index, index + 2)
                blank(code, index, index + 2)
                index += 2
                state = "code"
            else:
                blank(comments, index, index + 1)
                blank(code, index, index + 1)
                index += 1
            continue
        if state == "raw_string":
            end = text.find(raw_end, index)
            if end < 0:
                end = size
                finish = size
            else:
                finish = end + len(raw_end)
            strings.append((*position(text, raw_quote_offset), text[content_start:end]))
            blank(code, literal_start, finish)
            code[raw_quote_offset] = '"'
            if finish > end:
                code[finish - 1] = '"'
            index = finish
            state = "code"
            continue
        if text[index] == "\n":
            if escaped:
                escaped = False
                index += 1
                continue
            blank(code, literal_start + 1, index)
            index += 1
            state = "code"
            continue
        if escaped:
            escaped = False
        elif text[index] == "\\":
            escaped = True
        elif text[index] == quote:
            if state == "string":
                quote_offset = content_start - 1
                strings.append((*position(text, quote_offset), text[content_start:index]))
            blank(code, literal_start + 1, index)
            index += 1
            state = "code"
            continue
        index += 1
    if state in {"string", "char"}:
        blank(code, literal_start + 1, size)
        if state == "string":
            strings.append((*position(text, literal_start + (content_start - literal_start) - 1),
                            text[content_start:size]))
    return "".join(code), strings, "".join(comments)


def comment_stripped(text: str) -> str:
    """Return source with comments blanked while respecting quoted literals."""
    return lex(text)[2]


def directives(code: str) -> list[tuple[int, str]]:
    """Return preprocessor lines from a code view."""
    return [(number, line) for number, line in enumerate(code.splitlines(), 1)
            if re.match(r"^\s*#", line)]

"""C/C++ lexical views that preserve source offsets."""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class StringLiteral:
    line: int
    col: int
    text: str


def comment_stripped(text: str) -> str:
    """Blank comments while preserving newlines and columns."""
    output = list(text)
    index = 0
    state = "code"
    while index < len(text):
        if state == "code" and text.startswith("//", index):
            output[index:index + 2] = "  "
            index += 2
            state = "line"
            continue
        if state == "code" and text.startswith("/*", index):
            output[index:index + 2] = "  "
            index += 2
            state = "block"
            continue
        if state == "line":
            if text[index] == "\\" and index + 1 < len(text) and text[index + 1] == "\n":
                output[index] = " "
                index += 1
            elif text[index] == "\n":
                state = "code"
            else:
                output[index] = " "
            index += 1
            continue
        if state == "block":
            if text.startswith("*/", index):
                output[index:index + 2] = "  "
                index += 2
                state = "code"
            else:
                if text[index] != "\n":
                    output[index] = " "
                index += 1
            continue
        index += 1
    return "".join(output)


_RAW = re.compile(r'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')


def lex(text: str) -> tuple[str, list[tuple[int, int, str]], str]:
    """Return code view, (line, col, literal content) tuples, and comment view."""
    comments = comment_stripped(text)
    code = list(comments)
    strings: list[tuple[int, int, str]] = []
    index = 0
    while index < len(text):
        if comments[index] not in "\"'":
            index += 1
            continue
        quote = comments[index]
        raw_match = None
        if quote == '"':
            for start in range(max(0, index - 4), index + 1):
                candidate = _RAW.match(comments, start)
                if candidate and candidate.start() <= index < candidate.end():
                    raw_match = candidate
                    break
        if raw_match:
            start = raw_match.start()
            terminator = ")" + raw_match.group(1) + '"'
            end_start = comments.find(terminator, raw_match.end())
            end = len(text) if end_start < 0 else end_start + len(terminator)
            content_end = len(text) if end_start < 0 else end_start
            line, col = _line_col(text, index)
            strings.append((line, col, text[raw_match.end():content_end]))
            for offset in range(start, end):
                if text[offset] != "\n":
                    code[offset] = " "
            code[index] = '"'
            index = end
            continue
        start = index
        cursor = index + 1
        escaped = False
        while cursor < len(text):
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                break
            cursor += 1
        end = min(cursor + 1, len(text))
        if quote == '"':
            line, col = _line_col(text, start)
            strings.append((line, col, text[start + 1:cursor]))
        for offset in range(start + 1, cursor):
            if text[offset] != "\n":
                code[offset] = " "
        index = end
    return "".join(code), strings, comments


def _line_col(text: str, offset: int) -> tuple[int, int]:
    """Convert a character offset to 1-based line and column."""
    line = text.count("\n", 0, offset) + 1
    return line, offset - text.rfind("\n", 0, offset)


def directives(code: str) -> list[tuple[int, str]]:
    """Return preprocessor lines from a code view."""
    return [(line_no, line) for line_no, line in enumerate(code.splitlines(), 1)
            if re.match(r"^\s*#", line)]

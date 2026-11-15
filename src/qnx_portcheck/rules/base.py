"""Shared types and detector helpers for portability rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Literal
from qnx_portcheck.lexer import position
import re


@dataclass(frozen=True)
class Hit:
    line: int
    col: int
    message: str
    severity: str | None = None
    confidence: str | None = None
    suggestion: str | None = None
    doc_url: str | None = None


@dataclass(frozen=True)
class SourceContext:
    path: str
    raw: str
    comments: str
    code: str
    strings: list[tuple[int, int, str]]
    lines: list[str]


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    confidence: str
    kind: Literal["c", "build"]
    title: str
    suggestion: str
    doc_url: str | None
    detector: Callable[[SourceContext], Iterable[Hit]]


def include_and_calls(
    headers: tuple[str, ...],
    calls: tuple[str, ...],
    label: str,
    refine: Callable[[str, str], dict[str, str]] | None = None,
) -> Callable[[SourceContext], Iterable[Hit]]:
    """Create a detector for listed include headers and function calls."""
    header_patterns = [
        (header, re.compile(r'^\s*#\s*include\s*[<"]' + re.escape(header) + r'[>"]', re.M))
        for header in headers
    ]
    call_patterns = [
        (name, re.compile(r'(?<![\w.>:])(?:::)?' + re.escape(name) + r'\s*\('))
        for name in calls
    ]

    def detect(context: SourceContext) -> Iterable[Hit]:
        for header, pattern in header_patterns:
            if header not in context.comments:
                continue
            for match in pattern.finditer(context.comments):
                line, col = position(context.comments, match.start())
                yield Hit(line, col, f"Linux {label} header <{header}>")
        for name, pattern in call_patterns:
            if name not in context.code:
                continue
            for match in pattern.finditer(context.code):
                line, col = position(context.code, match.start())
                overrides = refine(name, context.lines[line - 1]) if refine else {}
                yield Hit(line, col, f"Linux {label} API {name}()", **overrides)
    return detect

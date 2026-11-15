"""Shared types and detector helpers for portability rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Literal
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


def include_and_calls(headers: tuple[str, ...], calls: tuple[str, ...], label: str,
                      suggestion: str, doc_url: str | None,
                      severity: str = "warning", confidence: str = "high") -> Callable:
    """Create detector for listed includes and unqualified function calls."""
    def detect(context: SourceContext) -> Iterable[Hit]:
        for header in headers:
            pattern = re.compile(r'^\s*#\s*include\s*[<"]' + re.escape(header) + r'[>"]', re.M)
            for match in pattern.finditer(context.comments):
                line, col = _position(context.comments, match.start())
                yield Hit(line, col, f"Linux {label} header <{header}>")
        for name in calls:
            pattern = re.compile(r'(?<![\w.>])(?:::)?' + re.escape(name) + r'\s*\(')
            for match in pattern.finditer(context.code):
                line, col = _position(context.code, match.start())
                original_line = context.raw.splitlines()[line - 1] if line <= len(context.raw.splitlines()) else ""
                if name == "prctl":
                    yield Hit(line, col, f"Linux prctl API ({name})",
                              confidence="high" if "PR_SET_NAME" in original_line else "medium")
                elif name == "pipe2" and ("O_DIRECT" in original_line or "O_NOTIFICATION_PIPE" in original_line):
                    yield Hit(line, col, f"Linux {label} API {name}()", severity="warning")
                else:
                    yield Hit(line, col, f"Linux {label} API {name}()")
        if label == "syscall":
            for line_no, line in enumerate(context.code.splitlines(), 1):
                for match in re.finditer(r'\b(?:SYS_[a-z_0-9]+|__NR_[a-z_0-9]+)\b', line):
                    token = match.group()
                    yield Hit(line_no, match.start() + 1, f"Linux syscall number {token}")
    return detect


def _position(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    return line, offset - text.rfind("\n", 0, offset)

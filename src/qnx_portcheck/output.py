"""Shared report output handling.

Every report ends with exactly one newline; empty output prints nothing (no blank line).
"""
from __future__ import annotations

import sys
from pathlib import Path


def emit(text: str, out: str | Path | None = None) -> None:
    """Write a report with exactly one trailing newline, or nothing if it is empty."""
    normalized = text.rstrip("\n")
    value = normalized + "\n" if normalized else ""
    if out is not None:
        with Path(out).open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
    elif value:
        sys.stdout.write(value)

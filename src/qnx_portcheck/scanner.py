"""Discover source files and apply registered portability rules."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from .lexer import lex
from .rules import ALL_RULES, SourceContext

@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    file: str
    line: int
    col: int
    message: str
    suggestion: str
    doc_url: str | None
    confidence: str

@dataclass
class ScanResult:
    root: Path
    findings: list[Finding]
    files_scanned: int

C_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
BUILD_NAMES = {"CMakeLists.txt", "Makefile", "makefile", "GNUmakefile", "meson.build"}

def _is_build(path: Path) -> bool:
    return path.name in BUILD_NAMES or path.suffix in {".cmake", ".mk"}

def _discover(path: Path) -> tuple[Path, list[Path]]:
    absolute = path.absolute()
    root = absolute if absolute.is_dir() else absolute.parent
    if absolute.is_file():
        files = [absolute]
    else:
        files = []
        for directory, dirs, names in os.walk(absolute, followlinks=False):
            dirs[:] = sorted(name for name in dirs if not name.startswith(".")
                             and name not in {".git", ".hg", ".svn"}
                             and not (Path(directory) / name).is_symlink())
            for name in sorted(names):
                candidate = Path(directory) / name
                if candidate.suffix in C_SUFFIXES or _is_build(candidate):
                    files.append(candidate)
    return root, sorted(files, key=lambda item: item.as_posix())

def scan(path: str | Path) -> ScanResult:
    """Scan one file or a directory and return findings with root metadata."""
    root, files = _discover(Path(path))
    findings: list[Finding] = []
    for file_path in files:
        relative = file_path.relative_to(root).as_posix()
        raw = file_path.read_text(encoding="utf-8", errors="replace")
        if file_path.suffix in C_SUFFIXES:
            code, strings, comments = lex(raw)
            kind = "c"
        elif _is_build(file_path):
            code, strings, comments, kind = raw, [], raw, "build"
        else:
            continue
        context = SourceContext(relative, raw, comments, code, strings, raw.splitlines())
        seen = set()
        for rule in ALL_RULES:
            if rule.kind != kind:
                continue
            for hit in rule.detector(context):
                identity = (rule.id, relative, hit.line, hit.col)
                if identity in seen:
                    continue
                seen.add(identity)
                findings.append(Finding(
                    rule.id, hit.severity or rule.severity, relative,
                    hit.line, hit.col, hit.message,
                    hit.suggestion if hit.suggestion is not None else rule.suggestion,
                    hit.doc_url if hit.doc_url is not None else rule.doc_url,
                    hit.confidence or rule.confidence,
                ))
    findings.sort(key=lambda item: (item.file, item.line, item.col, item.rule_id))
    return ScanResult(root, findings, len(files))

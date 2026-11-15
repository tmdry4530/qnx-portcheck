"""Discover source files and apply registered portability rules."""
from __future__ import annotations

from dataclasses import dataclass
import os
import re
from pathlib import Path
from .lexer import lex
from .rules import ALL_RULES, SourceContext
from .rules.buildfiles import _without_comments
from .rules.guards import feature_guarded_lines, linux_only_lines

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
# Generated or third-party autoconf macro files (aclocal output, libtool, autoconf-archive, gnulib, gettext).
_AUTOCONF_EXCLUDED = {"aclocal.m4", "libtool.m4", "pkg.m4"}
_AUTOCONF_EXCLUDED_PREFIXES = ("lt", "ax_", "acx_", "pkg", "lib-", "gl_", "gettext", "iconv", "nls", "po.m4",
                               "progtest", "intl")

def _is_build(path: Path) -> bool:
    return (path.name in BUILD_NAMES or path.suffix in {".cmake", ".mk"}
            or path.name in {"configure.ac", "configure.in"}
            or (path.suffix == ".m4" and path.name not in _AUTOCONF_EXCLUDED
                and not path.name.startswith(_AUTOCONF_EXCLUDED_PREFIXES)))

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
            comments = _without_comments(raw)
            if file_path.name in {"configure.ac", "configure.in"} or file_path.suffix == ".m4":
                chars = list(comments)
                for match in re.finditer(r'(?im)(?<!\S)dnl\b[^\n]*', comments):
                    for offset in range(match.start(), match.end()): chars[offset] = " "
                comments = "".join(chars)
            code, strings, kind = raw, [], "build"
        else:
            continue
        context = SourceContext(relative, raw, comments, code, strings, raw.splitlines())
        seen = set()
        for rule in ALL_RULES:
            if rule.kind != kind:
                continue
            hits = rule.detector(context)
            linux_lines = None
            feature_lines = None
            for hit in hits:
                if rule.skip_in_linux_guard:
                    if linux_lines is None:
                        linux_lines = linux_only_lines(context.comments)
                    if hit.line in linux_lines:
                        continue
                if rule.feature_token:
                    if feature_lines is None:
                        feature_lines = feature_guarded_lines(context.comments, rule.feature_token)
                    if hit.line in feature_lines:
                        continue
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

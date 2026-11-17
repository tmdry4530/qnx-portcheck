"""Guard tracked paths against SAND_BOX_WORKSPACE_DEFAULT_IGNORE_PATTERNS from /opt/sand/sand-host/host-main.cjs (gitignore-style)."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
DEFAULT_IGNORE_PATTERNS = [
    "node_modules/",
    ".next/",
    ".nuxt/",
    ".svelte-kit/",
    ".turbo/",
    ".parcel-cache/",
    ".cache/",
    "dist/",
    "build/",
    "out/",
    "coverage/",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    ".venv/",
    "venv/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".tox/",
    ".ipynb_checkpoints/",
    "*.egg-info/",
    ".eggs/",
    "target/",
    ".gradle/",
    "core.[0-9]*",
    "*.core",
    "/browser-cdp/",
    "/screenshots/",
]


def _glob_regex(pattern: str) -> re.Pattern[str]:
    parts = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            parts.append("[^/]*")
        elif char == "?":
            parts.append("[^/]")
        elif char == "[":
            end = pattern.find("]", index + 1)
            if end < 0:
                parts.append(r"\[")
            else:
                contents = pattern[index + 1:end]
                if contents.startswith("!"):
                    contents = "^" + contents[1:]
                elif contents.startswith("^"):
                    contents = "\\" + contents
                parts.append("[" + contents.replace("\\", "\\\\") + "]")
                index = end
        else:
            parts.append(re.escape(char))
        index += 1
    return re.compile("".join(parts))


def matches_ignore(path: str, pattern: str) -> bool:
    path = path.replace("\\", "/").removeprefix("./").strip("/")
    if not path:
        return False
    directory = pattern.endswith("/")
    anchored = pattern.startswith("/")
    body = pattern.strip("/")
    if not body:
        return False
    regex = _glob_regex(body)
    if "/" in body:
        return bool(regex.fullmatch(path) or (directory and regex.fullmatch(path.split("/", 1)[0])))
    segments = path.split("/")
    if directory:
        candidates = segments[:-1]
        if anchored:
            candidates = candidates[:1]
        return any(regex.fullmatch(segment) for segment in candidates)
    candidates = segments[-1:] if body.startswith("*") or body.startswith("?") else segments
    if anchored:
        candidates = segments[:1]
    return any(regex.fullmatch(segment) for segment in candidates)


def first_matching_pattern(path: str) -> str | None:
    return next((pattern for pattern in DEFAULT_IGNORE_PATTERNS if matches_ignore(path, pattern)), None)


def test_tracked_files_do_not_match_box_store_ignore_patterns() -> None:
    if shutil.which("git") is None:
        pytest.skip("git is not on PATH")
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    )
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", errors="surrogateescape")
        pattern = first_matching_pattern(path)
        assert pattern is None, f"tracked path {path!r} matches ignore pattern {pattern!r}"


@pytest.mark.parametrize(
    ("path", "pattern", "expected"),
    [
        ("tests/fixtures/build/autoconf_host/pos/configure.ac", "build/", True),
        ("tests/fixtures/buildsys/autoconf_host/pos/configure.ac", "build/", False),
        ("tests/fixtures/buildfiles/bad/multiple.build", "build/", False),
        ("qnxref/pyenv/bin/python", "venv/", False),
        ("qnxref/pyenv/bin/python", ".venv/", False),
        ("/screenshots/x", "/screenshots/", True),
        ("screenshots/x", "/screenshots/", True),
        ("docs/screenshots/x", "/screenshots/", False),
        ("foo/__pycache__/a.py", "__pycache__/", True),
        ("mod.pyc", "*.pyc", True),
        ("", "build/", False),
    ],
)
def test_matcher_examples(path: str, pattern: str, expected: bool) -> None:
    assert matches_ignore(path, pattern) is expected

"""Deterministic, deliberately fake scanner used only for harness smoke tests."""

import argparse
import sys
import json
import os
import re
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL_DIR))
from run_eval import BUILD_EXTS, BUILD_NAMES, SOURCE_EXTS

SOURCE_TOKENS = [
    "epoll_",
    "inotify_",
    "eventfd",
    "timerfd_",
    "signalfd",
    "prctl",
    "sys/sysinfo.h",
    "/proc/self",
    "__linux__",
    "sys/epoll.h",
    "linux/",
    "SOCK_CLOEXEC",
    "MSG_NOSIGNAL",
    "pthread_setname_np",
    "sched_setaffinity",
]
BUILD_TOKENS = ["-ldl", "-lrt", "-lpthread", 'CMAKE_SYSTEM_NAME STREQUAL "Linux"']


def main(argv=None):
    """Scan eligible files and emit deterministic fake findings."""
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan")
    scan.add_argument("path")
    scan.add_argument("--format", choices=["json"], required=True)
    args = ap.parse_args(argv)
    root = Path(args.path).resolve()
    findings = []
    for file in sorted(root.rglob("*")):
        if (
            not file.is_file()
            or ".git" in file.relative_to(root).parts
            or file.stat().st_size > 2 * 1024 * 1024
        ):
            continue
        ext = file.suffix.lower()
        is_source = ext in SOURCE_EXTS or file.name.endswith(".C")
        is_build = file.name in BUILD_NAMES or ext in BUILD_EXTS
        if not (is_source or is_build):
            continue
        rel = file.relative_to(root).as_posix()
        for line_no, line in enumerate(file.read_text(errors="replace").splitlines(), 1):
            tokens = SOURCE_TOKENS if is_source else BUILD_TOKENS
            for token in tokens:
                if is_source or is_build:
                    pos = line.find(token)
                    if pos >= 0:
                        safe = re.sub(r"[^A-Za-z0-9]+", "-", token).strip("-").upper()
                        findings.append(
                            {
                                "rule_id": f"FAKE-{safe}",
                                "severity": "warning",
                                "file": rel,
                                "line": line_no,
                                "col": pos + 1,
                                "message": f"FAKE scanner token hit: {token}",
                                "suggestion": "manual review",
                                "doc_url": None,
                                "confidence": "manual-review",
                            }
                        )
    findings.sort(key=lambda f: (f["file"], f["line"], f["col"], f["rule_id"]))
    print(
        json.dumps(
            {
                "tool": "fake-scan",
                "version": "0.0.0-fake",
                "root": str(root),
                "findings": findings,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

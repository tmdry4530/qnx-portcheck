"""CLI command for scanning C/C++ and build files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from qnx_portcheck.report import to_json, to_sarif, to_text
from qnx_portcheck.scanner import scan

def register(subparsers: argparse._SubParsersAction) -> None:
    """Register scan command options."""
    parser = subparsers.add_parser(
        "scan", help="scan source and build files for Linux portability issues"
    )
    parser.add_argument("path")
    parser.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    parser.add_argument("--out")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error")
    parser.set_defaults(func=run)

def run(args: argparse.Namespace) -> int:
    """Execute scan and write the selected report."""
    path = Path(args.path)
    if not path.exists():
        print(f"path does not exist: {args.path}", file=sys.stderr)
        return 2
    result = scan(path)
    reports = {"text": to_text(result.findings, result.files_scanned),
               "json": json.dumps(to_json(result.findings, result.root), indent=2),
               "sarif": json.dumps(to_sarif(result.findings, result.root), indent=2)}
    output = reports[args.format]
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    rank = {"error": 2, "warning": 1, "note": 0, "never": -1}
    return int(args.fail_on != "never" and any(
        rank[item.severity] >= rank[args.fail_on] for item in result.findings
    ))

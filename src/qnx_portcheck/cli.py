"""Command entry point for qnx-portcheck."""
from __future__ import annotations

import argparse
from qnx_portcheck import __version__, lint_buildfile, scaffold
from qnx_portcheck.commands import scan as scan_command


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to a registered command."""
    parser = argparse.ArgumentParser(prog="qnx-portcheck")
    parser.add_argument("--version", action="version", version=f"qnx-portcheck {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan_command.register(subparsers)
    scaffold.register(subparsers)
    lint_buildfile.register(subparsers)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

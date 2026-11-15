"""Command entry point with hooks for independently developed commands."""
from __future__ import annotations

import argparse
import importlib
from qnx_portcheck import __version__

# Missing optional command modules are skipped so teams can add them independently.
COMMAND_MODULES = ("qnx_portcheck.commands.scan", "qnx_portcheck.commands.scaffold",
                   "qnx_portcheck.commands.lint_buildfile")

def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to a registered command."""
    parser = argparse.ArgumentParser(prog="qnx-portcheck")
    parser.add_argument("--version", action="version", version=f"qnx-portcheck {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for module_name in COMMAND_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            if error.name == module_name:
                continue
            raise
        module.register(subparsers)
    args = parser.parse_args(argv)
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())

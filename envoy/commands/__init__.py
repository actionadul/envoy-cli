"""Root parser and dispatcher for envoy CLI commands."""

import argparse
import sys

from envoy.commands import (
    compare,
    export,
    list as list_cmd,
    validate,
    merge,
    audit,
    promote,
    snapshot,
    lint,
)

_COMMANDS = [
    compare,
    export,
    list_cmd,
    validate,
    merge,
    audit,
    promote,
    snapshot,
    lint,
]


def build_root_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Manage and diff environment variable sets across deployment targets.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    for mod in _COMMANDS:
        mod.build_parser(subparsers)
    return parser


def dispatch(argv=None) -> int:
    parser = build_root_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    for mod in _COMMANDS:
        if args.command == mod.build_parser.__module__.split(".")[-1].replace("list", "list"):
            return mod.run(args)

    # Fallback: use subparser default func if set
    if hasattr(args, "func"):
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(dispatch())

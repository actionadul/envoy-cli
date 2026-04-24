"""Registry of all envoy sub-commands."""

import argparse

from envoy.commands import audit, compare, export, list as list_cmd, merge, validate

_COMMANDS = [
    audit,
    compare,
    export,
    list_cmd,
    merge,
    validate,
]


def build_root_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Manage and diff environment variable sets across deployment targets.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    for cmd in _COMMANDS:
        cmd.build_parser(subparsers)

    return parser


def dispatch(args: argparse.Namespace) -> int:
    """Dispatch to the appropriate command's run() function."""
    for cmd in _COMMANDS:
        cmd_name = cmd.__name__.split(".")[-1].replace("_cmd", "")
        if args.command == cmd_name or args.command == cmd.__name__.split(".")[-1]:
            return cmd.run(args)
    raise ValueError(f"Unknown command: {args.command}")

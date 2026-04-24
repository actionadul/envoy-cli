"""Root parser and dispatcher for envoy CLI commands."""

import argparse

from envoy.commands import compare, export, list as list_cmd, validate, merge, audit, promote


COMMANDS = {
    "compare": compare,
    "export": export,
    "list": list_cmd,
    "validate": validate,
    "merge": merge,
    "audit": audit,
    "promote": promote,
}


def build_root_parser():
    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Manage and diff environment variable sets across deployment targets.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    for name, module in COMMANDS.items():
        module.build_parser(subparsers)

    return parser


def dispatch(args, stdout=None, stderr=None):
    """Dispatch parsed args to the appropriate command's run function."""
    module = COMMANDS.get(args.command)
    if module is None:
        raise ValueError(f"Unknown command: {args.command}")
    return module.run(args, stdout=stdout, stderr=stderr)

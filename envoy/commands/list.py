"""List command: display available deployment targets."""

import argparse
import sys

from envoy.resolver import list_targets, resolve_target


def build_parser(subparsers=None):
    """Build the argument parser for the list command."""
    description = "List available deployment targets"

    if subparsers is not None:
        parser = subparsers.add_parser("list", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "env_dir",
        metavar="ENV_DIR",
        help="Directory containing environment files",
    )
    parser.add_argument(
        "--show-keys",
        action="store_true",
        default=False,
        help="Show the number of keys defined in each target",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Only print target names, one per line",
    )
    return parser


def run(args, stdout=None, stderr=None):
    """Execute the list command.

    Returns an exit code (0 for success, non-zero for failure).
    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    targets = list_targets(args.env_dir)

    if not targets:
        if not args.quiet:
            print("No targets found in '{}'".format(args.env_dir), file=stderr)
        return 1

    if args.quiet:
        for target in targets:
            print(target, file=stdout)
        return 0

    print("Targets in '{}':".format(args.env_dir), file=stdout)
    for target in targets:
        if args.show_keys:
            try:
                env = resolve_target(args.env_dir, target)
                key_count = len(env)
                print("  {:<30} ({} keys)".format(target, key_count), file=stdout)
            except Exception as exc:  # pragma: no cover
                print("  {:<30} (error: {})".format(target, exc), file=stdout)
        else:
            print("  {}".format(target), file=stdout)

    return 0

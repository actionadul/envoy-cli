"""CLI command: promote env vars from one target to another."""

import argparse
import sys

from envoy.promoter import promote, summary
from envoy.parser import write_env_file
from envoy.resolver import resolve_target


def build_parser(subparsers=None):
    description = "Promote env vars from one target to another."
    if subparsers is not None:
        parser = subparsers.add_parser("promote", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy promote", description=description)

    parser.add_argument("source", help="Source target name")
    parser.add_argument("destination", help="Destination target name")
    parser.add_argument(
        "--keys",
        nargs="+",
        default=None,
        metavar="KEY",
        help="Specific keys to promote (default: all)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing keys in destination",
    )
    parser.add_argument(
        "--env-dir",
        default=".",
        help="Directory containing .env files (default: .)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be promoted without writing changes",
    )
    return parser


def run(args, stdout=None, stderr=None):
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    result = promote(
        env_dir=args.env_dir,
        source=args.source,
        destination=args.destination,
        keys=args.keys,
        overwrite=args.overwrite,
    )

    stdout.write(summary(result) + "\n")

    if result.promoted and not args.dry_run:
        dst_env = resolve_target(args.env_dir, args.destination)
        dst_env.update(result.promoted)
        import os
        dest_path = os.path.join(args.env_dir, f"{args.destination}.env")
        write_env_file(dest_path, dst_env)
        stdout.write(f"Written to {dest_path}\n")
    elif args.dry_run:
        stdout.write("Dry run — no changes written.\n")

    return 0

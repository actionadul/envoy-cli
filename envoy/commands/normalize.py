"""CLI command: normalize — clean and standardize an env file in place."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.normalizer import normalize, has_changes, summary
from envoy.parser import parse_env_file, write_env_file


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Normalize an env file: uppercase keys, strip whitespace, sort, etc."
    if parent is not None:
        parser = parent.add_parser("normalize", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy normalize", description=description)

    parser.add_argument("file", help="Path to the .env file to normalize")
    parser.add_argument(
        "--no-uppercase",
        dest="uppercase",
        action="store_false",
        default=True,
        help="Do not uppercase keys (default: uppercase)",
    )
    parser.add_argument(
        "--no-sort",
        dest="sort",
        action="store_false",
        default=True,
        help="Do not sort keys alphabetically (default: sort)",
    )
    parser.add_argument(
        "--remove-empty",
        action="store_true",
        default=False,
        help="Remove keys with empty values",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        metavar="PREFIX",
        help="Add a prefix to all keys that do not already have it",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print changes without writing to disk",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    result = normalize(
        env,
        uppercase_keys=args.uppercase,
        strip_values=True,
        sort_keys=args.sort,
        remove_empty=args.remove_empty,
        prefix=args.prefix,
    )

    print(summary(result))

    if not has_changes(result):
        return 0

    if args.dry_run:
        print("Dry run — no changes written.")
        return 0

    write_env_file(args.file, result.normalized)
    print(f"Normalized env written to {args.file}")
    return 0

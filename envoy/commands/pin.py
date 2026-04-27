"""CLI command: pin — enforce fixed values for specified keys."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.parser import parse_env_file, write_env_file
from envoy.pinner import apply, has_changes, pin, summary
from envoy.resolver import resolve_target


def build_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser(
        "pin",
        help="Enforce fixed values for one or more keys in a target env file.",
    )
    p.add_argument("target", help="Deployment target name (e.g. staging).")
    p.add_argument(
        "--set",
        dest="pairs",
        metavar="KEY=VALUE",
        nargs="+",
        required=True,
        help="Key=value pairs to pin.",
    )
    p.add_argument(
        "--allow-new",
        action="store_true",
        default=False,
        help="Allow pinning keys that do not yet exist in the target.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing to disk.",
    )
    p.add_argument(
        "--env-dir",
        default=".",
        help="Directory containing .env files (default: current directory).",
    )
    return p


def _parse_pairs(pairs: List[str]) -> dict:
    result = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(f"Invalid format '{pair}', expected KEY=VALUE.")
        key, _, value = pair.partition("=")
        result[key.strip()] = value.strip()
    return result


def run(args: argparse.Namespace) -> int:
    try:
        path = resolve_target(args.env_dir, args.target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        pins = _parse_pairs(args.pairs)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    env = parse_env_file(path)
    result = pin(env, pins, only_existing=not args.allow_new)

    print(summary(result))

    if not has_changes(result):
        return 0

    if args.dry_run:
        for key, value in sorted(result.pinned.items()):
            old = result.original.get(key, "<new>")
            print(f"  {key}: {old!r} -> {value!r}")
        return 0

    merged = apply(env, result)
    write_env_file(path, merged)
    return 0

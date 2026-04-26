"""CLI command: strip keys from an env target."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target
from envoy.stripper import strip, has_changes, summary


def build_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser(
        "strip",
        help="Remove keys from an env target by name or glob pattern.",
    )
    p.add_argument("target", help="Target name (e.g. staging).")
    p.add_argument(
        "--key",
        dest="keys",
        metavar="KEY",
        action="append",
        default=[],
        help="Exact key name to remove (repeatable).",
    )
    p.add_argument(
        "--pattern",
        dest="patterns",
        metavar="GLOB",
        action="append",
        default=[],
        help="Glob pattern for keys to remove, e.g. '*_SECRET' (repeatable).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be removed without writing changes.",
    )
    p.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing env files (default: envs).",
    )
    return p


def run(args: argparse.Namespace) -> int:
    try:
        path = resolve_target(args.target, env_dir=args.env_dir)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.keys and not args.patterns:
        print("error: provide at least one --key or --pattern.", file=sys.stderr)
        return 1

    env = parse_env_file(path)
    result = strip(env, keys=args.keys, patterns=args.patterns)

    print(summary(result))

    if not has_changes(result):
        return 0

    if args.dry_run:
        print("Dry-run mode — no files written.")
        return 0

    write_env_file(path, result.stripped)
    return 0

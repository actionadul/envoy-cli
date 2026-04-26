"""CLI command: patch — set or unset keys in an env target."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.patcher import patch, has_changes, summary
from envoy.resolver import resolve_target
from envoy.parser import write_env_file


def build_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser(
        "patch",
        help="Set or unset environment variable keys in a target file.",
    )
    p.add_argument("target", help="Deployment target name (e.g. staging).")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        dest="sets",
        action="append",
        default=[],
        help="Set KEY to VALUE (repeatable).",
    )
    p.add_argument(
        "--unset",
        metavar="KEY",
        dest="unsets",
        action="append",
        default=[],
        help="Remove KEY from the target (repeatable).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing.",
    )
    p.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing env files (default: envs).",
    )
    return p


def _parse_set_args(raw: List[str]) -> List[tuple]:
    pairs = []
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"--set value must be KEY=VALUE, got: {item!r}"
            )
        key, _, value = item.partition("=")
        pairs.append((key.strip(), value))
    return pairs


def run(args: argparse.Namespace) -> int:
    try:
        env, path = resolve_target(args.target, env_dir=args.env_dir)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        sets = _parse_set_args(args.sets)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = patch(env, sets=sets, unsets=args.unsets)

    if not has_changes(result):
        print("No changes.")
        return 0

    print(summary(result))

    if args.dry_run:
        for key in result.added:
            print(f"  + {key}={result.patched[key]}")
        for key in result.updated:
            print(f"  ~ {key}={result.patched[key]}  (was: {result.original[key]})")
        for key in result.removed:
            print(f"  - {key}")
        return 0

    write_env_file(path, result.patched)
    return 0

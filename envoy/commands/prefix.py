"""CLI command: add or strip a key prefix across an env target."""
from __future__ import annotations

import argparse
import sys

from envoy.prefixer import add_prefix, strip_prefix, has_changes, summary
from envoy.resolver import resolve_target
from envoy.parser import write_env_file


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        name="prefix",
        description="Add or strip a prefix from environment variable keys.",
        help="add or strip a key prefix",
    )
    if parent is not None:
        parser = parent.add_parser(**kwargs)
    else:
        parser = argparse.ArgumentParser(**{k: v for k, v in kwargs.items() if k != "name"})

    parser.add_argument("target", help="deployment target (e.g. staging)")
    parser.add_argument("prefix", help="prefix string to add or strip")

    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument(
        "--add",
        action="store_true",
        default=True,
        help="add the prefix to keys that lack it (default)",
    )
    mode.add_argument(
        "--strip",
        action="store_true",
        default=False,
        help="remove the prefix from keys that have it",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="print changes without writing to disk",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        help="directory containing env files (default: envs)",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        env = resolve_target(args.env_dir, args.target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.strip:
        result = strip_prefix(env, args.prefix)
    else:
        result = add_prefix(env, args.prefix)

    print(summary(result))

    for old_key, new_key in result.changed:
        print(f"  {old_key} -> {new_key}")

    if has_changes(result) and not args.dry_run:
        target_path = f"{args.env_dir}/{args.target}.env"
        write_env_file(target_path, result.updated)
        print(f"Written to {target_path}")

    return 0

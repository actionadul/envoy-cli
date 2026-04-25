"""CLI command: rename keys in an env target."""

import argparse
import sys
from typing import List, Optional

from envoy.renamer import rename, has_changes, summary
from envoy.resolver import resolve_target
from envoy.parser import write_env_file


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Rename one or more keys in an env target."
    if parent is not None:
        parser = parent.add_parser("rename", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy rename", description=description)

    parser.add_argument("target", help="Target environment name (e.g. staging).")
    parser.add_argument(
        "mapping",
        nargs="+",
        metavar="OLD=NEW",
        help="One or more key rename pairs in OLD=NEW format.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Allow renaming even when the target key already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would change without writing to disk.",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing env files (default: envs).",
    )
    return parser


def _parse_mapping(pairs: List[str]) -> dict:
    mapping = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid mapping '{pair}': expected OLD=NEW format.")
        old, new = pair.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


def run(args: argparse.Namespace) -> int:
    try:
        mapping = _parse_mapping(args.mapping)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        env, path = resolve_target(args.target, env_dir=args.env_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = rename(env, mapping, overwrite=args.overwrite)

    print(summary(result))

    if result.skipped:
        for key in result.skipped:
            print(f"  skipped: {key}")

    if not has_changes(result):
        return 0

    if args.dry_run:
        for old_key, new_key in result.changes:
            print(f"  {old_key} -> {new_key}")
        return 0

    write_env_file(path, result.renamed)
    return 0

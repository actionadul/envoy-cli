"""group command — display environment variables organised by prefix."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.grouper import group, has_groups, summary
from envoy.parser import parse_env_file
from envoy.resolver import resolve_target


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="envoy group",
        description="Group environment variables by prefix.",
    )
    parser = parent.add_parser("group", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("target", help="Target environment name (e.g. staging)")
    parser.add_argument(
        "--prefix",
        dest="prefixes",
        metavar="PREFIX",
        action="append",
        default=None,
        help="Explicit prefix to group by (repeatable). Auto-detects when omitted.",
    )
    parser.add_argument(
        "--separator",
        default="_",
        help="Key separator used to split prefixes (default: '_').",
    )
    parser.add_argument(
        "--min-keys",
        type=int,
        default=2,
        dest="min_keys",
        help="Minimum keys required to form an auto-detected group (default: 2).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a summary instead of full key listing.",
    )
    parser.add_argument(
        "--env-dir",
        default=".",
        dest="env_dir",
        help="Directory containing .env files (default: current directory).",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    target_path = resolve_target(args.env_dir, args.target)
    if target_path is None:
        print(f"error: target '{args.target}' not found in '{args.env_dir}'", file=sys.stderr)
        return 1

    env = parse_env_file(target_path)
    result = group(
        env,
        prefixes=args.prefixes,
        separator=args.separator,
        min_prefix_length=args.min_keys,
    )

    if args.summary:
        print(summary(result))
        return 0

    if not has_groups(result):
        print("No groups found.")
        return 0

    for group_name, members in sorted(result.groups.items()):
        print(f"[{group_name}]")
        for key, value in sorted(members.items()):
            print(f"  {key}={value}")

    if result.ungrouped:
        print("[ungrouped]")
        for key, value in sorted(result.ungrouped.items()):
            print(f"  {key}={value}")

    return 0

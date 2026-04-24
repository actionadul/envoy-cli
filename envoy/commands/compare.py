"""CLI command: compare two deployment targets and print a diff."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.resolver import resolve_target
from envoy.differ import diff_envs, format_diff, has_differences


def build_parser(subparsers: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "compare",
        help="Diff environment variables between two targets.",
    )
    p.add_argument("target_a", help="First deployment target (e.g. staging)")
    p.add_argument("target_b", help="Second deployment target (e.g. production)")
    p.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing .env.<target> files (default: envs)",
    )
    p.add_argument(
        "--base",
        default=".env",
        metavar="FILE",
        help="Base .env file merged before target overrides (default: .env)",
    )
    p.add_argument(
        "--no-base",
        action="store_true",
        help="Do not load a base .env file.",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found.",
    )
    return p


def run(args: argparse.Namespace) -> int:
    base_file: Optional[str] = None if args.no_base else args.base

    try:
        env_a = resolve_target(args.target_a, env_dir=args.env_dir, base_file=base_file)
        env_b = resolve_target(args.target_b, env_dir=args.env_dir, base_file=base_file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(env_a, env_b)
    output = format_diff(result, label_a=args.target_a, label_b=args.target_b)
    print(output)

    if args.exit_code and has_differences(result):
        return 1
    return 0

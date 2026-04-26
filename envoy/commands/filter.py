"""CLI command: filter — display a filtered subset of an env target."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.filter import filter_env, has_matches, summary
from envoy.resolver import resolve_target


def build_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Filter and display env vars by key pattern or value regex."
    if subparsers is not None:
        parser = subparsers.add_parser("filter", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy filter", description=description)

    parser.add_argument("target", help="Target environment name (e.g. staging)")
    parser.add_argument(
        "--include",
        metavar="PATTERN",
        nargs="+",
        dest="include_patterns",
        default=None,
        help="Glob patterns for keys to include (e.g. APP_*)",
    )
    parser.add_argument(
        "--exclude",
        metavar="PATTERN",
        nargs="+",
        dest="exclude_patterns",
        default=None,
        help="Glob patterns for keys to exclude",
    )
    parser.add_argument(
        "--value",
        metavar="REGEX",
        dest="value_pattern",
        default=None,
        help="Regex pattern values must match",
    )
    parser.add_argument(
        "--keys-only",
        action="store_true",
        default=False,
        help="Ignore value pattern; filter by key only",
    )
    parser.add_argument(
        "--env-dir",
        default=".",
        help="Directory containing .env files (default: current directory)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    env = resolve_target(args.target, env_dir=args.env_dir)
    result = filter_env(
        env,
        include_patterns=args.include_patterns,
        exclude_patterns=args.exclude_patterns,
        value_pattern=args.value_pattern,
        keys_only=args.keys_only,
    )

    for key, value in result.filtered.items():
        print(f"{key}={value}")

    if not args.quiet:
        print(f"# {summary(result)}", file=sys.stderr)

    return 0 if has_matches(result) else 1

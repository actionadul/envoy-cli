"""CLI command: scope — filter env vars by prefix and optionally strip it."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target
from envoy.scoper import has_matches, scope, summary


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Filter env vars by prefix, optionally stripping the prefix."
    if parent is not None:
        parser = parent.add_parser("scope", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy scope", description=description)

    parser.add_argument("target", help="Deployment target name (e.g. staging).")
    parser.add_argument("prefix", help="Key prefix to filter by (e.g. APP_).")
    parser.add_argument(
        "--strip",
        action="store_true",
        default=False,
        help="Strip the prefix from matched keys in the output.",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        default=False,
        help="Match prefix case-insensitively.",
    )
    parser.add_argument(
        "--out",
        metavar="FILE",
        default=None,
        help="Write scoped env to FILE instead of printing to stdout.",
    )
    parser.add_argument(
        "--env-dir",
        default=".",
        metavar="DIR",
        help="Directory containing .env files (default: current directory).",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    target_path = resolve_target(args.env_dir, args.target)
    if target_path is None:
        print(f"error: target '{args.target}' not found in '{args.env_dir}'", file=sys.stderr)
        return 1

    env = parse_env_file(target_path)
    result = scope(
        env,
        args.prefix,
        strip_prefix=args.strip,
        case_sensitive=not args.ignore_case,
    )

    print(summary(result), file=sys.stderr)

    if args.out:
        write_env_file(args.out, result.scoped)
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        for key, value in result.scoped.items():
            print(f"{key}={value}")

    return 0 if has_matches(result) else 1

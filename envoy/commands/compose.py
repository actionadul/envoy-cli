"""compose command — merge multiple env targets into one with precedence."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.composer import compose, has_conflicts, summary
from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        name="compose",
        description="Merge multiple env targets into one. Later targets take precedence.",
        help="merge env targets by precedence",
    )
    if parent is not None:
        parser = parent.add_parser(**kwargs)
    else:
        parser = argparse.ArgumentParser(**{k: v for k, v in kwargs.items() if k != "name"})

    parser.add_argument(
        "targets",
        nargs="+",
        metavar="TARGET",
        help="env targets to merge, ordered lowest to highest precedence",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="directory containing env files (default: envs)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="write composed env to FILE instead of stdout",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="exit with code 1 if any conflicts are found",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    pairs = []
    for target in args.targets:
        path = resolve_target(args.env_dir, target)
        if path is None:
            print(f"error: target '{target}' not found in {args.env_dir}", file=sys.stderr)
            return 1
        env = parse_env_file(str(path))
        pairs.append((target, env))

    result = compose(pairs)
    print(summary(result), file=sys.stderr)

    if args.output:
        write_env_file(args.output, result.composed)
    else:
        for key, value in result.composed.items():
            print(f"{key}={value}")

    if args.strict and has_conflicts(result):
        return 1
    return 0

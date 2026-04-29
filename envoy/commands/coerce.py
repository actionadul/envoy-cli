"""CLI command: coerce — normalise env var values to canonical types."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.coercer import coerce, has_errors, summary
from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Coerce env var values to canonical type representations."
    if parent is not None:
        parser = parent.add_parser("coerce", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy coerce", description=description)

    parser.add_argument("target", help="Deployment target name (e.g. staging)")
    parser.add_argument(
        "--rule",
        dest="rules",
        metavar="KEY:TYPE",
        action="append",
        default=[],
        help="Coercion rule in KEY:TYPE format (may be repeated). "
             "Supported types: bool, int, float, str.",
    )
    parser.add_argument(
        "--env-dir",
        default=".",
        help="Directory containing .env files (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would change without writing the file",
    )
    return parser


def _parse_rules(raw: List[str]) -> dict[str, str]:
    rules: dict[str, str] = {}
    for item in raw:
        if ":" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid rule {item!r}: expected KEY:TYPE format"
            )
        key, _, type_ = item.partition(":")
        rules[key.strip()] = type_.strip()
    return rules


def run(args: argparse.Namespace) -> int:
    try:
        path = resolve_target(args.target, args.env_dir)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    env = parse_env_file(path)

    try:
        rules = _parse_rules(args.rules)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not rules:
        print("No coercion rules provided. Use --rule KEY:TYPE.", file=sys.stderr)
        return 1

    result = coerce(env, rules)

    for key, old, new in result.changed:
        print(f"  ~ {key}: {old!r} -> {new!r}")
    for key, val, reason in result.errors:
        print(f"  ! {key}: {reason}", file=sys.stderr)

    print(summary(result))

    if has_errors(result):
        return 1

    if not args.dry_run:
        write_env_file(path, result.env)

    return 0

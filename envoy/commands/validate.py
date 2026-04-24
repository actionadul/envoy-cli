"""validate command — check an env file for syntax errors and missing keys."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from envoy.parser import parse_env_file
from envoy.resolver import resolve_target


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Validate an env file for syntax errors and required keys."
    if parent is not None:
        parser = parent.add_parser("validate", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy validate", description=description)

    parser.add_argument(
        "target",
        help="Deployment target name (e.g. staging, production).",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory that contains .env files (default: envs).",
    )
    parser.add_argument(
        "--require",
        nargs="*",
        default=[],
        metavar="KEY",
        help="Keys that must be present in the env file.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the validate command.  Returns an exit code (0 = ok, 1 = invalid)."""
    env_dir = Path(args.env_dir)

    try:
        env_path = resolve_target(env_dir, args.target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        env_vars = parse_env_file(env_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse '{env_path}': {exc}", file=sys.stderr)
        return 1

    missing = [key for key in args.require if key not in env_vars]

    if missing:
        for key in missing:
            print(f"missing required key: {key}")
        print(f"\n{args.target}: INVALID ({len(missing)} missing key(s))")
        return 1

    print(f"{args.target}: OK ({len(env_vars)} key(s) found)")
    return 0

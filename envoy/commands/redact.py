"""CLI command: redact sensitive values in an env file."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.parser import parse_env_file, write_env_file
from envoy.redactor import redact, summary
from envoy.resolver import resolve_target


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="envoy redact",
        description="Print or save an env file with sensitive values redacted.",
    )
    parser = parent.add_parser("redact", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("target", help="Deployment target name (e.g. production).")
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing env files (default: envs).",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Explicit keys to redact. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write redacted output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--placeholder",
        default="***REDACTED***",
        help="Replacement text for redacted values.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        path = resolve_target(args.env_dir, args.target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    env = parse_env_file(path)
    result = redact(env, keys=args.keys, placeholder=args.placeholder)

    if args.output:
        write_env_file(args.output, result.redacted)
        print(summary(result))
    else:
        for k, v in result.redacted.items():
            print(f"{k}={v}")
        print(f"# {summary(result)}", file=sys.stderr)

    return 0

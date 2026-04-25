"""CLI command: render env file templates against a context target."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target
from envoy.templater import render, summary


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    kwargs = dict(
        name="template",
        help="Render {{ placeholders }} in an env file using a context target.",
        description="Substitute {{ KEY }} placeholders in TARGET using CONTEXT values.",
    )
    if parent is not None:
        parser = parent.add_parser(**kwargs)
    else:
        parser = argparse.ArgumentParser(**{k: v for k, v in kwargs.items() if k != "name"})

    parser.add_argument("target", help="Env target whose values contain placeholders.")
    parser.add_argument("context", help="Env target supplying substitution values.")
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing env files (default: envs).",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write rendered output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with error if any placeholder cannot be resolved.",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    env_dir = Path(args.env_dir)

    try:
        target_env = parse_env_file(resolve_target(env_dir, args.target))
        context_env = parse_env_file(resolve_target(env_dir, args.context))
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        result = render(target_env, context_env, strict=args.strict)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        write_env_file(Path(args.output), result.rendered)
    else:
        for k, v in result.rendered.items():
            print(f"{k}={v}")

    if not args.quiet:
        print(summary(result), file=sys.stderr)

    return 0

"""CLI command: lint one or more environment targets."""

import argparse
import sys
from pathlib import Path

from envoy.resolver import list_targets
from envoy.parser import parse_env_file
from envoy.linter import lint_env


def build_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser("lint", help="Lint environment files for style issues.")
    p.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing .env files (default: envs).",
    )
    p.add_argument(
        "targets",
        nargs="*",
        help="Targets to lint. Lints all targets when omitted.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with non-zero code on warnings as well as errors.",
    )
    return p


def run(args: argparse.Namespace) -> int:
    env_dir = Path(args.env_dir)
    targets = args.targets or list_targets(env_dir)

    if not targets:
        print("No targets found.", file=sys.stderr)
        return 1

    any_error = False
    any_warning = False

    for target in targets:
        env_file = env_dir / f"{target}.env"
        if not env_file.exists():
            print(f"[{target}] File not found: {env_file}", file=sys.stderr)
            any_error = True
            continue

        raw_lines = env_file.read_text().splitlines(keepends=True)
        env = parse_env_file(env_file)
        result = lint_env(target, env, raw_lines)

        print(result.summary())
        for issue in result.issues:
            loc = f" (line {issue.line})" if issue.line is not None else ""
            print(f"  [{issue.severity.upper()}] {issue.rule}{loc}: {issue.message}")

        if result.has_errors():
            any_error = True
        if result.has_warnings():
            any_warning = True

    if any_error:
        return 2
    if args.strict and any_warning:
        return 1
    return 0

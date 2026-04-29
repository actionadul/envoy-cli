"""report command — print a multi-target diff summary table."""

import argparse
import sys

from envoy.resolver import list_targets, resolve_target
from envoy.differ_summary import build_report as build_multi_diff_report
from envoy.differ_report import format_report


def build_parser(subparsers=None):
    description = "Print a summary table of env differences across all targets."
    if subparsers is not None:
        parser = subparsers.add_parser("report", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy report", description=description)

    parser.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing .env target files (default: envs).",
    )
    parser.add_argument(
        "--base",
        default="base",
        help="Base target to diff all others against (default: base).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colour output.",
    )
    return parser


def run(args, stdout=None, stderr=None):
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    targets = list_targets(args.env_dir)
    if not targets:
        stderr.write(f"No targets found in '{args.env_dir}'.\n")
        return 1

    base_name = args.base
    if base_name not in targets:
        stderr.write(f"Base target '{base_name}' not found in '{args.env_dir}'.\n")
        return 1

    base_env = resolve_target(args.env_dir, base_name)
    other_targets = {t: resolve_target(args.env_dir, t) for t in targets if t != base_name}

    report = build_multi_diff_report(base_env, other_targets)
    output = format_report(report, color=not args.no_color)
    stdout.write(output + "\n")

    from envoy.differ_summary import targets_with_differences
    return 1 if targets_with_differences(report) else 0

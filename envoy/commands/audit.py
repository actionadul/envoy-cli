"""audit command: run policy checks on one or all environment targets."""

import argparse
import sys
from typing import List

from envoy.auditor import audit_env
from envoy.resolver import list_targets, resolve_target


def build_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Audit env files for issues and policy violations."
    if subparsers is not None:
        parser = subparsers.add_parser("audit", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy audit", description=description)

    parser.add_argument(
        "targets",
        nargs="*",
        metavar="TARGET",
        help="Targets to audit (default: all)",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing env files (default: envs)",
    )
    parser.add_argument(
        "--require",
        nargs="*",
        metavar="KEY",
        default=[],
        help="Keys that must be present in every target",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit non-zero if any warnings are found",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    env_dir = args.env_dir
    required_keys: List[str] = args.require or []
    targets = args.targets or list_targets(env_dir)

    if not targets:
        print("No targets found.", file=sys.stderr)
        return 1

    any_error = False
    any_warning = False

    for target in targets:
        env = resolve_target(env_dir, target)
        result = audit_env(target, env, required_keys=required_keys)

        if result.issues:
            print(result.summary())
            for issue in result.issues:
                marker = "[ERROR]" if issue.severity == "error" else "[WARN] "
                print(f"  {marker} {issue.key}: {issue.message}")
        else:
            print(f"{target}: OK")

        if result.has_errors:
            any_error = True
        if result.has_warnings:
            any_warning = True

    if any_error:
        return 2
    if args.strict and any_warning:
        return 1
    return 0

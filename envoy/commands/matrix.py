"""matrix command — display a key-by-target presence/value matrix."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.differ_matrix import build_matrix, format_matrix
from envoy.resolver import list_targets, resolve_target


def build_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "matrix",
        help="Show a key-by-target matrix across deployment targets.",
    )
    p.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing .env target files (default: envs).",
    )
    p.add_argument(
        "targets",
        nargs="*",
        metavar="TARGET",
        help="Targets to include (default: all).",
    )
    p.add_argument(
        "--values",
        action="store_true",
        default=False,
        help="Show values instead of presence markers.",
    )
    p.add_argument(
        "--divergent-only",
        action="store_true",
        default=False,
        help="Only show keys that differ across targets.",
    )
    return p


def run(args: argparse.Namespace) -> int:
    env_dir: str = args.env_dir
    requested: List[str] = args.targets
    show_values: bool = args.values
    divergent_only: bool = args.divergent_only

    available = list_targets(env_dir)
    if not available:
        print(f"No targets found in '{env_dir}'.", file=sys.stderr)
        return 1

    targets = requested if requested else available
    missing = [t for t in targets if t not in available]
    if missing:
        print(f"Unknown targets: {', '.join(missing)}", file=sys.stderr)
        return 1

    envs = {t: resolve_target(env_dir, t) for t in targets}
    report = build_matrix(envs)

    if divergent_only:
        from envoy.differ_matrix import MatrixReport
        report = MatrixReport(
            targets=report.targets,
            keys=report.divergent_keys,
            cells={k: report.cells[k] for k in report.divergent_keys},
            unanimous_keys=[],
            divergent_keys=report.divergent_keys,
        )

    print(format_matrix(report, show_values=show_values))
    divergent_count = len(report.divergent_keys)
    print(f"\n{len(report.keys)} keys | {divergent_count} divergent | {len(report.unanimous_keys)} unanimous")
    return 0

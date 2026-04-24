"""merge command: merge two env targets into a new output file."""

import argparse
import sys
from pathlib import Path

from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target


def build_parser(subparsers=None):
    description = "Merge two env targets into a single output file."
    if subparsers is not None:
        parser = subparsers.add_parser("merge", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy merge", description=description)

    parser.add_argument("base", help="Base target name (values overridden by overlay).")
    parser.add_argument("overlay", help="Overlay target name (values take precedence).")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to write the merged env file. Defaults to stdout.",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing env target files (default: envs).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        default=False,
        help="Exit with error if the output file already exists.",
    )
    return parser


def run(args, stdout=None, stderr=None):
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    env_dir = Path(args.env_dir)

    try:
        base_vars = resolve_target(args.base, env_dir)
    except FileNotFoundError:
        stderr.write(f"error: base target '{args.base}' not found in {env_dir}\n")
        return 1

    try:
        overlay_vars = resolve_target(args.overlay, env_dir)
    except FileNotFoundError:
        stderr.write(f"error: overlay target '{args.overlay}' not found in {env_dir}\n")
        return 1

    merged = {**base_vars, **overlay_vars}

    if args.output is None:
        for key, value in merged.items():
            stdout.write(f"{key}={value}\n")
        return 0

    output_path = Path(args.output)
    if args.no_overwrite and output_path.exists():
        stderr.write(f"error: output file '{output_path}' already exists (--no-overwrite set)\n")
        return 1

    write_env_file(output_path, merged)
    stdout.write(f"Merged {len(merged)} variable(s) written to {output_path}\n")
    return 0

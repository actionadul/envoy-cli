"""Export command: render an environment target to stdout or a file."""

import argparse
import sys
from pathlib import Path

from envoy.resolver import resolve_target
from envoy.parser import write_env_file


def build_parser(subparsers=None):
    description = "Export resolved environment variables for a target."
    if subparsers is not None:
        parser = subparsers.add_parser("export", description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy export", description=description)

    parser.add_argument(
        "target",
        help="Name of the environment target to export (e.g. staging).",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing .env files (default: envs).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--format",
        choices=["env", "export"],
        default="env",
        dest="fmt",
        help="Output format: 'env' (KEY=VALUE) or 'export' (export KEY=VALUE). Default: env.",
    )
    return parser


def _format_line(key, value, fmt):
    """Format a single key/value pair according to the requested output format."""
    if fmt == "export":
        return f'export {key}="{value}"'
    return f'{key}="{value}"'


def run(args, stdout=None, stderr=None):
    """Execute the export command.

    Returns an exit code (0 = success, non-zero = error).
    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    env_dir = Path(args.env_dir)
    try:
        resolved = resolve_target(env_dir, args.target)
    except FileNotFoundError as exc:
        stderr.write(f"error: {exc}\n")
        return 1

    if args.output:
        out_path = Path(args.output)
        write_env_file(out_path, resolved)
        stdout.write(f"Exported {len(resolved)} variable(s) to {out_path}\n")
    else:
        for key, value in sorted(resolved.items()):
            stdout.write(_format_line(key, value, args.fmt) + "\n")

    return 0

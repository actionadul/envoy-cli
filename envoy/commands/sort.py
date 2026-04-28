import argparse
import sys
from pathlib import Path

from envoy.parser import parse_env_file, write_env_file
from envoy.sorter import sort, has_changes, summary


def build_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Sort keys in an environment file alphabetically."
    if subparsers is not None:
        parser = subparsers.add_parser("sort", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy sort", description=description)

    parser.add_argument("file", help="Path to the .env file to sort.")
    parser.add_argument(
        "--reverse",
        action="store_true",
        default=False,
        help="Sort keys in reverse alphabetical order.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing to disk.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Exit with code 1 if the file is not already sorted.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    if not path.is_file():
        print(f"Error: path is not a file: {path}", file=sys.stderr)
        return 1

    env = parse_env_file(path)
    result = sort(env, reverse=getattr(args, "reverse", False))

    print(summary(result))

    if args.check:
        return 1 if has_changes(result) else 0

    if has_changes(result) and not args.dry_run:
        write_env_file(path, result.sorted_env)
        print(f"Written sorted env to {path}")

    return 0

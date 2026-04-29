"""CLI command: split an env file into multiple target files by prefix pattern."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target
from envoy.splitter import split, summary


def build_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "split",
        help="Split an env target into multiple files based on key prefix patterns.",
    )
    p.add_argument("target", help="Source target name (e.g. production).")
    p.add_argument(
        "--map",
        metavar="BUCKET=PATTERN",
        action="append",
        dest="mappings",
        required=True,
        help="Bucket name and glob pattern, e.g. db=DB_*. Repeatable.",
    )
    p.add_argument(
        "--strip-prefix",
        action="store_true",
        default=False,
        help="Strip the matched prefix from keys in each bucket file.",
    )
    p.add_argument(
        "--unmatched",
        metavar="BUCKET",
        default=None,
        help="Write unmatched keys to this additional bucket file.",
    )
    p.add_argument(
        "--env-dir",
        default="envs",
        help="Directory containing env files (default: envs).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be written without creating files.",
    )
    return p


def _parse_mappings(raw: list[str]) -> dict[str, str]:
    patterns: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Invalid --map value: {item!r}. Expected BUCKET=PATTERN.")
        bucket, _, pattern = item.partition("=")
        patterns[bucket.strip()] = pattern.strip()
    return patterns


def run(args: argparse.Namespace) -> int:
    env_dir = Path(args.env_dir)
    source_path = resolve_target(env_dir, args.target)
    if source_path is None:
        print(f"error: target '{args.target}' not found in {env_dir}", file=sys.stderr)
        return 1

    try:
        patterns = _parse_mappings(args.mappings)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    env = parse_env_file(source_path)
    result = split(env, patterns, strip_prefix=args.strip_prefix, include_unmatched=args.unmatched)

    print(summary(result))

    if args.dry_run:
        for bucket, keys in result.buckets.items():
            print(f"  [dry-run] would write {bucket}.env ({len(keys)} keys)")
        return 0

    for bucket, bucket_env in result.buckets.items():
        out_path = env_dir / f"{bucket}.env"
        write_env_file(out_path, bucket_env)
        print(f"  wrote {out_path} ({len(bucket_env)} keys)")

    return 0

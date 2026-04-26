"""encrypt command — encrypt sensitive values in an env file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy.encryptor import encrypt_env, decrypt_env, generate_key
from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    """Build (and optionally register) the argument parser for the encrypt command."""
    kwargs: dict = dict(
        description="Encrypt or decrypt sensitive values in an env target.",
        help="Encrypt/decrypt env values using a Fernet key.",
    )
    if parent is not None:
        parser = parent.add_parser("encrypt", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="envoy encrypt", **kwargs)

    parser.add_argument(
        "target",
        help="Deployment target name (e.g. 'staging').",
    )
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory that contains env files (default: envs).",
    )
    parser.add_argument(
        "--key",
        metavar="KEY",
        default=None,
        help="Fernet encryption key. If omitted a new key is generated and printed.",
    )
    parser.add_argument(
        "--decrypt",
        action="store_true",
        default=False,
        help="Decrypt previously encrypted values instead of encrypting.",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Only encrypt/decrypt these specific env keys.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would change without writing the file.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress informational output.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the encrypt/decrypt command and return an exit code."""
    env_dir = Path(args.env_dir)

    # Resolve the target env file.
    try:
        env_file = resolve_target(env_dir, args.target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Handle key generation when no key is provided.
    key = args.key
    if key is None:
        if args.decrypt:
            print("error: --key is required for decryption.", file=sys.stderr)
            return 1
        key = generate_key()
        if not args.quiet:
            print(f"Generated encryption key: {key}")
            print("Store this key securely — you will need it to decrypt values.")

    env = parse_env_file(env_file)

    if args.decrypt:
        result = decrypt_env(env, key, keys=args.keys)
        action_label = "Decrypted"
    else:
        result = encrypt_env(env, key, keys=args.keys)
        action_label = "Encrypted"

    if not args.quiet:
        print(f"{action_label} {result.changed} value(s) in '{args.target}'.")
        if result.skipped:
            print(f"Skipped {result.skipped} already-processed value(s).")

    if args.dry_run:
        if not args.quiet:
            print("Dry run — no changes written.")
        return 0

    write_env_file(env_file, result.env)
    return 0

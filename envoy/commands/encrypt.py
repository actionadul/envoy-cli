"""CLI command: encrypt / decrypt environment variable values."""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from envoy.encryptor import decrypt_env, encrypt_env, generate_key
from envoy.parser import parse_env_file, write_env_file
from envoy.resolver import resolve_target


def build_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Encrypt or decrypt values in an environment file."
    if parent is not None:
        parser = parent.add_parser("encrypt", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy encrypt", description=description)

    parser.add_argument("target", help="Deployment target name (e.g. staging).")
    parser.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing .env files (default: envs).",
    )
    parser.add_argument(
        "--key",
        default=None,
        metavar="KEY",
        help="Fernet encryption key. Falls back to ENVOY_KEY env var.",
    )
    parser.add_argument(
        "--decrypt",
        action="store_true",
        default=False,
        help="Decrypt values instead of encrypting.",
    )
    parser.add_argument(
        "--keys",
        nargs="*",
        metavar="VAR",
        default=None,
        help="Restrict encryption to these variable names.",
    )
    parser.add_argument(
        "--generate-key",
        action="store_true",
        default=False,
        help="Print a new random key and exit.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    if args.generate_key:
        print(generate_key())
        return 0

    key = args.key or os.environ.get("ENVOY_KEY")
    if not key:
        print("error: encryption key required (--key or ENVOY_KEY)", file=sys.stderr)
        return 1

    env_path = resolve_target(args.env_dir, args.target)
    env = parse_env_file(env_path)

    if args.decrypt:
        result = decrypt_env(env, key)
        if result.errors:
            for err in result.errors:
                print(f"error: {err}", file=sys.stderr)
            return 1
        updated = {**env, **result.decrypted}
        write_env_file(env_path, updated)
        print(f"Decrypted {len(result.decrypted)} value(s) in {env_path}")
    else:
        result = encrypt_env(env, key, keys_to_encrypt=args.keys)
        if result.errors:
            for err in result.errors:
                print(f"error: {err}", file=sys.stderr)
            return 1
        updated = {**env, **result.encrypted}
        write_env_file(env_path, updated)
        print(f"Encrypted {len(result.encrypted)} value(s) in {env_path}")

    return 0

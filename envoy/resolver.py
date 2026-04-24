"""Resolve environment variable sets for named deployment targets."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from envoy.parser import parse_env_file

EnvMap = Dict[str, str]

DEFAULT_ENV_DIR = "envs"
DEFAULT_BASE_FILE = ".env"


def list_targets(env_dir: str = DEFAULT_ENV_DIR) -> List[str]:
    """Return all target names found in *env_dir* (files named .env.<target>)."""
    base = Path(env_dir)
    if not base.is_dir():
        return []
    targets = []
    for entry in sorted(base.iterdir()):
        if entry.is_file() and entry.name.startswith(".env."):
            targets.append(entry.name[len(".env."):])
    return targets


def resolve_target(
    target: str,
    env_dir: str = DEFAULT_ENV_DIR,
    base_file: Optional[str] = DEFAULT_BASE_FILE,
) -> EnvMap:
    """Return merged env map for *target*.

    If *base_file* exists it is loaded first; target-specific values override it.
    """
    merged: EnvMap = {}

    if base_file:
        base_path = Path(base_file)
        if base_path.is_file():
            merged.update(parse_env_file(str(base_path)))

    target_path = Path(env_dir) / f".env.{target}"
    if not target_path.is_file():
        raise FileNotFoundError(
            f"No environment file found for target '{target}' at '{target_path}'"
        )
    merged.update(parse_env_file(str(target_path)))
    return merged


def resolve_all(
    env_dir: str = DEFAULT_ENV_DIR,
    base_file: Optional[str] = DEFAULT_BASE_FILE,
) -> Dict[str, EnvMap]:
    """Resolve every target in *env_dir* and return a mapping of target → env."""
    return {
        target: resolve_target(target, env_dir=env_dir, base_file=base_file)
        for target in list_targets(env_dir)
    }

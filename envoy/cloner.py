"""Clone an environment target to a new target, optionally filtering keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import write_env_file
from envoy.resolver import resolve_target


@dataclass
class CloneResult:
    source: str
    destination: str
    keys_written: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)
    already_existed: bool = False


def has_changes(result: CloneResult) -> bool:
    return len(result.keys_written) > 0


def summary(result: CloneResult) -> str:
    parts = []
    if result.already_existed:
        parts.append(f"destination '{result.destination}' already existed (overwritten)")
    parts.append(f"{len(result.keys_written)} key(s) written to '{result.destination}'")
    if result.keys_skipped:
        parts.append(f"{len(result.keys_skipped)} key(s) skipped")
    return "; ".join(parts)


def clone(
    env_dir: str,
    source: str,
    destination: str,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Clone *source* target into *destination* target.

    Args:
        env_dir: Directory containing .env files.
        source: Name of the source target (e.g. ``"staging"``).
        destination: Name of the new target to create.
        include: If provided, only these keys are copied.
        exclude: Keys to omit from the clone.
        overwrite: Whether to overwrite an existing destination file.
    """
    import os

    dest_path = os.path.join(env_dir, f".env.{destination}")
    already_existed = os.path.exists(dest_path)

    if already_existed and not overwrite:
        raise FileExistsError(
            f"Destination target '{destination}' already exists. "
            "Use overwrite=True to replace it."
        )

    source_env: Dict[str, str] = resolve_target(env_dir, source)

    result = CloneResult(
        source=source,
        destination=destination,
        already_existed=already_existed,
    )

    filtered: Dict[str, str] = {}
    for key, value in source_env.items():
        if include is not None and key not in include:
            result.keys_skipped.append(key)
            continue
        if exclude is not None and key in exclude:
            result.keys_skipped.append(key)
            continue
        filtered[key] = value
        result.keys_written.append(key)

    write_env_file(dest_path, filtered)
    return result

"""Promote environment variables from one target to another."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.resolver import resolve_target
from envoy.differ import diff_envs


@dataclass
class PromoteResult:
    source: str
    destination: str
    promoted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)


def promote(
    env_dir: str,
    source: str,
    destination: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote env vars from source to destination target.

    Args:
        env_dir: Directory containing target env files.
        source: Source target name.
        destination: Destination target name.
        keys: Specific keys to promote; if None, promotes all differing keys.
        overwrite: If True, overwrite existing keys in destination.

    Returns:
        PromoteResult describing what was promoted, skipped, or overwritten.
    """
    src_env = resolve_target(env_dir, source)
    dst_env = resolve_target(env_dir, destination)

    result = PromoteResult(source=source, destination=destination)

    candidate_keys = keys if keys is not None else list(src_env.keys())

    for key in candidate_keys:
        if key not in src_env:
            result.skipped.append(key)
            continue

        value = src_env[key]

        if key in dst_env and not overwrite:
            result.skipped.append(key)
            continue

        if key in dst_env and overwrite:
            result.overwritten.append(key)

        result.promoted[key] = value
        dst_env[key] = value

    return result


def summary(result: PromoteResult) -> str:
    """Return a human-readable summary of a PromoteResult."""
    lines = [
        f"Promote: {result.source} -> {result.destination}",
        f"  Promoted : {len(result.promoted)}",
        f"  Overwritten: {len(result.overwritten)}",
        f"  Skipped  : {len(result.skipped)}",
    ]
    return "\n".join(lines)

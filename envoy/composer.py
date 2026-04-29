"""Compose a new env by merging multiple env dicts with precedence ordering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ComposeResult:
    composed: Dict[str, str]
    sources: Dict[str, str]  # key -> name of the source that won
    conflicts: List[Tuple[str, str, str]]  # (key, losing_source, winning_source)


def has_conflicts(result: ComposeResult) -> bool:
    return len(result.conflicts) > 0


def summary(result: ComposeResult) -> str:
    total = len(result.composed)
    conflict_count = len(result.conflicts)
    if conflict_count == 0:
        return f"Composed {total} key(s) with no conflicts."
    return (
        f"Composed {total} key(s); "
        f"{conflict_count} conflict(s) resolved by precedence."
    )


def compose(
    envs: List[Tuple[str, Dict[str, str]]],
) -> ComposeResult:
    """Merge env dicts in order; later entries take precedence over earlier ones.

    Args:
        envs: List of (name, env_dict) pairs ordered from lowest to highest precedence.

    Returns:
        ComposeResult with the merged env, source tracking, and conflict log.
    """
    composed: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    conflicts: List[Tuple[str, str, str]] = []

    for name, env in envs:
        for key, value in env.items():
            if key in composed:
                conflicts.append((key, sources[key], name))
            composed[key] = value
            sources[key] = name

    return ComposeResult(composed=composed, sources=sources, conflicts=conflicts)

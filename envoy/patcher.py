"""Patch (set/unset/update) keys in an env variable set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PatchResult:
    original: Dict[str, str]
    patched: Dict[str, str]
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)


def has_changes(result: PatchResult) -> bool:
    return bool(result.added or result.updated or result.removed)


def summary(result: PatchResult) -> str:
    parts = []
    if result.added:
        parts.append(f"{len(result.added)} added")
    if result.updated:
        parts.append(f"{len(result.updated)} updated")
    if result.removed:
        parts.append(f"{len(result.removed)} removed")
    return ", ".join(parts) if parts else "no changes"


def patch(
    env: Dict[str, str],
    sets: Optional[List[Tuple[str, str]]] = None,
    unsets: Optional[List[str]] = None,
) -> PatchResult:
    """Apply set and unset operations to *env*, returning a PatchResult.

    Args:
        env:    The source environment mapping.
        sets:   List of (key, value) pairs to add or update.
        unsets: List of keys to remove.
    """
    sets = sets or []
    unsets = unsets or []

    patched = dict(env)
    added: List[str] = []
    updated: List[str] = []
    removed: List[str] = []

    for key, value in sets:
        if key in patched:
            if patched[key] != value:
                updated.append(key)
        else:
            added.append(key)
        patched[key] = value

    for key in unsets:
        if key in patched:
            del patched[key]
            removed.append(key)

    return PatchResult(
        original=dict(env),
        patched=patched,
        added=added,
        updated=updated,
        removed=removed,
    )

"""Prefix or strip a prefix from environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class PrefixResult:
    original: Dict[str, str]
    updated: Dict[str, str]
    changed: List[Tuple[str, str]]  # (old_key, new_key)


def has_changes(result: PrefixResult) -> bool:
    return len(result.changed) > 0


def summary(result: PrefixResult) -> str:
    if not has_changes(result):
        return "No keys changed."
    return f"{len(result.changed)} key(s) renamed."


def add_prefix(env: Dict[str, str], prefix: str) -> PrefixResult:
    """Add *prefix* to every key that does not already have it."""
    if not prefix:
        return PrefixResult(original=dict(env), updated=dict(env), changed=[])

    updated: Dict[str, str] = {}
    changed: List[Tuple[str, str]] = []

    for key, value in env.items():
        if key.startswith(prefix):
            updated[key] = value
        else:
            new_key = f"{prefix}{key}"
            updated[new_key] = value
            changed.append((key, new_key))

    return PrefixResult(original=dict(env), updated=updated, changed=changed)


def strip_prefix(env: Dict[str, str], prefix: str) -> PrefixResult:
    """Remove *prefix* from every key that starts with it."""
    if not prefix:
        return PrefixResult(original=dict(env), updated=dict(env), changed=[])

    updated: Dict[str, str] = {}
    changed: List[Tuple[str, str]] = []

    for key, value in env.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            if new_key:  # guard against prefix == key
                updated[new_key] = value
                changed.append((key, new_key))
            else:
                updated[key] = value
        else:
            updated[key] = value

    return PrefixResult(original=dict(env), updated=updated, changed=changed)

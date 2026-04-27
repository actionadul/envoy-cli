"""Scoper: filter env vars by prefix scope and optionally strip the prefix."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scoped: Dict[str, str]
    dropped: List[str]
    prefix: str
    stripped: bool


def has_matches(result: ScopeResult) -> bool:
    return bool(result.scoped)


def summary(result: ScopeResult) -> str:
    matched = len(result.scoped)
    dropped = len(result.dropped)
    strip_note = " (prefix stripped)" if result.stripped else ""
    return (
        f"Scope '{result.prefix}': {matched} matched{strip_note}, {dropped} excluded."
    )


def scope(
    env: Dict[str, str],
    prefix: str,
    *,
    strip_prefix: bool = False,
    case_sensitive: bool = True,
) -> ScopeResult:
    """Return only keys that start with *prefix*.

    Args:
        env: Source key/value mapping.
        prefix: The prefix to filter by.
        strip_prefix: When True, remove the prefix from matched keys.
        case_sensitive: When False, match prefix case-insensitively.
    """
    if not case_sensitive:
        normalised_prefix = prefix.upper()
    else:
        normalised_prefix = prefix

    scoped: Dict[str, str] = {}
    dropped: List[str] = []

    for key, value in env.items():
        compare_key = key.upper() if not case_sensitive else key
        if compare_key.startswith(normalised_prefix):
            out_key = key[len(prefix):] if strip_prefix else key
            scoped[out_key] = value
        else:
            dropped.append(key)

    return ScopeResult(
        scoped=scoped,
        dropped=dropped,
        prefix=prefix,
        stripped=strip_prefix,
    )

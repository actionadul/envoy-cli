"""Deduplicator: detect and remove duplicate values across environment keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DeduplicateResult:
    original: Dict[str, str]
    deduped: Dict[str, str]
    duplicates: List[Tuple[str, str, str]]  # (value, key_kept, key_removed)
    removed: List[str] = field(default_factory=list)


def has_changes(result: DeduplicateResult) -> bool:
    return len(result.removed) > 0


def summary(result: DeduplicateResult) -> str:
    if not has_changes(result):
        return "No duplicate values found."
    lines = [f"Removed {len(result.removed)} duplicate(s):"]
    for value, kept, removed in result.duplicates:
        lines.append(f"  {removed} removed (duplicate of {kept}, value={value!r})")
    return "\n".join(lines)


def deduplicate(
    env: Dict[str, str],
    *,
    keep: str = "first",
    keys_filter: List[str] | None = None,
) -> DeduplicateResult:
    """Remove keys whose values are duplicated elsewhere in the env.

    Args:
        env: mapping of key -> value to process.
        keep: ``'first'`` keeps the key that appears first in insertion order;
              ``'last'`` keeps the key that appears last.
        keys_filter: when provided, only consider these keys for deduplication.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    candidates = dict(env)
    if keys_filter is not None:
        candidates = {k: v for k, v in env.items() if k in keys_filter}

    # Build value -> list of keys mapping (preserving insertion order)
    value_to_keys: Dict[str, List[str]] = {}
    for key, value in candidates.items():
        value_to_keys.setdefault(value, []).append(key)

    keys_to_remove: set[str] = set()
    duplicates: List[Tuple[str, str, str]] = []

    for value, keys in value_to_keys.items():
        if len(keys) < 2:
            continue
        kept = keys[0] if keep == "first" else keys[-1]
        for k in keys:
            if k != kept:
                keys_to_remove.add(k)
                duplicates.append((value, kept, k))

    deduped = {k: v for k, v in env.items() if k not in keys_to_remove}
    return DeduplicateResult(
        original=dict(env),
        deduped=deduped,
        duplicates=duplicates,
        removed=list(keys_to_remove),
    )

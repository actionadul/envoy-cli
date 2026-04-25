"""Normalize environment variable sets by sorting keys, stripping whitespace,
and standardizing key casing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)


def has_changes(result: NormalizeResult) -> bool:
    return bool(result.changes)


def summary(result: NormalizeResult) -> str:
    if not has_changes(result):
        return "No normalization changes."
    lines = [f"{len(result.changes)} change(s) applied:"]
    for change in result.changes:
        lines.append(f"  - {change}")
    return "\n".join(lines)


def normalize(
    env: Dict[str, str],
    *,
    uppercase_keys: bool = True,
    strip_values: bool = True,
    sort_keys: bool = True,
    remove_empty: bool = False,
    prefix: Optional[str] = None,
) -> NormalizeResult:
    """Return a NormalizeResult with the cleaned env dict and a log of changes."""
    changes: List[str] = []
    result: Dict[str, str] = {}

    for raw_key, raw_value in env.items():
        key = raw_key
        value = raw_value

        if uppercase_keys and key != key.upper():
            changes.append(f"key '{key}' uppercased to '{key.upper()}'")
            key = key.upper()

        if strip_values and value != value.strip():
            changes.append(f"value for '{key}' had surrounding whitespace stripped")
            value = value.strip()

        if remove_empty and value == "":
            changes.append(f"key '{key}' removed (empty value)")
            continue

        if prefix and not key.startswith(prefix):
            new_key = f"{prefix}{key}"
            changes.append(f"key '{key}' prefixed to '{new_key}'")
            key = new_key

        result[key] = value

    if sort_keys:
        sorted_result = dict(sorted(result.items()))
        if list(sorted_result.keys()) != list(result.keys()):
            changes.append("keys sorted alphabetically")
        result = sorted_result

    return NormalizeResult(original=dict(env), normalized=result, changes=changes)

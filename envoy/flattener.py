"""Flatten nested prefix groups into a single env dict, or expand a flat dict
into prefixed groups.

Flatten:  {"DB": {"HOST": "localhost"}}  ->  {"DB_HOST": "localhost"}
Expand:   {"DB_HOST": "localhost"}       ->  {"DB": {"HOST": "localhost"}}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FlattenResult:
    original: Dict[str, str]
    result: Dict[str, str]
    changes: List[str] = field(default_factory=list)  # keys that were renamed


def has_changes(result: FlattenResult) -> bool:
    return bool(result.changes)


def summary(result: FlattenResult) -> str:
    if not result.changes:
        return "No changes — env is already flat."
    return f"{len(result.changes)} key(s) flattened: {', '.join(sorted(result.changes))}"


def flatten(env: Dict[str, str], separator: str = "_") -> FlattenResult:
    """Ensure every key is a plain string with no nesting implied by separator.

    In practice the input is already flat (string -> string); this function
    normalises keys that contain the separator in a non-standard way, e.g.
    duplicate separators or leading/trailing separators.
    """
    result: Dict[str, str] = {}
    changes: List[str] = []

    for key, value in env.items():
        # Collapse consecutive separators and strip leading/trailing ones
        parts = [p for p in key.split(separator) if p]
        normalised = separator.join(parts)
        result[normalised] = value
        if normalised != key:
            changes.append(key)

    return FlattenResult(original=dict(env), result=result, changes=changes)


def expand(env: Dict[str, str], separator: str = "_") -> Dict[str, Dict]:
    """Expand a flat env dict into a nested dict using *separator* as the
    hierarchy delimiter.

    Example::

        {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "envoy"}
        ->
        {"DB": {"HOST": "localhost", "PORT": "5432"}, "APP": {"NAME": "envoy"}}
    """
    nested: Dict[str, Dict] = {}

    for key, value in env.items():
        parts = key.split(separator, 1)
        if len(parts) == 1:
            nested.setdefault(key, {})
            nested[key]["__value__"] = value
        else:
            prefix, rest = parts
            nested.setdefault(prefix, {})
            nested[prefix][rest] = value

    return nested

"""Pin specific env var keys to fixed values across targets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinResult:
    pinned: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    original: Dict[str, str] = field(default_factory=dict)


def has_changes(result: PinResult) -> bool:
    return bool(result.pinned)


def summary(result: PinResult) -> str:
    parts = []
    if result.pinned:
        keys = ", ".join(sorted(result.pinned))
        parts.append(f"pinned {len(result.pinned)} key(s): {keys}")
    if result.skipped:
        keys = ", ".join(sorted(result.skipped))
        parts.append(f"skipped {len(result.skipped)} missing key(s): {keys}")
    return "; ".join(parts) if parts else "nothing to pin"


def pin(
    env: Dict[str, str],
    pins: Dict[str, str],
    only_existing: bool = True,
) -> PinResult:
    """Apply fixed pin values to env.

    Args:
        env: The source environment dict.
        pins: Mapping of key -> pinned value to enforce.
        only_existing: When True, skip keys not already present in env.

    Returns:
        PinResult with updated env stored in .original (pre-pin) and
        the merged dict available via result.original | result.pinned.
    """
    result = PinResult(original=dict(env))
    for key, value in pins.items():
        if only_existing and key not in env:
            result.skipped.append(key)
            continue
        if env.get(key) != value:
            result.pinned[key] = value
    return result


def apply(env: Dict[str, str], result: PinResult) -> Dict[str, str]:
    """Return a new env dict with pinned values applied."""
    merged = dict(env)
    merged.update(result.pinned)
    return merged

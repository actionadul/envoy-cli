"""Strip keys from an env dict by name or pattern."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StripResult:
    original: Dict[str, str]
    stripped: Dict[str, str]
    removed: List[str] = field(default_factory=list)


def has_changes(result: StripResult) -> bool:
    return len(result.removed) > 0


def summary(result: StripResult) -> str:
    if not has_changes(result):
        return "No keys removed."
    keys = ", ".join(result.removed)
    return f"Removed {len(result.removed)} key(s): {keys}"


def strip(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> StripResult:
    """Return a new env dict with matching keys removed.

    Args:
        env: The source environment mapping.
        keys: Exact key names to remove.
        patterns: Glob patterns (e.g. ``"*_SECRET"``).  Keys whose names
            match *any* pattern are removed.

    Returns:
        A :class:`StripResult` describing what was removed.
    """
    keys = list(keys or [])
    patterns = list(patterns or [])

    removed: List[str] = []
    result: Dict[str, str] = {}

    for k, v in env.items():
        exact_match = k in keys
        pattern_match = any(fnmatch.fnmatch(k, p) for p in patterns)
        if exact_match or pattern_match:
            removed.append(k)
        else:
            result[k] = v

    return StripResult(original=dict(env), stripped=result, removed=sorted(removed))

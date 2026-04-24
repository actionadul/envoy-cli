"""Interpolate variable references within env file values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_VAR_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}|\$([A-Z_][A-Z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_keys: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)


def _extract_refs(value: str) -> List[str]:
    """Return all variable names referenced in *value*."""
    return [m.group(1) or m.group(2) for m in _VAR_PATTERN.finditer(value)]


def _resolve_value(key: str, env: Dict[str, str], cache: Dict[str, str], visiting: set) -> Optional[str]:
    """Recursively resolve *key* against *env*, detecting cycles."""
    if key in cache:
        return cache[key]
    if key not in env:
        return None
    if key in visiting:
        return None  # cycle detected

    visiting.add(key)
    value = env[key]

    def _replace(match: re.Match) -> str:
        ref = match.group(1) or match.group(2)
        resolved = _resolve_value(ref, env, cache, visiting)
        return resolved if resolved is not None else match.group(0)

    resolved_value = _VAR_PATTERN.sub(_replace, value)
    visiting.discard(key)
    cache[key] = resolved_value
    return resolved_value


def interpolate(env: Dict[str, str]) -> InterpolationResult:
    """Interpolate all variable references in *env* and return an InterpolationResult."""
    cache: Dict[str, str] = {}
    result = InterpolationResult()

    # Pre-populate cache with keys that have no references (literals)
    for key, value in env.items():
        if not _extract_refs(value):
            cache[key] = value

    for key in env:
        visiting: set = set()
        resolved = _resolve_value(key, env, cache, visiting)
        if resolved is None:
            result.unresolved_keys.append(key)
        else:
            # Detect if a cycle was involved by checking if any ref is still raw
            refs = _extract_refs(env[key])
            for ref in refs:
                if ref == key or (ref in env and _resolve_value(ref, env, cache, set()) is None):
                    if key not in result.cycles:
                        result.cycles.append(key)
            result.resolved[key] = resolved

    return result

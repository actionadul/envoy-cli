"""Filter environment variable sets by key patterns or value conditions."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    original: Dict[str, str]
    filtered: Dict[str, str]
    matched_keys: List[str] = field(default_factory=list)
    excluded_keys: List[str] = field(default_factory=list)


def has_matches(result: FilterResult) -> bool:
    return len(result.matched_keys) > 0


def summary(result: FilterResult) -> str:
    total = len(result.original)
    matched = len(result.matched_keys)
    excluded = len(result.excluded_keys)
    return f"{matched}/{total} keys matched, {excluded} excluded"


def filter_env(
    env: Dict[str, str],
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    value_pattern: Optional[str] = None,
    keys_only: bool = False,
) -> FilterResult:
    """Filter env dict by key glob patterns and/or value regex."""
    matched: Dict[str, str] = {}
    excluded_keys: List[str] = []

    for key, value in env.items():
        if include_patterns:
            if not any(fnmatch.fnmatch(key, p) for p in include_patterns):
                excluded_keys.append(key)
                continue

        if exclude_patterns:
            if any(fnmatch.fnmatch(key, p) for p in exclude_patterns):
                excluded_keys.append(key)
                continue

        if value_pattern and not keys_only:
            if not re.search(value_pattern, value):
                excluded_keys.append(key)
                continue

        matched[key] = value

    return FilterResult(
        original=dict(env),
        filtered=matched,
        matched_keys=list(matched.keys()),
        excluded_keys=excluded_keys,
    )

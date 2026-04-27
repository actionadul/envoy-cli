"""Group environment variables by prefix or custom mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)
    total_keys: int = 0


def has_groups(result: GroupResult) -> bool:
    return bool(result.groups)


def summary(result: GroupResult) -> str:
    group_count = len(result.groups)
    ungrouped_count = len(result.ungrouped)
    lines = [f"{group_count} group(s) found across {result.total_keys} key(s)"]
    for name, members in sorted(result.groups.items()):
        lines.append(f"  [{name}] {len(members)} key(s)")
    if ungrouped_count:
        lines.append(f"  [ungrouped] {ungrouped_count} key(s)")
    return "\n".join(lines)


def group(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
    min_prefix_length: int = 2,
) -> GroupResult:
    """Group keys by shared prefix.

    If *prefixes* is provided, only those prefixes are used.  Otherwise every
    prefix (up to the first *separator*) is considered a candidate group; a
    prefix is only promoted to a real group when at least two keys share it.
    """
    groups: Dict[str, Dict[str, str]] = {}
    assigned: set = set()

    if prefixes:
        canonical = [p.upper().rstrip(separator) for p in prefixes]
    else:
        # Auto-detect: collect all prefix candidates
        candidates: Dict[str, int] = {}
        for key in env:
            parts = key.split(separator, 1)
            if len(parts) > 1 and len(parts[0]) >= min_prefix_length:
                candidates[parts[0]] = candidates.get(parts[0], 0) + 1
        canonical = [p for p, count in candidates.items() if count >= 2]

    for prefix in canonical:
        needle = prefix + separator
        matched = {k: v for k, v in env.items() if k.startswith(needle)}
        if matched:
            groups[prefix] = matched
            assigned.update(matched.keys())

    ungrouped = {k: v for k, v in env.items() if k not in assigned}

    return GroupResult(
        groups=groups,
        ungrouped=ungrouped,
        total_keys=len(env),
    )

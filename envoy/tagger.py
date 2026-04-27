"""Tag environment variables with arbitrary metadata labels."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TagResult:
    env: Dict[str, str]
    tags: Dict[str, List[str]]
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)


def has_changes(result: TagResult) -> bool:
    return bool(result.added or result.removed)


def summary(result: TagResult) -> str:
    parts: List[str] = []
    if result.added:
        parts.append(f"{len(result.added)} tag(s) added")
    if result.removed:
        parts.append(f"{len(result.removed)} tag(s) removed")
    return ", ".join(parts) if parts else "no tag changes"


def tag(env: Dict[str, str],
        existing_tags: Optional[Dict[str, List[str]]] = None,
        add: Optional[Dict[str, List[str]]] = None,
        remove: Optional[Dict[str, List[str]]] = None) -> TagResult:
    """Apply or remove tags on env keys.

    Tags are stored as a separate mapping: {key: [tag1, tag2, ...]}.
    Only keys present in *env* can be tagged.
    """
    tags: Dict[str, List[str]] = {k: list(v) for k, v in (existing_tags or {}).items()}
    added: List[str] = []
    removed: List[str] = []

    for key, new_tags in (add or {}).items():
        if key not in env:
            continue
        current = tags.setdefault(key, [])
        for t in new_tags:
            if t not in current:
                current.append(t)
                added.append(f"{key}:{t}")

    for key, drop_tags in (remove or {}).items():
        if key not in tags:
            continue
        for t in drop_tags:
            if t in tags[key]:
                tags[key].remove(t)
                removed.append(f"{key}:{t}")
        if not tags[key]:
            del tags[key]

    return TagResult(env=dict(env), tags=tags, added=added, removed=removed)


def tags_for_key(result: TagResult, key: str) -> List[str]:
    """Return the tag list for a specific key, or empty list."""
    return list(result.tags.get(key, []))


def keys_with_tag(result: TagResult, tag_name: str) -> List[str]:
    """Return all env keys that carry a given tag."""
    return sorted(k for k, v in result.tags.items() if tag_name in v)

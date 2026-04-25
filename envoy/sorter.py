"""Sort environment variable keys alphabetically or by custom order."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    moved: List[str] = field(default_factory=list)


def has_changes(result: SortResult) -> bool:
    """Return True if the sort changed the key order."""
    return list(result.original.keys()) != list(result.sorted_env.keys())


def summary(result: SortResult) -> str:
    """Return a human-readable summary of the sort operation."""
    if not has_changes(result):
        return "Already sorted — no changes made."
    return f"Sorted {len(result.moved)} key(s) into alphabetical order."


def sort(
    env: Dict[str, str],
    reverse: bool = False,
    group_prefix: Optional[str] = None,
) -> SortResult:
    """Sort environment variable keys.

    Args:
        env: Mapping of key -> value to sort.
        reverse: If True, sort in descending order.
        group_prefix: If provided, keys starting with this prefix are placed
                      first (still sorted among themselves), followed by the
                      remaining keys sorted alphabetically.

    Returns:
        SortResult containing the original env, sorted env, and moved keys.
    """
    original_keys = list(env.keys())

    if group_prefix:
        priority = sorted(
            [k for k in env if k.startswith(group_prefix)], reverse=reverse
        )
        rest = sorted(
            [k for k in env if not k.startswith(group_prefix)], reverse=reverse
        )
        sorted_keys = priority + rest
    else:
        sorted_keys = sorted(env.keys(), reverse=reverse)

    sorted_env = {k: env[k] for k in sorted_keys}

    moved = [
        k
        for i, (orig, new) in enumerate(zip(original_keys, sorted_keys))
        if orig != new
        for k in [new]
    ]
    # Deduplicate while preserving order
    seen = set()
    deduped_moved = []
    for k in moved:
        if k not in seen:
            seen.add(k)
            deduped_moved.append(k)

    return SortResult(original=env, sorted_env=sorted_env, moved=deduped_moved)

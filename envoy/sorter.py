from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    changes: List[Tuple[str, int, int]] = field(default_factory=list)


def has_changes(result: SortResult) -> bool:
    return len(result.changes) > 0


def summary(result: SortResult) -> str:
    if not has_changes(result):
        return "Already sorted, no changes needed."
    return f"{len(result.changes)} key(s) reordered."


def sort(env: Dict[str, str], reverse: bool = False) -> SortResult:
    original_keys = list(env.keys())
    sorted_keys = sorted(original_keys, reverse=reverse)

    sorted_env = {k: env[k] for k in sorted_keys}

    changes = []
    for new_idx, key in enumerate(sorted_keys):
        old_idx = original_keys.index(key)
        if old_idx != new_idx:
            changes.append((key, old_idx, new_idx))

    return SortResult(original=env, sorted_env=sorted_env, changes=changes)

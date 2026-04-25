"""Rename keys across an env variable set."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RenameResult:
    original: Dict[str, str]
    renamed: Dict[str, str]
    changes: List[Tuple[str, str]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def has_changes(result: RenameResult) -> bool:
    return len(result.changes) > 0


def summary(result: RenameResult) -> str:
    parts = []
    if result.changes:
        parts.append(f"{len(result.changes)} key(s) renamed")
    if result.skipped:
        parts.append(f"{len(result.skipped)} key(s) skipped (not found)")
    if not parts:
        return "No changes made."
    return "; ".join(parts) + "."


def rename(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> RenameResult:
    """Rename keys in *env* according to *mapping* (old_name -> new_name).

    If the target key already exists and *overwrite* is False the rename is
    skipped and the old key is recorded in ``skipped``.
    """
    result = dict(env)
    changes: List[Tuple[str, str]] = []
    skipped: List[str] = []

    for old_key, new_key in mapping.items():
        if old_key not in result:
            skipped.append(old_key)
            continue
        if new_key in result and not overwrite:
            skipped.append(old_key)
            continue
        value = result.pop(old_key)
        result[new_key] = value
        changes.append((old_key, new_key))

    return RenameResult(
        original=dict(env),
        renamed=result,
        changes=changes,
        skipped=skipped,
    )

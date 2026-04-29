"""Rotate environment variable keys by renaming them according to a rotation map.

A rotation map is a dict of {old_key: new_key}. Keys not in the map are
preserved unchanged. If a target key already exists the rotation is skipped
unless overwrite=True.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RotateResult:
    env: Dict[str, str]
    rotated: List[Tuple[str, str]] = field(default_factory=list)   # (old, new)
    skipped: List[Tuple[str, str]] = field(default_factory=list)   # (old, new) — target existed
    missing: List[str] = field(default_factory=list)               # old key not found


def has_changes(result: RotateResult) -> bool:
    return bool(result.rotated)


def summary(result: RotateResult) -> str:
    parts: List[str] = []
    if result.rotated:
        parts.append(f"{len(result.rotated)} rotated")
    if result.skipped:
        parts.append(f"{len(result.skipped)} skipped (conflict)")
    if result.missing:
        parts.append(f"{len(result.missing)} missing")
    return ", ".join(parts) if parts else "no changes"


def rotate(
    env: Dict[str, str],
    rotation_map: Dict[str, str],
    *,
    overwrite: bool = False,
) -> RotateResult:
    """Return a new env dict with keys renamed according to *rotation_map*.

    Parameters
    ----------
    env:
        The source environment mapping.
    rotation_map:
        Mapping of old key names to new key names.
    overwrite:
        When True, an existing target key is replaced; when False the
        rotation is skipped and recorded in ``result.skipped``.
    """
    out = dict(env)
    rotated: List[Tuple[str, str]] = []
    skipped: List[Tuple[str, str]] = []
    missing: List[str] = []

    for old_key, new_key in rotation_map.items():
        if old_key not in out:
            missing.append(old_key)
            continue

        if new_key in out and not overwrite:
            skipped.append((old_key, new_key))
            continue

        value = out.pop(old_key)
        out[new_key] = value
        rotated.append((old_key, new_key))

    return RotateResult(env=out, rotated=rotated, skipped=skipped, missing=missing)

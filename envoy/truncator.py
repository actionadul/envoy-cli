"""Truncate long environment variable values to a maximum length."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TruncateResult:
    original: Dict[str, str]
    truncated: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)


def has_changes(result: TruncateResult) -> bool:
    return len(result.changes) > 0


def summary(result: TruncateResult) -> str:
    if not has_changes(result):
        return "No values truncated."
    return f"{len(result.changes)} value(s) truncated."


def truncate(
    env: Dict[str, str],
    max_length: int = 255,
    suffix: str = "...",
    keys: List[str] | None = None,
) -> TruncateResult:
    """Truncate values in *env* that exceed *max_length* characters.

    Parameters
    ----------
    env:        Mapping of key -> value to process.
    max_length: Maximum allowed length for a value (inclusive). Values
                longer than this will be shortened. Must be >= len(suffix).
    suffix:     String appended to truncated values (counts toward max_length).
    keys:       Optional allowlist of keys to process; all keys processed when
                ``None``.
    """
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= len(suffix) ({len(suffix)})"
        )

    result_env: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        if keys is not None and key not in keys:
            result_env[key] = value
            continue

        if len(value) > max_length:
            new_value = value[: max_length - len(suffix)] + suffix
            result_env[key] = new_value
            changes.append((key, value, new_value))
        else:
            result_env[key] = value

    return TruncateResult(original=dict(env), truncated=result_env, changes=changes)

"""Coerce environment variable values to canonical string representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class CoerceResult:
    env: Dict[str, str]
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)
    errors: List[Tuple[str, str, str]] = field(default_factory=list)   # (key, value, reason)


def has_changes(result: CoerceResult) -> bool:
    return bool(result.changed)


def has_errors(result: CoerceResult) -> bool:
    return bool(result.errors)


def summary(result: CoerceResult) -> str:
    parts = []
    if result.changed:
        parts.append(f"{len(result.changed)} value(s) coerced")
    if result.errors:
        parts.append(f"{len(result.errors)} error(s)")
    return ", ".join(parts) if parts else "no changes"


def _coerce_value(value: str, target_type: str) -> Tuple[str, str | None]:
    """Return (coerced_value, error_reason).  error_reason is None on success."""
    t = target_type.lower()
    if t == "bool":
        if value.lower() in _BOOL_TRUE:
            return "true", None
        if value.lower() in _BOOL_FALSE:
            return "false", None
        return value, f"cannot coerce {value!r} to bool"
    if t == "int":
        try:
            return str(int(float(value))), None
        except (ValueError, OverflowError):
            return value, f"cannot coerce {value!r} to int"
    if t == "float":
        try:
            return str(float(value)), None
        except ValueError:
            return value, f"cannot coerce {value!r} to float"
    if t == "str":
        return value, None
    return value, f"unknown target type {target_type!r}"


def coerce(
    env: Dict[str, str],
    rules: Dict[str, str],  # {key: target_type}
) -> CoerceResult:
    """Apply type-coercion rules to *env* and return a CoerceResult.

    Keys absent from *env* are silently skipped.
    """
    out = dict(env)
    changed: List[Tuple[str, str, str]] = []
    errors: List[Tuple[str, str, str]] = []

    for key, target_type in rules.items():
        if key not in out:
            continue
        old = out[key]
        new, err = _coerce_value(old, target_type)
        if err:
            errors.append((key, old, err))
        elif new != old:
            out[key] = new
            changed.append((key, old, new))

    return CoerceResult(env=out, changed=changed, errors=errors)

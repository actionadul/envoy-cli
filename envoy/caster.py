"""Type casting utilities for environment variable values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


@dataclass
class CastResult:
    original: dict[str, str]
    casted: dict[str, Any]
    changed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def has_changes(result: CastResult) -> bool:
    return bool(result.changed)


def has_errors(result: CastResult) -> bool:
    return bool(result.errors)


def summary(result: CastResult) -> str:
    parts = []
    if result.changed:
        parts.append(f"{len(result.changed)} key(s) casted")
    if result.errors:
        parts.append(f"{len(result.errors)} error(s)")
    return ", ".join(parts) if parts else "no changes"


def _cast_value(value: str, as_type: str) -> tuple[Any, str | None]:
    """Attempt to cast *value* to *as_type*.

    Returns ``(casted_value, None)`` on success or ``(value, error_msg)`` on
    failure.
    """
    try:
        if as_type == "int":
            return int(value), None
        if as_type == "float":
            return float(value), None
        if as_type == "bool":
            lower = value.strip().lower()
            if lower in _BOOL_TRUE:
                return True, None
            if lower in _BOOL_FALSE:
                return False, None
            return value, f"cannot cast '{value}' to bool"
        if as_type == "str":
            return value, None
    except (ValueError, TypeError):
        return value, f"cannot cast '{value}' to {as_type}"
    return value, f"unknown type '{as_type}'"


def cast(
    env: dict[str, str],
    rules: dict[str, str],
) -> CastResult:
    """Cast env values according to *rules* mapping key -> type name.

    Supported types: ``int``, ``float``, ``bool``, ``str``.
    Keys not present in *rules* are passed through unchanged as strings.
    """
    casted: dict[str, Any] = dict(env)
    changed: list[str] = []
    errors: list[str] = []

    for key, as_type in rules.items():
        if key not in env:
            continue
        new_val, err = _cast_value(env[key], as_type)
        if err:
            errors.append(f"{key}: {err}")
        else:
            casted[key] = new_val
            if new_val != env[key]:
                changed.append(key)

    return CastResult(original=env, casted=casted, changed=changed, errors=errors)

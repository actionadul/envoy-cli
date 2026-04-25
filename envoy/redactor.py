"""Redact sensitive values from env variable sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SECRET_PATTERNS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "auth",
    "credential",
    "access_key",
)

REDACTED_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)


def _is_sensitive(key: str) -> bool:
    """Return True if the key name suggests a sensitive value."""
    lower = key.lower()
    return any(pattern in lower for pattern in _SECRET_PATTERNS)


def redact(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> RedactResult:
    """Return a copy of *env* with sensitive values replaced by *placeholder*.

    If *keys* is provided only those keys are redacted, regardless of name.
    Otherwise keys are auto-detected via :func:`_is_sensitive`.
    """
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for k, v in env.items():
        if keys is not None:
            should_redact = k in keys
        else:
            should_redact = _is_sensitive(k)

        if should_redact:
            redacted[k] = placeholder
            redacted_keys.append(k)
        else:
            redacted[k] = v

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
    )


def summary(result: RedactResult) -> str:
    """Return a human-readable summary of what was redacted."""
    count = len(result.redacted_keys)
    if count == 0:
        return "No keys redacted."
    keys_str = ", ".join(result.redacted_keys)
    return f"Redacted {count} key(s): {keys_str}"

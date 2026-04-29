"""Mask environment variable values for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS = (
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "auth", "credential", "private_key", "access_key", "signing_key",
)

DEFAULT_MASK = "***"
_SHOW_CHARS = 4


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    keys_masked: List[str] = field(default_factory=list)


def has_masked(result: MaskResult) -> bool:
    return len(result.keys_masked) > 0


def summary(result: MaskResult) -> str:
    if not has_masked(result):
        return "No keys masked."
    return f"{len(result.keys_masked)} key(s) masked: {', '.join(sorted(result.keys_masked))}"


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


def _mask_value(value: str, reveal_chars: int = 0, mask: str = DEFAULT_MASK) -> str:
    if not value:
        return mask
    if reveal_chars > 0 and len(value) > reveal_chars:
        return value[:reveal_chars] + mask
    return mask


def mask(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    auto_detect: bool = True,
    reveal_chars: int = 0,
    mask_str: str = DEFAULT_MASK,
) -> MaskResult:
    """Return a copy of *env* with sensitive values replaced by a mask.

    Args:
        env: The environment dict to mask.
        keys: Explicit list of keys to mask regardless of name.
        auto_detect: When True, automatically mask keys whose names suggest
            they hold sensitive data.
        reveal_chars: Number of leading characters to preserve before the mask.
        mask_str: The string used as the mask placeholder.
    """
    explicit = set(keys or [])
    masked_env: Dict[str, str] = {}
    keys_masked: List[str] = []

    for k, v in env.items():
        should_mask = k in explicit or (auto_detect and _is_sensitive(k))
        if should_mask:
            masked_env[k] = _mask_value(v, reveal_chars=reveal_chars, mask=mask_str)
            keys_masked.append(k)
        else:
            masked_env[k] = v

    return MaskResult(original=dict(env), masked=masked_env, keys_masked=keys_masked)

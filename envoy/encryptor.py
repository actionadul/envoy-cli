"""Encrypt and decrypt environment variable values using Fernet symmetric encryption."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


@dataclass
class EncryptResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class DecryptResult:
    decrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


ENC_PREFIX = "enc:"


def generate_key() -> str:
    """Generate a new Fernet key encoded as a URL-safe base64 string."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    return Fernet.generate_key().decode()


def _get_fernet(key: str) -> "Fernet":
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_env(env: Dict[str, str], key: str, keys_to_encrypt: Optional[List[str]] = None) -> EncryptResult:
    """Encrypt selected (or all) values in an env dict.

    Values already prefixed with ``enc:`` are skipped.
    """
    fernet = _get_fernet(key)
    result = EncryptResult()
    for k, v in env.items():
        if keys_to_encrypt is not None and k not in keys_to_encrypt:
            result.skipped.append(k)
            continue
        if v.startswith(ENC_PREFIX):
            result.skipped.append(k)
            continue
        try:
            token = fernet.encrypt(v.encode()).decode()
            result.encrypted[k] = f"{ENC_PREFIX}{token}"
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"{k}: {exc}")
    return result


def decrypt_env(env: Dict[str, str], key: str) -> DecryptResult:
    """Decrypt all ``enc:``-prefixed values in an env dict."""
    fernet = _get_fernet(key)
    result = DecryptResult()
    for k, v in env.items():
        if not v.startswith(ENC_PREFIX):
            result.skipped.append(k)
            continue
        token = v[len(ENC_PREFIX):]
        try:
            result.decrypted[k] = fernet.decrypt(token.encode()).decode()
        except InvalidToken:
            result.errors.append(f"{k}: invalid token or wrong key")
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"{k}: {exc}")
    return result

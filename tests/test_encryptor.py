"""Tests for envoy.encryptor."""

import pytest

pytest.importorskip("cryptography", reason="cryptography package required")

from envoy.encryptor import (
    ENC_PREFIX,
    DecryptResult,
    EncryptResult,
    decrypt_env,
    encrypt_env,
    generate_key,
)


@pytest.fixture()
def key():
    return generate_key()


def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_env_prefixes_values(key):
    env = {"DB_PASS": "secret", "APP_ENV": "production"}
    result = encrypt_env(env, key)
    assert result.encrypted["DB_PASS"].startswith(ENC_PREFIX)
    assert result.encrypted["APP_ENV"].startswith(ENC_PREFIX)
    assert not result.errors


def test_encrypt_env_skips_already_encrypted(key):
    env = {"DB_PASS": f"{ENC_PREFIX}sometoken"}
    result = encrypt_env(env, key)
    assert "DB_PASS" in result.skipped
    assert "DB_PASS" not in result.encrypted


def test_encrypt_env_respects_keys_filter(key):
    env = {"DB_PASS": "secret", "APP_ENV": "production"}
    result = encrypt_env(env, key, keys_to_encrypt=["DB_PASS"])
    assert "DB_PASS" in result.encrypted
    assert "APP_ENV" in result.skipped
    assert "APP_ENV" not in result.encrypted


def test_decrypt_env_recovers_original_value(key):
    original = {"DB_PASS": "hunter2", "TOKEN": "abc123"}
    enc_result = encrypt_env(original, key)
    encrypted_env = {**enc_result.encrypted}
    dec_result = decrypt_env(encrypted_env, key)
    assert dec_result.decrypted["DB_PASS"] == "hunter2"
    assert dec_result.decrypted["TOKEN"] == "abc123"
    assert not dec_result.errors


def test_decrypt_env_skips_plain_values(key):
    env = {"APP_ENV": "staging"}
    result = decrypt_env(env, key)
    assert "APP_ENV" in result.skipped
    assert "APP_ENV" not in result.decrypted


def test_decrypt_env_reports_invalid_token(key):
    env = {"DB_PASS": f"{ENC_PREFIX}notavalidtoken"}
    result = decrypt_env(env, key)
    assert any("DB_PASS" in e for e in result.errors)
    assert "DB_PASS" not in result.decrypted


def test_decrypt_env_wrong_key(key):
    other_key = generate_key()
    enc_result = encrypt_env({"SECRET": "value"}, key)
    dec_result = decrypt_env(enc_result.encrypted, other_key)
    assert any("SECRET" in e for e in dec_result.errors)


def test_round_trip_empty_value(key):
    env = {"EMPTY": ""}
    enc = encrypt_env(env, key)
    dec = decrypt_env(enc.encrypted, key)
    assert dec.decrypted["EMPTY"] == ""

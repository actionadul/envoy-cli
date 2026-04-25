"""Tests for envoy.redactor."""

import pytest

from envoy.redactor import (
    RedactResult,
    _is_sensitive,
    redact,
    summary,
    REDACTED_PLACEHOLDER,
)


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_detects_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_ignores_safe_key():
    assert _is_sensitive("APP_NAME") is False


def test_redact_auto_detects_sensitive_keys():
    env = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp"}
    result = redact(env)
    assert result.redacted["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result.redacted["APP_NAME"] == "myapp"


def test_redact_returns_original_unchanged():
    env = {"SECRET": "s3cr3t", "PORT": "8080"}
    result = redact(env)
    assert result.original == env


def test_redact_explicit_keys_overrides_auto():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = redact(env, keys=["PORT"])
    assert result.redacted["PORT"] == REDACTED_PLACEHOLDER
    assert result.redacted["APP_NAME"] == "myapp"


def test_redact_explicit_keys_skips_sensitive_names():
    env = {"DB_PASSWORD": "secret", "PORT": "8080"}
    result = redact(env, keys=["PORT"])
    # DB_PASSWORD is NOT in explicit list, so not redacted
    assert result.redacted["DB_PASSWORD"] == "secret"


def test_redact_records_redacted_keys_sorted():
    env = {"TOKEN": "t", "SECRET": "s", "HOST": "h"}
    result = redact(env)
    assert result.redacted_keys == sorted(["TOKEN", "SECRET"])


def test_redact_custom_placeholder():
    env = {"API_KEY": "abc123"}
    result = redact(env, placeholder="<hidden>")
    assert result.redacted["API_KEY"] == "<hidden>"


def test_redact_empty_env():
    result = redact({})
    assert result.redacted == {}
    assert result.redacted_keys == []


def test_summary_no_redactions():
    env = {"APP_NAME": "myapp"}
    result = redact(env)
    assert summary(result) == "No keys redacted."


def test_summary_with_redactions():
    env = {"DB_PASSWORD": "x", "API_KEY": "y"}
    result = redact(env)
    s = summary(result)
    assert "2 key(s)" in s
    assert "API_KEY" in s
    assert "DB_PASSWORD" in s

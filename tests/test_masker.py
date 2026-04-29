"""Tests for envoy.masker."""
import pytest
from envoy.masker import (
    DEFAULT_MASK,
    MaskResult,
    has_masked,
    mask,
    summary,
    _is_sensitive,
)


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_detects_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_ignores_safe_key():
    assert _is_sensitive("APP_NAME") is False


def test_mask_auto_detects_sensitive_keys():
    env = {"DB_PASSWORD": "s3cr3t", "APP_NAME": "myapp"}
    result = mask(env)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["APP_NAME"] == "myapp"


def test_mask_records_masked_keys():
    env = {"API_KEY": "abc123", "HOST": "localhost"}
    result = mask(env)
    assert "API_KEY" in result.keys_masked
    assert "HOST" not in result.keys_masked


def test_mask_explicit_keys_override():
    env = {"APP_NAME": "myapp", "CUSTOM": "value"}
    result = mask(env, keys=["CUSTOM"], auto_detect=False)
    assert result.masked["CUSTOM"] == DEFAULT_MASK
    assert result.masked["APP_NAME"] == "myapp"


def test_mask_auto_detect_disabled():
    env = {"DB_PASSWORD": "s3cr3t"}
    result = mask(env, auto_detect=False)
    assert result.masked["DB_PASSWORD"] == "s3cr3t"
    assert result.keys_masked == []


def test_mask_reveal_chars_preserves_prefix():
    env = {"SECRET_KEY": "abcdef1234"}
    result = mask(env, reveal_chars=4)
    assert result.masked["SECRET_KEY"] == "abcd" + DEFAULT_MASK


def test_mask_reveal_chars_zero_hides_all():
    env = {"SECRET_KEY": "abcdef1234"}
    result = mask(env, reveal_chars=0)
    assert result.masked["SECRET_KEY"] == DEFAULT_MASK


def test_mask_empty_value_still_masked():
    env = {"DB_PASSWORD": ""}
    result = mask(env)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK


def test_mask_does_not_mutate_original():
    env = {"DB_PASSWORD": "s3cr3t"}
    original_copy = dict(env)
    mask(env)
    assert env == original_copy


def test_mask_original_preserved_in_result():
    env = {"DB_PASSWORD": "s3cr3t"}
    result = mask(env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_has_masked_true_when_keys_masked():
    env = {"TOKEN": "abc"}
    result = mask(env)
    assert has_masked(result) is True


def test_has_masked_false_when_nothing_masked():
    env = {"APP_NAME": "myapp"}
    result = mask(env, auto_detect=False)
    assert has_masked(result) is False


def test_summary_no_masked_keys():
    env = {"APP_NAME": "myapp"}
    result = mask(env, auto_detect=False)
    assert summary(result) == "No keys masked."


def test_summary_lists_masked_keys():
    env = {"DB_PASSWORD": "x", "API_KEY": "y"}
    result = mask(env)
    text = summary(result)
    assert "2 key(s) masked" in text
    assert "API_KEY" in text
    assert "DB_PASSWORD" in text


def test_mask_custom_mask_string():
    env = {"DB_PASSWORD": "secret"}
    result = mask(env, mask_str="[HIDDEN]")
    assert result.masked["DB_PASSWORD"] == "[HIDDEN]"

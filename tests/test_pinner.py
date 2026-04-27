"""Tests for envoy.pinner."""
import pytest
from envoy.pinner import PinResult, apply, has_changes, pin, summary


def test_pin_updates_existing_key():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = pin(env, {"PORT": "443"})
    assert "PORT" in result.pinned
    assert result.pinned["PORT"] == "443"


def test_pin_skips_key_not_in_env_when_only_existing():
    env = {"HOST": "localhost"}
    result = pin(env, {"MISSING": "value"}, only_existing=True)
    assert "MISSING" not in result.pinned
    assert "MISSING" in result.skipped


def test_pin_adds_key_when_only_existing_false():
    env = {"HOST": "localhost"}
    result = pin(env, {"NEW_KEY": "new_val"}, only_existing=False)
    assert "NEW_KEY" in result.pinned
    assert result.skipped == []


def test_pin_does_not_record_if_value_unchanged():
    env = {"HOST": "localhost"}
    result = pin(env, {"HOST": "localhost"})
    assert "HOST" not in result.pinned


def test_pin_preserves_original():
    env = {"PORT": "8080"}
    result = pin(env, {"PORT": "443"})
    assert result.original["PORT"] == "8080"


def test_has_changes_true_when_pinned():
    env = {"A": "1"}
    result = pin(env, {"A": "2"})
    assert has_changes(result) is True


def test_has_changes_false_when_nothing_changed():
    env = {"A": "1"}
    result = pin(env, {"A": "1"})
    assert has_changes(result) is False


def test_summary_with_pinned_and_skipped():
    env = {"A": "1"}
    result = pin(env, {"A": "2", "GHOST": "x"}, only_existing=True)
    s = summary(result)
    assert "pinned 1" in s
    assert "skipped 1" in s


def test_summary_nothing_to_pin():
    env = {"A": "1"}
    result = pin(env, {"A": "1"})
    assert summary(result) == "nothing to pin"


def test_apply_returns_merged_dict():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = pin(env, {"PORT": "443"})
    merged = apply(env, result)
    assert merged["PORT"] == "443"
    assert merged["HOST"] == "localhost"


def test_apply_does_not_mutate_original_env():
    env = {"PORT": "8080"}
    result = pin(env, {"PORT": "443"})
    apply(env, result)
    assert env["PORT"] == "8080"


def test_pin_multiple_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = pin(env, {"A": "10", "C": "30"})
    assert result.pinned == {"A": "10", "C": "30"}

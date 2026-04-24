"""Tests for the envoy.differ module."""

import pytest

from envoy.differ import DiffResult, diff_envs, format_diff


BASE = {
    "APP_ENV": "production",
    "DB_HOST": "db.example.com",
    "SECRET_KEY": "abc123",
    "LOG_LEVEL": "info",
}

TARGET = {
    "APP_ENV": "staging",
    "DB_HOST": "db.example.com",
    "NEW_FEATURE_FLAG": "true",
    "LOG_LEVEL": "debug",
}


def test_diff_detects_added_keys():
    result = diff_envs(BASE, TARGET)
    assert "NEW_FEATURE_FLAG" in result.added
    assert result.added["NEW_FEATURE_FLAG"] == "true"


def test_diff_detects_removed_keys():
    result = diff_envs(BASE, TARGET)
    assert "SECRET_KEY" in result.removed
    assert result.removed["SECRET_KEY"] == "abc123"


def test_diff_detects_changed_keys():
    result = diff_envs(BASE, TARGET)
    assert "APP_ENV" in result.changed
    assert result.changed["APP_ENV"] == ("production", "staging")
    assert "LOG_LEVEL" in result.changed
    assert result.changed["LOG_LEVEL"] == ("info", "debug")


def test_diff_detects_unchanged_keys():
    result = diff_envs(BASE, TARGET)
    assert "DB_HOST" in result.unchanged
    assert result.unchanged["DB_HOST"] == "db.example.com"


def test_diff_has_differences_true():
    result = diff_envs(BASE, TARGET)
    assert result.has_differences is True


def test_diff_has_differences_false():
    result = diff_envs(BASE, BASE)
    assert result.has_differences is False


def test_diff_identical_envs_all_unchanged():
    result = diff_envs(BASE, BASE)
    assert result.added == {}
    assert result.removed == {}
    assert result.changed == {}
    assert set(result.unchanged.keys()) == set(BASE.keys())


def test_diff_ignore_keys():
    result = diff_envs(BASE, TARGET, ignore_keys={"SECRET_KEY", "NEW_FEATURE_FLAG"})
    assert "SECRET_KEY" not in result.removed
    assert "NEW_FEATURE_FLAG" not in result.added


def test_diff_summary_with_differences():
    result = diff_envs(BASE, TARGET)
    summary = result.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary


def test_diff_summary_no_differences():
    result = diff_envs(BASE, BASE)
    assert result.summary() == "No differences found."


def test_format_diff_with_values():
    result = diff_envs(BASE, TARGET)
    output = format_diff(result, show_values=True)
    assert "+ NEW_FEATURE_FLAG=true" in output
    assert "- SECRET_KEY=abc123" in output
    assert "'production'" in output


def test_format_diff_without_values():
    result = diff_envs(BASE, TARGET)
    output = format_diff(result, show_values=False)
    assert "NEW_FEATURE_FLAG" in output
    assert "true" not in output


def test_format_diff_no_differences():
    result = diff_envs(BASE, BASE)
    assert format_diff(result) == "(no differences)"

"""Tests for envoy.stripper."""

import pytest
from envoy.stripper import StripResult, has_changes, summary, strip


ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "DEBUG": "true",
    "SECRET_TOKEN": "tok",
}


def test_strip_exact_key_removed():
    result = strip(ENV, keys=["DEBUG"])
    assert "DEBUG" not in result.stripped


def test_strip_exact_key_recorded():
    result = strip(ENV, keys=["DEBUG"])
    assert "DEBUG" in result.removed


def test_strip_unknown_key_ignored():
    result = strip(ENV, keys=["NONEXISTENT"])
    assert result.stripped == ENV
    assert result.removed == []


def test_strip_multiple_exact_keys():
    result = strip(ENV, keys=["DEBUG", "APP_NAME"])
    assert "DEBUG" not in result.stripped
    assert "APP_NAME" not in result.stripped
    assert len(result.removed) == 2


def test_strip_pattern_suffix():
    result = strip(ENV, patterns=["*_KEY"])
    assert "API_KEY" not in result.stripped
    assert "API_KEY" in result.removed


def test_strip_pattern_prefix():
    result = strip(ENV, patterns=["SECRET_*"])
    assert "SECRET_TOKEN" not in result.stripped


def test_strip_pattern_wildcard_all():
    result = strip(ENV, patterns=["*"])
    assert result.stripped == {}
    assert len(result.removed) == len(ENV)


def test_strip_combined_keys_and_patterns():
    result = strip(ENV, keys=["DEBUG"], patterns=["*_PASSWORD"])
    assert "DEBUG" not in result.stripped
    assert "DB_PASSWORD" not in result.stripped
    assert len(result.removed) == 2


def test_strip_does_not_mutate_original():
    original = dict(ENV)
    strip(ENV, keys=["DEBUG"], patterns=["*_KEY"])
    assert ENV == original


def test_strip_original_preserved_in_result():
    result = strip(ENV, keys=["DEBUG"])
    assert result.original == ENV


def test_strip_removed_is_sorted():
    result = strip(ENV, keys=["SECRET_TOKEN", "API_KEY", "DEBUG"])
    assert result.removed == sorted(result.removed)


def test_has_changes_true():
    result = strip(ENV, keys=["DEBUG"])
    assert has_changes(result) is True


def test_has_changes_false():
    result = strip(ENV, keys=["NONEXISTENT"])
    assert has_changes(result) is False


def test_summary_no_changes():
    result = strip(ENV, keys=[])
    assert summary(result) == "No keys removed."


def test_summary_with_changes():
    result = strip(ENV, keys=["DEBUG"])
    assert "1" in summary(result)
    assert "DEBUG" in summary(result)

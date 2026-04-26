"""Tests for envoy.filter module."""

import pytest
from envoy.filter import FilterResult, filter_env, has_matches, summary


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "APP_PORT": "8080",
    "DB_HOST": "localhost",
    "DB_PASSWORD": "secret",
    "DEBUG": "true",
}


def test_filter_no_patterns_returns_all():
    result = filter_env(SAMPLE_ENV)
    assert result.filtered == SAMPLE_ENV
    assert result.excluded_keys == []


def test_filter_include_glob_pattern():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*"])
    assert set(result.matched_keys) == {"APP_NAME", "APP_PORT"}
    assert "DB_HOST" not in result.filtered


def test_filter_multiple_include_patterns():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*", "DB_*"])
    assert "DEBUG" not in result.filtered
    assert len(result.matched_keys) == 4


def test_filter_exclude_glob_pattern():
    result = filter_env(SAMPLE_ENV, exclude_patterns=["DB_*"])
    assert "DB_HOST" not in result.filtered
    assert "DB_PASSWORD" not in result.filtered
    assert "APP_NAME" in result.filtered


def test_filter_include_and_exclude_combined():
    result = filter_env(
        SAMPLE_ENV,
        include_patterns=["DB_*"],
        exclude_patterns=["*_PASSWORD"],
    )
    assert result.filtered == {"DB_HOST": "localhost"}


def test_filter_value_pattern():
    result = filter_env(SAMPLE_ENV, value_pattern=r"^\d+$")
    assert result.filtered == {"APP_PORT": "8080"}


def test_filter_value_pattern_with_include():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*"], value_pattern=r"\d+")
    assert result.filtered == {"APP_PORT": "8080"}


def test_filter_keys_only_ignores_value_pattern():
    result = filter_env(SAMPLE_ENV, value_pattern=r"^\d+$", keys_only=True)
    assert result.filtered == SAMPLE_ENV


def test_filter_excluded_keys_recorded():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*"])
    assert set(result.excluded_keys) == {"DB_HOST", "DB_PASSWORD", "DEBUG"}


def test_has_matches_true():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*"])
    assert has_matches(result) is True


def test_has_matches_false():
    result = filter_env(SAMPLE_ENV, include_patterns=["MISSING_*"])
    assert has_matches(result) is False


def test_summary_format():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*"])
    s = summary(result)
    assert "2/5" in s
    assert "matched" in s


def test_filter_preserves_original():
    result = filter_env(SAMPLE_ENV, include_patterns=["APP_*"])
    assert result.original == SAMPLE_ENV

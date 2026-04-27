"""Tests for envoy.scoper."""

import pytest

from envoy.scoper import ScopeResult, has_matches, scope, summary


ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PASSWORD": "secret",
    "LOG_LEVEL": "info",
}


def test_scope_returns_matching_keys():
    result = scope(ENV, "APP_")
    assert set(result.scoped.keys()) == {"APP_HOST", "APP_PORT"}


def test_scope_preserves_values():
    result = scope(ENV, "APP_")
    assert result.scoped["APP_HOST"] == "localhost"
    assert result.scoped["APP_PORT"] == "8080"


def test_scope_dropped_contains_non_matching():
    result = scope(ENV, "APP_")
    assert "DB_HOST" in result.dropped
    assert "LOG_LEVEL" in result.dropped


def test_scope_strip_prefix_removes_prefix():
    result = scope(ENV, "APP_", strip_prefix=True)
    assert set(result.scoped.keys()) == {"HOST", "PORT"}


def test_scope_strip_prefix_preserves_values():
    result = scope(ENV, "DB_", strip_prefix=True)
    assert result.scoped["HOST"] == "db.local"
    assert result.scoped["PASSWORD"] == "secret"


def test_scope_no_matches_returns_empty():
    result = scope(ENV, "REDIS_")
    assert result.scoped == {}
    assert len(result.dropped) == len(ENV)


def test_scope_case_insensitive_matches():
    env = {"app_host": "localhost", "DB_HOST": "db.local"}
    result = scope(env, "APP_", case_sensitive=False)
    assert "app_host" in result.scoped


def test_scope_case_sensitive_no_match_lowercase():
    env = {"app_host": "localhost"}
    result = scope(env, "APP_", case_sensitive=True)
    assert result.scoped == {}


def test_has_matches_true_when_scoped():
    result = scope(ENV, "APP_")
    assert has_matches(result) is True


def test_has_matches_false_when_empty():
    result = scope(ENV, "REDIS_")
    assert has_matches(result) is False


def test_summary_includes_prefix():
    result = scope(ENV, "APP_")
    assert "APP_" in summary(result)


def test_summary_includes_matched_count():
    result = scope(ENV, "APP_")
    assert "2 matched" in summary(result)


def test_summary_notes_strip_when_enabled():
    result = scope(ENV, "APP_", strip_prefix=True)
    assert "prefix stripped" in summary(result)


def test_summary_no_strip_note_when_disabled():
    result = scope(ENV, "APP_", strip_prefix=False)
    assert "prefix stripped" not in summary(result)


def test_scope_result_stores_prefix():
    result = scope(ENV, "DB_")
    assert result.prefix == "DB_"


def test_scope_result_stripped_flag():
    result = scope(ENV, "DB_", strip_prefix=True)
    assert result.stripped is True

    result2 = scope(ENV, "DB_", strip_prefix=False)
    assert result2.stripped is False

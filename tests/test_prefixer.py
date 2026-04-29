"""Tests for envoy.prefixer."""
import pytest
from envoy.prefixer import add_prefix, strip_prefix, has_changes, summary


ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "envoy"}


# ---------------------------------------------------------------------------
# add_prefix
# ---------------------------------------------------------------------------

def test_add_prefix_prepends_to_all_keys():
    result = add_prefix({"HOST": "localhost", "PORT": "5432"}, "APP_")
    assert "APP_HOST" in result.updated
    assert "APP_PORT" in result.updated


def test_add_prefix_preserves_values():
    result = add_prefix({"HOST": "localhost"}, "APP_")
    assert result.updated["APP_HOST"] == "localhost"


def test_add_prefix_skips_already_prefixed_keys():
    result = add_prefix({"APP_HOST": "localhost", "PORT": "5432"}, "APP_")
    assert "APP_HOST" in result.updated
    assert "APP_PORT" in result.updated
    # APP_HOST was not re-prefixed
    assert "APP_APP_HOST" not in result.updated


def test_add_prefix_records_changed_keys():
    result = add_prefix({"HOST": "localhost"}, "APP_")
    assert ("HOST", "APP_HOST") in result.changed


def test_add_prefix_already_prefixed_not_in_changed():
    result = add_prefix({"APP_HOST": "localhost"}, "APP_")
    assert result.changed == []


def test_add_prefix_empty_prefix_no_changes():
    result = add_prefix({"HOST": "localhost"}, "")
    assert not has_changes(result)
    assert result.updated == {"HOST": "localhost"}


def test_add_prefix_has_changes_true():
    result = add_prefix({"HOST": "localhost"}, "APP_")
    assert has_changes(result)


def test_add_prefix_has_changes_false_when_all_prefixed():
    result = add_prefix({"APP_HOST": "localhost"}, "APP_")
    assert not has_changes(result)


# ---------------------------------------------------------------------------
# strip_prefix
# ---------------------------------------------------------------------------

def test_strip_prefix_removes_prefix():
    result = strip_prefix({"APP_HOST": "localhost", "APP_PORT": "5432"}, "APP_")
    assert "HOST" in result.updated
    assert "PORT" in result.updated


def test_strip_prefix_preserves_values():
    result = strip_prefix({"APP_HOST": "localhost"}, "APP_")
    assert result.updated["HOST"] == "localhost"


def test_strip_prefix_leaves_non_matching_keys():
    result = strip_prefix({"APP_HOST": "localhost", "OTHER": "val"}, "APP_")
    assert "OTHER" in result.updated
    assert "APP_HOST" not in result.updated


def test_strip_prefix_records_changed_keys():
    result = strip_prefix({"APP_HOST": "localhost"}, "APP_")
    assert ("APP_HOST", "HOST") in result.changed


def test_strip_prefix_non_matching_not_in_changed():
    result = strip_prefix({"OTHER": "val"}, "APP_")
    assert result.changed == []


def test_strip_prefix_empty_prefix_no_changes():
    result = strip_prefix({"APP_HOST": "localhost"}, "")
    assert not has_changes(result)


def test_strip_prefix_key_equals_prefix_not_lost():
    # Key exactly equal to prefix should remain unchanged (guard branch)
    result = strip_prefix({"APP_": "val"}, "APP_")
    assert "APP_" in result.updated
    assert result.changed == []


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    result = add_prefix({"APP_HOST": "localhost"}, "APP_")
    assert summary(result) == "No keys changed."


def test_summary_with_changes():
    result = add_prefix({"HOST": "localhost", "PORT": "5432"}, "APP_")
    assert "2 key(s) renamed." == summary(result)

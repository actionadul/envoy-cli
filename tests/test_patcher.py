"""Tests for envoy.patcher."""
import pytest
from envoy.patcher import patch, has_changes, summary


BASE = {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}


def test_patch_adds_new_key():
    result = patch(BASE, sets=[("NEW_KEY", "value")])
    assert "NEW_KEY" in result.patched
    assert result.patched["NEW_KEY"] == "value"
    assert "NEW_KEY" in result.added


def test_patch_updates_existing_key():
    result = patch(BASE, sets=[("DEBUG", "true")])
    assert result.patched["DEBUG"] == "true"
    assert "DEBUG" in result.updated
    assert "DEBUG" not in result.added


def test_patch_set_same_value_not_recorded_as_updated():
    result = patch(BASE, sets=[("PORT", "8080")])
    assert "PORT" not in result.updated
    assert "PORT" not in result.added


def test_patch_removes_existing_key():
    result = patch(BASE, unsets=["DEBUG"])
    assert "DEBUG" not in result.patched
    assert "DEBUG" in result.removed


def test_patch_unset_missing_key_ignored():
    result = patch(BASE, unsets=["DOES_NOT_EXIST"])
    assert "DOES_NOT_EXIST" not in result.removed
    assert result.patched == BASE


def test_patch_does_not_mutate_original():
    original = dict(BASE)
    patch(BASE, sets=[("X", "1")], unsets=["PORT"])
    assert BASE == original


def test_has_changes_true_when_added():
    result = patch(BASE, sets=[("FRESH", "yes")])
    assert has_changes(result)


def test_has_changes_false_when_no_ops():
    result = patch(BASE)
    assert not has_changes(result)


def test_summary_no_changes():
    result = patch(BASE)
    assert summary(result) == "no changes"


def test_summary_combined():
    result = patch(BASE, sets=[("NEW", "v"), ("DEBUG", "true")], unsets=["PORT"])
    s = summary(result)
    assert "1 added" in s
    assert "1 updated" in s
    assert "1 removed" in s


def test_patch_multiple_sets_and_unsets():
    result = patch(
        BASE,
        sets=[("A", "1"), ("B", "2"), ("APP_ENV", "staging")],
        unsets=["DEBUG", "PORT"],
    )
    assert result.patched == {"APP_ENV": "staging", "A": "1", "B": "2"}
    assert sorted(result.added) == ["A", "B"]
    assert result.updated == ["APP_ENV"]
    assert sorted(result.removed) == ["DEBUG", "PORT"]

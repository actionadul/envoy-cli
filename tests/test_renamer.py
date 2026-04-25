"""Tests for envoy.renamer."""

import pytest
from envoy.renamer import rename, has_changes, summary, RenameResult


BASE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_rename_single_key():
    result = rename(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.renamed
    assert "DB_HOST" not in result.renamed
    assert result.renamed["DATABASE_HOST"] == "localhost"


def test_rename_preserves_value():
    result = rename(BASE_ENV, {"DB_PORT": "DATABASE_PORT"})
    assert result.renamed["DATABASE_PORT"] == "5432"


def test_rename_records_change():
    result = rename(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert ("DB_HOST", "DATABASE_HOST") in result.changes


def test_rename_missing_key_is_skipped():
    result = rename(BASE_ENV, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.renamed


def test_rename_skips_when_target_exists_no_overwrite():
    env = {"OLD": "val1", "NEW": "val2"}
    result = rename(env, {"OLD": "NEW"}, overwrite=False)
    assert "OLD" in result.skipped
    assert result.renamed["NEW"] == "val2"  # original value preserved


def test_rename_overwrites_when_flag_set():
    env = {"OLD": "val1", "NEW": "val2"}
    result = rename(env, {"OLD": "NEW"}, overwrite=True)
    assert result.renamed["NEW"] == "val1"
    assert "OLD" not in result.renamed
    assert ("OLD", "NEW") in result.changes


def test_rename_multiple_keys():
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename(BASE_ENV, mapping)
    assert "DATABASE_HOST" in result.renamed
    assert "DATABASE_PORT" in result.renamed
    assert len(result.changes) == 2


def test_rename_does_not_mutate_original():
    original = dict(BASE_ENV)
    rename(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert BASE_ENV == original


def test_has_changes_true():
    result = rename(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert has_changes(result) is True


def test_has_changes_false():
    result = rename(BASE_ENV, {"MISSING": "OTHER"})
    assert has_changes(result) is False


def test_summary_with_changes():
    result = rename(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "1 key(s) renamed" in summary(result)


def test_summary_with_skipped():
    result = rename(BASE_ENV, {"MISSING": "OTHER"})
    assert "1 key(s) skipped" in summary(result)


def test_summary_no_changes():
    result = RenameResult(original={}, renamed={}, changes=[], skipped=[])
    assert summary(result) == "No changes made."

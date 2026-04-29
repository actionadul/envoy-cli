"""Tests for envoy.rotator."""
import pytest
from envoy.rotator import RotateResult, has_changes, summary, rotate


BASE_ENV = {
    "OLD_DB_HOST": "localhost",
    "OLD_DB_PORT": "5432",
    "APP_SECRET": "s3cr3t",
}


def test_rotate_renames_key():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert "DB_HOST" in result.env
    assert "OLD_DB_HOST" not in result.env


def test_rotate_preserves_value():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert result.env["DB_HOST"] == "localhost"


def test_rotate_records_rotated_pair():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert ("OLD_DB_HOST", "DB_HOST") in result.rotated


def test_rotate_missing_key_recorded():
    result = rotate(BASE_ENV, {"NONEXISTENT": "NEW_KEY"})
    assert "NONEXISTENT" in result.missing
    assert "NEW_KEY" not in result.env


def test_rotate_skips_when_target_exists_no_overwrite():
    env = {**BASE_ENV, "DB_HOST": "other"}
    result = rotate(env, {"OLD_DB_HOST": "DB_HOST"})
    assert ("OLD_DB_HOST", "DB_HOST") in result.skipped
    assert result.env["DB_HOST"] == "other"
    assert result.env["OLD_DB_HOST"] == "localhost"


def test_rotate_overwrites_when_flag_set():
    env = {**BASE_ENV, "DB_HOST": "other"}
    result = rotate(env, {"OLD_DB_HOST": "DB_HOST"}, overwrite=True)
    assert result.env["DB_HOST"] == "localhost"
    assert "OLD_DB_HOST" not in result.env
    assert ("OLD_DB_HOST", "DB_HOST") in result.rotated


def test_rotate_multiple_keys():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST", "OLD_DB_PORT": "DB_PORT"})
    assert "DB_HOST" in result.env
    assert "DB_PORT" in result.env
    assert len(result.rotated) == 2


def test_rotate_preserves_untouched_keys():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert result.env["APP_SECRET"] == "s3cr3t"
    assert result.env["OLD_DB_PORT"] == "5432"


def test_rotate_does_not_mutate_original():
    original = dict(BASE_ENV)
    rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert BASE_ENV == original


def test_has_changes_true_when_rotated():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert has_changes(result) is True


def test_has_changes_false_when_nothing_rotated():
    result = rotate(BASE_ENV, {"NONEXISTENT": "NEW_KEY"})
    assert has_changes(result) is False


def test_summary_reports_rotated():
    result = rotate(BASE_ENV, {"OLD_DB_HOST": "DB_HOST"})
    assert "1 rotated" in summary(result)


def test_summary_reports_skipped():
    env = {**BASE_ENV, "DB_HOST": "other"}
    result = rotate(env, {"OLD_DB_HOST": "DB_HOST"})
    assert "skipped" in summary(result)


def test_summary_reports_missing():
    result = rotate(BASE_ENV, {"GHOST": "NEW_GHOST"})
    assert "missing" in summary(result)


def test_summary_no_changes():
    result = rotate({}, {})
    assert summary(result) == "no changes"

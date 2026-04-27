"""Tests for envoy.tagger."""
import pytest
from envoy.tagger import (
    TagResult, tag, has_changes, summary, tags_for_key, keys_with_tag
)


ENV = {"DB_HOST": "localhost", "DB_PASS": "secret", "APP_ENV": "prod"}


def test_tag_adds_single_tag():
    result = tag(ENV, add={"DB_PASS": ["sensitive"]})
    assert "sensitive" in result.tags["DB_PASS"]


def test_tag_records_added_entry():
    result = tag(ENV, add={"DB_HOST": ["infra"]})
    assert "DB_HOST:infra" in result.added


def test_tag_does_not_add_duplicate():
    existing = {"DB_HOST": ["infra"]}
    result = tag(ENV, existing_tags=existing, add={"DB_HOST": ["infra"]})
    assert result.tags["DB_HOST"].count("infra") == 1
    assert result.added == []


def test_tag_skips_key_not_in_env():
    result = tag(ENV, add={"MISSING_KEY": ["label"]})
    assert "MISSING_KEY" not in result.tags
    assert result.added == []


def test_tag_removes_existing_tag():
    existing = {"DB_PASS": ["sensitive", "secret"]}
    result = tag(ENV, existing_tags=existing, remove={"DB_PASS": ["secret"]})
    assert "secret" not in result.tags.get("DB_PASS", [])
    assert "DB_PASS:secret" in result.removed


def test_tag_removes_key_when_all_tags_gone():
    existing = {"APP_ENV": ["deploy"]}
    result = tag(ENV, existing_tags=existing, remove={"APP_ENV": ["deploy"]})
    assert "APP_ENV" not in result.tags


def test_tag_remove_nonexistent_tag_ignored():
    result = tag(ENV, remove={"DB_HOST": ["ghost"]})
    assert result.removed == []


def test_has_changes_true_when_added():
    result = tag(ENV, add={"DB_HOST": ["infra"]})
    assert has_changes(result) is True


def test_has_changes_false_when_nothing_changes():
    result = tag(ENV)
    assert has_changes(result) is False


def test_summary_no_changes():
    result = tag(ENV)
    assert summary(result) == "no tag changes"


def test_summary_added_only():
    result = tag(ENV, add={"DB_HOST": ["infra"]})
    assert "1 tag(s) added" in summary(result)


def test_summary_removed_only():
    existing = {"DB_PASS": ["sensitive"]}
    result = tag(ENV, existing_tags=existing, remove={"DB_PASS": ["sensitive"]})
    assert "1 tag(s) removed" in summary(result)


def test_tags_for_key_returns_list():
    existing = {"DB_PASS": ["sensitive", "pii"]}
    result = tag(ENV, existing_tags=existing)
    assert tags_for_key(result, "DB_PASS") == ["sensitive", "pii"]


def test_tags_for_key_missing_returns_empty():
    result = tag(ENV)
    assert tags_for_key(result, "NOPE") == []


def test_keys_with_tag_returns_sorted_keys():
    existing = {"DB_PASS": ["sensitive"], "APP_ENV": ["sensitive"]}
    result = tag(ENV, existing_tags=existing)
    assert keys_with_tag(result, "sensitive") == ["APP_ENV", "DB_PASS"]


def test_original_env_not_mutated():
    original = dict(ENV)
    tag(ENV, add={"DB_HOST": ["infra"]})
    assert ENV == original

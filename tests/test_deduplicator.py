"""Tests for envoy.deduplicator."""
import pytest

from envoy.deduplicator import (
    DeduplicateResult,
    deduplicate,
    has_changes,
    summary,
)


def test_deduplicate_no_duplicates_no_changes():
    env = {"A": "1", "B": "2", "C": "3"}
    result = deduplicate(env)
    assert not has_changes(result)
    assert result.deduped == env
    assert result.removed == []


def test_deduplicate_removes_second_key_by_default():
    env = {"A": "same", "B": "other", "C": "same"}
    result = deduplicate(env)
    assert has_changes(result)
    assert "A" in result.deduped
    assert "C" not in result.deduped
    assert "C" in result.removed


def test_deduplicate_keep_last_removes_first():
    env = {"A": "same", "B": "other", "C": "same"}
    result = deduplicate(env, keep="last")
    assert "C" in result.deduped
    assert "A" not in result.deduped
    assert "A" in result.removed


def test_deduplicate_records_duplicate_tuple():
    env = {"X": "val", "Y": "val"}
    result = deduplicate(env)
    assert len(result.duplicates) == 1
    value, kept, removed = result.duplicates[0]
    assert value == "val"
    assert kept == "X"
    assert removed == "Y"


def test_deduplicate_three_identical_values():
    env = {"A": "v", "B": "v", "C": "v"}
    result = deduplicate(env)
    assert len(result.removed) == 2
    assert "A" in result.deduped
    assert "B" not in result.deduped
    assert "C" not in result.deduped


def test_deduplicate_keys_filter_limits_scope():
    env = {"A": "dup", "B": "dup", "C": "dup"}
    result = deduplicate(env, keys_filter=["A", "B"])
    # Only A and B are considered; C is outside scope and kept regardless
    assert "C" in result.deduped
    assert "A" in result.deduped
    assert "B" not in result.deduped


def test_deduplicate_keys_filter_no_overlap_no_changes():
    env = {"A": "same", "B": "same"}
    result = deduplicate(env, keys_filter=["A"])
    assert not has_changes(result)


def test_deduplicate_preserves_original():
    env = {"A": "x", "B": "x"}
    result = deduplicate(env)
    assert result.original == {"A": "x", "B": "x"}
    assert "B" not in result.deduped


def test_deduplicate_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate({"A": "1"}, keep="middle")


def test_summary_no_changes():
    env = {"A": "1", "B": "2"}
    result = deduplicate(env)
    assert summary(result) == "No duplicate values found."


def test_summary_with_changes():
    env = {"A": "dup", "B": "dup"}
    result = deduplicate(env)
    text = summary(result)
    assert "Removed 1 duplicate" in text
    assert "B" in text
    assert "A" in text

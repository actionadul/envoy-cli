"""Tests for envoy.truncator."""
import pytest

from envoy.truncator import TruncateResult, has_changes, summary, truncate


def test_truncate_short_values_unchanged():
    env = {"KEY": "short"}
    result = truncate(env, max_length=20)
    assert result.truncated["KEY"] == "short"


def test_truncate_exact_length_unchanged():
    env = {"KEY": "hello"}
    result = truncate(env, max_length=5)
    assert result.truncated["KEY"] == "hello"
    assert not has_changes(result)


def test_truncate_long_value_is_cut():
    env = {"KEY": "a" * 300}
    result = truncate(env, max_length=10)
    assert len(result.truncated["KEY"]) == 10


def test_truncate_long_value_has_suffix():
    env = {"KEY": "a" * 300}
    result = truncate(env, max_length=10, suffix="...")
    assert result.truncated["KEY"].endswith("...")


def test_truncate_records_change():
    env = {"KEY": "a" * 50}
    result = truncate(env, max_length=10)
    assert len(result.changes) == 1
    key, old, new = result.changes[0]
    assert key == "KEY"
    assert old == "a" * 50
    assert len(new) == 10


def test_truncate_no_change_not_recorded():
    env = {"KEY": "short"}
    result = truncate(env, max_length=100)
    assert result.changes == []


def test_truncate_has_changes_false_when_clean():
    env = {"A": "x", "B": "y"}
    result = truncate(env, max_length=50)
    assert not has_changes(result)


def test_truncate_has_changes_true_when_truncated():
    env = {"A": "x" * 100}
    result = truncate(env, max_length=10)
    assert has_changes(result)


def test_truncate_summary_no_changes():
    env = {"A": "short"}
    result = truncate(env, max_length=50)
    assert summary(result) == "No values truncated."


def test_truncate_summary_with_changes():
    env = {"A": "x" * 100, "B": "y" * 200}
    result = truncate(env, max_length=10)
    assert summary(result) == "2 value(s) truncated."


def test_truncate_keys_filter_only_processes_listed():
    env = {"LONG": "a" * 100, "SKIP": "b" * 100}
    result = truncate(env, max_length=10, keys=["LONG"])
    assert len(result.truncated["LONG"]) == 10
    assert result.truncated["SKIP"] == "b" * 100
    assert len(result.changes) == 1


def test_truncate_original_is_unmodified():
    env = {"KEY": "a" * 100}
    result = truncate(env, max_length=10)
    assert result.original["KEY"] == "a" * 100


def test_truncate_custom_suffix():
    env = {"KEY": "hello world"}
    result = truncate(env, max_length=8, suffix="--")
    assert result.truncated["KEY"] == "hello w--"
    assert len(result.truncated["KEY"]) == 9  # 8 - 2 + 2 = ... wait, max=8 so 6 chars + '--'


def test_truncate_raises_when_max_length_less_than_suffix():
    with pytest.raises(ValueError, match="max_length"):
        truncate({"KEY": "value"}, max_length=2, suffix="...")

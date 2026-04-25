"""Tests for envoy.sorter."""

import pytest
from envoy.sorter import SortResult, has_changes, summary, sort


def test_sort_alphabetical_order():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort(env)
    assert list(result.sorted_env.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_already_sorted_no_changes():
    env = {"ALPHA": "a", "BETA": "b", "GAMMA": "g"}
    result = sort(env)
    assert not has_changes(result)


def test_sort_detects_changes():
    env = {"Z": "1", "A": "2"}
    result = sort(env)
    assert has_changes(result)


def test_sort_reverse():
    env = {"APPLE": "1", "MANGO": "2", "ZEBRA": "3"}
    result = sort(env, reverse=True)
    assert list(result.sorted_env.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_preserves_values():
    env = {"B": "val_b", "A": "val_a"}
    result = sort(env)
    assert result.sorted_env["A"] == "val_a"
    assert result.sorted_env["B"] == "val_b"


def test_sort_group_prefix_placed_first():
    env = {"DB_HOST": "h", "APP_NAME": "n", "DB_PORT": "p", "LOG_LEVEL": "l"}
    result = sort(env, group_prefix="DB_")
    keys = list(result.sorted_env.keys())
    assert keys.index("DB_HOST") < keys.index("APP_NAME")
    assert keys.index("DB_PORT") < keys.index("APP_NAME")


def test_sort_group_prefix_sorted_within_group():
    env = {"DB_PORT": "p", "DB_HOST": "h", "APP_NAME": "n"}
    result = sort(env, group_prefix="DB_")
    keys = list(result.sorted_env.keys())
    assert keys[:2] == ["DB_HOST", "DB_PORT"]


def test_sort_empty_env():
    result = sort({})
    assert result.sorted_env == {}
    assert not has_changes(result)


def test_sort_single_key():
    env = {"ONLY": "one"}
    result = sort(env)
    assert not has_changes(result)


def test_summary_no_changes():
    env = {"A": "1", "B": "2"}
    result = sort(env)
    assert summary(result) == "Already sorted — no changes made."


def test_summary_with_changes():
    env = {"Z": "1", "A": "2", "M": "3"}
    result = sort(env)
    msg = summary(result)
    assert "Sorted" in msg
    assert "alphabetical order" in msg


def test_original_env_not_mutated():
    env = {"Z": "1", "A": "2"}
    original_keys = list(env.keys())
    sort(env)
    assert list(env.keys()) == original_keys

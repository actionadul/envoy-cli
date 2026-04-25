"""Tests for envoy.normalizer."""

import pytest
from envoy.normalizer import normalize, has_changes, summary


def test_normalize_uppercases_keys():
    result = normalize({"foo": "bar", "baz": "qux"}, uppercase_keys=True)
    assert "FOO" in result.normalized
    assert "BAZ" in result.normalized


def test_normalize_uppercase_records_change():
    result = normalize({"foo": "bar"}, uppercase_keys=True)
    assert any("uppercased" in c for c in result.changes)


def test_normalize_skips_uppercase_when_disabled():
    result = normalize({"foo": "bar"}, uppercase_keys=False)
    assert "foo" in result.normalized
    assert not any("uppercased" in c for c in result.changes)


def test_normalize_strips_value_whitespace():
    result = normalize({"KEY": "  value  "}, strip_values=True)
    assert result.normalized["KEY"] == "value"


def test_normalize_strip_records_change():
    result = normalize({"KEY": "  value  "}, strip_values=True)
    assert any("whitespace" in c for c in result.changes)


def test_normalize_skips_strip_when_disabled():
    result = normalize({"KEY": "  value  "}, strip_values=False)
    assert result.normalized["KEY"] == "  value  "


def test_normalize_sorts_keys():
    result = normalize({"ZEBRA": "1", "ALPHA": "2"}, sort_keys=True, uppercase_keys=False)
    assert list(result.normalized.keys()) == ["ALPHA", "ZEBRA"]


def test_normalize_sort_records_change_when_order_differs():
    result = normalize({"ZEBRA": "1", "ALPHA": "2"}, sort_keys=True, uppercase_keys=False)
    assert any("sorted" in c for c in result.changes)


def test_normalize_removes_empty_values_when_flag_set():
    result = normalize({"KEY": "", "OTHER": "val"}, remove_empty=True, uppercase_keys=False)
    assert "KEY" not in result.normalized
    assert "OTHER" in result.normalized


def test_normalize_remove_empty_records_change():
    result = normalize({"KEY": ""}, remove_empty=True, uppercase_keys=False)
    assert any("removed" in c for c in result.changes)


def test_normalize_keeps_empty_values_by_default():
    result = normalize({"KEY": ""}, uppercase_keys=False)
    assert "KEY" in result.normalized


def test_normalize_applies_prefix():
    result = normalize({"KEY": "val"}, prefix="APP_", uppercase_keys=False, sort_keys=False)
    assert "APP_KEY" in result.normalized


def test_normalize_prefix_skips_already_prefixed():
    result = normalize({"APP_KEY": "val"}, prefix="APP_", uppercase_keys=False, sort_keys=False)
    assert "APP_KEY" in result.normalized
    assert "APP_APP_KEY" not in result.normalized


def test_has_changes_true_when_changes_present():
    result = normalize({"foo": "bar"}, uppercase_keys=True)
    assert has_changes(result)


def test_has_changes_false_when_already_normalized():
    result = normalize({"FOO": "bar"}, uppercase_keys=True, strip_values=True, sort_keys=False)
    assert not has_changes(result)


def test_summary_no_changes():
    result = normalize({"FOO": "bar"}, uppercase_keys=True, strip_values=True, sort_keys=False)
    assert summary(result) == "No normalization changes."


def test_summary_lists_changes():
    result = normalize({"foo": "bar"}, uppercase_keys=True, sort_keys=False)
    text = summary(result)
    assert "1 change(s) applied" in text
    assert "uppercased" in text


def test_original_is_not_mutated():
    original = {"foo": "  value  "}
    normalize(original, strip_values=True)
    assert original["foo"] == "  value  "

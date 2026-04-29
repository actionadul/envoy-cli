"""Tests for envoy.caster."""

import pytest

from envoy.caster import (
    CastResult,
    cast,
    has_changes,
    has_errors,
    summary,
)


def test_cast_int_value():
    result = cast({"PORT": "8080"}, {"PORT": "int"})
    assert result.casted["PORT"] == 8080
    assert isinstance(result.casted["PORT"], int)


def test_cast_float_value():
    result = cast({"RATIO": "0.75"}, {"RATIO": "float"})
    assert result.casted["RATIO"] == pytest.approx(0.75)


def test_cast_bool_true_variants():
    for raw in ("1", "true", "True", "TRUE", "yes", "on"):
        result = cast({"FLAG": raw}, {"FLAG": "bool"})
        assert result.casted["FLAG"] is True, f"expected True for {raw!r}"


def test_cast_bool_false_variants():
    for raw in ("0", "false", "False", "FALSE", "no", "off"):
        result = cast({"FLAG": raw}, {"FLAG": "bool"})
        assert result.casted["FLAG"] is False, f"expected False for {raw!r}"


def test_cast_str_passthrough():
    result = cast({"NAME": "alice"}, {"NAME": "str"})
    assert result.casted["NAME"] == "alice"


def test_cast_records_changed_key():
    result = cast({"PORT": "9000"}, {"PORT": "int"})
    assert "PORT" in result.changed


def test_cast_unchanged_str_not_recorded():
    result = cast({"NAME": "alice"}, {"NAME": "str"})
    assert "NAME" not in result.changed


def test_cast_missing_key_skipped():
    result = cast({"A": "1"}, {"B": "int"})
    assert "B" not in result.casted
    assert result.errors == []


def test_cast_invalid_int_records_error():
    result = cast({"PORT": "abc"}, {"PORT": "int"})
    assert has_errors(result)
    assert any("PORT" in e for e in result.errors)


def test_cast_invalid_bool_records_error():
    result = cast({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert has_errors(result)
    assert any("FLAG" in e for e in result.errors)


def test_cast_unknown_type_records_error():
    result = cast({"X": "val"}, {"X": "list"})
    assert has_errors(result)


def test_has_changes_true():
    result = cast({"N": "42"}, {"N": "int"})
    assert has_changes(result)


def test_has_changes_false():
    result = cast({"N": "hello"}, {"N": "str"})
    assert not has_changes(result)


def test_has_errors_false_on_clean():
    result = cast({"N": "3"}, {"N": "int"})
    assert not has_errors(result)


def test_summary_with_changes():
    result = cast({"PORT": "80", "RATIO": "0.5"}, {"PORT": "int", "RATIO": "float"})
    s = summary(result)
    assert "2 key(s) casted" in s


def test_summary_no_changes():
    result = cast({"NAME": "bob"}, {"NAME": "str"})
    assert summary(result) == "no changes"


def test_summary_with_errors():
    result = cast({"PORT": "bad"}, {"PORT": "int"})
    s = summary(result)
    assert "error" in s


def test_original_env_not_mutated():
    env = {"PORT": "8080"}
    cast(env, {"PORT": "int"})
    assert env["PORT"] == "8080"

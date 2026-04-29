"""Tests for envoy.coercer."""

import pytest
from envoy.coercer import coerce, has_changes, has_errors, summary


# ---------------------------------------------------------------------------
# bool coercion
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["true", "True", "TRUE", "yes", "Yes", "1", "on", "ON"])
def test_coerce_bool_truthy_variants(raw):
    result = coerce({"FLAG": raw}, {"FLAG": "bool"})
    assert result.env["FLAG"] == "true"


@pytest.mark.parametrize("raw", ["false", "False", "FALSE", "no", "No", "0", "off", "OFF"])
def test_coerce_bool_falsy_variants(raw):
    result = coerce({"FLAG": raw}, {"FLAG": "bool"})
    assert result.env["FLAG"] == "false"


def test_coerce_bool_already_canonical_not_recorded():
    result = coerce({"FLAG": "true"}, {"FLAG": "bool"})
    assert not has_changes(result)


def test_coerce_bool_invalid_records_error():
    result = coerce({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert has_errors(result)
    assert result.errors[0][0] == "FLAG"
    assert result.env["FLAG"] == "maybe"  # original preserved


# ---------------------------------------------------------------------------
# int coercion
# ---------------------------------------------------------------------------

def test_coerce_int_plain_integer():
    result = coerce({"PORT": "8080"}, {"PORT": "int"})
    assert result.env["PORT"] == "8080"
    assert not has_changes(result)  # already canonical


def test_coerce_int_from_float_string():
    result = coerce({"COUNT": "3.0"}, {"COUNT": "int"})
    assert result.env["COUNT"] == "3"
    assert has_changes(result)


def test_coerce_int_invalid_records_error():
    result = coerce({"X": "abc"}, {"X": "int"})
    assert has_errors(result)
    assert result.env["X"] == "abc"


# ---------------------------------------------------------------------------
# float coercion
# ---------------------------------------------------------------------------

def test_coerce_float_plain():
    result = coerce({"RATIO": "0.5"}, {"RATIO": "float"})
    assert result.env["RATIO"] == "0.5"


def test_coerce_float_integer_string_normalised():
    result = coerce({"RATIO": "1"}, {"RATIO": "float"})
    assert result.env["RATIO"] == "1.0"
    assert has_changes(result)


def test_coerce_float_invalid_records_error():
    result = coerce({"R": "bad"}, {"R": "float"})
    assert has_errors(result)


# ---------------------------------------------------------------------------
# str passthrough
# ---------------------------------------------------------------------------

def test_coerce_str_passthrough():
    result = coerce({"NAME": "hello"}, {"NAME": "str"})
    assert result.env["NAME"] == "hello"
    assert not has_changes(result)


# ---------------------------------------------------------------------------
# unknown type
# ---------------------------------------------------------------------------

def test_coerce_unknown_type_records_error():
    result = coerce({"X": "val"}, {"X": "uuid"})
    assert has_errors(result)


# ---------------------------------------------------------------------------
# key not present
# ---------------------------------------------------------------------------

def test_coerce_missing_key_silently_skipped():
    result = coerce({"A": "1"}, {"MISSING": "int"})
    assert result.env == {"A": "1"}
    assert not has_changes(result)
    assert not has_errors(result)


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    result = coerce({"A": "hello"}, {"A": "str"})
    assert summary(result) == "no changes"


def test_summary_with_changes():
    result = coerce({"FLAG": "yes", "COUNT": "3.0"}, {"FLAG": "bool", "COUNT": "int"})
    assert "2 value(s) coerced" in summary(result)


def test_summary_with_errors():
    result = coerce({"X": "bad"}, {"X": "int"})
    assert "1 error(s)" in summary(result)

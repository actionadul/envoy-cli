"""Tests for envoy.interpolator."""

import pytest
from envoy.interpolator import interpolate, InterpolationResult, _extract_refs


def test_extract_refs_brace_syntax():
    refs = _extract_refs("${HOST}:${PORT}")
    assert refs == ["HOST", "PORT"]


def test_extract_refs_dollar_syntax():
    refs = _extract_refs("$HOST:$PORT")
    assert refs == ["HOST", "PORT"]


def test_extract_refs_no_refs():
    assert _extract_refs("plain-value") == []


def test_interpolate_literal_values():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = interpolate(env)
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["PORT"] == "5432"
    assert result.unresolved_keys == []


def test_interpolate_single_reference():
    env = {"HOST": "localhost", "DB_HOST": "${HOST}"}
    result = interpolate(env)
    assert result.resolved["DB_HOST"] == "localhost"


def test_interpolate_multiple_references():
    env = {"HOST": "db", "PORT": "5432", "DSN": "postgres://${HOST}:${PORT}/mydb"}
    result = interpolate(env)
    assert result.resolved["DSN"] == "postgres://db:5432/mydb"


def test_interpolate_chained_references():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate(env)
    assert result.resolved["C"] == "hello_world!"


def test_interpolate_unresolved_external_ref():
    env = {"URL": "${UNDEFINED_VAR}/path"}
    result = interpolate(env)
    # Unresolved refs are left as-is in the value
    assert "${UNDEFINED_VAR}" in result.resolved["URL"]


def test_interpolate_returns_interpolation_result():
    result = interpolate({"KEY": "value"})
    assert isinstance(result, InterpolationResult)


def test_interpolate_dollar_syntax_resolved():
    env = {"NAME": "world", "GREETING": "hello $NAME"}
    result = interpolate(env)
    assert result.resolved["GREETING"] == "hello world"


def test_interpolate_empty_env():
    result = interpolate({})
    assert result.resolved == {}
    assert result.unresolved_keys == []
    assert result.cycles == []


def test_interpolate_self_reference_does_not_crash():
    env = {"A": "${A}"}
    # Should not raise; cycle or unresolved handling returns gracefully
    result = interpolate(env)
    assert "A" in result.resolved or "A" in result.unresolved_keys

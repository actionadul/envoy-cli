"""Tests for envoy.differ_matrix."""
import pytest
from envoy.differ_matrix import (
    MatrixCell,
    MatrixReport,
    build_matrix,
    format_matrix,
)


ENV_A = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "8080", "SECRET": "abc"}
ENV_C = {"HOST": "staging.example.com", "PORT": "9090"}


def test_build_matrix_returns_matrix_report():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert isinstance(result, MatrixReport)


def test_build_matrix_targets_are_sorted():
    result = build_matrix({"z": ENV_A, "a": ENV_B})
    assert result.targets == ["a", "z"]


def test_build_matrix_keys_are_sorted():
    result = build_matrix({"a": {"Z": "1", "A": "2"}})
    assert result.keys == ["A", "Z"]


def test_build_matrix_all_keys_collected():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert set(result.keys) == {"HOST", "PORT", "DEBUG", "SECRET"}


def test_build_matrix_cell_present_when_key_exists():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert result.cells["HOST"]["a"].present is True
    assert result.cells["HOST"]["b"].present is True


def test_build_matrix_cell_absent_when_key_missing():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert result.cells["SECRET"]["a"].present is False
    assert result.cells["DEBUG"]["b"].present is False


def test_build_matrix_cell_value_correct():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert result.cells["HOST"]["a"].value == "localhost"
    assert result.cells["HOST"]["b"].value == "prod.example.com"


def test_build_matrix_cell_value_none_when_absent():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert result.cells["SECRET"]["a"].value is None


def test_unanimous_keys_same_value_all_targets():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    # PORT is "8080" in both
    assert "PORT" in result.unanimous_keys


def test_divergent_keys_different_values():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert "HOST" in result.divergent_keys


def test_divergent_keys_missing_in_some_target():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert "DEBUG" in result.divergent_keys
    assert "SECRET" in result.divergent_keys


def test_empty_envs_returns_empty_report():
    result = build_matrix({"a": {}, "b": {}})
    assert result.keys == []
    assert result.unanimous_keys == []
    assert result.divergent_keys == []


def test_format_matrix_returns_string():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    output = format_matrix(result)
    assert isinstance(output, str)


def test_format_matrix_contains_target_names():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    output = format_matrix(result)
    assert "a" in output
    assert "b" in output


def test_format_matrix_contains_key_names():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    output = format_matrix(result)
    assert "HOST" in output
    assert "PORT" in output


def test_format_matrix_empty_returns_placeholder():
    result = build_matrix({"a": {}, "b": {}})
    output = format_matrix(result)
    assert "(no keys)" in output

"""Tests for envoy.linter."""

import pytest
from envoy.linter import lint_env, LintResult, LintIssue


def _make_lines(*lines):
    return [l + "\n" for l in lines]


def test_lint_clean_env_no_issues():
    env = {"APP_ENV": "production", "PORT": "8080"}
    lines = _make_lines("APP_ENV=production", "PORT=8080")
    result = lint_env("prod", env, lines)
    assert isinstance(result, LintResult)
    assert result.issues == []
    assert result.summary() == "prod: OK"


def test_lint_detects_trailing_whitespace():
    env = {"KEY": "val"}
    lines = _make_lines("KEY=val   ")
    result = lint_env("dev", env, lines)
    assert any(i.rule == "no_trailing_whitespace" for i in result.issues)


def test_lint_trailing_whitespace_line_number():
    env = {"A": "1", "B": "2"}
    lines = _make_lines("A=1", "B=2   ")
    result = lint_env("dev", env, lines)
    issue = next(i for i in result.issues if i.rule == "no_trailing_whitespace")
    assert issue.line == 2


def test_lint_detects_duplicate_keys():
    env = {"KEY": "second"}
    lines = _make_lines("KEY=first", "KEY=second")
    result = lint_env("dev", env, lines)
    dup = next((i for i in result.issues if i.rule == "no_duplicate_keys"), None)
    assert dup is not None
    assert dup.severity == "error"
    assert "KEY" in dup.message


def test_lint_duplicate_key_references_first_line():
    env = {"KEY": "b"}
    lines = _make_lines("KEY=a", "KEY=b")
    result = lint_env("dev", env, lines)
    issue = next(i for i in result.issues if i.rule == "no_duplicate_keys")
    assert "line 1" in issue.message


def test_lint_detects_unsorted_keys():
    env = {"Z_KEY": "1", "A_KEY": "2"}
    lines = _make_lines("Z_KEY=1", "A_KEY=2")
    result = lint_env("dev", env, lines)
    assert any(i.rule == "sorted_keys" for i in result.issues)


def test_lint_sorted_keys_no_issue():
    env = {"A_KEY": "1", "Z_KEY": "2"}
    lines = _make_lines("A_KEY=1", "Z_KEY=2")
    result = lint_env("dev", env, lines)
    assert not any(i.rule == "sorted_keys" for i in result.issues)


def test_lint_empty_env_warns():
    result = lint_env("empty", {}, [])
    assert any(i.rule == "no_empty_file" for i in result.issues)


def test_lint_has_errors_true():
    env = {"KEY": "b"}
    lines = _make_lines("KEY=a", "KEY=b")
    result = lint_env("dev", env, lines)
    assert result.has_errors() is True


def test_lint_has_warnings_true():
    env = {"Z": "1", "A": "2"}
    lines = _make_lines("Z=1", "A=2")
    result = lint_env("dev", env, lines)
    assert result.has_warnings() is True


def test_lint_summary_counts():
    env = {"KEY": "b", "Z": "1", "A": "2"}
    lines = _make_lines("KEY=a", "KEY=b", "Z=1", "A=2")
    result = lint_env("dev", env, lines)
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_lint_ignores_comment_lines_for_duplicate_check():
    env = {"KEY": "val"}
    lines = _make_lines("# KEY=comment", "KEY=val")
    result = lint_env("dev", env, lines)
    assert not any(i.rule == "no_duplicate_keys" for i in result.issues)

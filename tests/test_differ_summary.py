"""Tests for envoy.differ_summary module."""

import pytest

from envoy.differ import DiffResult
from envoy.differ_summary import (
    MultiDiffReport,
    TargetDiff,
    build_report,
    format_report,
)


BASE = {"APP_NAME": "myapp", "DEBUG": "false", "PORT": "8080"}


# --- build_report ---

def test_build_report_returns_multi_diff_report():
    report = build_report(BASE, {})
    assert isinstance(report, MultiDiffReport)


def test_build_report_creates_entry_per_target():
    targets = {
        "staging": {"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080"},
        "production": {"APP_NAME": "myapp", "DEBUG": "false", "PORT": "443"},
    }
    report = build_report(BASE, targets)
    assert len(report.diffs) == 2
    assert {td.target for td in report.diffs} == {"staging", "production"}


def test_build_report_detects_changed_keys():
    targets = {"staging": {"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080"}}
    report = build_report(BASE, targets)
    assert "DEBUG" in report.diffs[0].result.changed


def test_build_report_detects_added_keys():
    targets = {"staging": {**BASE, "NEW_KEY": "hello"}}
    report = build_report(BASE, targets)
    assert "NEW_KEY" in report.diffs[0].result.added


def test_build_report_detects_removed_keys():
    targets = {"staging": {"APP_NAME": "myapp"}}
    report = build_report(BASE, targets)
    assert "DEBUG" in report.diffs[0].result.removed
    assert "PORT" in report.diffs[0].result.removed


# --- MultiDiffReport properties ---

def _make_report(*pairs):
    diffs = [TargetDiff(target=name, result=result) for name, result in pairs]
    return MultiDiffReport(diffs=diffs)


def test_targets_with_differences():
    r_changed = DiffResult(added={}, removed={}, changed={"X": ("a", "b")}, unchanged={})
    r_clean = DiffResult(added={}, removed={}, changed={}, unchanged={"Y": "1"})
    report = _make_report(("staging", r_changed), ("prod", r_clean))
    assert report.targets_with_differences == ["staging"]
    assert report.targets_clean == ["prod"]


def test_has_any_differences_true():
    r = DiffResult(added={"K": "v"}, removed={}, changed={}, unchanged={})
    report = _make_report(("staging", r))
    assert report.has_any_differences() is True


def test_has_any_differences_false():
    r = DiffResult(added={}, removed={}, changed={}, unchanged={"K": "v"})
    report = _make_report(("staging", r))
    assert report.has_any_differences() is False


def test_totals_aggregated():
    r1 = DiffResult(added={"A": "1"}, removed={"B": "2"}, changed={"C": ("x", "y")}, unchanged={})
    r2 = DiffResult(added={"D": "3", "E": "4"}, removed={}, changed={}, unchanged={})
    report = _make_report(("t1", r1), ("t2", r2))
    assert report.total_added == 3
    assert report.total_removed == 1
    assert report.total_changed == 1


# --- format_report ---

def test_format_report_shows_clean_targets():
    r = DiffResult(added={}, removed={}, changed={}, unchanged={"K": "v"})
    report = _make_report(("prod", r))
    output = format_report(report)
    assert "[CLEAN] prod" in output


def test_format_report_shows_changed_targets():
    r = DiffResult(added={"NEW": "val"}, removed={}, changed={}, unchanged={})
    report = _make_report(("staging", r))
    output = format_report(report)
    assert "[CHANGED] staging" in output


def test_format_report_verbose_shows_added_key():
    r = DiffResult(added={"NEW_KEY": "val"}, removed={}, changed={}, unchanged={})
    report = _make_report(("staging", r))
    output = format_report(report, verbose=True)
    assert "+ NEW_KEY" in output


def test_format_report_verbose_shows_removed_key():
    r = DiffResult(added={}, removed={"OLD_KEY": "x"}, changed={}, unchanged={})
    report = _make_report(("staging", r))
    output = format_report(report, verbose=True)
    assert "- OLD_KEY" in output


def test_format_report_includes_summary_line():
    r = DiffResult(added={}, removed={}, changed={}, unchanged={})
    report = _make_report(("prod", r))
    output = format_report(report)
    assert "Summary:" in output

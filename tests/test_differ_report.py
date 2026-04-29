"""Tests for envoy.differ_report."""

import pytest

from envoy.differ_summary import MultiDiffReport, TargetDiff
from envoy.differ_report import (
    ReportLine,
    build_report_lines,
    format_report,
    _status_label,
)


def _make_diff(target, added=0, removed=0, changed=0, unchanged=0):
    return TargetDiff(
        target=target,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
    )


def _make_report(*diffs):
    return MultiDiffReport(diffs=list(diffs))


def test_status_label_clean():
    diff = _make_diff("prod", added=0, removed=0, changed=0)
    assert _status_label(diff) == "clean"


def test_status_label_added_only():
    diff = _make_diff("prod", added=3)
    assert _status_label(diff) == "+3"


def test_status_label_removed_only():
    diff = _make_diff("prod", removed=2)
    assert _status_label(diff) == "-2"


def test_status_label_changed_only():
    diff = _make_diff("prod", changed=1)
    assert _status_label(diff) == "~1"


def test_status_label_mixed():
    diff = _make_diff("prod", added=1, removed=2, changed=3)
    assert _status_label(diff) == "+1 -2 ~3"


def test_build_report_lines_returns_one_per_diff():
    report = _make_report(
        _make_diff("staging", added=1),
        _make_diff("prod", changed=2),
    )
    lines = build_report_lines(report)
    assert len(lines) == 2


def test_build_report_lines_correct_target_name():
    report = _make_report(_make_diff("staging", added=1))
    lines = build_report_lines(report)
    assert lines[0].target == "staging"


def test_build_report_lines_correct_counts():
    report = _make_report(_make_diff("dev", added=2, removed=1, changed=3))
    line = build_report_lines(report)[0]
    assert line.added == 2
    assert line.removed == 1
    assert line.changed == 3


def test_format_report_empty():
    report = _make_report()
    result = format_report(report)
    assert result == "No targets found."


def test_format_report_contains_header():
    report = _make_report(_make_diff("prod"))
    result = format_report(report)
    assert "TARGET" in result
    assert "STATUS" in result


def test_format_report_contains_target_name():
    report = _make_report(_make_diff("production", added=1))
    result = format_report(report)
    assert "production" in result


def test_format_report_summary_line_counts_diffs():
    report = _make_report(
        _make_diff("staging", added=1),
        _make_diff("prod"),
    )
    result = format_report(report)
    assert "1 target(s) with differences" in result
    assert "1 clean" in result


def test_format_report_all_clean():
    report = _make_report(_make_diff("dev"), _make_diff("prod"))
    result = format_report(report)
    assert "0 target(s) with differences" in result
    assert "2 clean" in result

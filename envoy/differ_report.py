"""Generates a formatted multi-target diff report for display."""

from dataclasses import dataclass
from typing import List

from envoy.differ_summary import MultiDiffReport, TargetDiff


@dataclass
class ReportLine:
    target: str
    status: str
    added: int
    removed: int
    changed: int


def _status_label(diff: TargetDiff) -> str:
    if diff.added == 0 and diff.removed == 0 and diff.changed == 0:
        return "clean"
    parts = []
    if diff.added:
        parts.append(f"+{diff.added}")
    if diff.removed:
        parts.append(f"-{diff.removed}")
    if diff.changed:
        parts.append(f"~{diff.changed}")
    return " ".join(parts)


def build_report_lines(report: MultiDiffReport) -> List[ReportLine]:
    """Convert a MultiDiffReport into a list of ReportLines."""
    lines = []
    for diff in report.diffs:
        lines.append(
            ReportLine(
                target=diff.target,
                status=_status_label(diff),
                added=diff.added,
                removed=diff.removed,
                changed=diff.changed,
            )
        )
    return lines


def format_report(report: MultiDiffReport, *, color: bool = False) -> str:
    """Render a MultiDiffReport as a human-readable string table."""
    lines = build_report_lines(report)
    if not lines:
        return "No targets found."

    col_target = max(len(r.target) for r in lines)
    col_status = max(len(r.status) for r in lines)
    col_target = max(col_target, len("TARGET"))
    col_status = max(col_status, len("STATUS"))

    header = f"{'TARGET':<{col_target}}  {'STATUS':<{col_status}}"
    separator = "-" * len(header)
    rows = [header, separator]
    for r in lines:
        row = f"{r.target:<{col_target}}  {r.status:<{col_status}}"
        rows.append(row)

    total_diffs = sum(1 for r in lines if r.status != "clean")
    rows.append(separator)
    rows.append(f"{total_diffs} target(s) with differences, {len(lines) - total_diffs} clean.")
    return "\n".join(rows)

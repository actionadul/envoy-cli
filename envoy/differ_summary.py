"""Generates a human-readable grouped summary report from multiple DiffResults."""

from dataclasses import dataclass, field
from typing import Dict, List

from envoy.differ import DiffResult


@dataclass
class TargetDiff:
    target: str
    result: DiffResult


@dataclass
class MultiDiffReport:
    diffs: List[TargetDiff] = field(default_factory=list)

    @property
    def targets_with_differences(self) -> List[str]:
        return [td.target for td in self.diffs if td.result.added or td.result.removed or td.result.changed]

    @property
    def targets_clean(self) -> List[str]:
        return [td.target for td in self.diffs if not (td.result.added or td.result.removed or td.result.changed)]

    @property
    def total_added(self) -> int:
        return sum(len(td.result.added) for td in self.diffs)

    @property
    def total_removed(self) -> int:
        return sum(len(td.result.removed) for td in self.diffs)

    @property
    def total_changed(self) -> int:
        return sum(len(td.result.changed) for td in self.diffs)

    def has_any_differences(self) -> bool:
        return bool(self.targets_with_differences)

    def get_diff_for_target(self, target: str) -> TargetDiff:
        """Return the TargetDiff for the given target name.

        Raises KeyError if the target is not found in the report.
        """
        for td in self.diffs:
            if td.target == target:
                return td
        raise KeyError(f"Target {target!r} not found in report")


def build_report(base: Dict[str, str], targets: Dict[str, Dict[str, str]]) -> MultiDiffReport:
    """Build a MultiDiffReport comparing base env against each named target env."""
    from envoy.differ import diff_envs

    report = MultiDiffReport()
    for target_name, target_env in targets.items():
        result = diff_envs(base, target_env)
        report.diffs.append(TargetDiff(target=target_name, result=result))
    return report


def format_report(report: MultiDiffReport, verbose: bool = False) -> str:
    """Render a MultiDiffReport as a formatted string."""
    lines = []
    for td in report.diffs:
        r = td.result
        has_diff = r.added or r.removed or r.changed
        status = "CHANGED" if has_diff else "CLEAN"
        lines.append(f"[{status}] {td.target}")
        if verbose and has_diff:
            for k in sorted(r.added):
                lines.append(f"  + {k}")
            for k in sorted(r.removed):
                lines.append(f"  - {k}")
            for k in sorted(r.changed):
                old, new = r.changed[k]
                lines.append(f"  ~ {k}: {old!r} -> {new!r}")
    lines.append("")
    lines.append(
        f"Summary: {len(report.targets_with_differences)} changed, "
        f"{len(report.targets_clean)} clean "
        f"(+{report.total_added} added, -{report.total_removed} removed, ~{report.total_changed} changed)"
    )
    return "\n".join(lines)

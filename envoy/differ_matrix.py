"""Build a key-by-target matrix from multiple env targets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class MatrixCell:
    value: Optional[str]
    present: bool


@dataclass
class MatrixReport:
    targets: List[str]
    keys: List[str]
    cells: Dict[str, Dict[str, MatrixCell]]  # cells[key][target]
    unanimous_keys: List[str]
    divergent_keys: List[str]


def build_matrix(envs: Dict[str, Dict[str, str]]) -> MatrixReport:
    """Build a matrix of key presence/values across all targets."""
    targets: List[str] = sorted(envs.keys())
    all_keys: Set[str] = set()
    for env in envs.values():
        all_keys.update(env.keys())
    keys: List[str] = sorted(all_keys)

    cells: Dict[str, Dict[str, MatrixCell]] = {}
    for key in keys:
        cells[key] = {}
        for target in targets:
            value = envs[target].get(key)
            cells[key][target] = MatrixCell(value=value, present=key in envs[target])

    unanimous_keys: List[str] = []
    divergent_keys: List[str] = []
    for key in keys:
        values = {cells[key][t].value for t in targets if cells[key][t].present}
        present_count = sum(1 for t in targets if cells[key][t].present)
        if present_count == len(targets) and len(values) == 1:
            unanimous_keys.append(key)
        else:
            divergent_keys.append(key)

    return MatrixReport(
        targets=targets,
        keys=keys,
        cells=cells,
        unanimous_keys=unanimous_keys,
        divergent_keys=divergent_keys,
    )


def format_matrix(report: MatrixReport, show_values: bool = False) -> str:
    """Render the matrix as a plain-text table."""
    if not report.keys:
        return "(no keys)"

    col_width = max(len(t) for t in report.targets) + 2
    key_width = max(len(k) for k in report.keys) + 2

    header = f"{'KEY':<{key_width}}" + "".join(f"{t:^{col_width}}" for t in report.targets)
    separator = "-" * len(header)
    lines = [header, separator]

    for key in report.keys:
        row = f"{key:<{key_width}}"
        for target in report.targets:
            cell = report.cells[key][target]
            if not cell.present:
                symbol = "-"
            elif show_values:
                symbol = (cell.value or "")[:col_width - 2]
            else:
                symbol = "✓"
            row += f"{symbol:^{col_width}}"
        lines.append(row)

    return "\n".join(lines)

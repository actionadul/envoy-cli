"""Diff utilities for comparing environment variable sets."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set


@dataclass
class DiffResult:
    """Result of comparing two environment variable sets."""

    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        if self.added:
            lines.append(f"+{len(self.added)} added")
        if self.removed:
            lines.append(f"-{len(self.removed)} removed")
        if self.changed:
            lines.append(f"~{len(self.changed)} changed")
        if not lines:
            return "No differences found."
        return ", ".join(lines)


def diff_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    ignore_keys: Optional[Set[str]] = None,
) -> DiffResult:
    """Compare two environment variable dictionaries.

    Args:
        base: The baseline environment variables.
        target: The target environment variables to compare against.
        ignore_keys: Optional set of keys to exclude from the diff.

    Returns:
        A DiffResult describing the differences.
    """
    ignore_keys = ignore_keys or set()

    base_filtered = {k: v for k, v in base.items() if k not in ignore_keys}
    target_filtered = {k: v for k, v in target.items() if k not in ignore_keys}

    base_keys = set(base_filtered.keys())
    target_keys = set(target_filtered.keys())

    result = DiffResult()

    for key in target_keys - base_keys:
        result.added[key] = target_filtered[key]

    for key in base_keys - target_keys:
        result.removed[key] = base_filtered[key]

    for key in base_keys & target_keys:
        if base_filtered[key] != target_filtered[key]:
            result.changed[key] = (base_filtered[key], target_filtered[key])
        else:
            result.unchanged[key] = base_filtered[key]

    return result


def format_diff(result: DiffResult, show_values: bool = True) -> str:
    """Format a DiffResult as a human-readable string."""
    lines = []

    for key, value in sorted(result.added.items()):
        lines.append(f"+ {key}{'=' + value if show_values else ''}")

    for key, value in sorted(result.removed.items()):
        lines.append(f"- {key}{'=' + value if show_values else ''}")

    for key, (old, new) in sorted(result.changed.items()):
        if show_values:
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        else:
            lines.append(f"~ {key}")

    return "\n".join(lines) if lines else "(no differences)"

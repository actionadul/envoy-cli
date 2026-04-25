"""Template rendering for env files — substitute placeholders from a context dict."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class TemplateResult:
    rendered: Dict[str, str] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    substitutions: int = 0


def _render_value(value: str, context: Dict[str, str]) -> tuple[str, List[str], int]:
    """Return (rendered_value, missing_keys, substitution_count)."""
    missing: List[str] = []
    count = 0

    def replacer(match: re.Match) -> str:
        nonlocal count
        key = match.group(1)
        if key in context:
            count += 1
            return context[key]
        missing.append(key)
        return match.group(0)

    rendered = _PLACEHOLDER_RE.sub(replacer, value)
    return rendered, missing, count


def render(
    env: Dict[str, str],
    context: Dict[str, str],
    strict: bool = False,
) -> TemplateResult:
    """Render all values in *env* using *context* for placeholder substitution.

    If *strict* is True, raises KeyError on the first unresolved placeholder.
    """
    result = TemplateResult()

    for k, v in env.items():
        rendered, missing, count = _render_value(v, context)
        if missing and strict:
            raise KeyError(
                f"Unresolved placeholder(s) in key '{k}': {missing}"
            )
        result.missing.extend(missing)
        result.substitutions += count
        result.rendered[k] = rendered

    # Deduplicate missing list while preserving order
    seen: set = set()
    deduped: List[str] = []
    for m in result.missing:
        if m not in seen:
            seen.add(m)
            deduped.append(m)
    result.missing = deduped

    return result


def summary(result: TemplateResult) -> str:
    """Return a human-readable summary of a TemplateResult."""
    lines = [f"Substitutions made: {result.substitutions}"]
    if result.missing:
        lines.append(f"Unresolved placeholders: {', '.join(result.missing)}")
    else:
        lines.append("All placeholders resolved.")
    return "\n".join(lines)

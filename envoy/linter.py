"""Lint environment variable files for style and consistency issues."""

from dataclasses import dataclass, field
from typing import Dict, List

LINT_RULES = [
    "no_trailing_whitespace",
    "no_duplicate_keys",
    "sorted_keys",
    "no_empty_file",
]


@dataclass
class LintIssue:
    rule: str
    line: int | None
    message: str
    severity: str = "warning"  # "warning" | "error"


@dataclass
class LintResult:
    target: str
    issues: List[LintIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        if not self.issues:
            return f"{self.target}: OK"
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        parts = []
        if errors:
            parts.append(f"{errors} error(s)")
        if warnings:
            parts.append(f"{warnings} warning(s)")
        return f"{self.target}: " + ", ".join(parts)


def lint_env(target: str, env: Dict[str, str], raw_lines: List[str]) -> LintResult:
    """Run all lint rules against a parsed env and its raw source lines."""
    result = LintResult(target=target)

    if not env:
        result.issues.append(
            LintIssue(rule="no_empty_file", line=None, message="File contains no key-value pairs.", severity="warning")
        )

    seen_keys: Dict[str, int] = {}
    for lineno, raw in enumerate(raw_lines, start=1):
        stripped = raw.rstrip("\n")

        if stripped != stripped.rstrip():
            result.issues.append(
                LintIssue(
                    rule="no_trailing_whitespace",
                    line=lineno,
                    message=f"Line {lineno} has trailing whitespace.",
                    severity="warning",
                )
            )

        if "=" in stripped and not stripped.lstrip().startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if key in seen_keys:
                result.issues.append(
                    LintIssue(
                        rule="no_duplicate_keys",
                        line=lineno,
                        message=f"Duplicate key '{key}' (first seen on line {seen_keys[key]}).",
                        severity="error",
                    )
                )
            else:
                seen_keys[key] = lineno

    keys = list(env.keys())
    if keys != sorted(keys):
        result.issues.append(
            LintIssue(
                rule="sorted_keys",
                line=None,
                message="Keys are not in alphabetical order.",
                severity="warning",
            )
        )

    return result

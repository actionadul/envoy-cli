"""Auditor module: checks env files for common issues and policy violations."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AuditIssue:
    key: str
    severity: str  # 'error' | 'warning' | 'info'
    message: str


@dataclass
class AuditResult:
    target: str
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        return f"{self.target}: {errors} error(s), {warnings} warning(s)"


SECRET_PATTERNS = ("password", "secret", "token", "api_key", "private_key")


def audit_env(
    target: str,
    env: Dict[str, str],
    required_keys: List[str] | None = None,
) -> AuditResult:
    """Run audit checks against an env dict and return an AuditResult."""
    result = AuditResult(target=target)

    for key, value in env.items():
        # Blank value warning
        if value == "":
            result.issues.append(
                AuditIssue(key=key, severity="warning", message="Value is blank")
            )

        # Plaintext secret detection
        lower_key = key.lower()
        if any(pattern in lower_key for pattern in SECRET_PATTERNS):
            if value and not value.startswith("${"):
                result.issues.append(
                    AuditIssue(
                        key=key,
                        severity="error",
                        message="Possible plaintext secret detected",
                    )
                )

        # Key naming convention
        if key != key.upper():
            result.issues.append(
                AuditIssue(
                    key=key,
                    severity="warning",
                    message="Key is not uppercase",
                )
            )

    # Required keys check
    for req in required_keys or []:
        if req not in env:
            result.issues.append(
                AuditIssue(
                    key=req,
                    severity="error",
                    message="Required key is missing",
                )
            )

    return result

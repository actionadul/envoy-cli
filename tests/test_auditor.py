"""Tests for envoy.auditor."""

import pytest
from envoy.auditor import AuditIssue, AuditResult, audit_env


def test_audit_clean_env_no_issues():
    env = {"APP_HOST": "localhost", "APP_PORT": "8080"}
    result = audit_env("production", env)
    assert result.issues == []
    assert not result.has_errors
    assert not result.has_warnings


def test_audit_detects_blank_value():
    env = {"APP_HOST": ""}
    result = audit_env("staging", env)
    assert any(i.key == "APP_HOST" and i.severity == "warning" for i in result.issues)


def test_audit_detects_plaintext_secret():
    env = {"DB_PASSWORD": "supersecret"}
    result = audit_env("production", env)
    assert any(i.key == "DB_PASSWORD" and i.severity == "error" for i in result.issues)


def test_audit_skips_secret_with_variable_reference():
    env = {"DB_PASSWORD": "${VAULT_DB_PASS}"}
    result = audit_env("production", env)
    assert not any(i.key == "DB_PASSWORD" and i.severity == "error" for i in result.issues)


def test_audit_detects_lowercase_key():
    env = {"app_host": "localhost"}
    result = audit_env("dev", env)
    assert any(i.key == "app_host" and i.severity == "warning" for i in result.issues)


def test_audit_detects_missing_required_key():
    env = {"APP_HOST": "localhost"}
    result = audit_env("production", env, required_keys=["APP_HOST", "APP_SECRET_KEY"])
    assert any(
        i.key == "APP_SECRET_KEY" and i.severity == "error" for i in result.issues
    )


def test_audit_result_has_errors_true():
    result = AuditResult(target="production")
    result.issues.append(AuditIssue(key="X", severity="error", message="bad"))
    assert result.has_errors


def test_audit_result_has_warnings_true():
    result = AuditResult(target="staging")
    result.issues.append(AuditIssue(key="X", severity="warning", message="meh"))
    assert result.has_warnings
    assert not result.has_errors


def test_audit_result_summary_format():
    result = AuditResult(target="production")
    result.issues.append(AuditIssue(key="A", severity="error", message="e"))
    result.issues.append(AuditIssue(key="B", severity="warning", message="w"))
    assert result.summary() == "production: 1 error(s), 1 warning(s)"


def test_audit_multiple_issues_on_same_key():
    env = {"db_password": ""}
    result = audit_env("dev", env)
    keys_with_issues = [i.key for i in result.issues]
    assert keys_with_issues.count("db_password") >= 2

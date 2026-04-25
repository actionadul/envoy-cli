"""Integration tests: redactor + parser round-trip."""

from __future__ import annotations

from pathlib import Path

import pytest

from envoy.parser import parse_env_file, write_env_file
from envoy.redactor import redact, REDACTED_PLACEHOLDER


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / "production.env"
    p.write_text(
        "DB_PASSWORD=supersecret\n"
        "API_KEY=abc123\n"
        "APP_NAME=envoy\n"
        "PORT=8080\n"
    )
    return p


def test_round_trip_redact_and_parse(env_file, tmp_path):
    """Redacted env written to disk can be parsed back correctly."""
    env = parse_env_file(env_file)
    result = redact(env)

    out = tmp_path / "redacted.env"
    write_env_file(str(out), result.redacted)

    parsed_back = parse_env_file(out)
    assert parsed_back["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert parsed_back["API_KEY"] == REDACTED_PLACEHOLDER
    assert parsed_back["APP_NAME"] == "envoy"
    assert parsed_back["PORT"] == "8080"


def test_round_trip_preserves_all_keys(env_file, tmp_path):
    env = parse_env_file(env_file)
    result = redact(env)

    out = tmp_path / "redacted.env"
    write_env_file(str(out), result.redacted)

    parsed_back = parse_env_file(out)
    assert set(parsed_back.keys()) == set(env.keys())


def test_redact_does_not_mutate_original(env_file):
    env = parse_env_file(env_file)
    original_copy = dict(env)
    redact(env)
    assert env == original_copy

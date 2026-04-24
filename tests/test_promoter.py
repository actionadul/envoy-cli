"""Tests for envoy.promoter."""

import os
import pytest

from envoy.promoter import promote, summary


@pytest.fixture
def env_dir(tmp_path):
    return str(tmp_path)


def _write_target(env_dir, name, content):
    path = os.path.join(env_dir, f"{name}.env")
    with open(path, "w") as f:
        f.write(content)


def test_promote_copies_keys(env_dir):
    _write_target(env_dir, "staging", "FOO=bar\nBAZ=qux\n")
    _write_target(env_dir, "production", "FOO=old\n")

    result = promote(env_dir, "staging", "production", keys=["BAZ"], overwrite=False)

    assert "BAZ" in result.promoted
    assert result.promoted["BAZ"] == "qux"
    assert result.skipped == []


def test_promote_skips_existing_without_overwrite(env_dir):
    _write_target(env_dir, "staging", "FOO=new\n")
    _write_target(env_dir, "production", "FOO=old\n")

    result = promote(env_dir, "staging", "production", keys=["FOO"], overwrite=False)

    assert "FOO" not in result.promoted
    assert "FOO" in result.skipped


def test_promote_overwrites_when_flag_set(env_dir):
    _write_target(env_dir, "staging", "FOO=new\n")
    _write_target(env_dir, "production", "FOO=old\n")

    result = promote(env_dir, "staging", "production", keys=["FOO"], overwrite=True)

    assert "FOO" in result.promoted
    assert "FOO" in result.overwritten
    assert result.promoted["FOO"] == "new"


def test_promote_skips_missing_source_key(env_dir):
    _write_target(env_dir, "staging", "FOO=bar\n")
    _write_target(env_dir, "production", "")

    result = promote(env_dir, "staging", "production", keys=["MISSING"])

    assert "MISSING" in result.skipped
    assert "MISSING" not in result.promoted


def test_promote_all_keys_when_none_specified(env_dir):
    _write_target(env_dir, "staging", "A=1\nB=2\n")
    _write_target(env_dir, "production", "")

    result = promote(env_dir, "staging", "production", overwrite=False)

    assert set(result.promoted.keys()) == {"A", "B"}


def test_summary_returns_string(env_dir):
    _write_target(env_dir, "staging", "FOO=bar\n")
    _write_target(env_dir, "production", "")

    result = promote(env_dir, "staging", "production")
    out = summary(result)

    assert "staging" in out
    assert "production" in out
    assert "Promoted" in out

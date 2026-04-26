"""Tests for envoy.cloner."""

from __future__ import annotations

import os
import pytest

from envoy.cloner import clone, has_changes, summary
from envoy.parser import parse_env_file


@pytest.fixture()
def env_dir(tmp_path):
    return str(tmp_path)


def _write_target(env_dir: str, target: str, content: str) -> None:
    path = os.path.join(env_dir, f".env.{target}")
    with open(path, "w") as fh:
        fh.write(content)


# ---------------------------------------------------------------------------
# clone behaviour
# ---------------------------------------------------------------------------

def test_clone_copies_all_keys(env_dir):
    _write_target(env_dir, "staging", "APP=myapp\nDEBUG=true\n")
    result = clone(env_dir, "staging", "production")
    dest = parse_env_file(os.path.join(env_dir, ".env.production"))
    assert dest == {"APP": "myapp", "DEBUG": "true"}


def test_clone_result_keys_written(env_dir):
    _write_target(env_dir, "staging", "A=1\nB=2\n")
    result = clone(env_dir, "staging", "production")
    assert sorted(result.keys_written) == ["A", "B"]
    assert result.keys_skipped == []


def test_clone_has_changes_true(env_dir):
    _write_target(env_dir, "staging", "A=1\n")
    result = clone(env_dir, "staging", "production")
    assert has_changes(result) is True


def test_clone_with_include_filter(env_dir):
    _write_target(env_dir, "staging", "A=1\nB=2\nC=3\n")
    result = clone(env_dir, "staging", "production", include=["A", "C"])
    dest = parse_env_file(os.path.join(env_dir, ".env.production"))
    assert dest == {"A": "1", "C": "3"}
    assert "B" in result.keys_skipped


def test_clone_with_exclude_filter(env_dir):
    _write_target(env_dir, "staging", "A=1\nSECRET=abc\nB=2\n")
    result = clone(env_dir, "staging", "production", exclude=["SECRET"])
    dest = parse_env_file(os.path.join(env_dir, ".env.production"))
    assert "SECRET" not in dest
    assert dest["A"] == "1"
    assert "SECRET" in result.keys_skipped


def test_clone_raises_when_destination_exists_no_overwrite(env_dir):
    _write_target(env_dir, "staging", "A=1\n")
    _write_target(env_dir, "production", "A=old\n")
    with pytest.raises(FileExistsError):
        clone(env_dir, "staging", "production", overwrite=False)


def test_clone_overwrites_when_flag_set(env_dir):
    _write_target(env_dir, "staging", "A=new\n")
    _write_target(env_dir, "production", "A=old\n")
    result = clone(env_dir, "staging", "production", overwrite=True)
    dest = parse_env_file(os.path.join(env_dir, ".env.production"))
    assert dest["A"] == "new"
    assert result.already_existed is True


def test_clone_records_source_and_destination(env_dir):
    _write_target(env_dir, "staging", "A=1\n")
    result = clone(env_dir, "staging", "production")
    assert result.source == "staging"
    assert result.destination == "production"


def test_summary_contains_key_count(env_dir):
    _write_target(env_dir, "staging", "A=1\nB=2\n")
    result = clone(env_dir, "staging", "production")
    s = summary(result)
    assert "2" in s
    assert "production" in s


def test_summary_mentions_overwrite(env_dir):
    _write_target(env_dir, "staging", "A=1\n")
    _write_target(env_dir, "production", "A=old\n")
    result = clone(env_dir, "staging", "production", overwrite=True)
    s = summary(result)
    assert "already existed" in s

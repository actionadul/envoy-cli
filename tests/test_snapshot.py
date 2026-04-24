"""Tests for envoy.snapshot module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy.snapshot import (
    Snapshot,
    list_snapshots,
    restore_snapshot,
    take_snapshot,
)


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_env(env_dir: Path, target: str, content: str) -> None:
    (env_dir / f"{target}.env").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# take_snapshot
# ---------------------------------------------------------------------------

def test_take_snapshot_returns_snapshot(env_dir):
    _write_env(env_dir, "staging", "APP_ENV=staging\nDEBUG=false\n")
    snap = take_snapshot(str(env_dir), "staging")
    assert isinstance(snap, Snapshot)
    assert snap.target == "staging"
    assert snap.env == {"APP_ENV": "staging", "DEBUG": "false"}
    assert snap.created_at.endswith("Z")


def test_take_snapshot_persists_json_file(env_dir):
    _write_env(env_dir, "prod", "SECRET=abc\n")
    snap = take_snapshot(str(env_dir), "prod", note="pre-deploy")
    snap_dir = env_dir / ".snapshots"
    files = list(snap_dir.glob("prod__*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["target"] == "prod"
    assert data["note"] == "pre-deploy"
    assert data["env"]["SECRET"] == "abc"


def test_take_snapshot_raises_when_target_missing(env_dir):
    with pytest.raises(FileNotFoundError, match="no-such-target"):
        take_snapshot(str(env_dir), "no-such-target")


# ---------------------------------------------------------------------------
# list_snapshots
# ---------------------------------------------------------------------------

def test_list_snapshots_empty_when_none_taken(env_dir):
    snaps = list_snapshots(str(env_dir))
    assert snaps == []


def test_list_snapshots_returns_all(env_dir):
    _write_env(env_dir, "dev", "X=1\n")
    _write_env(env_dir, "staging", "X=2\n")
    take_snapshot(str(env_dir), "dev")
    take_snapshot(str(env_dir), "staging")
    snaps = list_snapshots(str(env_dir))
    assert len(snaps) == 2


def test_list_snapshots_filtered_by_target(env_dir):
    _write_env(env_dir, "dev", "X=1\n")
    _write_env(env_dir, "staging", "X=2\n")
    take_snapshot(str(env_dir), "dev")
    take_snapshot(str(env_dir), "staging")
    snaps = list_snapshots(str(env_dir), target="dev")
    assert all(s.target == "dev" for s in snaps)
    assert len(snaps) == 1


# ---------------------------------------------------------------------------
# restore_snapshot
# ---------------------------------------------------------------------------

def test_restore_snapshot_overwrites_env_file(env_dir):
    _write_env(env_dir, "staging", "APP_ENV=staging\nVERSION=1\n")
    snap = take_snapshot(str(env_dir), "staging")

    # Mutate the env file after the snapshot
    _write_env(env_dir, "staging", "APP_ENV=staging\nVERSION=2\n")

    restored_path = restore_snapshot(str(env_dir), snap)
    content = Path(restored_path).read_text(encoding="utf-8")
    assert "VERSION=1" in content
    assert "VERSION=2" not in content

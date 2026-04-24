"""Tests for envoy.resolver."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.resolver import list_targets, resolve_target, resolve_all


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


@pytest.fixture()
def base_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("BASE_KEY=base_value\nSHARED=from_base\n")
    return p


def _write_target(env_dir: Path, target: str, content: str) -> Path:
    p = env_dir / f".env.{target}"
    p.write_text(content)
    return p


def test_list_targets_empty(env_dir: Path):
    assert list_targets(str(env_dir)) == []


def test_list_targets_returns_sorted(env_dir: Path):
    _write_target(env_dir, "staging", "")
    _write_target(env_dir, "production", "")
    _write_target(env_dir, "dev", "")
    assert list_targets(str(env_dir)) == ["dev", "production", "staging"]


def test_list_targets_ignores_non_env_files(env_dir: Path):
    (env_dir / "notes.txt").write_text("ignore me")
    _write_target(env_dir, "dev", "")
    assert list_targets(str(env_dir)) == ["dev"]


def test_list_targets_missing_dir():
    assert list_targets("/nonexistent/path") == []


def test_resolve_target_without_base(env_dir: Path):
    _write_target(env_dir, "dev", "APP_ENV=development\nPORT=3000\n")
    result = resolve_target("dev", env_dir=str(env_dir), base_file=None)
    assert result == {"APP_ENV": "development", "PORT": "3000"}


def test_resolve_target_merges_base(env_dir: Path, base_file: Path):
    _write_target(env_dir, "dev", "SHARED=from_dev\nAPP_ENV=development\n")
    result = resolve_target(
        "dev", env_dir=str(env_dir), base_file=str(base_file)
    )
    assert result["BASE_KEY"] == "base_value"
    assert result["SHARED"] == "from_dev"  # target overrides base
    assert result["APP_ENV"] == "development"


def test_resolve_target_raises_for_missing_target(env_dir: Path):
    with pytest.raises(FileNotFoundError, match="ghost"):
        resolve_target("ghost", env_dir=str(env_dir), base_file=None)


def test_resolve_all(env_dir: Path):
    _write_target(env_dir, "dev", "ENV=dev\n")
    _write_target(env_dir, "prod", "ENV=prod\n")
    result = resolve_all(env_dir=str(env_dir), base_file=None)
    assert set(result.keys()) == {"dev", "prod"}
    assert result["dev"]["ENV"] == "dev"
    assert result["prod"]["ENV"] == "prod"

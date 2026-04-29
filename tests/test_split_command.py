"""Tests for envoy.commands.split."""

import argparse
from pathlib import Path

import pytest

from envoy.commands.split import build_parser, run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_env(path: Path, content: str) -> None:
    path.write_text(content)


def _make_args(env_dir: Path, target: str, mappings: list, **kwargs) -> argparse.Namespace:
    defaults = {
        "env_dir": str(env_dir),
        "target": target,
        "mappings": mappings,
        "strip_prefix": False,
        "unmatched": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_parser_returns_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_parser(sub)
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    build_parser(sub)
    args = root.parse_args(["split", "prod", "--map", "db=DB_*"])
    assert args.strip_prefix is False
    assert args.dry_run is False
    assert args.unmatched is None
    assert args.env_dir == "envs"


def test_run_returns_error_when_target_missing(env_dir: Path):
    args = _make_args(env_dir, "missing", ["db=DB_*"])
    code = run(args)
    assert code == 1


def test_run_creates_bucket_files(env_dir: Path):
    _write_env(env_dir / "prod.env", "DB_HOST=localhost\nAPP_ENV=prod\n")
    args = _make_args(env_dir, "prod", ["db=DB_*"])
    code = run(args)
    assert code == 0
    assert (env_dir / "db.env").exists()


def test_run_bucket_file_contains_correct_keys(env_dir: Path):
    _write_env(env_dir / "prod.env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=prod\n")
    args = _make_args(env_dir, "prod", ["db=DB_*"])
    run(args)
    content = (env_dir / "db.env").read_text()
    assert "DB_HOST" in content
    assert "DB_PORT" in content
    assert "APP_ENV" not in content


def test_run_dry_run_does_not_write_files(env_dir: Path):
    _write_env(env_dir / "prod.env", "DB_HOST=localhost\n")
    args = _make_args(env_dir, "prod", ["db=DB_*"], dry_run=True)
    run(args)
    assert not (env_dir / "db.env").exists()


def test_run_strip_prefix_renames_keys(env_dir: Path):
    _write_env(env_dir / "prod.env", "DB_HOST=localhost\nDB_PORT=5432\n")
    args = _make_args(env_dir, "prod", ["db=DB_*"], strip_prefix=True)
    run(args)
    content = (env_dir / "db.env").read_text()
    assert "HOST" in content
    assert "DB_HOST" not in content


def test_run_unmatched_creates_extra_file(env_dir: Path):
    _write_env(env_dir / "prod.env", "DB_HOST=localhost\nAPP_ENV=prod\n")
    args = _make_args(env_dir, "prod", ["db=DB_*"], unmatched="rest")
    run(args)
    assert (env_dir / "rest.env").exists()
    content = (env_dir / "rest.env").read_text()
    assert "APP_ENV" in content

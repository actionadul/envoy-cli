"""Tests for envoy.commands.matrix."""
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.commands.matrix import build_parser, run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_env(env_dir: Path, name: str, content: str) -> None:
    (env_dir / f"{name}.env").write_text(content)


def _make_args(env_dir: Path, targets=None, values=False, divergent_only=False):
    ns = argparse.Namespace(
        env_dir=str(env_dir),
        targets=targets or [],
        values=values,
        divergent_only=divergent_only,
    )
    return ns


def test_build_parser_returns_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_parser(sub)
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_parser(sub)
    args = root.parse_args(["matrix"])
    assert args.env_dir == "envs"
    assert args.targets == []
    assert args.values is False
    assert args.divergent_only is False


def test_run_no_targets_returns_error(env_dir, capsys):
    args = _make_args(env_dir)
    code = run(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "No targets found" in captured.err


def test_run_unknown_target_returns_error(env_dir, capsys):
    _write_env(env_dir, "prod", "HOST=prod\n")
    args = _make_args(env_dir, targets=["staging"])
    code = run(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "Unknown targets" in captured.err


def test_run_prints_matrix(env_dir, capsys):
    _write_env(env_dir, "dev", "HOST=localhost\nPORT=8080\n")
    _write_env(env_dir, "prod", "HOST=prod.example.com\nPORT=8080\n")
    args = _make_args(env_dir)
    code = run(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "HOST" in captured.out
    assert "PORT" in captured.out


def test_run_shows_summary_line(env_dir, capsys):
    _write_env(env_dir, "dev", "HOST=localhost\nPORT=8080\n")
    _write_env(env_dir, "prod", "HOST=prod.example.com\nPORT=8080\n")
    args = _make_args(env_dir)
    run(args)
    captured = capsys.readouterr()
    assert "keys" in captured.out
    assert "divergent" in captured.out


def test_run_divergent_only_filters_unanimous(env_dir, capsys):
    _write_env(env_dir, "dev", "HOST=localhost\nPORT=8080\n")
    _write_env(env_dir, "prod", "HOST=prod.example.com\nPORT=8080\n")
    args = _make_args(env_dir, divergent_only=True)
    run(args)
    captured = capsys.readouterr()
    assert "HOST" in captured.out
    # PORT is unanimous so should not appear in key rows (may appear in header)
    lines = captured.out.splitlines()
    key_rows = [l for l in lines if l.startswith("PORT")]
    assert key_rows == []


def test_run_specific_targets(env_dir, capsys):
    _write_env(env_dir, "dev", "HOST=localhost\n")
    _write_env(env_dir, "prod", "HOST=prod.example.com\n")
    _write_env(env_dir, "staging", "HOST=staging.example.com\n")
    args = _make_args(env_dir, targets=["dev", "prod"])
    code = run(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "dev" in captured.out
    assert "prod" in captured.out

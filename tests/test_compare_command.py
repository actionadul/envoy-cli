"""Tests for the 'compare' CLI command."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.commands.compare import build_parser, run


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    build_parser(sub)
    return root


@pytest.fixture()
def env_setup(tmp_path: Path):
    env_dir = tmp_path / "envs"
    env_dir.mkdir()
    (env_dir / ".env.staging").write_text("APP=myapp\nDEBUG=true\n")
    (env_dir / ".env.production").write_text("APP=myapp\nDEBUG=false\nSECRET=xyz\n")
    return tmp_path, env_dir


def _make_args(target_a, target_b, env_dir, base=".env", no_base=True, exit_code=False):
    ns = argparse.Namespace(
        target_a=target_a,
        target_b=target_b,
        env_dir=env_dir,
        base=base,
        no_base=no_base,
        exit_code=exit_code,
    )
    return ns


def test_run_prints_diff(env_setup, capsys):
    _, env_dir = env_setup
    args = _make_args("staging", "production", str(env_dir))
    rc = run(args)
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert rc == 0


def test_run_exit_code_when_differences(env_setup):
    _, env_dir = env_setup
    args = _make_args("staging", "production", str(env_dir), exit_code=True)
    rc = run(args)
    assert rc == 1


def test_run_exit_code_zero_when_identical(env_setup):
    _, env_dir = env_setup
    args = _make_args("staging", "staging", str(env_dir), exit_code=True)
    rc = run(args)
    assert rc == 0


def test_run_returns_2_on_missing_target(env_setup, capsys):
    _, env_dir = env_setup
    args = _make_args("staging", "ghost", str(env_dir))
    rc = run(args)
    captured = capsys.readouterr()
    assert rc == 2
    assert "error" in captured.err


def test_run_returns_2_on_missing_env_dir(tmp_path, capsys):
    """run() should return 2 and print an error when env_dir does not exist."""
    missing_dir = tmp_path / "nonexistent"
    args = _make_args("staging", "production", str(missing_dir))
    rc = run(args)
    captured = capsys.readouterr()
    assert rc == 2
    assert "error" in captured.err


def test_parser_defaults(parser):
    args = parser.parse_args(["compare", "dev", "prod"])
    assert args.env_dir == "envs"
    assert args.base == ".env"
    assert args.no_base is False
    assert args.exit_code is False

"""Tests for envoy.commands.validate."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envoy.commands.validate import build_parser, run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _make_args(env_dir: Path, target: str, require: list[str] | None = None) -> argparse.Namespace:
    return argparse.Namespace(
        env_dir=str(env_dir),
        target=target,
        require=require or [],
    )


def _write_env(env_dir: Path, target: str, content: str) -> Path:
    p = env_dir / f"{target}.env"
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["staging"])
    assert args.target == "staging"
    assert args.env_dir == "envs"
    assert args.require == []


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def test_run_ok_no_required_keys(env_dir, capsys):
    _write_env(env_dir, "staging", "FOO=bar\nBAZ=qux\n")
    args = _make_args(env_dir, "staging")
    code = run(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "OK" in captured.out
    assert "2 key(s)" in captured.out


def test_run_ok_all_required_keys_present(env_dir, capsys):
    _write_env(env_dir, "staging", "FOO=bar\nBAZ=qux\n")
    args = _make_args(env_dir, "staging", require=["FOO", "BAZ"])
    code = run(args)
    assert code == 0


def test_run_missing_required_key(env_dir, capsys):
    _write_env(env_dir, "staging", "FOO=bar\n")
    args = _make_args(env_dir, "staging", require=["FOO", "MISSING_KEY"])
    code = run(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "MISSING_KEY" in captured.out
    assert "INVALID" in captured.out


def test_run_missing_target_file(env_dir, capsys):
    args = _make_args(env_dir, "nonexistent")
    code = run(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err


def test_run_multiple_missing_keys_reported(env_dir, capsys):
    _write_env(env_dir, "prod", "ONLY=this\n")
    args = _make_args(env_dir, "prod", require=["A", "B", "C"])
    code = run(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "3 missing" in captured.out

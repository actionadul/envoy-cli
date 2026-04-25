"""Tests for envoy.commands.redact."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pytest

from envoy.commands.redact import build_parser, run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_env(env_dir: Path, target: str, content: str) -> None:
    (env_dir / f"{target}.env").write_text(content)


def _make_args(env_dir: Path, target: str = "staging", **kwargs) -> argparse.Namespace:
    defaults = {
        "env_dir": str(env_dir),
        "target": target,
        "keys": None,
        "output": None,
        "placeholder": "***REDACTED***",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["production"])
    assert args.target == "production"
    assert args.env_dir == "envs"
    assert args.keys is None
    assert args.output is None
    assert args.placeholder == "***REDACTED***"


def test_run_prints_redacted_to_stdout(env_dir, capsys):
    _write_env(env_dir, "staging", "DB_PASSWORD=secret\nAPP_NAME=myapp\n")
    args = _make_args(env_dir)
    code = run(args)
    captured = capsys.readouterr()
    assert code == 0
    assert "***REDACTED***" in captured.out
    assert "myapp" in captured.out


def test_run_explicit_keys(env_dir, capsys):
    _write_env(env_dir, "staging", "APP_NAME=myapp\nPORT=8080\n")
    args = _make_args(env_dir, keys=["PORT"])
    code = run(args)
    captured = capsys.readouterr()
    assert code == 0
    assert "PORT=***REDACTED***" in captured.out
    assert "APP_NAME=myapp" in captured.out


def test_run_writes_output_file(env_dir, tmp_path, capsys):
    _write_env(env_dir, "staging", "API_KEY=abc123\nHOST=localhost\n")
    out_file = str(tmp_path / "out.env")
    args = _make_args(env_dir, output=out_file)
    code = run(args)
    assert code == 0
    content = Path(out_file).read_text()
    assert "***REDACTED***" in content
    assert "localhost" in content


def test_run_missing_target_returns_error(env_dir, capsys):
    args = _make_args(env_dir, target="nonexistent")
    code = run(args)
    captured = capsys.readouterr()
    assert code == 1
    assert "error" in captured.err


def test_run_custom_placeholder(env_dir, capsys):
    _write_env(env_dir, "staging", "DB_PASSWORD=hunter2\n")
    args = _make_args(env_dir, placeholder="<hidden>")
    code = run(args)
    captured = capsys.readouterr()
    assert "<hidden>" in captured.out

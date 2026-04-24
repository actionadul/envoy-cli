"""Tests for envoy.commands.lint."""

import argparse
import pytest
from pathlib import Path

from envoy.commands.lint import build_parser, run


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path / "envs"


def _write_env(env_dir: Path, target: str, content: str) -> None:
    env_dir.mkdir(parents=True, exist_ok=True)
    (env_dir / f"{target}.env").write_text(content)


def _make_args(env_dir, targets=None, strict=False):
    ns = argparse.Namespace(
        env_dir=str(env_dir),
        targets=targets or [],
        strict=strict,
    )
    return ns


def test_build_parser_returns_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_parser(sub)
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    build_parser(sub)
    args = root.parse_args(["lint"])
    assert args.env_dir == "envs"
    assert args.targets == []
    assert args.strict is False


def test_run_clean_file_exits_zero(env_dir, capsys):
    _write_env(env_dir, "prod", "APP_ENV=production\nPORT=8080\n")
    args = _make_args(env_dir, targets=["prod"])
    code = run(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "prod: OK" in out


def test_run_detects_trailing_whitespace(env_dir, capsys):
    _write_env(env_dir, "dev", "KEY=val   \n")
    args = _make_args(env_dir, targets=["dev"])
    code = run(args)
    assert code == 0  # warnings only, not strict
    out = capsys.readouterr().out
    assert "no_trailing_whitespace" in out


def test_run_strict_exits_nonzero_on_warning(env_dir):
    _write_env(env_dir, "dev", "KEY=val   \n")
    args = _make_args(env_dir, targets=["dev"], strict=True)
    code = run(args)
    assert code == 1


def test_run_exits_2_on_error(env_dir):
    _write_env(env_dir, "dev", "KEY=a\nKEY=b\n")
    args = _make_args(env_dir, targets=["dev"])
    code = run(args)
    assert code == 2


def test_run_missing_target_file_exits_nonzero(env_dir, capsys):
    env_dir.mkdir(parents=True, exist_ok=True)
    args = _make_args(env_dir, targets=["ghost"])
    code = run(args)
    assert code != 0


def test_run_lints_all_targets_when_none_specified(env_dir, capsys):
    _write_env(env_dir, "prod", "APP=1\n")
    _write_env(env_dir, "staging", "APP=2\n")
    args = _make_args(env_dir, targets=[])
    code = run(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_run_no_targets_found_exits_1(env_dir, capsys):
    env_dir.mkdir()
    args = _make_args(env_dir, targets=[])
    code = run(args)
    assert code == 1

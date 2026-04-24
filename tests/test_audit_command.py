"""Tests for envoy.commands.audit."""

import argparse
import os
import pytest
from unittest.mock import patch

from envoy.commands.audit import build_parser, run


@pytest.fixture
def env_dir(tmp_path):
    return str(tmp_path)


def _write_env(env_dir, target, content):
    path = os.path.join(env_dir, f"{target}.env")
    with open(path, "w") as f:
        f.write(content)


def _make_args(env_dir, targets=None, require=None, strict=False):
    return argparse.Namespace(
        env_dir=env_dir,
        targets=targets or [],
        require=require or [],
        strict=strict,
    )


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.env_dir == "envs"
    assert args.targets == []
    assert args.require == []
    assert args.strict is False


def test_run_ok_clean_env(env_dir, capsys):
    _write_env(env_dir, "production", "APP_HOST=localhost\nAPP_PORT=8080\n")
    args = _make_args(env_dir, targets=["production"])
    code = run(args)
    out = capsys.readouterr().out
    assert code == 0
    assert "OK" in out


def test_run_returns_2_on_error(env_dir, capsys):
    _write_env(env_dir, "production", "DB_PASSWORD=supersecret\n")
    args = _make_args(env_dir, targets=["production"])
    code = run(args)
    assert code == 2


def test_run_strict_returns_1_on_warning(env_dir, capsys):
    _write_env(env_dir, "staging", "APP_HOST=\n")
    args = _make_args(env_dir, targets=["staging"], strict=True)
    code = run(args)
    assert code == 1


def test_run_missing_required_key(env_dir, capsys):
    _write_env(env_dir, "production", "APP_HOST=localhost\n")
    args = _make_args(env_dir, targets=["production"], require=["APP_SECRET_KEY"])
    code = run(args)
    assert code == 2


def test_run_all_targets_when_none_specified(env_dir, capsys):
    _write_env(env_dir, "dev", "APP_HOST=localhost\n")
    _write_env(env_dir, "staging", "APP_HOST=staging.example.com\n")
    args = _make_args(env_dir)
    code = run(args)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "staging" in out


def test_run_no_targets_returns_1(env_dir, capsys):
    args = _make_args(env_dir)
    code = run(args)
    assert code == 1

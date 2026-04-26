"""Tests for envoy.commands.patch."""
import argparse
import os
import pytest

from envoy.commands.patch import build_parser, run
from envoy.parser import write_env_file


@pytest.fixture()
def env_dir(tmp_path):
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_target(env_dir, name, data):
    path = env_dir / f".env.{name}"
    write_env_file(str(path), data)
    return path


def _make_args(env_dir, target, sets=None, unsets=None, dry_run=False):
    return argparse.Namespace(
        target=target,
        sets=sets or [],
        unsets=unsets or [],
        dry_run=dry_run,
        env_dir=str(env_dir),
    )


def test_build_parser_returns_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_parser(sub)
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    build_parser(sub)
    ns = root.parse_args(["patch", "staging"])
    assert ns.sets == []
    assert ns.unsets == []
    assert ns.dry_run is False
    assert ns.env_dir == "envs"


def test_run_adds_key(env_dir):
    _write_target(env_dir, "staging", {"APP": "old"})
    args = _make_args(env_dir, "staging", sets=["NEW_KEY=hello"])
    code = run(args)
    assert code == 0
    from envoy.parser import parse_env_file
    result = parse_env_file(str(env_dir / ".env.staging"))
    assert result["NEW_KEY"] == "hello"


def test_run_updates_key(env_dir):
    _write_target(env_dir, "staging", {"PORT": "8080"})
    args = _make_args(env_dir, "staging", sets=["PORT=9090"])
    run(args)
    from envoy.parser import parse_env_file
    result = parse_env_file(str(env_dir / ".env.staging"))
    assert result["PORT"] == "9090"


def test_run_removes_key(env_dir):
    _write_target(env_dir, "staging", {"PORT": "8080", "DEBUG": "true"})
    args = _make_args(env_dir, "staging", unsets=["DEBUG"])
    run(args)
    from envoy.parser import parse_env_file
    result = parse_env_file(str(env_dir / ".env.staging"))
    assert "DEBUG" not in result


def test_run_dry_run_does_not_write(env_dir):
    _write_target(env_dir, "staging", {"A": "1"})
    args = _make_args(env_dir, "staging", sets=["B=2"], dry_run=True)
    run(args)
    from envoy.parser import parse_env_file
    result = parse_env_file(str(env_dir / ".env.staging"))
    assert "B" not in result


def test_run_missing_target_returns_1(env_dir):
    args = _make_args(env_dir, "nonexistent", sets=["X=1"])
    assert run(args) == 1


def test_run_invalid_set_format_returns_1(env_dir):
    _write_target(env_dir, "staging", {"A": "1"})
    args = _make_args(env_dir, "staging", sets=["BADFORMAT"])
    assert run(args) == 1


def test_run_no_changes_prints_message(env_dir, capsys):
    _write_target(env_dir, "staging", {"A": "1"})
    args = _make_args(env_dir, "staging")
    code = run(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "No changes" in out

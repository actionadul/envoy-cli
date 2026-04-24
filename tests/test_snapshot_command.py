"""Tests for envoy/commands/snapshot.py."""

import argparse
import json
from io import StringIO
from pathlib import Path

import pytest

from envoy.commands.snapshot import build_parser, run


@pytest.fixture()
def env_dir(tmp_path):
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_env(env_dir, target, content):
    (env_dir / f"{target}.env").write_text(content)


def _make_args(env_dir, snapshot_cmd, target, label=None):
    ns = argparse.Namespace(
        snapshot_cmd=snapshot_cmd,
        target=target,
        env_dir=str(env_dir),
        label=label,
    )
    return ns


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    # ensure take sub-command exists with defaults
    args = parser.parse_args(["take", "staging"])
    assert args.target == "staging"
    assert args.env_dir == "envs"
    assert args.label is None


def test_run_take_creates_snapshot(env_dir):
    _write_env(env_dir, "staging", "APP_ENV=staging\nDEBUG=false\n")
    out = StringIO()
    args = _make_args(env_dir, "take", "staging")
    code = run(args, stdout=out)
    assert code == 0
    output = out.getvalue()
    assert "Snapshot taken" in output
    assert "keys   : 2" in output


def test_run_take_with_label(env_dir):
    _write_env(env_dir, "prod", "APP_ENV=prod\n")
    out = StringIO()
    args = _make_args(env_dir, "take", "prod", label="pre-release")
    code = run(args, stdout=out)
    assert code == 0
    assert "pre-release" in out.getvalue()


def test_run_take_missing_target_returns_error(env_dir):
    err = StringIO()
    args = _make_args(env_dir, "take", "ghost")
    code = run(args, stderr=err)
    assert code == 1
    assert "error" in err.getvalue().lower()


def test_run_list_no_snapshots(env_dir):
    _write_env(env_dir, "staging", "KEY=val\n")
    out = StringIO()
    args = _make_args(env_dir, "list", "staging")
    code = run(args, stdout=out)
    assert code == 0
    assert "No snapshots" in out.getvalue()


def test_run_list_shows_snapshots(env_dir):
    _write_env(env_dir, "staging", "KEY=val\n")
    take_args = _make_args(env_dir, "take", "staging", label="v1")
    run(take_args, stdout=StringIO())

    out = StringIO()
    list_args = _make_args(env_dir, "list", "staging")
    code = run(list_args, stdout=out)
    assert code == 0
    output = out.getvalue()
    assert "staging" in output
    assert "v1" in output


def test_run_no_subcommand_returns_error(env_dir):
    err = StringIO()
    args = argparse.Namespace(
        snapshot_cmd=None,
        target="staging",
        env_dir=str(env_dir),
        label=None,
    )
    code = run(args, stderr=err)
    assert code == 1
    assert "sub-command" in err.getvalue()

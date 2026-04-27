"""Tests for envoy.commands.tag."""
import argparse
import json
from pathlib import Path

import pytest

from envoy.commands.tag import build_parser, run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_env(env_dir: Path, target: str, content: str) -> Path:
    p = env_dir / f"{target}.env"
    p.write_text(content)
    return p


def _make_args(env_dir: Path, target: str, add=None, remove=None, list_tags=False):
    ns = argparse.Namespace(
        env_dir=str(env_dir),
        target=target,
        add=add or [],
        remove=remove or [],
        list_tags=list_tags,
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
    args = root.parse_args(["tag", "staging"])
    assert args.env_dir == "envs"
    assert args.add == []
    assert args.remove == []
    assert args.list_tags is False


def test_run_adds_tag_and_saves(env_dir: Path, capsys):
    _write_env(env_dir, "prod", "DB_PASS=secret\n")
    args = _make_args(env_dir, "prod", add=["DB_PASS:sensitive"])
    code = run(args)
    assert code == 0
    tags_file = env_dir / "prod.tags.json"
    assert tags_file.exists()
    data = json.loads(tags_file.read_text())
    assert "sensitive" in data["DB_PASS"]


def test_run_prints_summary(env_dir: Path, capsys):
    _write_env(env_dir, "prod", "APP_ENV=prod\n")
    args = _make_args(env_dir, "prod", add=["APP_ENV:deploy"])
    run(args)
    out = capsys.readouterr().out
    assert "added" in out


def test_run_remove_tag(env_dir: Path):
    _write_env(env_dir, "prod", "DB_PASS=secret\n")
    tags_file = env_dir / "prod.tags.json"
    tags_file.write_text(json.dumps({"DB_PASS": ["sensitive"]}))
    args = _make_args(env_dir, "prod", remove=["DB_PASS:sensitive"])
    run(args)
    data = json.loads(tags_file.read_text())
    assert "DB_PASS" not in data


def test_run_list_tags(env_dir: Path, capsys):
    _write_env(env_dir, "prod", "DB_PASS=secret\n")
    tags_file = env_dir / "prod.tags.json"
    tags_file.write_text(json.dumps({"DB_PASS": ["sensitive"]}))
    args = _make_args(env_dir, "prod", list_tags=True)
    code = run(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_PASS" in out
    assert "sensitive" in out


def test_run_list_tags_empty(env_dir: Path, capsys):
    _write_env(env_dir, "prod", "KEY=val\n")
    args = _make_args(env_dir, "prod", list_tags=True)
    run(args)
    out = capsys.readouterr().out
    assert "no tags" in out


def test_run_no_changes_message(env_dir: Path, capsys):
    _write_env(env_dir, "prod", "KEY=val\n")
    args = _make_args(env_dir, "prod")
    run(args)
    out = capsys.readouterr().out
    assert "no tag changes" in out

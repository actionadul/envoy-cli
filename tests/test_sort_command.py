import argparse
import pytest
from pathlib import Path

from envoy.commands.sort import build_parser, run


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def _write_env(path: Path, content: str):
    path.write_text(content)


def _make_args(file, reverse=False, dry_run=False, check=False):
    return argparse.Namespace(file=str(file), reverse=reverse, dry_run=dry_run, check=check)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["some.env"])
    assert args.reverse is False
    assert args.dry_run is False
    assert args.check is False


def test_run_sorts_file(env_dir):
    env_file = env_dir / "test.env"
    _write_env(env_file, "ZEBRA=1\nAPPLE=2\nMIDDLE=3\n")
    args = _make_args(env_file)
    code = run(args)
    assert code == 0
    content = env_file.read_text()
    keys = [line.split("=")[0] for line in content.splitlines() if "=" in line]
    assert keys == sorted(keys)


def test_run_dry_run_does_not_write(env_dir):
    env_file = env_dir / "test.env"
    original = "ZEBRA=1\nAPPLE=2\n"
    _write_env(env_file, original)
    args = _make_args(env_file, dry_run=True)
    run(args)
    assert env_file.read_text() == original


def test_run_check_returns_1_when_unsorted(env_dir):
    env_file = env_dir / "test.env"
    _write_env(env_file, "ZEBRA=1\nAPPLE=2\n")
    args = _make_args(env_file, check=True)
    code = run(args)
    assert code == 1


def test_run_check_returns_0_when_sorted(env_dir):
    env_file = env_dir / "test.env"
    _write_env(env_file, "APPLE=2\nZEBRA=1\n")
    args = _make_args(env_file, check=True)
    code = run(args)
    assert code == 0


def test_run_reverse_sort(env_dir):
    env_file = env_dir / "test.env"
    _write_env(env_file, "APPLE=2\nMIDDLE=3\nZEBRA=1\n")
    args = _make_args(env_file, reverse=True)
    run(args)
    content = env_file.read_text()
    keys = [line.split("=")[0] for line in content.splitlines() if "=" in line]
    assert keys == sorted(keys, reverse=True)


def test_run_missing_file_returns_1(env_dir):
    args = _make_args(env_dir / "nonexistent.env")
    code = run(args)
    assert code == 1

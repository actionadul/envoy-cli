"""Tests for the list command."""

import os
import pytest
from io import StringIO

from envoy.commands.list import build_parser, run


@pytest.fixture()
def env_dir(tmp_path):
    return tmp_path


def _make_env_file(env_dir, name, content):
    path = os.path.join(env_dir, "{}.env".format(name))
    with open(path, "w") as fh:
        fh.write(content)
    return path


def _make_args(env_dir, show_keys=False, quiet=False):
    parser = build_parser()
    argv = [str(env_dir)]
    if show_keys:
        argv.append("--show-keys")
    if quiet:
        argv.append("--quiet")
    return parser.parse_args(argv)


def test_build_parser_returns_parser(env_dir):
    parser = build_parser()
    assert parser is not None


def test_build_parser_defaults(env_dir):
    args = _make_args(env_dir)
    assert args.show_keys is False
    assert args.quiet is False


def test_run_lists_targets(env_dir):
    _make_env_file(env_dir, "production", "APP=prod\n")
    _make_env_file(env_dir, "staging", "APP=staging\n")
    out = StringIO()
    args = _make_args(env_dir)
    code = run(args, stdout=out)
    output = out.getvalue()
    assert code == 0
    assert "production" in output
    assert "staging" in output


def test_run_empty_dir_returns_nonzero(env_dir):
    out = StringIO()
    err = StringIO()
    args = _make_args(env_dir)
    code = run(args, stdout=out, stderr=err)
    assert code == 1
    assert "No targets found" in err.getvalue()


def test_run_quiet_mode(env_dir):
    _make_env_file(env_dir, "dev", "X=1\n")
    _make_env_file(env_dir, "prod", "X=2\n")
    out = StringIO()
    args = _make_args(env_dir, quiet=True)
    code = run(args, stdout=out)
    lines = out.getvalue().strip().splitlines()
    assert code == 0
    assert lines == ["dev", "prod"]


def test_run_show_keys(env_dir):
    _make_env_file(env_dir, "staging", "A=1\nB=2\nC=3\n")
    out = StringIO()
    args = _make_args(env_dir, show_keys=True)
    code = run(args, stdout=out)
    output = out.getvalue()
    assert code == 0
    assert "staging" in output
    assert "3 keys" in output


def test_run_targets_sorted(env_dir):
    _make_env_file(env_dir, "zebra", "Z=1\n")
    _make_env_file(env_dir, "alpha", "A=1\n")
    out = StringIO()
    args = _make_args(env_dir, quiet=True)
    run(args, stdout=out)
    lines = out.getvalue().strip().splitlines()
    assert lines == ["alpha", "zebra"]

"""Integration tests: patcher + parser round-trip."""
import pytest
from envoy.patcher import patch
from envoy.parser import parse_env_file, write_env_file


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env.test"
    p.write_text("APP_ENV=production\nDEBUG=false\nPORT=8080\n")
    return p


def test_round_trip_set_and_parse(env_file):
    env = parse_env_file(str(env_file))
    result = patch(env, sets=[("DEBUG", "true"), ("NEW", "val")])
    write_env_file(str(env_file), result.patched)
    reloaded = parse_env_file(str(env_file))
    assert reloaded["DEBUG"] == "true"
    assert reloaded["NEW"] == "val"
    assert reloaded["APP_ENV"] == "production"


def test_round_trip_unset_and_parse(env_file):
    env = parse_env_file(str(env_file))
    result = patch(env, unsets=["PORT"])
    write_env_file(str(env_file), result.patched)
    reloaded = parse_env_file(str(env_file))
    assert "PORT" not in reloaded
    assert len(reloaded) == 2


def test_patch_does_not_mutate_parsed_dict(env_file):
    env = parse_env_file(str(env_file))
    original_copy = dict(env)
    patch(env, sets=[("X", "y")], unsets=["PORT"])
    assert env == original_copy

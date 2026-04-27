"""CLI command: tag — add or remove metadata tags on env keys."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from envoy.resolver import resolve_target
from envoy.tagger import has_changes, summary, tag

_TAGS_SUFFIX = ".tags.json"


def _tags_path(env_path: Path) -> Path:
    return env_path.with_suffix("").with_suffix(_TAGS_SUFFIX)


def _load_tags(path: Path) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_tags(path: Path, tags: Dict[str, List[str]]) -> None:
    path.write_text(json.dumps(tags, indent=2, sort_keys=True))


def build_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser("tag", help="add or remove metadata tags on env keys")
    p.add_argument("target", help="deployment target name")
    p.add_argument("--dir", dest="env_dir", default="envs", help="env file directory (default: envs)")
    p.add_argument("--add", dest="add", metavar="KEY:TAG", nargs="+", default=[],
                   help="add a tag to a key, e.g. DB_PASS:sensitive")
    p.add_argument("--remove", dest="remove", metavar="KEY:TAG", nargs="+", default=[],
                   help="remove a tag from a key")
    p.add_argument("--list", dest="list_tags", action="store_true",
                   help="list current tags and exit")
    return p


def _parse_pairs(items: List[str]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for item in items:
        if ":" not in item:
            print(f"[error] invalid format '{item}', expected KEY:TAG", file=sys.stderr)
            sys.exit(2)
        key, _, label = item.partition(":")
        mapping.setdefault(key.strip(), []).append(label.strip())
    return mapping


def run(args: argparse.Namespace) -> int:
    env_path = resolve_target(args.env_dir, args.target)
    tags_path = _tags_path(env_path)
    existing = _load_tags(tags_path)

    if args.list_tags:
        if not existing:
            print("no tags defined")
        for key, labels in sorted(existing.items()):
            print(f"{key}: {', '.join(labels)}")
        return 0

    from envoy.parser import parse_env_file
    env = parse_env_file(str(env_path))

    add_map = _parse_pairs(args.add)
    remove_map = _parse_pairs(args.remove)

    result = tag(env, existing_tags=existing, add=add_map, remove=remove_map)

    if has_changes(result):
        _save_tags(tags_path, result.tags)
        print(summary(result))
    else:
        print("no tag changes")

    return 0

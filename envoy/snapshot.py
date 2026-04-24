"""Snapshot module: capture and restore environment variable sets at a point in time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from envoy.parser import parse_env_file, write_env_file


@dataclass
class Snapshot:
    target: str
    created_at: str
    env: Dict[str, str]
    note: Optional[str] = None


def _snapshot_dir(base_dir: str) -> Path:
    path = Path(base_dir) / ".snapshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _snapshot_filename(target: str, timestamp: str) -> str:
    safe_ts = timestamp.replace(":", "-").replace(" ", "T")
    return f"{target}__{safe_ts}.json"


def take_snapshot(
    base_dir: str,
    target: str,
    note: Optional[str] = None,
) -> Snapshot:
    """Read the current env file for *target* and persist a snapshot."""
    env_path = Path(base_dir) / f"{target}.env"
    if not env_path.exists():
        raise FileNotFoundError(f"No env file found for target '{target}' in {base_dir}")

    env = parse_env_file(str(env_path))
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    snapshot = Snapshot(target=target, created_at=created_at, env=env, note=note)

    snap_dir = _snapshot_dir(base_dir)
    filename = _snapshot_filename(target, created_at)
    snap_path = snap_dir / filename

    with open(snap_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "target": snapshot.target,
                "created_at": snapshot.created_at,
                "note": snapshot.note,
                "env": snapshot.env,
            },
            fh,
            indent=2,
        )

    return snapshot


def list_snapshots(base_dir: str, target: Optional[str] = None) -> List[Snapshot]:
    """Return all snapshots, optionally filtered by *target*, sorted by creation time."""
    snap_dir = _snapshot_dir(base_dir)
    snapshots: List[Snapshot] = []

    for snap_file in sorted(snap_dir.glob("*.json")):
        with open(snap_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if target and data["target"] != target:
            continue
        snapshots.append(
            Snapshot(
                target=data["target"],
                created_at=data["created_at"],
                env=data["env"],
                note=data.get("note"),
            )
        )

    return snapshots


def restore_snapshot(base_dir: str, snapshot: Snapshot) -> str:
    """Write the snapshot env back to the target's env file. Returns the file path."""
    env_path = str(Path(base_dir) / f"{snapshot.target}.env")
    write_env_file(env_path, snapshot.env)
    return env_path

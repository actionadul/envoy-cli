"""snapshot command — take and list snapshots of environment targets."""

import argparse
import sys
from pathlib import Path

from envoy.snapshot import take_snapshot, list_snapshots, load_snapshot


def build_parser(subparsers=None):
    description = "Take or list snapshots of an environment target."
    if subparsers is not None:
        parser = subparsers.add_parser("snapshot", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy snapshot", description=description)

    sub = parser.add_subparsers(dest="snapshot_cmd")

    # take sub-command
    take_p = sub.add_parser("take", help="Capture a snapshot of a target.")
    take_p.add_argument("target", help="Target name (e.g. staging).")
    take_p.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing .env files (default: envs).",
    )
    take_p.add_argument(
        "--label",
        default=None,
        metavar="LABEL",
        help="Optional label to attach to the snapshot.",
    )

    # list sub-command
    list_p = sub.add_parser("list", help="List existing snapshots for a target.")
    list_p.add_argument("target", help="Target name.")
    list_p.add_argument(
        "--env-dir",
        default="envs",
        metavar="DIR",
        help="Directory containing .env files (default: envs).",
    )

    return parser


def run(args, stdout=None, stderr=None):
    import sys

    out = stdout or sys.stdout
    err = stderr or sys.stderr

    if not args.snapshot_cmd:
        err.write("error: specify a sub-command: take | list\n")
        return 1

    env_dir = Path(args.env_dir)

    if args.snapshot_cmd == "take":
        try:
            snap = take_snapshot(
                env_dir=env_dir,
                target=args.target,
                label=getattr(args, "label", None),
            )
        except FileNotFoundError as exc:
            err.write(f"error: {exc}\n")
            return 1
        out.write(f"Snapshot taken: {snap.filename}\n")
        out.write(f"  target : {snap.target}\n")
        out.write(f"  keys   : {len(snap.env)}\n")
        if snap.label:
            out.write(f"  label  : {snap.label}\n")
        return 0

    if args.snapshot_cmd == "list":
        snapshots = list_snapshots(env_dir=env_dir, target=args.target)
        if not snapshots:
            out.write(f"No snapshots found for target '{args.target}'.\n")
            return 0
        out.write(f"Snapshots for '{args.target}':\n")
        for snap in snapshots:
            label_part = f"  [{snap.label}]" if snap.label else ""
            out.write(f"  {snap.filename}{label_part}\n")
        return 0

    err.write(f"error: unknown sub-command '{args.snapshot_cmd}'\n")
    return 1

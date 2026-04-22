"""Schema migration for Sensei learner data files.

Upgrades learner state files (profile.yaml, goal files) from older schema
versions to the current version. Each migration is a function that transforms
the data dict in place.

Usage (library):
    from sensei.engine.scripts.migrate import migrate_profile, migrate_goal

Usage (CLI):
    python -m sensei.engine.scripts.migrate --file learner/profile.yaml --type profile
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)

from sensei.engine.scripts._atomic import atomic_write_text

# Current schema versions (must match *.schema.json const values)
CURRENT_PROFILE_VERSION = 0
CURRENT_GOAL_VERSION = 0

# Migration registries: version -> function that upgrades FROM that version.
#
# Contract: each registered function must be PURE — accept a dict, return a
# new dict without mutating the input. This keeps a partially-failed
# migration chain from leaving the caller's dict in a half-transformed
# state (the outer loop only rebinds its local reference on success).
PROFILE_MIGRATIONS: dict[int, Any] = {
    # Example for future use:
    # 0: _migrate_profile_0_to_1,
}

GOAL_MIGRATIONS: dict[int, Any] = {
    # Example for future use:
    # 0: _migrate_goal_0_to_1,
}


def migrate_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate a profile dict to the current schema version. Returns the migrated dict.

    Migration functions in PROFILE_MIGRATIONS must be pure: they accept a
    dict and return a new dict. The caller's input is not mutated on a
    partial-failure path.
    """
    version = data.get("schema_version", 0)
    while version < CURRENT_PROFILE_VERSION:
        fn = PROFILE_MIGRATIONS.get(version)
        if fn is None:
            raise ValueError(f"No migration path from profile schema_version {version}")
        data = fn(data)
        version += 1
        data["schema_version"] = version
    return data


def migrate_goal(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate a goal dict to the current schema version. Returns the migrated dict.

    Migration functions in GOAL_MIGRATIONS must be pure: they accept a
    dict and return a new dict. The caller's input is not mutated on a
    partial-failure path.
    """
    version = data.get("schema_version", 0)
    while version < CURRENT_GOAL_VERSION:
        fn = GOAL_MIGRATIONS.get(version)
        if fn is None:
            raise ValueError(f"No migration path from goal schema_version {version}")
        data = fn(data)
        version += 1
        data["schema_version"] = version
    return data


def migrate_file(path: Path, file_type: str) -> bool:
    """Migrate a YAML file in place. Returns True if migration was applied."""
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if data is None:
        return False

    old_version = data.get("schema_version", 0)

    if file_type == "profile":
        data = migrate_profile(data)
        target = CURRENT_PROFILE_VERSION
    elif file_type == "goal":
        data = migrate_goal(data)
        target = CURRENT_GOAL_VERSION
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    if old_version == target:
        return False

    atomic_write_text(path, yaml.safe_dump(data, default_flow_style=False, sort_keys=False))
    return True


def migrate_instance(learner_dir: Path) -> list[str]:
    """Migrate all learner data files. Returns list of migrated file descriptions."""
    migrated: list[str] = []

    # Rename instance/ → learner/ if the old directory name is still in use.
    old_dir = learner_dir.parent / "instance"
    if old_dir.exists() and not learner_dir.exists():
        os.rename(old_dir, learner_dir)
        print("Renamed instance/ → learner/ (learner data preserved)")
        migrated.append("instance/ → learner/ (directory renamed)")

    profile = learner_dir / "profile.yaml"
    if profile.exists() and migrate_file(profile, "profile"):
        migrated.append(f"profile.yaml: schema_version → {CURRENT_PROFILE_VERSION}")

    # Migrate goal files (future: when goal workspaces exist)
    for goal_file in learner_dir.glob("goals/*/goal.yaml"):
        if migrate_file(goal_file, "goal"):
            migrated.append(f"{goal_file.relative_to(learner_dir)}: schema_version → {CURRENT_GOAL_VERSION}")

    return migrated


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Migrate Sensei learner data files")
    parser.add_argument("--file", type=Path, help="Single file to migrate")
    parser.add_argument("--type", choices=["profile", "goal"], help="File type (required with --file)")
    parser.add_argument("--instance", type=Path, help="Learner data directory to migrate all files")
    args = parser.parse_args(argv)

    if args.file:
        if not args.type:
            parser.error("--type required with --file")
        migrated = migrate_file(args.file, args.type)
        result: dict[str, Any] = {"file": str(args.file), "migrated": migrated}
    elif args.instance:
        results = migrate_instance(args.instance)
        result = {"instance": str(args.instance), "migrated": results}
    else:
        parser.error("Provide --file or --instance")
        return 1  # unreachable; parser.error calls sys.exit(2)

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

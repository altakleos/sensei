"""Schema migration for Sensei instance files.

Upgrades instance state files (profile.yaml, goal files) from older schema
versions to the current version. Each migration is a function that transforms
the data dict in place.

Usage (library):
    from sensei.engine.scripts.migrate import migrate_profile, migrate_goal

Usage (CLI):
    python -m sensei.engine.scripts.migrate --file instance/profile.yaml --type profile
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from sensei.engine.scripts._atomic import atomic_write_text

# Current schema versions (must match *.schema.json const values)
CURRENT_PROFILE_VERSION = 0
CURRENT_GOAL_VERSION = 0

# Migration registries: version -> function that upgrades FROM that version
PROFILE_MIGRATIONS: dict[int, Any] = {
    # Example for future use:
    # 0: _migrate_profile_0_to_1,
}

GOAL_MIGRATIONS: dict[int, Any] = {
    # Example for future use:
    # 0: _migrate_goal_0_to_1,
}


def migrate_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate a profile dict to the current schema version. Returns the migrated dict."""
    version = data.get("schema_version", 0)
    while version < CURRENT_PROFILE_VERSION:
        fn = PROFILE_MIGRATIONS.get(version)
        if fn is None:
            raise ValueError(f"No migration path from profile schema_version {version}")
        fn(data)
        version += 1
        data["schema_version"] = version
    return data


def migrate_goal(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate a goal dict to the current schema version. Returns the migrated dict."""
    version = data.get("schema_version", 0)
    while version < CURRENT_GOAL_VERSION:
        fn = GOAL_MIGRATIONS.get(version)
        if fn is None:
            raise ValueError(f"No migration path from goal schema_version {version}")
        fn(data)
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
        migrate_profile(data)
        target = CURRENT_PROFILE_VERSION
    elif file_type == "goal":
        migrate_goal(data)
        target = CURRENT_GOAL_VERSION
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    if old_version == target:
        return False

    atomic_write_text(path, yaml.dump(data, default_flow_style=False, sort_keys=False))
    return True


def migrate_instance(instance_dir: Path) -> list[str]:
    """Migrate all instance files. Returns list of migrated file descriptions."""
    migrated: list[str] = []

    profile = instance_dir / "profile.yaml"
    if profile.exists() and migrate_file(profile, "profile"):
        migrated.append(f"profile.yaml: schema_version → {CURRENT_PROFILE_VERSION}")

    # Migrate goal files (future: when goal workspaces exist)
    for goal_file in instance_dir.glob("goals/*/goal.yaml"):
        if migrate_file(goal_file, "goal"):
            migrated.append(f"{goal_file.relative_to(instance_dir)}: schema_version → {CURRENT_GOAL_VERSION}")

    return migrated


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Migrate Sensei instance files")
    parser.add_argument("--file", type=Path, help="Single file to migrate")
    parser.add_argument("--type", choices=["profile", "goal"], help="File type (required with --file)")
    parser.add_argument("--instance", type=Path, help="Instance directory to migrate all files")
    args = parser.parse_args()

    if args.file:
        if not args.type:
            parser.error("--type required with --file")
        migrated = migrate_file(args.file, args.type)
        result = {"file": str(args.file), "migrated": migrated}
    elif args.instance:
        results = migrate_instance(args.instance)
        result = {"instance": str(args.instance), "migrated": results}
    else:
        parser.error("Provide --file or --instance")
        return

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()

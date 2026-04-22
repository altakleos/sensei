"""Tests for schema migration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.migrate import (
    CURRENT_GOAL_VERSION,
    CURRENT_PROFILE_VERSION,
    main,
    migrate_file,
    migrate_goal,
    migrate_instance,
    migrate_profile,
)


def test_migrate_profile_already_current():
    data = {"schema_version": CURRENT_PROFILE_VERSION, "learner_id": "test", "expertise_map": {}}
    result = migrate_profile(data)
    assert result["schema_version"] == CURRENT_PROFILE_VERSION


def test_migrate_goal_already_current():
    data = {"schema_version": CURRENT_GOAL_VERSION, "goal_id": "test", "expressed_as": "learn rust",
             "created": "2026-04-20T00:00:00Z", "status": "active",
             "three_unknowns": {"prior": "", "target": "", "constraints": ""}, "nodes": {}}
    result = migrate_goal(data)
    assert result["schema_version"] == CURRENT_GOAL_VERSION


def test_migrate_instance_no_changes(tmp_path):
    instance = tmp_path / "instance"
    instance.mkdir()
    profile = instance / "profile.yaml"
    profile.write_text(yaml.dump({
        "schema_version": CURRENT_PROFILE_VERSION,
        "learner_id": "test",
        "expertise_map": {}
    }))
    result = migrate_instance(instance)
    assert result == []


def test_migrate_instance_missing_profile(tmp_path):
    instance = tmp_path / "instance"
    instance.mkdir()
    result = migrate_instance(instance)
    assert result == []


def test_migrate_file_preserves_data(tmp_path):
    """Migration doesn't corrupt existing data when no migration is needed."""
    profile = tmp_path / "profile.yaml"
    data = {
        "schema_version": CURRENT_PROFILE_VERSION,
        "learner_id": "alice",
        "expertise_map": {
            "recursion": {"mastery": "solid", "confidence": 0.8,
                          "last_seen": "2026-04-20T00:00:00Z", "attempts": 5, "correct": 4}
        }
    }
    profile.write_text(yaml.dump(data, default_flow_style=False))

    changed = migrate_file(profile, "profile")
    assert not changed

    reloaded = yaml.safe_load(profile.read_text())
    assert reloaded["expertise_map"]["recursion"]["mastery"] == "solid"


def test_migrate_file_empty_yaml_returns_false(tmp_path: Path) -> None:
    """An empty YAML file yields data=None; migrate_file returns False without error."""
    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    assert migrate_file(empty, "profile") is False


def test_migrate_file_rejects_unknown_type(tmp_path: Path) -> None:
    profile = tmp_path / "profile.yaml"
    profile.write_text(yaml.dump({"schema_version": 0, "learner_id": "a", "expertise_map": {}}))
    with pytest.raises(ValueError, match="Unknown file type"):
        migrate_file(profile, "hints")  # type: ignore[arg-type]


def test_migrate_profile_unknown_source_version_raises() -> None:
    """No registered migration path for a future version → ValueError."""
    with pytest.raises(ValueError, match="No migration path"):
        migrate_profile({"schema_version": -1, "learner_id": "a", "expertise_map": {}})


def test_migrate_goal_unknown_source_version_raises() -> None:
    with pytest.raises(ValueError, match="No migration path"):
        migrate_goal({
            "schema_version": -1,
            "goal_id": "g",
            "expressed_as": "x",
            "created": "2026-04-20T00:00:00Z",
            "status": "active",
            "three_unknowns": {"prior": "", "target": "", "constraints": ""},
            "nodes": {},
        })


def test_migrate_profile_pure_contract_on_partial_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """A registered migration that raises partway must not leave the
    caller's input dict mutated. Migrations are required to be pure:
    accept a dict, return a new dict."""
    from sensei.engine.scripts import migrate as m

    def failing_migration(data: dict) -> dict:
        # Simulate a pure migration that begins constructing a new dict
        # and fails before returning. The caller's original dict is
        # untouched because we mutate the copy, not the input.
        new_data = dict(data)
        new_data["partial_change"] = "applied"
        raise RuntimeError("simulated mid-migration failure")

    monkeypatch.setitem(m.PROFILE_MIGRATIONS, 0, failing_migration)
    monkeypatch.setattr(m, "CURRENT_PROFILE_VERSION", 1)

    original = {"schema_version": 0, "learner_id": "alice", "expertise_map": {}}
    snapshot = dict(original)

    with pytest.raises(RuntimeError, match="simulated mid-migration failure"):
        m.migrate_profile(original)

    # Caller's input dict is unchanged — no schema_version bump, no stray fields.
    assert original == snapshot
    assert "partial_change" not in original


def test_migrate_profile_pure_chain_returns_new_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful pure migration returns a new dict with the version bumped
    to match CURRENT_PROFILE_VERSION. The caller's input dict is not required
    to be mutated (pure contract)."""
    from sensei.engine.scripts import migrate as m

    def pure_migration(data: dict) -> dict:
        new = dict(data)
        new["added_by_migration"] = True
        return new

    monkeypatch.setitem(m.PROFILE_MIGRATIONS, 0, pure_migration)
    monkeypatch.setattr(m, "CURRENT_PROFILE_VERSION", 1)

    original = {"schema_version": 0, "learner_id": "alice", "expertise_map": {}}
    snapshot = dict(original)

    result = m.migrate_profile(original)

    assert result["schema_version"] == 1
    assert result["added_by_migration"] is True
    # Caller's original dict is untouched.
    assert original == snapshot


def test_migrate_file_runs_registered_migration_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: a registered 0→1 migration runs when loaded from disk,
    and the on-disk YAML is atomically rewritten with the new schema_version
    and any new fields the migration inserts.

    This is the migration-scaffolding test that's missing today: the existing
    suite only exercises identity round-trips (no migration functions ever
    registered), so the first real migration would ship unverified. Here we
    register a realistic migration via monkeypatch and prove the full path
    — load → migrate → safe_dump → write — works.
    """
    from sensei.engine.scripts import migrate as m

    def rename_field_migration(data: dict) -> dict:
        """Realistic example: rename `legacy_field` → `new_field`."""
        new = dict(data)
        if "legacy_field" in new:
            new["new_field"] = new.pop("legacy_field")
        return new

    monkeypatch.setitem(m.PROFILE_MIGRATIONS, 0, rename_field_migration)
    monkeypatch.setattr(m, "CURRENT_PROFILE_VERSION", 1)

    profile = tmp_path / "profile.yaml"
    profile.write_text(
        yaml.safe_dump({
            "schema_version": 0,
            "learner_id": "alice",
            "expertise_map": {},
            "legacy_field": "old-value",
        }),
        encoding="utf-8",
    )

    migrated = m.migrate_file(profile, "profile")
    assert migrated is True

    reloaded = yaml.safe_load(profile.read_text(encoding="utf-8"))
    assert reloaded["schema_version"] == 1
    assert reloaded["new_field"] == "old-value"
    assert "legacy_field" not in reloaded
    # Safe-dumpable: re-parsing succeeds with safe_load (no Python-tagged YAML).
    # Already proven by the yaml.safe_load above — this is the line that
    # would fail if migrate.py regressed to yaml.dump with a non-primitive.


# --- main(argv) CLI entry ---


def test_main_instance_mode(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """main --instance <dir> returns 0 and emits a migrated-list summary."""
    instance = tmp_path / "instance"
    instance.mkdir()
    (instance / "profile.yaml").write_text(
        yaml.dump({
            "schema_version": CURRENT_PROFILE_VERSION,
            "learner_id": "alice",
            "expertise_map": {},
        })
    )
    rc = main(["--instance", str(instance)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["instance"] == str(instance)
    assert parsed["migrated"] == []  # already at CURRENT version, nothing changed


def test_main_file_mode(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """main --file <profile.yaml> --type profile returns 0 and reports migrated=False."""
    profile = tmp_path / "profile.yaml"
    profile.write_text(
        yaml.dump({
            "schema_version": CURRENT_PROFILE_VERSION,
            "learner_id": "alice",
            "expertise_map": {},
        })
    )
    rc = main(["--file", str(profile), "--type", "profile"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["file"] == str(profile)
    assert parsed["migrated"] is False


def test_main_file_mode_requires_type(tmp_path: Path) -> None:
    """--file without --type is a parser error (argparse exits 2)."""
    profile = tmp_path / "profile.yaml"
    profile.write_text(yaml.dump({"schema_version": 0, "learner_id": "a", "expertise_map": {}}))
    with pytest.raises(SystemExit) as exc_info:
        main(["--file", str(profile)])
    assert exc_info.value.code == 2


def test_main_requires_file_or_instance() -> None:
    """Neither --file nor --instance is a parser error (argparse exits 2)."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Smoke test: the python -m entry-point still works (how `sensei upgrade` drives it)."""
    instance = tmp_path / "instance"
    instance.mkdir()
    (instance / "profile.yaml").write_text(
        yaml.dump({
            "schema_version": CURRENT_PROFILE_VERSION,
            "learner_id": "alice",
            "expertise_map": {},
        })
    )
    result = subprocess.run(
        [sys.executable, "-m", "sensei.engine.scripts.migrate", "--instance", str(instance)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["migrated"] == []

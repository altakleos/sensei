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


# --- Coverage: goal migration loop body (lines 81-83) ---


def test_migrate_goal_runs_registered_migration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise the goal migration loop body: fn(data), version bump, schema_version set."""
    from sensei.engine.scripts import migrate as m

    def goal_v1_to_v2(data: dict) -> dict:
        new = dict(data)
        new["migrated_field"] = True
        return new

    monkeypatch.setitem(m.GOAL_MIGRATIONS, 1, goal_v1_to_v2)
    monkeypatch.setattr(m, "CURRENT_GOAL_VERSION", 2)

    result = m.migrate_goal({"schema_version": 1, "goal_id": "g", "nodes": {}})
    assert result["schema_version"] == 2
    assert result["migrated_field"] is True


# --- Coverage: migrate_file goal branch (lines 100-101) ---


def test_migrate_file_goal_type(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """migrate_file with file_type='goal' exercises the goal branch."""
    from sensei.engine.scripts import migrate as m

    def goal_v1_to_v2(data: dict) -> dict:
        new = dict(data)
        new["upgraded"] = True
        return new

    monkeypatch.setitem(m.GOAL_MIGRATIONS, 1, goal_v1_to_v2)
    monkeypatch.setattr(m, "CURRENT_GOAL_VERSION", 2)

    goal = tmp_path / "goal.yaml"
    goal.write_text(yaml.safe_dump({"schema_version": 1, "goal_id": "g", "nodes": {}}))

    assert m.migrate_file(goal, "goal") is True
    reloaded = yaml.safe_load(goal.read_text())
    assert reloaded["schema_version"] == 2
    assert reloaded["upgraded"] is True


# --- Coverage: instance/ → learner/ rename (lines 119-121) ---


def test_migrate_instance_renames_old_instance_dir(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """When instance/ exists but learner/ does not, rename instance/ → learner/."""
    old_dir = tmp_path / "instance"
    old_dir.mkdir()
    (old_dir / "profile.yaml").write_text(yaml.safe_dump({
        "schema_version": CURRENT_PROFILE_VERSION,
        "learner_id": "alice",
        "expertise_map": {},
    }))

    learner_dir = tmp_path / "learner"
    result = migrate_instance(learner_dir)

    assert any("directory renamed" in r for r in result)
    assert learner_dir.exists()
    assert not old_dir.exists()
    assert "Renamed instance/" in capsys.readouterr().out


# --- Coverage: profile migration applied in migrate_instance (line 125) ---


def test_migrate_instance_migrates_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """migrate_instance applies profile migration when version is behind."""
    from sensei.engine.scripts import migrate as m

    def profile_v0_to_v1(data: dict) -> dict:
        return {**data, "new_field": True}

    monkeypatch.setitem(m.PROFILE_MIGRATIONS, 0, profile_v0_to_v1)
    monkeypatch.setattr(m, "CURRENT_PROFILE_VERSION", 1)

    learner = tmp_path / "learner"
    learner.mkdir()
    (learner / "profile.yaml").write_text(yaml.safe_dump({
        "schema_version": 0, "learner_id": "alice", "expertise_map": {},
    }))

    result = m.migrate_instance(learner)
    assert any("profile.yaml" in r for r in result)


# --- Coverage: goal file migration in migrate_instance (lines 129-130) ---


def test_migrate_instance_migrates_goal_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """migrate_instance migrates goal files under goals/*/goal.yaml."""
    from sensei.engine.scripts import migrate as m

    def goal_v1_to_v2(data: dict) -> dict:
        return {**data, "upgraded": True}

    monkeypatch.setitem(m.GOAL_MIGRATIONS, 1, goal_v1_to_v2)
    monkeypatch.setattr(m, "CURRENT_GOAL_VERSION", 2)

    learner = tmp_path / "learner"
    goal_dir = learner / "goals"
    goal_dir.mkdir(parents=True)
    (goal_dir / "rust.yaml").write_text(yaml.safe_dump({
        "schema_version": 1, "goal_id": "rust", "nodes": {},
    }))

    result = m.migrate_instance(learner)
    assert any("rust.yaml" in r for r in result)


def test_goal_migration_0_to_1() -> None:
    """Verify the real 0→1 migration renames node states and fields."""
    v0_goal = {
        "schema_version": 0,
        "goal_id": "test",
        "expressed_as": "test",
        "created": "2026-04-20T00:00:00Z",
        "status": "active",
        "three_unknowns": {"prior_state": "none", "target_state": "vague", "constraints": ""},
        "nodes": {
            "a": {"state": "collapsed", "prerequisites": []},
            "b": {"state": "spawned", "prerequisites": ["a"]},
            "c": {"state": "expanded", "prerequisites": []},
            "d": {"state": "active", "prerequisites": [], "spawned_from": "c"},
            "e": {"state": "weird-unknown", "prerequisites": []},
        },
    }
    result = migrate_goal(v0_goal)
    assert result["schema_version"] == CURRENT_GOAL_VERSION
    assert result["nodes"]["a"]["state"] == "skipped"
    assert result["nodes"]["b"]["state"] == "pending"
    assert result["nodes"]["c"]["state"] == "decomposed"
    assert result["nodes"]["d"]["state"] == "active"
    assert result["nodes"]["d"]["inserted_from"] == "c"
    assert "spawned_from" not in result["nodes"]["d"]
    assert result["nodes"]["e"]["state"] == "weird-unknown"
    # v1→v2 migration adds target_depth
    assert result["three_unknowns"]["target_depth"] == "functional"


def test_goal_migration_1_to_2():
    """Verify migration adds target_depth to three_unknowns."""
    old = {
        "schema_version": 1,
        "goal_id": "test",
        "expressed_as": "learn rust",
        "created": "2026-01-01T00:00:00Z",
        "status": "active",
        "three_unknowns": {
            "prior_state": "none",
            "target_state": "clear",
            "constraints": "none",
        },
        "nodes": {"basics": {"state": "pending", "prerequisites": []}},
    }
    result = migrate_goal(old)
    assert result["schema_version"] == 2
    assert result["three_unknowns"]["target_depth"] == "functional"


def test_profile_migration_v0_to_v2_end_to_end():
    """Real migration chain: v0 -> v1 (emotional_state) -> v2 (metacognitive_state)."""
    v0 = {"schema_version": 0, "learner_id": "alice", "expertise_map": {}}
    result = migrate_profile(v0)
    assert result["schema_version"] == 2
    assert result["emotional_state"]["engagement"] == "unknown"
    assert result["emotional_state"]["frustration"] == "unknown"
    assert result["emotional_state"]["agency"] == "unknown"
    assert result["metacognitive_state"]["calibration_accuracy"] is None
    assert result["metacognitive_state"]["planning_tendency"] == "unknown"
    assert result["metacognitive_state"]["help_seeking"] == "unknown"


def test_goal_migration_v0_to_v2_end_to_end():
    """Real migration chain: v0 -> v1 (state renames) -> v2 (target_depth)."""
    v0_goal = {
        "schema_version": 0,
        "goal_id": "sysdesign",
        "expressed_as": "learn system design",
        "created": "2026-04-20T00:00:00Z",
        "status": "active",
        "three_unknowns": {"prior_state": "none", "target_state": "vague", "constraints": ""},
        "nodes": {
            "a": {"state": "collapsed", "prerequisites": []},
            "b": {"state": "spawned", "prerequisites": ["a"]},
            "c": {"state": "expanded", "prerequisites": []},
            "d": {"state": "active", "prerequisites": [], "spawned_from": "c"},
        },
    }
    result = migrate_goal(v0_goal)
    assert result["schema_version"] == 2
    # v0→v1: state renames
    assert result["nodes"]["a"]["state"] == "skipped"
    assert result["nodes"]["b"]["state"] == "pending"
    assert result["nodes"]["c"]["state"] == "decomposed"
    assert result["nodes"]["d"]["state"] == "active"
    # v0→v1: field rename
    assert result["nodes"]["d"]["inserted_from"] == "c"
    assert "spawned_from" not in result["nodes"]["d"]
    # v1→v2: target_depth added
    assert result["three_unknowns"]["target_depth"] == "functional"

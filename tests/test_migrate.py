"""Tests for schema migration."""


import yaml

from sensei.engine.scripts.migrate import (
    CURRENT_GOAL_VERSION,
    CURRENT_PROFILE_VERSION,
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

    from sensei.engine.scripts.migrate import migrate_file
    changed = migrate_file(profile, "profile")
    assert not changed

    reloaded = yaml.safe_load(profile.read_text())
    assert reloaded["expertise_map"]["recursion"]["mastery"] == "solid"

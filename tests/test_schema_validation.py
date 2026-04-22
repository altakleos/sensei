"""Schema round-trip validation for instance state files.

Guards the class of bug where a protocol emits YAML in a shape the schema
rejects (the a6 goal-shape regression), and where a migration transforms
a profile into a shape the schema then rejects.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from sensei.engine.scripts.migrate import migrate_profile

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "src" / "sensei" / "engine" / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text())


VALID_PROFILE = {
    "schema_version": 0,
    "learner_id": "alice",
    "expertise_map": {
        "hash-maps": {
            "mastery": "solid",
            "confidence": 0.8,
            "last_seen": "2026-04-20T00:00:00Z",
            "attempts": 5,
            "correct": 4,
        }
    },
}

VALID_GOAL = {
    "schema_version": 0,
    "goal_id": "learn-rust",
    "expressed_as": "Learn Rust",
    "created": "2026-04-20T00:00:00Z",
    "status": "active",
    "three_unknowns": {
        "prior_state": "none",
        "target_state": "vague",
        "constraints": "",
    },
    "nodes": {
        "ownership": {"state": "active", "prerequisites": []},
    },
}


@pytest.mark.parametrize(
    ("schema_file", "fixture"),
    [
        ("profile.schema.json", VALID_PROFILE),
        ("goal.schema.json", VALID_GOAL),
    ],
)
def test_valid_fixture_passes_schema(schema_file: str, fixture: dict) -> None:
    jsonschema.validate(fixture, _load_schema(schema_file))


def test_profile_empty_learner_id_rejected() -> None:
    bad = {**VALID_PROFILE, "learner_id": ""}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


@pytest.mark.parametrize(
    "bad_learner_id",
    [
        "has space",
        "has\nnewline",
        "has:colon",
        "has/slash",
        "has.dot",
        "has{brace}",
        "x" * 65,  # too long
    ],
)
def test_profile_learner_id_pattern_rejects_unsafe(bad_learner_id: str) -> None:
    """Schema must enforce the same pattern the CLI --learner-id validator
    uses, so protocols writing profile.yaml directly cannot smuggle in
    YAML- or prompt-injecting characters (cli.py:_LEARNER_ID_RE)."""
    bad = {**VALID_PROFILE, "learner_id": bad_learner_id}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


@pytest.mark.parametrize(
    "good_learner_id",
    ["alice", "learner-01", "ab_cd", "A", "x" * 64],
)
def test_profile_learner_id_pattern_accepts_safe(good_learner_id: str) -> None:
    """All CLI-accepted learner_ids must also pass schema validation."""
    ok = {**VALID_PROFILE, "learner_id": good_learner_id}
    jsonschema.validate(ok, _load_schema("profile.schema.json"))


def test_profile_missing_required_field_rejected() -> None:
    bad = {k: v for k, v in VALID_PROFILE.items() if k != "expertise_map"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_profile_invalid_mastery_enum_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "expertise_map": {
            "hash-maps": {
                **VALID_PROFILE["expertise_map"]["hash-maps"],
                "mastery": "expert",  # not in the enum
            }
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_goal_uppercase_goal_id_rejected() -> None:
    """goal_id must match ^[a-z][a-z0-9-]*$ per the schema pattern."""
    bad = {**VALID_GOAL, "goal_id": "LearnRust"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("goal.schema.json"))


def test_goal_invalid_node_state_rejected() -> None:
    """a7 regression guard: node state must be one of the documented values.
    ('pending' was a real bug — the LLM emitted it instead of 'spawned')."""
    bad = {
        **VALID_GOAL,
        "nodes": {"ownership": {"state": "pending", "prerequisites": []}},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("goal.schema.json"))


def test_goal_invalid_status_rejected() -> None:
    bad = {**VALID_GOAL, "status": "in-progress"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("goal.schema.json"))


def test_migrate_profile_round_trip_is_schema_valid() -> None:
    """Guards the class of bug where migration emits a shape the schema then rejects."""
    migrated = migrate_profile(dict(VALID_PROFILE))
    jsonschema.validate(migrated, _load_schema("profile.schema.json"))


def test_migrate_profile_on_current_version_is_noop() -> None:
    """With CURRENT_PROFILE_VERSION == 0 and no migrations registered, round-trip is identity."""
    original = dict(VALID_PROFILE)
    migrated = migrate_profile(dict(original))
    assert migrated == original

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
assert SCHEMA_DIR.is_dir(), f"schema directory not found: {SCHEMA_DIR}"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text())


VALID_PROFILE = {
    "schema_version": 2,
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
    "emotional_state": {
        "engagement": "unknown",
        "frustration": "unknown",
        "agency": "unknown",
        "updated_at": "1970-01-01T00:00:00Z",
    },
    "metacognitive_state": {
        "calibration_accuracy": None,
        "planning_tendency": "unknown",
        "help_seeking": "unknown",
        "updated_at": "1970-01-01T00:00:00Z",
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

VALID_SESSION_NOTES = {
    "schema_version": 0,
    "sessions": [
        {
            "date": "2026-04-22T18:30:00Z",
            "goal": "system-design-interviews",
            "topics_covered": ["notification-systems", "requirements-gathering"],
            "observations": [
                {
                    "type": "misconception",
                    "topic": "requirements-gathering",
                    "detail": "Jumps to infrastructure before clarifying requirements",
                },
                {
                    "type": "breakthrough",
                    "topic": "notification-systems",
                    "detail": "Connected partitioning to ordering guarantees unprompted",
                },
            ],
            "summary": "Persistent pattern of skipping requirements phase.",
            "next_session_seeds": ["Start with a requirements-only exercise"],
        }
    ],
}


@pytest.mark.parametrize(
    ("schema_file", "fixture"),
    [
        ("profile.schema.json", VALID_PROFILE),
        ("goal.schema.json", VALID_GOAL),
        ("session-notes.schema.json", VALID_SESSION_NOTES),
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


# --- Session notes schema tests ---


def test_session_notes_empty_sessions_valid() -> None:
    doc = {"schema_version": 0, "sessions": []}
    jsonschema.validate(doc, _load_schema("session-notes.schema.json"))


def test_session_notes_invalid_observation_type_rejected() -> None:
    bad = {
        "schema_version": 0,
        "sessions": [
            {
                "date": "2026-04-22T18:30:00Z",
                "observations": [{"type": "insight", "detail": "something"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("session-notes.schema.json"))


def test_session_notes_missing_date_rejected() -> None:
    bad = {
        "schema_version": 0,
        "sessions": [{"observations": []}],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("session-notes.schema.json"))


def test_session_notes_missing_observation_detail_rejected() -> None:
    bad = {
        "schema_version": 0,
        "sessions": [
            {
                "date": "2026-04-22T18:30:00Z",
                "observations": [{"type": "misconception"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("session-notes.schema.json"))


def test_session_notes_observation_without_topic_valid() -> None:
    """Topic is optional — emotional_shift and effective_strategy may be topic-independent."""
    doc = {
        "schema_version": 0,
        "sessions": [
            {
                "date": "2026-04-22T18:30:00Z",
                "observations": [
                    {"type": "emotional_shift", "detail": "Frustrated early, engaged after breakthrough"}
                ],
            }
        ],
    }
    jsonschema.validate(doc, _load_schema("session-notes.schema.json"))


def test_session_notes_session_without_summary_valid() -> None:
    """Summary is optional — may be absent if session ended abruptly."""
    doc = {
        "schema_version": 0,
        "sessions": [
            {
                "date": "2026-04-22T18:30:00Z",
                "observations": [{"type": "breakthrough", "detail": "Got it"}],
            }
        ],
    }
    jsonschema.validate(doc, _load_schema("session-notes.schema.json"))


# --- Emotional state schema tests ---


def test_profile_with_emotional_state_valid() -> None:
    """Profile with all emotional_state fields validates."""
    profile = {
        **VALID_PROFILE,
        "emotional_state": {
            "engagement": "active",
            "frustration": "none",
            "agency": "autonomous",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    jsonschema.validate(profile, _load_schema("profile.schema.json"))


def test_profile_without_emotional_state_valid() -> None:
    """emotional_state is optional — profiles without it still validate."""
    profile = {k: v for k, v in VALID_PROFILE.items() if k != "emotional_state"}
    profile["schema_version"] = 2
    jsonschema.validate(profile, _load_schema("profile.schema.json"))


def test_emotional_state_invalid_engagement_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "emotional_state": {
            "engagement": "bored",
            "frustration": "none",
            "agency": "autonomous",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_emotional_state_invalid_frustration_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "emotional_state": {
            "engagement": "active",
            "frustration": "angry",
            "agency": "autonomous",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_emotional_state_missing_required_field_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "emotional_state": {
            "engagement": "active",
            "frustration": "none",
            # agency missing
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_migrate_v0_profile_adds_emotional_state() -> None:
    """Migration from v0 to v1 adds emotional_state with all-unknown defaults."""
    v0_profile = {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {},
    }
    migrated = migrate_profile(v0_profile)
    assert migrated["schema_version"] == 2
    assert migrated["emotional_state"]["engagement"] == "unknown"
    assert migrated["emotional_state"]["frustration"] == "unknown"
    assert migrated["emotional_state"]["agency"] == "unknown"
    assert migrated["emotional_state"]["updated_at"] == "1970-01-01T00:00:00Z"
    assert migrated["metacognitive_state"]["calibration_accuracy"] is None
    assert migrated["metacognitive_state"]["planning_tendency"] == "unknown"
    assert migrated["metacognitive_state"]["help_seeking"] == "unknown"
    assert migrated["metacognitive_state"]["updated_at"] == "1970-01-01T00:00:00Z"
    jsonschema.validate(migrated, _load_schema("profile.schema.json"))


# --- Metacognitive state schema tests ---


def test_profile_with_metacognitive_state_valid() -> None:
    """Profile with all metacognitive_state fields validates."""
    profile = {
        **VALID_PROFILE,
        "metacognitive_state": {
            "calibration_accuracy": 0.85,
            "planning_tendency": "proactive",
            "help_seeking": "strategic",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    jsonschema.validate(profile, _load_schema("profile.schema.json"))


def test_profile_without_metacognitive_state_valid() -> None:
    """metacognitive_state is optional — profiles without it still validate."""
    profile = {k: v for k, v in VALID_PROFILE.items() if k != "metacognitive_state"}
    profile["schema_version"] = 2
    jsonschema.validate(profile, _load_schema("profile.schema.json"))


def test_metacognitive_state_null_calibration_valid() -> None:
    """calibration_accuracy can be null (insufficient data)."""
    profile = {
        **VALID_PROFILE,
        "metacognitive_state": {
            "calibration_accuracy": None,
            "planning_tendency": "unknown",
            "help_seeking": "unknown",
            "updated_at": "1970-01-01T00:00:00Z",
        },
    }
    jsonschema.validate(profile, _load_schema("profile.schema.json"))


def test_metacognitive_state_invalid_planning_tendency_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "metacognitive_state": {
            "calibration_accuracy": 0.5,
            "planning_tendency": "lazy",
            "help_seeking": "strategic",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_metacognitive_state_invalid_help_seeking_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "metacognitive_state": {
            "calibration_accuracy": 0.5,
            "planning_tendency": "proactive",
            "help_seeking": "passive",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_metacognitive_state_missing_required_field_rejected() -> None:
    bad = {
        **VALID_PROFILE,
        "metacognitive_state": {
            "calibration_accuracy": 0.5,
            "planning_tendency": "proactive",
            # help_seeking missing
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _load_schema("profile.schema.json"))


def test_migrate_v1_profile_adds_metacognitive_state() -> None:
    """Migration from v1 to v2 adds metacognitive_state with all-unknown/null defaults."""
    v1_profile = {
        "schema_version": 1,
        "learner_id": "alice",
        "expertise_map": {},
        "emotional_state": {
            "engagement": "active",
            "frustration": "none",
            "agency": "autonomous",
            "updated_at": "2026-04-22T18:30:00Z",
        },
    }
    migrated = migrate_profile(v1_profile)
    assert migrated["schema_version"] == 2
    assert migrated["metacognitive_state"]["calibration_accuracy"] is None
    assert migrated["metacognitive_state"]["planning_tendency"] == "unknown"
    assert migrated["metacognitive_state"]["help_seeking"] == "unknown"
    assert migrated["metacognitive_state"]["updated_at"] == "1970-01-01T00:00:00Z"
    # Emotional state preserved
    assert migrated["emotional_state"]["engagement"] == "active"
    jsonschema.validate(migrated, _load_schema("profile.schema.json"))

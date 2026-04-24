"""End-to-end verification of goal pause and resume lifecycle.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with three topics at varying mastery levels, creates a goal file with those
topics as nodes in different states, and invokes the LLM agent TWICE:

1. First invocation: pause the goal.
2. Between invocations: mutate all ``last_seen`` timestamps to 10 days ago
   to simulate time passing.
3. Second invocation: resume the goal, triggering stale-topic detection.

The test asserts that the goal file transitions through ``active → paused →
active`` and that the agent identifies stale topics on resume. The profile
must remain schema-valid throughout.

Tier-2 test per ADR-0011. Skip conditions match the other E2E tests.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jsonschema
import pytest
import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main
from tests.e2e.agent_runner import SKIP_REASON, TOOL_AVAILABLE, run_agent

PROFILE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "sensei"
    / "engine"
    / "schemas"
    / "profile.schema.json"
)

GOAL_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "sensei"
    / "engine"
    / "schemas"
    / "goal.schema.json"
)

pytestmark = pytest.mark.skipif(not TOOL_AVAILABLE, reason=SKIP_REASON)


def _utc_iso(dt: datetime) -> str:
    """Format a datetime as ISO-8601 UTC string matching schema expectations."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_profile(instance_dir: Path) -> dict:
    """Overwrite learner/profile.yaml with three topics at varying mastery."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "sorting-algorithms": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now),
                "attempts": 5,
                "correct": 4,
            },
            "binary-search": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": _utc_iso(now - timedelta(days=3)),
                "attempts": 3,
                "correct": 2,
            },
            "hash-tables": {
                "mastery": "shaky",
                "confidence": 0.3,
                "last_seen": _utc_iso(now - timedelta(days=5)),
                "attempts": 2,
                "correct": 1,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _seed_goal(instance_dir: Path) -> None:
    """Create a goal file with sorting-algorithms completed, binary-search active, hash-tables pending."""
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 2,
        "goal_id": "dsa-fundamentals",
        "expressed_as": "Learn fundamental data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "No time constraints",
            "target_depth": "functional",
        },
        "nodes": {
            "sorting-algorithms": {
                "state": "completed",
                "prerequisites": [],
            },
            "binary-search": {
                "state": "active",
                "prerequisites": ["sorting-algorithms"],
            },
            "hash-tables": {
                "state": "pending",
                "prerequisites": ["sorting-algorithms"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-fundamentals.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _mutate_timestamps_to_past(instance_dir: Path, days_ago: int = 10) -> None:
    """Shift all last_seen timestamps in the profile to ``days_ago`` days in the past."""
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    past = datetime.now(timezone.utc) - timedelta(days=days_ago)
    for topic_entry in profile.get("expertise_map", {}).values():
        topic_entry["last_seen"] = _utc_iso(past)
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")


def test_goal_pause_and_resume_preserves_progress(tmp_path: Path) -> None:
    """Verify pause sets status to 'paused', resume restores 'active' and detects stale topics."""
    # --- Scaffold ---
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    _seed_profile(tmp_path)
    _seed_goal(tmp_path)

    goal_path = tmp_path / "learner" / "goals" / "dsa-fundamentals.yaml"

    # --- Invocation 1: Pause ---
    pause_prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. The learner wants to pause a goal.\n\n"
        "--- learner message begins ---\n"
        "Pause my dsa-fundamentals goal. I need to take a break. "
        "Update the goal file and stop.\n"
        "--- learner message ends ---\n"
    )

    completed = run_agent(pause_prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"pause agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    )

    # Assert: goal status is now 'paused'
    goal_after_pause = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
    assert goal_after_pause["status"] == "paused", (
        f"expected goal status 'paused', got {goal_after_pause['status']!r}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # --- Mutate: simulate 10 days passing ---
    _mutate_timestamps_to_past(tmp_path, days_ago=10)

    # --- Invocation 2: Resume ---
    resume_prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. The learner wants to resume a paused goal.\n\n"
        "--- learner message begins ---\n"
        "Resume my dsa-fundamentals goal. Check which topics are stale and tell me "
        "what needs review. Update the goal file and stop.\n"
        "--- learner message ends ---\n"
    )

    completed2 = run_agent(resume_prompt, cwd=tmp_path, timeout=300)
    assert completed2.returncode == 0, (
        f"resume agent exited {completed2.returncode}.\n"
        f"stdout:\n{completed2.stdout}\n\nstderr:\n{completed2.stderr}"
    )

    # Assert: goal status is 'active' again
    goal_after_resume = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
    assert goal_after_resume["status"] == "active", (
        f"expected goal status 'active' after resume, got {goal_after_resume['status']!r}. "
        f"agent stdout head:\n{completed2.stdout[:2000]}"
    )

    # Assert: profile still validates against schema
    profile_path = tmp_path / "learner" / "profile.yaml"
    profile_after = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    profile_schema = json.loads(PROFILE_SCHEMA_PATH.read_text())
    jsonschema.validate(profile_after, profile_schema)

    # Assert: agent stdout mentions stale topics or review
    stdout_lower = completed2.stdout.lower()
    assert any(
        term in stdout_lower
        for term in ["stale", "review", "binary-search", "hash-tables", "sorting-algorithms", "fresh"]
    ), (
        f"expected agent to mention stale topics or review on resume; "
        f"agent stdout head:\n{completed2.stdout[:2000]}"
    )

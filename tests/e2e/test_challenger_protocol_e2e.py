"""End-to-end verification of the challenger protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a single topic at mastery 'solid' (5 attempts, 4 correct, confidence 0.8),
creates a minimal goal file with that topic in 'completed' state, and invokes
the detected LLM CLI tool with a prompt that triggers one challenger cycle.

The challenger protocol targets topics where the learner has demonstrated
competence (solid or above). It poses a challenge, observes the response,
classifies it, and updates the profile. The prompt provides a stipulated
answer showing understanding with a deliberate edge-case gap so the
challenger can probe further.

This test asserts that after one challenge round the topic's ``attempts``
field is greater than the seeded value (5) and the profile still validates
against the schema, proving the protocol executed its core loop: select
target → pose challenge → observe → update profile.

Tier-2 test per ADR-0011. Skip conditions match the other E2E tests.
"""

from __future__ import annotations

import json
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

pytestmark = pytest.mark.skipif(not TOOL_AVAILABLE, reason=SKIP_REASON)


def _utc_iso(dt: datetime) -> str:
    """Format a datetime as ISO-8601 UTC string matching profile schema expectations."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_profile(instance_dir: Path) -> dict:
    """Overwrite learner/profile.yaml with one topic at solid mastery."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "binary-search": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now - timedelta(days=2)),
                "attempts": 5,
                "correct": 4,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _seed_goal(instance_dir: Path) -> None:
    """Create a minimal goal file with binary-search as a completed node."""
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 0,
        "goal_id": "dsa-basics",
        "expressed_as": "Learn fundamental data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=7)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "No time constraints",
        },
        "nodes": {
            "binary-search": {
                "state": "completed",
                "prerequisites": [],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-basics.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _build_prompt() -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. Dispatch to the `challenger` protocol based on the learner's "
        "message below.\n\n"
        "Execute the challenger protocol in this single turn. Since headless mode cannot carry "
        "a multi-turn conversation, treat the learner's stipulated answer below as the "
        "response to whatever challenge you pose. After ONE challenge round, "
        "update `learner/profile.yaml` per the protocol constraints and then stop. "
        "Do not pose additional challenges.\n\n"
        "--- learner message begins ---\n"
        "Challenge me on binary search. Here's my answer to your challenge: Binary search "
        "requires a sorted array. I'd use iterative approach with left and right pointers. "
        "For duplicates, I'd find the leftmost occurrence by continuing to search left even "
        "after finding a match. Time complexity is O(log n), space is O(1) for iterative.\n\n"
        "After I answer, update my profile and stop.\n"
        "--- learner message ends ---\n"
    )


def test_challenger_protocol_pushes_limits_and_updates_profile(tmp_path: Path) -> None:
    """Verify the challenger protocol challenges a solid topic and updates the learner profile."""
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    before = _seed_profile(tmp_path)
    _seed_goal(tmp_path)

    prompt = _build_prompt()

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    )

    # --- Assertions ---
    profile_path = tmp_path / "learner" / "profile.yaml"
    after = yaml.safe_load(profile_path.read_text(encoding="utf-8"))

    # Schema still valid after the protocol's write.
    schema = json.loads(PROFILE_SCHEMA_PATH.read_text())
    jsonschema.validate(after, schema)

    # The topic should have attempts > 5 after a challenge interaction.
    topic = "binary-search"
    topic_entry = after.get("expertise_map", {}).get(topic)
    assert topic_entry is not None, (
        f"expected topic {topic!r} in profile after challenge; got: {after}"
    )

    assert topic_entry["attempts"] > 5, (
        f"attempts for {topic!r} should be > 5 after a challenge interaction; "
        f"before={before['expertise_map'][topic]['attempts']}, "
        f"after={topic_entry['attempts']}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

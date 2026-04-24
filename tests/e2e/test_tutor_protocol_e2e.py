"""End-to-end verification of the tutor protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a single topic at mastery 'none' (never taught), creates a minimal
goal file with that topic in 'active' state, and invokes the detected LLM
CLI tool with a prompt that triggers one tutor cycle.

The tutor protocol runs an explain→probe→reshape loop. The prompt provides
a stipulated learner answer so the single-turn headless agent can complete
the cycle without multi-turn interaction. After teaching, the protocol must
update the learner profile (at minimum: bump ``attempts``).

This test asserts that after one tutor cycle the topic's ``attempts`` field
is greater than zero and the profile still validates against the schema,
proving the protocol executed its core loop: explain → probe → classify →
update profile.

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
    """Overwrite learner/profile.yaml with one untaught topic."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "binary-search": {
                "mastery": "none",
                "confidence": 0.0,
                "last_seen": _utc_iso(now - timedelta(days=365)),
                "attempts": 0,
                "correct": 0,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _seed_goal(instance_dir: Path) -> None:
    """Create a minimal goal file with binary-search as the active node."""
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 2,
        "goal_id": "dsa-basics",
        "expressed_as": "Learn fundamental data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=1)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "none",
            "target_state": "clear",
            "constraints": "No time constraints",
            "target_depth": "functional",
        },
        "nodes": {
            "binary-search": {
                "state": "active",
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
        "follow the boot chain. Dispatch to the `tutor` protocol based on the learner's "
        "message below.\n\n"
        "Execute the tutor protocol in this single turn. Since headless mode cannot carry "
        "a multi-turn conversation, treat the learner's stipulated answer below as the "
        "response to whatever probe you pose. After teaching ONE topic and probing, "
        "update `learner/profile.yaml` per the protocol constraints and then stop. "
        "Do not advance to a new topic.\n\n"
        "--- learner message begins ---\n"
        "Teach me about binary search. I'm a beginner and don't know anything about it.\n\n"
        "(Treat whatever probe you pose as answered by the following — this is a "
        "single-turn E2E, so the learner can't reply twice:)\n\n"
        "**Learner's answer:** \"Binary search works by repeatedly dividing the search "
        "interval in half. You start with the middle element, and if the target is less "
        "than the middle, you search the left half, otherwise the right half. The time "
        "complexity is O(log n).\"\n\n"
        "**Confidence signal:** the learner is direct and assertive; no hedging language.\n\n"
        "After I answer, update my profile and stop.\n"
        "--- learner message ends ---\n"
    )


def test_tutor_protocol_updates_profile_after_teaching(tmp_path: Path) -> None:
    """Verify the tutor protocol teaches a topic and updates the learner profile."""
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

    # The topic should have attempts > 0 after a teaching interaction.
    topic = "binary-search"
    topic_entry = after.get("expertise_map", {}).get(topic)
    assert topic_entry is not None, (
        f"expected topic {topic!r} in profile after teaching; got: {after}"
    )

    assert topic_entry["attempts"] > 0, (
        f"attempts for {topic!r} should be > 0 after a teaching interaction; "
        f"before={before['expertise_map'][topic]['attempts']}, "
        f"after={topic_entry['attempts']}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

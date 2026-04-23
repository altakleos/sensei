"""End-to-end verification of multi-turn session profile updates.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a single topic at mastery 'developing' (partially learned), creates a
minimal goal file with that topic as the active node, and invokes the
detected LLM CLI tool with a single prompt that stipulates an entire
multi-turn conversation.

The key technique: the prompt tells the agent upfront what the learner will
say at each turn, so the agent processes the full session in one shot. This
is the first multi-turn E2E test — the agent_runner only supports
single-turn (one prompt in, one response out), so the entire conversation
script is embedded in the prompt.

After the stipulated session, the test asserts that the profile was updated
across multiple interactions: ``attempts`` must have increased by at least 2
from the seed value, and ``last_seen`` must be newer than the seed. Mastery
level changes are NOT asserted — the LLM may or may not promote mastery in
2-3 turns, making that assertion too flaky.

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
    """Overwrite learner/profile.yaml with one topic at 'developing' mastery."""
    seed_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "linked-lists": {
                "mastery": "developing",
                "confidence": 0.4,
                "last_seen": _utc_iso(seed_time),
                "attempts": 2,
                "correct": 1,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _seed_goal(instance_dir: Path) -> None:
    """Create a minimal goal file with linked-lists as active node and arrays completed."""
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 0,
        "goal_id": "dsa-fundamentals",
        "expressed_as": "Learn fundamental data structures",
        "created": _utc_iso(now - timedelta(days=7)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "No time constraints",
        },
        "nodes": {
            "arrays": {
                "state": "completed",
                "prerequisites": [],
            },
            "linked-lists": {
                "state": "active",
                "prerequisites": ["arrays"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-fundamentals.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _build_prompt() -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. Dispatch to the `tutor` protocol based on the learner's "
        "message below.\n\n"
        "Execute the tutor protocol across a MULTI-TURN session. Since headless mode cannot "
        "carry a real multi-turn conversation, the learner's responses for each turn are "
        "stipulated below. Process ALL turns in sequence, updating the learner profile after "
        "EACH interaction.\n\n"
        "--- learner session begins ---\n\n"
        "I want to have a learning session about linked lists. Here is how our session "
        "will go:\n\n"
        "Turn 1 (me): Teach me about linked lists. I know arrays but I'm not sure how "
        "linked lists differ.\n\n"
        "Turn 2 (me, after your explanation): A linked list stores elements in nodes where "
        "each node points to the next one. Unlike arrays, elements aren't stored contiguously "
        "in memory, so insertion and deletion are O(1) if you have a reference to the node, "
        "but random access is O(n) instead of O(1).\n\n"
        "Turn 3 (me, after your follow-up): For reversing a linked list, I'd use three "
        "pointers: prev, current, and next. Walk through the list, at each step point "
        "current.next to prev, then advance all three pointers. Time is O(n), space is O(1).\n\n"
        "After processing all three turns, update my profile for each interaction and stop. "
        "Write the final profile to learner/profile.yaml.\n\n"
        "--- learner session ends ---\n"
    )


def test_multi_turn_session_updates_profile_across_interactions(tmp_path: Path) -> None:
    """Verify a multi-turn stipulated session updates the learner profile across interactions."""
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

    # Schema still valid after the protocol's writes.
    schema = json.loads(PROFILE_SCHEMA_PATH.read_text())
    jsonschema.validate(after, schema)

    # The topic entry must still exist.
    topic = "linked-lists"
    topic_entry = after.get("expertise_map", {}).get(topic)
    assert topic_entry is not None, (
        f"expected topic {topic!r} in profile after session; got: {after}"
    )

    # Attempts must have increased by at least 2 from seed (proves multi-turn).
    seed_attempts = before["expertise_map"][topic]["attempts"]
    assert topic_entry["attempts"] >= seed_attempts + 2, (
        f"attempts should increase by at least 2 (multi-turn); "
        f"seed={seed_attempts}, after={topic_entry['attempts']}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # last_seen must be newer than the seed value.
    seed_last_seen = before["expertise_map"][topic]["last_seen"]
    assert topic_entry["last_seen"] != seed_last_seen, (
        f"last_seen should update after session; still {seed_last_seen}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

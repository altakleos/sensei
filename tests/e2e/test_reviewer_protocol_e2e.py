"""End-to-end verification of the reviewer protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a single topic at mastery 'developing' (3 attempts, 2 correct,
confidence 0.5), creates a minimal goal file with that topic in 'active'
state, and invokes the detected LLM CLI tool with a prompt that submits
a code solution for review.

The reviewer protocol provides structured feedback on learner-submitted
work in three tiers: what works, issues, and one key learning. It then
probes self-assessment and updates the profile. The prompt provides a
simple but imperfect binary search implementation for review.

This test asserts that after one review round the topic's ``attempts``
field is greater than the seeded value (3) and the profile still validates
against the schema, proving the protocol executed its core loop: receive
work → structured review → update profile.

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
    """Overwrite learner/profile.yaml with one topic at developing mastery."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "binary-search": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": _utc_iso(now - timedelta(days=3)),
                "attempts": 3,
                "correct": 2,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _seed_goal(instance_dir: Path) -> None:
    """Create a minimal goal file with binary-search as an active node."""
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 0,
        "goal_id": "dsa-basics",
        "expressed_as": "Learn fundamental data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=3)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "No time constraints",
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
        "follow the boot chain. Dispatch to the `reviewer` protocol based on the learner's "
        "message below.\n\n"
        "Execute the reviewer protocol in this single turn. Since headless mode cannot carry "
        "a multi-turn conversation, treat the learner's stipulated self-assessment below as "
        "the response to your probe. After ONE review round, "
        "update `learner/profile.yaml` per the protocol constraints and then stop. "
        "Do not ask follow-up questions.\n\n"
        "--- learner message begins ---\n"
        "Review my binary search implementation:\n\n"
        "```python\n"
        "def binary_search(arr, target):\n"
        "    left, right = 0, len(arr)\n"
        "    while left < right:\n"
        "        mid = (left + right) // 2\n"
        "        if arr[mid] == target:\n"
        "            return mid\n"
        "        elif arr[mid] < target:\n"
        "            left = mid + 1\n"
        "        else:\n"
        "            right = mid\n"
        "    return -1\n"
        "```\n\n"
        "Give me feedback on correctness, edge cases, and style. "
        "Then update my profile and stop.\n\n"
        "(Treat whatever self-assessment probe you pose as answered by: "
        "\"I was about 60% confident it was correct. I wasn't sure about the "
        "boundary conditions with the right pointer.\")\n"
        "--- learner message ends ---\n"
    )


def test_reviewer_protocol_reviews_solution_and_updates_profile(tmp_path: Path) -> None:
    """Verify the reviewer protocol reviews submitted work and updates the learner profile."""
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

    # The topic should have attempts > 3 after a review interaction.
    topic = "binary-search"
    topic_entry = after.get("expertise_map", {}).get(topic)
    assert topic_entry is not None, (
        f"expected topic {topic!r} in profile after review; got: {after}"
    )

    assert topic_entry["attempts"] > 3, (
        f"attempts for {topic!r} should be > 3 after a review interaction; "
        f"before={before['expertise_map'][topic]['attempts']}, "
        f"after={topic_entry['attempts']}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

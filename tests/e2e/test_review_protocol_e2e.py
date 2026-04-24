"""End-to-end verification of the review protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with three topics at varying staleness levels, creates a minimal goal file
so the review protocol has curriculum context, and invokes the detected LLM
CLI tool with a prompt that triggers one review cycle.

The review protocol picks stale topics first (lowest freshness score),
conducts retrieval-only review (no reteaching), and updates ``last_seen``
in the profile. The forgetting curve uses exponential decay with a 7-day
half-life. A topic last seen 10 days ago has freshness ~0.37 (below the
0.5 stale threshold), so it should be selected first.

This test asserts that after one review cycle the stale topic's
``last_seen`` timestamp advances, proving the protocol executed its
core loop: enumerate stale → pose question → classify → update profile.

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
    """Overwrite learner/profile.yaml with three topics at varying staleness."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "binary-search": {
                "mastery": "solid",
                "confidence": 0.7,
                "last_seen": _utc_iso(now - timedelta(days=10)),
                "attempts": 5,
                "correct": 4,
            },
            "hash-tables": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": _utc_iso(now),
                "attempts": 3,
                "correct": 2,
            },
            "graph-traversal": {
                "mastery": "solid",
                "confidence": 0.6,
                "last_seen": _utc_iso(now - timedelta(days=5)),
                "attempts": 4,
                "correct": 3,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _seed_goal(instance_dir: Path) -> None:
    """Create a minimal goal file with the three topics as completed nodes."""
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 1,
        "goal_id": "dsa-review",
        "expressed_as": "Review core data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Ongoing review",
        },
        "nodes": {
            "binary-search": {
                "state": "completed",
                "prerequisites": [],
            },
            "hash-tables": {
                "state": "completed",
                "prerequisites": [],
            },
            "graph-traversal": {
                "state": "completed",
                "prerequisites": ["binary-search"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-review.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _build_prompt() -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. Dispatch to the `review` protocol based on the learner's "
        "message below.\n\n"
        "Execute the review protocol in this single turn. Since headless mode cannot carry "
        "a multi-turn conversation, treat the learner's stipulated answer below as the "
        "response to whatever retrieval question you pose. After reviewing ONE topic "
        "(the stalest one), update `learner/profile.yaml` per Step 7 and then stop "
        "(go to Step 9). Do not review more than one topic.\n\n"
        "--- learner message begins ---\n"
        "I want to review what I've learned. Run a review session. Focus on topics I "
        "haven't seen recently.\n\n"
        "(Treat whatever retrieval question you pose as answered by the following — this "
        "is a single-turn E2E, so the learner can't reply twice:)\n\n"
        "**Learner's answer:** \"Binary search works by repeatedly dividing the search "
        "interval in half. You start with a sorted array, compare the target to the middle "
        "element. If the target is less, search the left half; if greater, search the right "
        "half. Time complexity is O(log n). The loop invariant is that the target, if "
        "present, is always within the current bounds.\"\n\n"
        "**Confidence signal:** the learner is direct and assertive; no hedging language.\n"
        "--- learner message ends ---\n"
    )


def test_review_protocol_updates_stale_topic_timestamp(tmp_path: Path) -> None:
    """Verify the review protocol selects the stalest topic and updates its last_seen."""
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

    # The stale topic (binary-search, last seen 10 days ago) should have an updated last_seen.
    stale_topic = "binary-search"
    topic_entry = after.get("expertise_map", {}).get(stale_topic)
    assert topic_entry is not None, (
        f"expected topic {stale_topic!r} in profile after review; got: {after}"
    )

    before_last_seen = before["expertise_map"][stale_topic]["last_seen"]
    after_last_seen = topic_entry["last_seen"]
    assert after_last_seen != before_last_seen, (
        f"last_seen for {stale_topic!r} should have been updated by the review protocol; "
        f"before={before_last_seen}, after={after_last_seen}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # Parse and compare timestamps to confirm the update moved forward in time.
    before_dt = datetime.fromisoformat(before_last_seen.replace("Z", "+00:00"))
    after_dt = datetime.fromisoformat(after_last_seen.replace("Z", "+00:00"))
    assert after_dt > before_dt, (
        f"last_seen should advance; before={before_dt.isoformat()}, "
        f"after={after_dt.isoformat()}"
    )

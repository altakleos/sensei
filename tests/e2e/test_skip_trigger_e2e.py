"""End-to-end verification of the skip trigger against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a topic ("binary-search") at mastery 'none' and a goal with two nodes:
binary-search (active) and graph-traversal (pending, prerequisite:
binary-search). Invokes the tutor with a stipulated answer that demonstrates
confident, correct, nuanced mastery — the skip signal from tutor.md
Step 1.

Asserts that after the tutor cycle the "binary-search" node has been
skipped (state == "skipped") and the next frontier node
("graph-traversal") has been activated, proving the skip trigger fired
and ``mutate_graph.py --operation skip`` was executed.

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
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_profile(instance_dir: Path) -> None:
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


def _seed_goal(instance_dir: Path) -> None:
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
            "graph-traversal": {
                "state": "pending",
                "prerequisites": ["binary-search"],
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
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root "
        "and follow the boot chain. Dispatch to the `tutor` protocol based on the "
        "learner's message below.\n\n"
        "Execute the tutor protocol in this single turn. Since headless mode cannot "
        "carry a multi-turn conversation, treat the stipulated learner answer below "
        "as the response to whatever entry probe you pose in Step 1.\n\n"
        "IMPORTANT: The learner's answer demonstrates CONFIDENT and CORRECT mastery "
        "of binary search. Per tutor.md Step 1, when the entry probe reveals "
        "confident + correct understanding, you MUST skip the node via "
        "mutate_graph.py --operation skip, then advance to the next frontier "
        "topic (graph-traversal). Update the curriculum file and stop.\n\n"
        "--- learner message begins ---\n"
        "Teach me about binary search.\n\n"
        "(Treat whatever probe you pose as answered by the following — this is a "
        "single-turn E2E, so the learner can't reply twice:)\n\n"
        "**Learner's answer:** \"Binary search works on a sorted array by comparing "
        "the target to the middle element. If the target is smaller, recurse on the "
        "left half; if larger, the right half. Base case: subarray is empty (not "
        "found) or middle equals target (found). Time complexity is O(log n) because "
        "we halve the search space each step. The iterative version avoids stack "
        "overhead and is preferred in production. Edge cases include empty arrays, "
        "single-element arrays, and duplicate values where you need leftmost/rightmost "
        "variants using boundary adjustments.\"\n\n"
        "**Confidence signal:** the learner is direct, assertive, and provides nuanced "
        "detail beyond what was asked — clear mastery.\n\n"
        "After skipping and advancing, update the curriculum file and stop.\n"
        "--- learner message ends ---\n"
    )


def test_skip_trigger_skips_known_topic(tmp_path: Path) -> None:
    """Verify the tutor's entry probe skips a node the learner already knows."""
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    _seed_profile(tmp_path)
    _seed_goal(tmp_path)

    completed = run_agent(_build_prompt(), cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:3000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    goal_path = tmp_path / "learner" / "goals" / "dsa-basics.yaml"
    goal_after = yaml.safe_load(goal_path.read_text(encoding="utf-8"))

    schema = json.loads(GOAL_SCHEMA_PATH.read_text())
    jsonschema.validate(goal_after, schema)

    nodes = goal_after["nodes"]

    # binary-search should be skipped.
    assert nodes["binary-search"]["state"] == "skipped", (
        f"expected 'binary-search' state to be 'skipped'; "
        f"got '{nodes['binary-search']['state']}'. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # graph-traversal should have advanced from pending (now active or completed).
    assert nodes["graph-traversal"]["state"] != "pending", (
        f"expected 'graph-traversal' to advance from 'pending' after skip "
        f"unblocked it; still '{nodes['graph-traversal']['state']}'. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

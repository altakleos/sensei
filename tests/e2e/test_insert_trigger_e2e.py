"""End-to-end verification of the insert trigger against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a topic ("distributed-consensus") at mastery 'none' and a goal with
that single active node. Invokes the tutor with stipulated answers that
fail twice on the same concept, revealing a prerequisite gap — the insert
signal from tutor.md Step 4 (two-failure rule).

Asserts that after the tutor cycle a new prerequisite node has been inserted
into the curriculum (state == "inserted"), proving the two-failure rule fired
and ``mutate_graph.py --operation insert`` was executed.

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
            "distributed-consensus": {
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
        "goal_id": "distributed-systems",
        "expressed_as": "Learn distributed systems for senior engineer interviews",
        "created": _utc_iso(now - timedelta(days=3)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "8 weeks",
            "target_depth": "functional",
        },
        "nodes": {
            "distributed-consensus": {
                "state": "active",
                "prerequisites": [],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "distributed-systems.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _build_prompt() -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root "
        "and follow the boot chain. Dispatch to the `tutor` protocol based on the "
        "learner's message below.\n\n"
        "Execute the tutor protocol in this single turn. Since headless mode cannot "
        "carry a multi-turn conversation, treat the stipulated learner answers below "
        "as the responses to your probes. The learner fails TWICE on the same concept, "
        "revealing a prerequisite gap.\n\n"
        "IMPORTANT: The learner's answers show they cannot understand distributed "
        "consensus because they lack foundational knowledge of network partitions and "
        "failure modes. Per tutor.md Step 4 (two-failure rule), after two failures "
        "where the diagnosis is a prerequisite gap, you MUST insert a new prerequisite "
        "node via mutate_graph.py --operation insert. Update the curriculum file and "
        "stop.\n\n"
        "--- learner message begins ---\n"
        "Teach me about distributed consensus.\n\n"
        "(Treat whatever probes you pose as answered by the following — this is a "
        "single-turn E2E. The learner gives TWO failed attempts:)\n\n"
        "**Learner's answer to first probe about consensus:**\n"
        "\"I think consensus means all the servers agree? Like they vote? I don't "
        "really understand why they can't just talk to each other and agree. Why "
        "would a server disagree?\"\n"
        "**Confidence signal:** uncertain, confused, fundamental misunderstanding.\n\n"
        "(You reshape and try a different angle per Step 4.)\n\n"
        "**Learner's answer to second probe (reshaped) about consensus:**\n"
        "\"I still don't get it. If a server crashes, can't the others just ignore "
        "it? Why do we need a protocol for this? What's a network partition — is "
        "that when the network breaks?\"\n"
        "**Confidence signal:** confused, no improvement, reveals they don't "
        "understand network partitions or failure modes — a prerequisite gap.\n\n"
        "The learner has failed twice. Diagnose: this is a prerequisite gap (the "
        "learner lacks understanding of network fundamentals and failure modes, "
        "which are prerequisites for consensus). Insert the prerequisite node, "
        "update the curriculum file, and stop.\n"
        "--- learner message ends ---\n"
    )


def test_insert_trigger_creates_prerequisite_node(tmp_path: Path) -> None:
    """Verify the two-failure rule inserts a prerequisite node."""
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

    goal_path = tmp_path / "learner" / "goals" / "distributed-systems.yaml"
    goal_after = yaml.safe_load(goal_path.read_text(encoding="utf-8"))

    schema = json.loads(GOAL_SCHEMA_PATH.read_text())
    jsonschema.validate(goal_after, schema)

    nodes = goal_after["nodes"]

    # The original node should still exist.
    assert "distributed-consensus" in nodes, (
        f"original node missing; nodes: {list(nodes)}"
    )

    # A new prerequisite node should have been inserted.
    inserted_nodes = {
        slug: node for slug, node in nodes.items()
        if slug != "distributed-consensus" and node["state"] == "inserted"
    }
    assert len(inserted_nodes) >= 1, (
        f"expected at least 1 inserted prerequisite node after two-failure rule; "
        f"found {len(inserted_nodes)}. all nodes: {list(nodes)}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

"""End-to-end verification of mastery calibration fixes.

Two tests that prove the mastery calibration changes work against a real LLM:

1. A single correct answer no longer completes a topic — the promotion rules
   cap advancement at one level per interaction, and the evidence gate
   requires 3+ attempts at 90%+ accuracy.

2. A deep goal does not skip a known topic after a single probe — deep goals
   require 3 probes (recall + application + transfer) before skipping.

Tier-2 tests per ADR-0011. Skip conditions match the other E2E tests.
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
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Test 1: Single correct answer does NOT complete a topic
# ---------------------------------------------------------------------------


def _seed_test1(instance_dir: Path) -> dict:
    """Seed a functional goal with a topic at mastery 'none', 0 attempts."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "load-balancing": {
                "mastery": "none",
                "confidence": 0.0,
                "last_seen": _utc_iso(now - timedelta(days=365)),
                "attempts": 0,
                "correct": 0,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 2,
        "goal_id": "sys-design-interview",
        "expressed_as": "Prepare for system design interviews",
        "created": _utc_iso(now - timedelta(days=1)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "8 weeks",
            "target_depth": "functional",
        },
        "nodes": {
            "load-balancing": {
                "state": "active",
                "prerequisites": [],
            },
            "caching": {
                "state": "pending",
                "prerequisites": ["load-balancing"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "sys-design-interview.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )
    return profile


def test_single_answer_does_not_complete_topic(tmp_path: Path) -> None:
    """A single correct answer should NOT complete a topic at 'none' mastery.

    The promotion rules cap advancement at one level per interaction (none→shaky
    at best), and the evidence gate requires 3+ attempts. After one interaction,
    the topic should still be active — not completed.
    """
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0

    _seed_test1(tmp_path)

    prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root "
        "and follow the boot chain. Dispatch to the `tutor` protocol based on the "
        "learner's message below.\n\n"
        "Execute the tutor protocol in this single turn. Since headless mode cannot "
        "carry a multi-turn conversation, treat the stipulated learner answer below "
        "as the response to whatever probe you pose.\n\n"
        "IMPORTANT: Follow the mastery promotion rules in Step 5b exactly. A topic "
        "at 'none' mastery can advance at most ONE level per interaction. The evidence "
        "gate in Step 6 requires --min-attempts 3 --min-ratio 0.9. With only one "
        "interaction, the gate MUST fail.\n\n"
        "After teaching and updating the profile, stop.\n\n"
        "--- learner message begins ---\n"
        "Teach me about load balancing.\n\n"
        "(Treat whatever probe you pose as answered by the following — this is a "
        "single-turn E2E, so the learner can't reply twice:)\n\n"
        "**Learner's answer:** \"Load balancing distributes incoming traffic across "
        "multiple servers to ensure no single server is overwhelmed. Common algorithms "
        "include round-robin, least connections, and weighted distribution. It improves "
        "availability and fault tolerance.\"\n\n"
        "**Confidence signal:** direct and clear.\n\n"
        "After updating the profile per Step 5b, attempt the mastery gate in Step 6. "
        "The gate should fail because attempts < 3. Update the profile and stop.\n"
        "--- learner message ends ---\n"
    )

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:3000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    # Check the goal file — load-balancing should NOT be completed.
    goal_path = tmp_path / "learner" / "goals" / "sys-design-interview.yaml"
    goal_after = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
    schema = json.loads(GOAL_SCHEMA_PATH.read_text())
    jsonschema.validate(goal_after, schema)

    node_state = goal_after["nodes"]["load-balancing"]["state"]
    assert node_state == "active", (
        f"expected 'load-balancing' to remain 'active' after one interaction; "
        f"got '{node_state}'. The promotion rules and evidence gate should prevent "
        f"completion after a single answer.\n"
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # Check the profile — mastery should be at most 'shaky' (one level up from none).
    profile_after = yaml.safe_load(
        (tmp_path / "learner" / "profile.yaml").read_text(encoding="utf-8")
    )
    mastery = profile_after["expertise_map"]["load-balancing"]["mastery"]
    assert mastery in ("none", "shaky"), (
        f"expected mastery at most 'shaky' after one interaction (promotion rules: "
        f"max one level per interaction from 'none'); got '{mastery}'.\n"
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )


# ---------------------------------------------------------------------------
# Test 2: Deep goal does NOT skip a known topic after one probe
# ---------------------------------------------------------------------------


def _seed_test2(instance_dir: Path) -> None:
    """Seed a deep goal with a topic the learner already knows at 'solid'."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "consistent-hashing": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now - timedelta(days=3)),
                "attempts": 5,
                "correct": 5,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 2,
        "goal_id": "distributed-systems-deep",
        "expressed_as": "Deeply master distributed systems",
        "created": _utc_iso(now - timedelta(days=7)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "6 months",
            "target_depth": "deep",
        },
        "nodes": {
            "consistent-hashing": {
                "state": "active",
                "prerequisites": [],
            },
            "consensus-protocols": {
                "state": "pending",
                "prerequisites": ["consistent-hashing"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "distributed-systems-deep.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def test_deep_goal_does_not_skip_on_single_probe(tmp_path: Path) -> None:
    """A deep goal should NOT skip a topic after a single correct probe.

    Deep goals require 3 probes (recall + application + transfer) before
    skipping. With only one stipulated answer, the topic should remain active.
    """
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0

    _seed_test2(tmp_path)

    prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root "
        "and follow the boot chain. Dispatch to the `tutor` protocol based on the "
        "learner's message below.\n\n"
        "Execute the tutor protocol in this single turn. Since headless mode cannot "
        "carry a multi-turn conversation, treat the stipulated learner answer below "
        "as the response to your FIRST probe only.\n\n"
        "IMPORTANT: This goal has target_depth 'deep'. Per tutor.md Step 1, deep "
        "goals require THREE probes (recall + application + transfer) before skipping. "
        "You only have ONE stipulated answer. You MUST NOT skip the topic. After the "
        "first probe, note that you need 2 more probes in future sessions. Update the "
        "profile and stop.\n\n"
        "--- learner message begins ---\n"
        "Let's work on consistent hashing.\n\n"
        "(Treat whatever probe you pose as answered by the following — this is a "
        "single-turn E2E, so the learner can't reply twice. You have only ONE "
        "answer, not three:)\n\n"
        "**Learner's answer:** \"Consistent hashing maps both keys and nodes to "
        "positions on a hash ring. Each key is assigned to the next node clockwise. "
        "When a node is added or removed, only K/N keys need to move. Virtual nodes "
        "improve distribution uniformity.\"\n\n"
        "**Confidence signal:** direct, assertive, correct.\n\n"
        "This is only the recall-level probe. You still need application and transfer "
        "probes before you can skip. Do NOT skip. Update the profile and stop.\n"
        "--- learner message ends ---\n"
    )

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:3000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    # Check the goal file — consistent-hashing should NOT be skipped.
    goal_path = tmp_path / "learner" / "goals" / "distributed-systems-deep.yaml"
    goal_after = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
    schema = json.loads(GOAL_SCHEMA_PATH.read_text())
    jsonschema.validate(goal_after, schema)

    node_state = goal_after["nodes"]["consistent-hashing"]["state"]
    assert node_state == "active", (
        f"expected 'consistent-hashing' to remain 'active' in a deep goal after "
        f"only one probe; got '{node_state}'. Deep goals require 3 probes before "
        f"skipping.\n"
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

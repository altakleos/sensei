"""End-to-end verification of the performance-training protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance with a goal that has performance training
active at stage 1 (format-aware understanding). Invokes the LLM with a prompt
that triggers a tutor cycle under performance training conditions.

The performance-training protocol is a phase overlay — it modifies how the
active mode behaves when ``performance_training.active`` is true. At stage 1,
the tutor should frame material in the shape the performance format demands
(interview-style for interview prep).

This test asserts the agent produces output, the profile is updated (attempts
bumped), and the goal file's performance_training state is preserved.

Tier-2 test per ADR-0011.
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
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_instance(instance_dir: Path) -> dict:
    """Populate profile and goal with performance training active at stage 1."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "system-design-basics": {
                "mastery": "shaky",
                "confidence": 0.3,
                "last_seen": _utc_iso(now - timedelta(days=3)),
                "attempts": 2,
                "correct": 1,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")

    goal = {
        "schema_version": 2,
        "goal_id": "interview-prep",
        "expressed_as": "Prepare for system design interviews at L6",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "some",
            "target_state": "clear",
            "constraints": "8 weeks until interview",
            "target_depth": "functional",
        },
        "performance_training": {
            "active": True,
            "stage": 1,
            "format": "technical interview",
            "counters": {
                "automate": 0,
                "verbalize": 0,
                "time_pressure": 0,
                "simulated_eval": 0,
                "full_mock": 0,
            },
        },
        "nodes": {
            "system-design-basics": {"state": "active", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "interview-prep.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )

    return profile


def test_performance_training_stage1_teaches_in_interview_format(
    tmp_path: Path,
) -> None:
    """Verify performance training stage 1 teaches with format-aware framing."""
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    before = _seed_instance(tmp_path)

    prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. The current goal has performance training active at stage 1. "
        "Dispatch to the tutor protocol with the performance-training overlay.\n\n"
        "Execute one teaching cycle. Since headless mode cannot carry a multi-turn "
        "conversation, treat the learner's stipulated answer below as the response to "
        "whatever probe you pose. After teaching, update the profile and stop.\n\n"
        "--- learner message begins ---\n"
        "Teach me about system design basics. I'm preparing for an L6 interview.\n\n"
        "(Treat whatever probe you pose as answered by the following:)\n\n"
        "**Learner's answer:** \"For a URL shortener, I'd start by clarifying requirements: "
        "expected QPS, URL length constraints, analytics needs. Then I'd design the API "
        "endpoints, choose a hash function for short codes, and use a key-value store for "
        "the mapping. For scale, I'd add a cache layer and partition by hash prefix.\"\n\n"
        "**Confidence signal:** direct and structured, uses interview vocabulary.\n\n"
        "After I answer, update my profile and stop.\n"
        "--- learner message ends ---\n"
    )

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:2000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    # Profile should be updated.
    profile_path = tmp_path / "learner" / "profile.yaml"
    after = yaml.safe_load(profile_path.read_text(encoding="utf-8"))

    schema = json.loads(PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(after, schema)

    topic = "system-design-basics"
    topic_entry = after.get("expertise_map", {}).get(topic)
    assert topic_entry is not None, (
        f"expected topic {topic!r} in profile after teaching"
    )
    assert topic_entry["attempts"] > before["expertise_map"][topic]["attempts"], (
        f"attempts for {topic!r} should increase after teaching"
    )

    # Goal's performance_training state should still be active at stage 1.
    goal_path = tmp_path / "learner" / "goals" / "interview-prep.yaml"
    goal_after = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
    pt = goal_after.get("performance_training", {})
    assert pt.get("active") is True, "performance_training should remain active"
    assert pt.get("stage") >= 1, "stage should be >= 1 after one cycle"

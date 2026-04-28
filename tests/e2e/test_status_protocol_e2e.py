"""End-to-end verification of the status protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates the learner profile with
topics at varying staleness, creates a goal with progress, and invokes the
LLM with a prompt that triggers the status protocol.

The status protocol gathers data from profile, curriculum, and decay systems,
then presents a progress narrative. This test asserts the agent produces output
without crashing and does NOT modify the profile (status is read-only).

Tier-2 test per ADR-0011.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main
from tests.e2e.agent_runner import SKIP_REASON, TOOL_AVAILABLE, run_agent

pytestmark = pytest.mark.skipif(not TOOL_AVAILABLE, reason=SKIP_REASON)


def _utc_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_instance(instance_dir: Path) -> dict:
    """Populate profile with mixed-staleness topics and a goal with progress."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "binary-search": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now - timedelta(days=1)),
                "attempts": 5,
                "correct": 4,
            },
            "hash-tables": {
                "mastery": "shaky",
                "confidence": 0.4,
                "last_seen": _utc_iso(now - timedelta(days=14)),
                "attempts": 3,
                "correct": 1,
            },
            "recursion": {
                "mastery": "none",
                "confidence": 0.0,
                "last_seen": _utc_iso(now - timedelta(days=30)),
                "attempts": 1,
                "correct": 0,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")

    goal = {
        "schema_version": 2,
        "goal_id": "dsa-basics",
        "expressed_as": "Learn fundamental data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=30)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "none",
            "target_state": "clear",
            "constraints": "",
            "target_depth": "functional",
        },
        "nodes": {
            "binary-search": {"state": "completed", "prerequisites": []},
            "hash-tables": {"state": "active", "prerequisites": ["binary-search"]},
            "recursion": {"state": "pending", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-basics.yaml").write_text(yaml.safe_dump(goal), encoding="utf-8")

    return profile


def test_status_protocol_reports_progress(tmp_path: Path) -> None:
    """Verify the status protocol produces a progress report without modifying state."""
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    before_profile = _seed_instance(tmp_path)

    prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. The learner is asking about their progress.\n\n"
        "--- learner message begins ---\n"
        "How am I doing? Show me my progress.\n"
        "--- learner message ends ---\n"
    )

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:2000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    # Status is read-only — profile should be unchanged.
    profile_path = tmp_path / "learner" / "profile.yaml"
    after_profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    assert after_profile["expertise_map"] == before_profile["expertise_map"], (
        "status protocol must not modify expertise_map"
    )

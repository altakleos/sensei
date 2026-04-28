"""End-to-end verification of the personality protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates the learner profile, and
invokes the LLM with a prompt designed to trigger personality-governed
behavior: the mentor should refuse to give a direct answer and instead
redirect the learner to work through the problem.

The personality protocol defines the mentor's identity, tone, and forbidden
behaviors (no "Great question!", no giving answers, no coddling). This test
asserts the agent's response does NOT contain forbidden praise tokens and
DOES contain a redirect or question (Socratic behavior).

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


def _seed_instance(instance_dir: Path) -> None:
    """Populate profile and goal so the tutor protocol can engage."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "sorting": {
                "mastery": "shaky",
                "confidence": 0.3,
                "last_seen": _utc_iso(now - timedelta(days=2)),
                "attempts": 2,
                "correct": 1,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 2,
        "goal_id": "algorithms",
        "expressed_as": "Learn sorting algorithms",
        "created": _utc_iso(now - timedelta(days=7)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "some",
            "target_state": "clear",
            "constraints": "",
            "target_depth": "functional",
        },
        "nodes": {
            "sorting": {"state": "active", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "algorithms.yaml").write_text(yaml.safe_dump(goal), encoding="utf-8")


# Forbidden praise tokens from personality.md
_FORBIDDEN_TOKENS = [
    "Great question!",
    "Good question",
    "That's a great question",
    "Great answer!",
    "Nice work!",
    "Well done!",
    "Excellent!",
    "Nice!",
]


def test_personality_refuses_direct_answer_and_avoids_forbidden_praise(
    tmp_path: Path,
) -> None:
    """Verify the mentor refuses to give a direct answer and avoids forbidden tokens."""
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    _seed_instance(tmp_path)

    prompt = (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. Dispatch to the tutor protocol. The personality protocol "
        "is always active.\n\n"
        "--- learner message begins ---\n"
        "Just give me the answer — what's the time complexity of merge sort and why? "
        "Don't make me work through it, just tell me.\n"
        "--- learner message ends ---\n"
    )

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:2000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    output = completed.stdout.lower()

    # The mentor should NOT use forbidden praise tokens.
    for token in _FORBIDDEN_TOKENS:
        assert token.lower() not in output, (
            f"Forbidden praise token found in output: {token!r}"
        )

    # The mentor should redirect — look for question marks (Socratic probing).
    assert "?" in completed.stdout, (
        "Expected the mentor to ask a question (Socratic redirect) instead of "
        "giving a direct answer"
    )

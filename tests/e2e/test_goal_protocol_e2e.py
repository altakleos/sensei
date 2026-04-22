"""End-to-end verification of the goal protocol against a headless LLM agent.

Scaffolds a fresh Sensei instance in a tmp directory, invokes the detected
LLM CLI tool (Claude Code or Kiro) with a boot-chain prompt and the learner
fixture, and asserts the LLM produced a schema-valid goal file under
``learner/goals/``.

This is a Tier-2 check per ADR-0011 — "prose verified by prose" at the LLM
layer. It runs manually before tagging a release (see
``docs/operations/release-playbook.md``), not in default CI. The skip
condition keeps CI green on runners that lack a supported CLI tool or
auth credentials:

1. Neither ``claude`` nor ``kiro-cli`` is on PATH, OR
2. No auth configured (``ANTHROPIC_API_KEY`` / ``SENSEI_E2E`` for Claude;
   ``SENSEI_E2E`` for Kiro).
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main
from tests.e2e.agent_runner import SKIP_REASON, TOOL_AVAILABLE, run_agent

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "sensei"
    / "engine"
    / "schemas"
    / "goal.schema.json"
)
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "learner-wants-rust.md"

pytestmark = pytest.mark.skipif(not TOOL_AVAILABLE, reason=SKIP_REASON)


def _build_prompt(fixture_text: str) -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. Dispatch to the `goal` protocol based on the learner's "
        "message below.\n\n"
        "Execute the goal protocol to completion IN THIS SINGLE TURN. Do not ask clarifying "
        "questions — the fixture already supplies enough context (the three unknowns and "
        "a priority). Write the resulting goal file to `learner/goals/<slug>.yaml` and "
        "finish.\n\n"
        "--- learner message begins ---\n"
        f"{fixture_text}\n"
        "--- learner message ends ---\n"
    )


def test_goal_protocol_produces_schema_valid_goal(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    prompt = _build_prompt(FIXTURE_PATH.read_text(encoding="utf-8"))

    completed = run_agent(prompt, cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    )

    goals_dir = tmp_path / "learner" / "goals"
    goal_files = sorted(goals_dir.glob("*.yaml"))
    assert goal_files, (
        f"No goal file created under {goals_dir}. "
        f"agent stdout:\n{completed.stdout[:4000]}"
    )

    goal_data = yaml.safe_load(goal_files[0].read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text())
    # Raises jsonschema.ValidationError with a useful diagnostic on failure.
    jsonschema.validate(goal_data, schema)

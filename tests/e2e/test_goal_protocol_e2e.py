"""End-to-end verification of the goal protocol against headless Claude Code.

Scaffolds a fresh Sensei instance in a tmp directory, invokes `claude -p` with
a boot-chain prompt and the learner fixture, and asserts the LLM produced a
schema-valid goal file under ``learner/goals/``.

This is a Tier-2 check per ADR-0011 — "prose verified by prose" at the LLM
layer. It runs manually before tagging a release (see
``docs/operations/release-playbook.md``), not in default CI. The two skip
conditions keep CI green on runners that lack either the ``claude`` CLI or
auth credentials:

1. The ``claude`` binary is not on PATH, OR
2. Neither ``ANTHROPIC_API_KEY`` nor ``SENSEI_E2E`` is set (OAuth-only
   Claude Code users opt in via ``SENSEI_E2E=1``).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import jsonschema
import pytest
import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main

CLAUDE_BIN = shutil.which("claude")
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "sensei"
    / "engine"
    / "schemas"
    / "goal.schema.json"
)
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "learner-wants-rust.md"
OPTED_IN = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("SENSEI_E2E"))

pytestmark = [
    pytest.mark.skipif(CLAUDE_BIN is None, reason="headless `claude` CLI not on PATH"),
    pytest.mark.skipif(
        not OPTED_IN,
        reason="set ANTHROPIC_API_KEY or SENSEI_E2E=1 to run the Tier-2 E2E",
    ),
]


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

    assert CLAUDE_BIN is not None  # narrow for mypy; skip above guarantees this
    completed = subprocess.run(
        [
            CLAUDE_BIN,
            "--print",
            "--permission-mode",
            "acceptEdits",
            "--output-format",
            "json",
            prompt,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert completed.returncode == 0, (
        f"claude exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    )

    goals_dir = tmp_path / "learner" / "goals"
    goal_files = sorted(goals_dir.glob("*.yaml"))
    assert goal_files, (
        f"No goal file created under {goals_dir}. "
        f"claude stdout:\n{completed.stdout[:4000]}"
    )

    goal_data = yaml.safe_load(goal_files[0].read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text())
    # Raises jsonschema.ValidationError with a useful diagnostic on failure.
    jsonschema.validate(goal_data, schema)

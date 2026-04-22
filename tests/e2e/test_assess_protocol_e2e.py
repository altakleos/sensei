"""End-to-end verification of the assess protocol against headless Claude Code.

Scaffolds a fresh Sensei instance, pre-populates profile.yaml with one topic
at `developing` mastery, invokes `claude -p` with a boot-chain prompt and a
learner fixture that supplies both the assessment request and a stipulated
correct answer (since `-p` mode is single-turn), and asserts the LLM
updated `learner/profile.yaml` per Step 5 of the protocol.

Second Tier-2 test — complements the `goal` E2E in
`test_goal_protocol_e2e.py`. One data point was an anecdote; two is a
pattern.

Skip conditions match the goal E2E:
  - `claude` binary not on PATH, OR
  - Neither `ANTHROPIC_API_KEY` nor `SENSEI_E2E` is set.
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
    / "profile.schema.json"
)
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "learner-requests-assessment.md"
OPTED_IN = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("SENSEI_E2E"))

pytestmark = [
    pytest.mark.skipif(CLAUDE_BIN is None, reason="headless `claude` CLI not on PATH"),
    pytest.mark.skipif(
        not OPTED_IN,
        reason="set ANTHROPIC_API_KEY or SENSEI_E2E=1 to run the Tier-2 E2E",
    ),
]


def _seed_profile_with_topic(instance_dir: Path, topic: str) -> dict:
    """Overwrite learner/profile.yaml with a profile containing one pre-populated topic
    at mastery 'developing' with attempts=0, correct=0."""
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile = {
        "schema_version": 0,
        "learner_id": "e2e",
        "expertise_map": {
            topic: {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": "2026-04-14T00:00:00Z",
                "attempts": 0,
                "correct": 0,
            }
        },
    }
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return profile


def _build_prompt(fixture_text: str) -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root and "
        "follow the boot chain. Dispatch to the `assess` protocol based on the learner's "
        "message below.\n\n"
        "Execute the protocol END-TO-END in this single turn. Since `-p` mode cannot carry "
        "a multi-turn conversation, treat the fixture's stipulated answer and confidence "
        "signal as the learner's response to whatever assessment question you pose. "
        "Follow every step in order, run the mastery-check script, and update "
        "`learner/profile.yaml` per Step 5. Do not teach, hint, or explain during any "
        "step — the assessor exception is absolute.\n\n"
        "--- learner message begins ---\n"
        f"{fixture_text}\n"
        "--- learner message ends ---\n"
    )


def test_assess_protocol_updates_profile_with_attempts(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    topic = "recursion"
    before = _seed_profile_with_topic(tmp_path, topic)

    prompt = _build_prompt(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert CLAUDE_BIN is not None
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

    profile_path = tmp_path / "learner" / "profile.yaml"
    after = yaml.safe_load(profile_path.read_text(encoding="utf-8"))

    # Schema still valid after the protocol's write.
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.validate(after, schema)

    # The topic entry exists and attempts/correct reflect the assessment.
    topic_entry = after.get("expertise_map", {}).get(topic)
    assert topic_entry is not None, (
        f"expected topic {topic!r} in profile after assessment; got: {after}"
    )
    before_attempts = before["expertise_map"][topic]["attempts"]
    assert topic_entry["attempts"] > before_attempts, (
        f"attempts should increase after assessment; before={before_attempts}, "
        f"after={topic_entry['attempts']}. "
        f"claude stdout head:\n{completed.stdout[:2000]}"
    )
    # The fixture stipulates a correct answer, so correct should be >= 1.
    assert topic_entry["correct"] >= 1, (
        f"correct should be >= 1 after a correct answer; got {topic_entry['correct']}. "
        f"claude stdout head:\n{completed.stdout[:2000]}"
    )
    # last_seen should have advanced — simple sentinel: different from the seeded value.
    assert topic_entry["last_seen"] != before["expertise_map"][topic]["last_seen"], (
        "last_seen should update per Step 5 of the protocol"
    )

"""End-to-end verification of the hints triage protocol.

Scaffolds a fresh Sensei instance, pre-populates `learner/inbox/` with two
representative hint files (a Rust ownership blog post and a Tokio async
snippet — both scoped to the same learning goal as the goal E2E), invokes
the detected LLM CLI tool (Claude Code or Kiro) with a boot-chain prompt
that dispatches to the `hints` protocol, and asserts the triage artifact:
`learner/hints/hints.yaml` has at least one registered hint and the inbox
has been drained.

Third Tier-2 E2E — completes the hints ADR graduation loop (ADR-0017 /
-0018 / -0019) with live behavioural evidence. Tier-1 coverage already
lives in `tests/transcripts/hints.md`; this fixture moves the hints
protocol from "fixture-verified lexically" to "fixture-verified +
artifact-verified end-to-end."

Skip conditions match the other two Tier-2 E2Es:
  - Neither ``claude`` nor ``kiro-cli`` on PATH, OR
  - No auth configured (see ``agent_runner.py`` for details).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main
from tests.e2e.agent_runner import SKIP_REASON, TOOL_AVAILABLE, run_agent

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inbox-rust-hints"

pytestmark = pytest.mark.skipif(not TOOL_AVAILABLE, reason=SKIP_REASON)


def _seed_inbox(instance_dir: Path) -> list[Path]:
    """Copy fixture hint files into learner/inbox/. Returns the list of seeded paths."""
    inbox = instance_dir / "learner" / "inbox"
    seeded: list[Path] = []
    for src in sorted(FIXTURE_DIR.glob("*.md")):
        if src.name == "README.md":  # the fixture's own README is metadata, not a hint
            continue
        dst = inbox / src.name
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        seeded.append(dst)
    return seeded


def _build_prompt() -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root "
        "and follow the boot chain. The learner just said:\n\n"
        "    process my hints\n\n"
        "Dispatch to the `hints` triage protocol and execute it to completion. "
        "Treat every markdown file under `learner/inbox/` as a hint the learner "
        "dropped (except any file explicitly named README.md, which is fixture "
        "metadata). For each hint: classify, score relevance, register into "
        "`learner/hints/hints.yaml`, and move the file from `learner/inbox/` to "
        "`learner/hints/active/` or `learner/hints/archive/` as the protocol "
        "directs. Do not teach or explain hint content — this is administrative "
        "triage, not a tutor session.\n"
    )


def test_hints_protocol_drains_inbox_and_populates_registry(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    seeded = _seed_inbox(tmp_path)
    assert len(seeded) >= 2, f"expected ≥2 seeded inbox files, got {len(seeded)}"
    inbox_dir = tmp_path / "learner" / "inbox"
    hints_registry = tmp_path / "learner" / "hints" / "hints.yaml"

    before = yaml.safe_load(hints_registry.read_text(encoding="utf-8"))
    assert before == {"schema_version": 0, "hints": []}, (
        f"registry should start empty post-init, got: {before}"
    )

    completed = run_agent(_build_prompt(), cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout head:\n{completed.stdout[:2000]}\n\nstderr:\n{completed.stderr}"
    )

    # Primary artifact assertion: hints.yaml has grown.
    after = yaml.safe_load(hints_registry.read_text(encoding="utf-8"))
    assert isinstance(after, dict), f"hints.yaml no longer a mapping: {after!r}"
    assert "hints" in after, f"hints.yaml missing 'hints' key after triage: {after!r}"
    assert len(after["hints"]) >= 1, (
        f"expected at least 1 hint registered after triage; got {len(after['hints'])}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # Secondary assertion: inbox drained. Seeded files moved to active/ or archive/.
    remaining_inbox = [
        p for p in inbox_dir.glob("*") if p.is_file() and p.name != ".gitkeep"
    ]
    assert not remaining_inbox, (
        f"expected inbox to be drained after triage; still has: "
        f"{[p.name for p in remaining_inbox]}"
    )

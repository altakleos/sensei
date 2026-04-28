"""Tests for scripts/teaching_density.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sensei.engine.scripts.teaching_density import (
    compute_teaching_density,
    compute_teaching_stats,
    main,
)


# --- Pure-function behaviour ---


def test_no_teaching_tokens_zero_density() -> None:
    text = "[MENTOR] What's next?\n[LEARNER] hash maps\n"
    stats = compute_teaching_stats(text)
    assert stats["mentor_turns"] == 1
    assert stats["teaching_token_count"] == 0
    assert stats["teaching_density"] == 0.0


def test_let_me_explain_counts() -> None:
    text = "[MENTOR] Let me explain how recursion works.\n[LEARNER] ok\n"
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 1
    assert stats["teaching_density"] == pytest.approx(1.0)


def test_the_answer_is_variants_count() -> None:
    """`the answer is` / `the correct answer is` / `the right answer is` all match."""
    text = (
        "[MENTOR] The answer is 42.\n"
        "[LEARNER] hmm\n"
        "[MENTOR] The correct answer is actually 43.\n"
        "[LEARNER] ok\n"
        "[MENTOR] The right answer is 44.\n"
        "[LEARNER] confused\n"
    )
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 3


def test_multi_token_single_turn() -> None:
    """A turn with multiple teaching tokens counts each."""
    text = "[MENTOR] Let me explain. Think about this. The answer is X.\n[LEARNER] ok\n"
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 3
    assert stats["mentor_turns"] == 1
    assert stats["teaching_density"] == pytest.approx(3.0)


def test_density_averages_across_turns() -> None:
    """Two turns: turn 1 has 2 tokens, turn 2 has 0 → density 1.0."""
    text = (
        "[MENTOR] Let me explain. Think about this.\n"
        "[LEARNER] ok\n"
        "[MENTOR] Now what?\n"
        "[LEARNER] dunno\n"
    )
    stats = compute_teaching_stats(text)
    assert stats["mentor_turns"] == 2
    assert stats["teaching_token_count"] == 2
    assert stats["teaching_density"] == pytest.approx(1.0)


def test_learner_teaching_tokens_ignored() -> None:
    """Only the mentor's teaching tokens count."""
    text = (
        "[MENTOR] What do you think?\n"
        "[LEARNER] Let me explain my reasoning. The answer is X.\n"
    )
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 0


def test_token_in_code_fence_ignored() -> None:
    """A teaching phrase inside a fenced code block must not count.

    Framing prose ("look at this code:") is deliberately benign so the
    only teaching tokens in the input are inside the fence.
    """
    text = (
        "[MENTOR] look at this code:\n"
        "```python\n# the answer is 42, but let me explain why\nfn()\n```\nproceed.\n"
        "[LEARNER] ok\n"
    )
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 0


def test_token_in_frontmatter_ignored() -> None:
    """Frontmatter is stripped before turn extraction; teaching there doesn't count."""
    text = (
        "---\n"
        "note: \"let me explain the format\"\n"
        "---\n"
        "[MENTOR] What's next?\n[LEARNER] yes\n"
    )
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 0


def test_case_insensitive_matching() -> None:
    """Patterns match regardless of case."""
    text = "[MENTOR] LET ME EXPLAIN. think about this.\n[LEARNER] ok\n"
    stats = compute_teaching_stats(text)
    assert stats["teaching_token_count"] == 2


def test_actually_comma_pattern_specific() -> None:
    """`actually,` matches; bare `actually` (no comma) doesn't, to avoid false positives."""
    text = (
        "[MENTOR] Actually, let me reconsider.\n"
        "[LEARNER] ok\n"
        "[MENTOR] You actually might be right about that.\n"
        "[LEARNER] hmm\n"
    )
    stats = compute_teaching_stats(text)
    # First turn: matches "actually," AND "let me" — but "let me" alone isn't
    # in the taxonomy; "let me explain" is. Just "actually," matches → 1.
    assert stats["teaching_token_count"] == 1


def test_no_mentor_turns_yields_zero() -> None:
    text = "[LEARNER] hi\n"
    stats = compute_teaching_stats(text)
    assert stats["mentor_turns"] == 0
    assert stats["teaching_density"] == 0.0


def test_empty_string_yields_zero() -> None:
    stats = compute_teaching_stats("")
    assert stats == {
        "mentor_turns": 0,
        "teaching_token_count": 0,
        "teaching_density": 0.0,
    }


def test_compute_teaching_density_convenience() -> None:
    text = "[MENTOR] Let me explain.\n[LEARNER] ok\n[MENTOR] What's next?\n[LEARNER] dunno\n"
    assert compute_teaching_density(text) == pytest.approx(0.5)


# --- CLI entry point ---


def test_main_writes_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    transcript = tmp_path / "t.dogfood.md"
    transcript.write_text("[MENTOR] Let me explain.\n[LEARNER] ok\n", encoding="utf-8")
    rc = main(["--transcript", str(transcript)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["mentor_turns"] == 1
    assert parsed["teaching_token_count"] == 1
    assert parsed["teaching_density"] == pytest.approx(1.0)


def test_main_missing_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--transcript", str(tmp_path / "nope.md")])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert "not found" in parsed["error"]


def test_main_no_mentor_turns_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = tmp_path / "learner_only.md"
    transcript.write_text("[LEARNER] hi\n", encoding="utf-8")
    rc = main(["--transcript", str(transcript)])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert "no [MENTOR] turns" in parsed["error"]


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Mirrors the silence_ratio / question_density siblings."""
    transcript = tmp_path / "t.dogfood.md"
    transcript.write_text("[MENTOR] The answer is 42.\n[LEARNER] ok\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "sensei.engine.scripts.teaching_density", "--transcript", str(transcript)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["teaching_token_count"] == 1

"""Tests for scripts/question_density.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sensei.engine.scripts.question_density import (
    compute_question_density,
    compute_question_stats,
    main,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRANSCRIPTS_DIR = _REPO_ROOT / "tests" / "transcripts"


# --- Pure-function behaviour ---


def test_no_questions_zero_density() -> None:
    text = "[MENTOR] hello world\n[LEARNER] yes\n"
    stats = compute_question_stats(text)
    assert stats["mentor_turns"] == 1
    assert stats["mentor_questions"] == 0
    assert stats["question_density"] == 0.0


def test_one_question_per_turn() -> None:
    text = "[MENTOR] What's next?\n[LEARNER] hash maps\n"
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 1
    assert stats["question_density"] == pytest.approx(1.0)


def test_multi_question_single_turn() -> None:
    text = "[MENTOR] Why? What if?\n[LEARNER] hmm\n"
    stats = compute_question_stats(text)
    assert stats["mentor_turns"] == 1
    assert stats["mentor_questions"] == 2
    assert stats["question_density"] == pytest.approx(2.0)


def test_density_averages_across_turns() -> None:
    """One Q in turn 1, two in turn 2 → density 1.5."""
    text = "[MENTOR] What?\n[LEARNER] dunno\n[MENTOR] Why? How?\n[LEARNER] still no\n"
    stats = compute_question_stats(text)
    assert stats["mentor_turns"] == 2
    assert stats["mentor_questions"] == 3
    assert stats["question_density"] == pytest.approx(1.5)


def test_learner_questions_ignored() -> None:
    """Only the mentor's questions count toward density."""
    text = (
        "[MENTOR] tell me what you know.\n"
        "[LEARNER] what about hash maps? where do I start?\n"
    )
    stats = compute_question_stats(text)
    assert stats["mentor_turns"] == 1
    assert stats["mentor_questions"] == 0


def test_question_in_code_fence_ignored() -> None:
    """A ? inside a fenced code block must not count."""
    text = (
        "[MENTOR] consider this:\n"
        "```python\n# What does this do?\nfn()\n```\nproceed.\n"
        "[LEARNER] ok\n"
    )
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 0


def test_question_in_frontmatter_ignored() -> None:
    """Frontmatter is stripped before turn extraction; ? there doesn't count."""
    text = (
        "---\n"
        "title: \"is this a question?\"\n"
        "---\n"
        "[MENTOR] hello\n[LEARNER] yes\n"
    )
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 0


def test_emphatic_double_question_counts_once() -> None:
    """`Really??` is one rhetorical question, not two."""
    text = "[MENTOR] Really??\n[LEARNER] sure\n"
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 1


def test_emphatic_triple_question_counts_once() -> None:
    """`What???` is also one question."""
    text = "[MENTOR] What???\n[LEARNER] yeah\n"
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 1


def test_question_followed_by_exclamation_counts() -> None:
    """`?!` is rhetorical-emphatic; one question."""
    text = "[MENTOR] Are you sure?!\n[LEARNER] yes\n"
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 1


def test_question_mark_inside_word_does_not_count() -> None:
    """A ? not at sentence-boundary (e.g. ?fragment) doesn't count."""
    text = "[MENTOR] the path /tmp/?fragment is unusual.\n[LEARNER] ok\n"
    stats = compute_question_stats(text)
    assert stats["mentor_questions"] == 0


def test_no_mentor_turns_yields_zero() -> None:
    text = "[LEARNER] hi\n"
    stats = compute_question_stats(text)
    assert stats["mentor_turns"] == 0
    assert stats["question_density"] == 0.0


def test_empty_string_yields_zero() -> None:
    stats = compute_question_stats("")
    assert stats == {
        "mentor_turns": 0,
        "mentor_questions": 0,
        "question_density": 0.0,
    }


def test_compute_question_density_convenience() -> None:
    text = "[MENTOR] What?\n[LEARNER] hi\n[MENTOR] Why?\n[LEARNER] dunno\n"
    assert compute_question_density(text) == pytest.approx(1.0)


# --- CLI entry point ---


def test_main_writes_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    transcript = tmp_path / "t.dogfood.md"
    transcript.write_text("[MENTOR] What?\n[LEARNER] hi\n", encoding="utf-8")
    rc = main(["--transcript", str(transcript)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["mentor_turns"] == 1
    assert parsed["mentor_questions"] == 1
    assert parsed["question_density"] == pytest.approx(1.0)


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
    """Mirrors the silence_ratio sibling: protocols invoke via shell subprocess."""
    transcript = tmp_path / "t.dogfood.md"
    transcript.write_text("[MENTOR] Why?\n[LEARNER] dunno\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "sensei.engine.scripts.question_density", "--transcript", str(transcript)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["question_density"] == pytest.approx(1.0)

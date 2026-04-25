"""Tests for scripts/silence_ratio.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sensei.engine.scripts.silence_ratio import (
    compute_turn_stats,
    compute_word_share,
    main,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRANSCRIPTS_DIR = _REPO_ROOT / "tests" / "transcripts"


# --- Pure-function behaviour ---


def test_balanced_transcript() -> None:
    text = "[MENTOR] one two three\n[LEARNER] alpha beta gamma\n"
    stats = compute_turn_stats(text)
    assert stats["mentor_words"] == 3
    assert stats["learner_words"] == 3
    assert stats["mentor_word_share"] == pytest.approx(0.5)
    assert stats["mentor_turns"] == 1
    assert stats["learner_turns"] == 1


def test_mentor_dominates() -> None:
    text = "[MENTOR] " + "word " * 9 + "\n[LEARNER] one\n"
    stats = compute_turn_stats(text)
    assert stats["mentor_word_share"] == pytest.approx(0.9)


def test_no_learner_turns() -> None:
    """A transcript with only mentor turns yields share 1.0 (degenerate but valid)."""
    text = "[MENTOR] hello world\n[MENTOR] another turn here\n"
    stats = compute_turn_stats(text)
    assert stats["mentor_turns"] == 2
    assert stats["learner_turns"] == 0
    assert stats["mentor_word_share"] == pytest.approx(1.0)


def test_no_mentor_turns() -> None:
    text = "[LEARNER] hello\n[LEARNER] another\n"
    stats = compute_turn_stats(text)
    assert stats["mentor_word_share"] == pytest.approx(0.0)


def test_empty_string() -> None:
    """Degenerate empty input yields zero counts and 0.0 share."""
    stats = compute_turn_stats("")
    assert stats == {
        "mentor_words": 0,
        "learner_words": 0,
        "mentor_word_share": 0.0,
        "mentor_turns": 0,
        "learner_turns": 0,
    }


def test_punctuation_does_not_count_as_words() -> None:
    """Word-share must not be skewed by who uses more punctuation."""
    text = "[MENTOR] yes!!!.??\n[LEARNER] yes\n"
    stats = compute_turn_stats(text)
    assert stats["mentor_words"] == 1
    assert stats["learner_words"] == 1


def test_frontmatter_is_stripped() -> None:
    text = (
        "---\n"
        "protocol: assess\n"
        "agent: claude\n"
        "---\n"
        "[MENTOR] hello\n[LEARNER] world\n"
    )
    stats = compute_turn_stats(text)
    assert stats["mentor_words"] == 1
    assert stats["learner_words"] == 1


def test_multiline_turns_accumulate() -> None:
    text = (
        "[MENTOR] line one\n"
        "line two\n"
        "[LEARNER] response\n"
    )
    stats = compute_turn_stats(text)
    assert stats["mentor_words"] == 4  # "line one line two"
    assert stats["learner_words"] == 1
    assert stats["mentor_turns"] == 1


def test_compute_word_share_convenience() -> None:
    text = "[MENTOR] one\n[LEARNER] one two three\n"
    assert compute_word_share(text) == pytest.approx(0.25)


# --- CLI entry point ---


def test_main_writes_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    transcript = tmp_path / "t.dogfood.md"
    transcript.write_text("[MENTOR] hi\n[LEARNER] yes\n", encoding="utf-8")
    rc = main(["--transcript", str(transcript)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["mentor_words"] == 1
    assert parsed["learner_words"] == 1


def test_main_missing_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--transcript", str(tmp_path / "nope.md")])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert "not found" in parsed["error"]


def test_main_empty_transcript_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = tmp_path / "empty.md"
    transcript.write_text("", encoding="utf-8")
    rc = main(["--transcript", str(transcript)])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert "no [MENTOR] or [LEARNER] turns" in parsed["error"]


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Protocols invoke this helper via .sensei/run, which is shell subprocess."""
    transcript = tmp_path / "t.dogfood.md"
    transcript.write_text("[MENTOR] one\n[LEARNER] two three\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "sensei.engine.scripts.silence_ratio", "--transcript", str(transcript)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["mentor_word_share"] == pytest.approx(1 / 3)


# --- Calibration: every shipped dogfood transcript stays inside its band ---
#
# These pin the bands declared in `tests/transcripts/<protocol>.md` fixture
# frontmatter. If a future dogfood capture drifts above the ceiling, the
# fixture-level assertion in `tests/transcripts/test_fixtures.py` catches
# it. This test is the lower-level guard: the helper itself must produce
# stable values for the committed transcripts.


@pytest.mark.parametrize(
    "transcript_name,max_share",
    [
        ("assess.dogfood.md", 0.80),
        ("review.dogfood.md", 0.75),
        ("hints.dogfood.md", 0.95),
        ("performance_training.dogfood.md", 0.95),
        ("cross_goal_review.dogfood.md", 0.55),
    ],
)
def test_shipped_dogfood_within_band(transcript_name: str, max_share: float) -> None:
    path = _TRANSCRIPTS_DIR / transcript_name
    if not path.is_file():
        pytest.skip(f"transcript not committed: {path}")
    share = compute_word_share(path.read_text(encoding="utf-8"))
    assert share <= max_share, (
        f"{transcript_name}: mentor word-share {share:.3f} exceeds band ceiling {max_share:.2f}. "
        f"Either the dogfood drifted (re-capture) or the band is wrong (widen)."
    )

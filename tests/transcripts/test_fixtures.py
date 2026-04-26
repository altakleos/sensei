"""Runs transcript-fixture assertions against committed dogfood transcripts.

The heavy lifting (discovery, parametrization, turn extraction) lives in
`conftest.py`. This module provides only the assertion function that runs
per parametrised `transcript_case`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from sensei.engine.scripts.question_density import compute_question_density
from sensei.engine.scripts.silence_ratio import compute_word_share
from sensei.engine.scripts.teaching_density import compute_teaching_density

from .conftest import extract_mentor_turns


def test_transcript_fixture(transcript_case: tuple[str, Path, Path, dict[str, Any]]) -> None:
    case_id, fixture_path, dogfood_path, fixture = transcript_case

    if not dogfood_path.is_file():
        pytest.fail(
            f"No dogfood transcript at {dogfood_path.name}. "
            f"Fixture {case_id!r} must be captured before this fixture lands. "
            f"See docs/design/transcript-fixtures.md § Cadence."
        )

    dogfood_text = dogfood_path.read_text(encoding="utf-8")
    mentor_turns = extract_mentor_turns(dogfood_text)
    assert mentor_turns, f"no [MENTOR] turns found in {dogfood_path}"

    forbidden = fixture.get("forbidden_phrases") or []
    for phrase in forbidden:
        for turn in mentor_turns:
            assert phrase not in turn, (
                f"forbidden phrase {phrase!r} appeared in a mentor turn of "
                f"{dogfood_path.name}. Turn: {turn!r}"
            )

    one_of = fixture.get("required_one_of") or []
    if one_of:
        matched = any(
            re.search(pattern, turn, flags=re.MULTILINE)
            for pattern in one_of
            for turn in mentor_turns
        )
        assert matched, (
            f"no mentor turn in {dogfood_path.name} matches any required_one_of "
            f"pattern {one_of!r}. Mentor turns: {mentor_turns!r}"
        )

    all_of = fixture.get("required_all_of") or []
    for pattern in all_of:
        matched = any(
            re.search(pattern, turn, flags=re.MULTILINE) for turn in mentor_turns
        )
        assert matched, (
            f"required_all_of pattern {pattern!r} did not match any mentor turn in "
            f"{dogfood_path.name}. Mentor turns: {mentor_turns!r}"
        )

    # Per-fixture silence-ratio band: the mentor's word-share against the
    # learner. Optional — fixtures without `silence_ratio:` are unchanged.
    silence = fixture.get("silence_ratio") or {}
    if silence:
        share = compute_word_share(dogfood_text)
        lo = silence.get("min")
        hi = silence.get("max")
        if lo is not None:
            assert share >= lo, (
                f"silence_ratio: mentor word-share {share:.3f} below min {lo} in "
                f"{dogfood_path.name}. The mentor is too quiet for this protocol; "
                f"either re-capture or relax the band."
            )
        if hi is not None:
            assert share <= hi, (
                f"silence_ratio: mentor word-share {share:.3f} above max {hi} in "
                f"{dogfood_path.name}. The mentor is talking too much for this protocol; "
                f"either re-capture or widen the band (and explain why)."
            )

    # Per-fixture question-density band: mentor questions per mentor turn.
    # Catches Socratic-stance regressions (mentor stops asking, starts
    # lecturing) that silence_ratio would miss because total mentor word-
    # count stays comparable. Optional — fixtures without `question_density:`
    # are unchanged. Per docs/plans/question-density-metric.md.
    density_band = fixture.get("question_density") or {}
    if density_band:
        density = compute_question_density(dogfood_text)
        lo = density_band.get("min")
        hi = density_band.get("max")
        if lo is not None:
            assert density >= lo, (
                f"question_density: mentor density {density:.3f} below min {lo} in "
                f"{dogfood_path.name}. The mentor isn't asking enough for this protocol "
                f"— Socratic stance regressed toward lecture mode. Either re-capture or "
                f"relax the band (and explain why)."
            )
        if hi is not None:
            assert density <= hi, (
                f"question_density: mentor density {density:.3f} above max {hi} in "
                f"{dogfood_path.name}. The mentor is over-questioning for this protocol "
                f"— a narrative protocol drifted toward interrogation. Either re-capture "
                f"or widen the band (and explain why)."
            )

    # Per-fixture teaching-density band: count of canonical teaching-token
    # appearances per mentor turn. Closes the assessor-exception adherence
    # gap (audit Risk #4). For protocols where teaching is forbidden
    # (assess, review, challenger, reviewer, cross_goal_review, status,
    # hints), the band is `max: 0.0` — any teaching token signals a
    # regression. Optional — fixtures without `teaching_density:` are
    # unchanged. Per docs/plans/teaching-density-metric.md.
    teaching_band = fixture.get("teaching_density") or {}
    if teaching_band:
        teaching = compute_teaching_density(dogfood_text)
        hi = teaching_band.get("max")
        if hi is not None:
            assert teaching <= hi, (
                f"teaching_density: mentor density {teaching:.3f} above max {hi} in "
                f"{dogfood_path.name}. Teaching language appeared in a protocol where "
                f"teaching is forbidden — assessor-exception or no-reteach regression. "
                f"Either re-capture (preferred) or document the loosening with a "
                f"comment naming why the new ceiling is justified."
            )

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

from sensei.engine.scripts.silence_ratio import compute_word_share

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

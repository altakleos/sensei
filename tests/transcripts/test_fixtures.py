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

from .conftest import extract_mentor_turns


def test_transcript_fixture(transcript_case: tuple[str, Path, Path, dict[str, Any]]) -> None:
    case_id, fixture_path, dogfood_path, fixture = transcript_case

    if not dogfood_path.is_file():
        pytest.skip(
            f"No dogfood transcript at {dogfood_path.name}. "
            f"Fixture {case_id!r} cannot be evaluated until a session is captured. "
            f"See docs/design/transcript-fixtures.md § Cadence."
        )

    mentor_turns = extract_mentor_turns(dogfood_path.read_text(encoding="utf-8"))
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

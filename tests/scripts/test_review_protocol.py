"""Integration tests for the review protocol's orchestration primitives.

These tests do NOT exercise the LLM's interpretation of the prose-as-code
protocol file. They do verify that the helpers the protocol invokes
compose correctly when driven in the sequence `review.md` specifies: read
profile, enumerate stale topics via decay, rank stale-first, classify the
response, apply the v1 update rule, re-validate.

Behavioural correctness of the prose itself requires dogfood testing with
a real LLM agent and is out of scope for pytest.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
import yaml

from sensei.engine.scripts.check_profile import validate_profile
from sensei.engine.scripts.classify_confidence import classify
from sensei.engine.scripts.decay import freshness

HALF_LIFE = 7.0
STALE = 0.5


def _utc(days_ago: int, now: datetime) -> str:
    return (now - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _profile_with(topics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": topics,
    }


def _topic(mastery: str, last_seen: str, attempts: int = 0, correct: int = 0, confidence: float = 0.5) -> dict:
    return {
        "mastery": mastery,
        "confidence": confidence,
        "last_seen": last_seen,
        "attempts": attempts,
        "correct": correct,
    }


def _enumerate_stale(profile: dict, now: datetime) -> list[tuple[str, float]]:
    """Simulate Step 2+3+4 of the protocol: rank stale topics by freshness ascending."""
    results: list[tuple[str, float]] = []
    for slug, state in profile["expertise_map"].items():
        last_seen_str = state["last_seen"].replace("Z", "+00:00")
        last_seen = datetime.fromisoformat(last_seen_str)
        r = freshness(last_seen=last_seen, half_life_days=HALF_LIFE, now=now, stale_threshold=STALE)
        if r["stale"]:
            results.append((slug, float(r["freshness"])))
    # Stale-first: lowest freshness first, ties broken by earliest last_seen.
    results.sort(key=lambda item: (item[1], profile["expertise_map"][item[0]]["last_seen"]))
    return results


def _apply_update(profile: dict, slug: str, correctness: str, now: datetime) -> dict:
    """Apply the V1 update rule from step 7 to a deep copy of the profile."""
    updated = yaml.safe_load(yaml.safe_dump(profile))  # simple deep copy
    state = updated["expertise_map"][slug]
    state["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    state["attempts"] += 1
    if correctness == "correct":
        state["correct"] += 1
    # mastery and confidence deliberately unchanged per design doc.
    return updated


def test_empty_profile_yields_no_stale() -> None:
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    profile = _profile_with({})
    assert _enumerate_stale(profile, now) == []


def test_fresh_topic_is_not_stale() -> None:
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    profile = _profile_with({
        "recursion": _topic(mastery="solid", last_seen=_utc(1, now)),
    })
    assert _enumerate_stale(profile, now) == []


def test_stale_ranking_by_freshness_ascending() -> None:
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    profile = _profile_with({
        # fresh — not stale
        "fresh": _topic(mastery="solid", last_seen=_utc(1, now)),
        # 14 days old → freshness ~0.25 (very stale)
        "most-stale": _topic(mastery="solid", last_seen=_utc(14, now)),
        # 10 days old → freshness ~0.37
        "medium-stale": _topic(mastery="developing", last_seen=_utc(10, now)),
        # 8 days old → freshness ~0.45
        "least-stale": _topic(mastery="shaky", last_seen=_utc(8, now)),
    })
    ranking = _enumerate_stale(profile, now)
    slugs = [slug for slug, _ in ranking]
    assert slugs == ["most-stale", "medium-stale", "least-stale"]
    # All freshness scores below the threshold.
    assert all(f < STALE for _, f in ranking)


def test_tie_break_by_earliest_last_seen() -> None:
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    # Both 14 days stale but different timestamps on that day.
    a_last = (now - timedelta(days=14, hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    b_last = (now - timedelta(days=14, hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    profile = _profile_with({
        "a": _topic(mastery="solid", last_seen=a_last),
        "b": _topic(mastery="solid", last_seen=b_last),
    })
    ranking = _enumerate_stale(profile, now)
    # 'a' has earlier last_seen, should rank first on tie.
    assert [slug for slug, _ in ranking] == ["a", "b"]


def test_happy_path_update_cycle() -> None:
    """Simulate a full review of one topic, correct+confident."""
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    profile = _profile_with({
        "recursion": _topic(mastery="solid", last_seen=_utc(14, now), attempts=3, correct=2, confidence=0.7),
    })
    ranking = _enumerate_stale(profile, now)
    assert ranking[0][0] == "recursion"

    quadrant = classify("confident", "correct")
    assert quadrant["quadrant"] == "mastery"

    updated = _apply_update(profile, "recursion", "correct", now)
    topic = updated["expertise_map"]["recursion"]
    assert topic["attempts"] == 4
    assert topic["correct"] == 3
    assert topic["mastery"] == "solid"          # unchanged per design
    assert topic["confidence"] == 0.7           # unchanged per design
    # last_seen was refreshed.
    assert topic["last_seen"].startswith(now.strftime("%Y-%m-%d"))

    status, errors = validate_profile(updated)
    assert status == "ok", errors


def test_incorrect_response_does_not_bump_correct() -> None:
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    profile = _profile_with({
        "bfs": _topic(mastery="shaky", last_seen=_utc(14, now), attempts=2, correct=1),
    })
    updated = _apply_update(profile, "bfs", "incorrect", now)
    topic = updated["expertise_map"]["bfs"]
    assert topic["attempts"] == 3
    assert topic["correct"] == 1               # unchanged
    status, errors = validate_profile(updated)
    assert status == "ok", errors


def test_update_preserves_cross_field_invariant() -> None:
    """Under any sequence of updates, correct never exceeds attempts."""
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    profile = _profile_with({
        "t": _topic(mastery="shaky", last_seen=_utc(14, now), attempts=0, correct=0),
    })
    # 10 rounds alternating correct/incorrect.
    for i in range(10):
        correctness = "correct" if i % 2 == 0 else "incorrect"
        profile = _apply_update(profile, "t", correctness, now + timedelta(minutes=i))
    topic = profile["expertise_map"]["t"]
    assert topic["attempts"] == 10
    assert topic["correct"] == 5
    assert topic["correct"] <= topic["attempts"]
    status, errors = validate_profile(profile)
    assert status == "ok", errors


def test_classifier_labels_align_with_update_rule() -> None:
    """All four quadrants produce valid updates under the v1 rule."""
    now = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    base = _profile_with({
        "x": _topic(mastery="developing", last_seen=_utc(14, now), attempts=0, correct=0),
    })
    for confidence in ("confident", "uncertain"):
        for correctness in ("correct", "incorrect"):
            classify(confidence, correctness)  # sanity: no ValueError
            updated = _apply_update(base, "x", correctness, now)
            status, errors = validate_profile(updated)
            assert status == "ok", (confidence, correctness, errors)

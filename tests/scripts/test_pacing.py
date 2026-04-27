"""Tests for scripts/pacing.py.

Covers compute_pacing (velocity, projection, pace status) and CLI main().
"""

from __future__ import annotations

from datetime import datetime, timezone

import yaml

from sensei.engine.scripts.pacing import compute_pacing, main

NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)
CREATED = "2026-05-01T00:00:00Z"


def _nodes(*completed_isos: str, remaining: int = 0) -> dict[str, dict]:
    """Build a nodes dict with *completed_isos* completed and *remaining* incomplete."""
    nodes: dict[str, dict] = {}
    for i, iso in enumerate(completed_isos):
        nodes[f"done-{i}"] = {"state": "completed", "completed_at": iso}
    for j in range(remaining):
        nodes[f"todo-{j}"] = {"state": "not_started"}
    return nodes


# ── T7: unit tests for compute_pacing ────────────────────────────────────


def test_zero_completions_returns_null_velocity() -> None:
    nodes = _nodes(remaining=5)
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r["velocity_topics_per_day"] is None
    assert r["projected_completion"] is None
    assert r["completed_count"] == 0
    assert r["remaining_count"] == 5


def test_single_completion_uses_created_as_anchor() -> None:
    # 1 node completed 10 days after created → velocity = 1/10 = 0.1
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=9)
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r["velocity_topics_per_day"] == 0.1
    assert r["completed_count"] == 1
    assert r["remaining_count"] == 9


def test_multiple_completions_weighted_velocity() -> None:
    # 3 completions: day 5, day 10, day 15 after created.
    # Intervals: [5, 5] days. With uniform intervals, velocity = 1/5 = 0.2.
    nodes = _nodes(
        "2026-05-06T00:00:00Z",
        "2026-05-11T00:00:00Z",
        "2026-05-16T00:00:00Z",
        remaining=2,
    )
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r["velocity_topics_per_day"] == 0.2
    assert r["completed_count"] == 3


def test_recency_decay_weights_recent_more() -> None:
    # Intervals: old=10 days, recent=2 days.
    # Lower decay → more weight on recent → higher velocity.
    nodes = _nodes(
        "2026-05-11T00:00:00Z",  # 10 days after created
        "2026-05-21T00:00:00Z",  # +10 days
        "2026-05-23T00:00:00Z",  # +2 days
        remaining=2,
    )
    r_high_decay = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW, recency_decay=0.9)
    r_low_decay = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW, recency_decay=0.1)
    # Low decay → recent interval (2d) dominates → higher velocity.
    assert r_low_decay["velocity_topics_per_day"] > r_high_decay["velocity_topics_per_day"]


def test_review_overhead_reduces_velocity() -> None:
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=4)
    # Profile with a stale topic (stability=1 → freshness decays fast).
    profile = {"topic-a": {"stability": 1.0}}
    r_with = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=profile, now=NOW)
    r_without = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r_with["velocity_topics_per_day"] < r_without["velocity_topics_per_day"]


def test_no_profile_skips_review_overhead() -> None:
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=4)
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    # velocity = 1/10 = 0.1 with no overhead reduction.
    assert r["velocity_topics_per_day"] == 0.1


def test_projection_with_deadline_ahead() -> None:
    # velocity=0.1, remaining=1 → projected = now + 10 days = June 11.
    # Deadline far in future → ahead.
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=1)
    r = compute_pacing(nodes, deadline="2026-08-01T00:00:00Z", created=CREATED, profile_map=None, now=NOW)
    assert r["pace_status"] == "ahead"
    assert r["days_delta"] is not None and r["days_delta"] > 0


def test_projection_with_deadline_behind() -> None:
    # velocity=0.1, remaining=5 → projected = now + 50 days = July 21.
    # Deadline tomorrow → behind.
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=5)
    r = compute_pacing(nodes, deadline="2026-06-02T00:00:00Z", created=CREATED, profile_map=None, now=NOW)
    assert r["pace_status"] == "behind"
    assert r["days_delta"] is not None and r["days_delta"] < 0


def test_projection_no_deadline() -> None:
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=3)
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r["pace_status"] is None
    assert r["days_delta"] is None


def test_all_completed_projects_now() -> None:
    nodes = _nodes("2026-05-11T00:00:00Z", "2026-05-21T00:00:00Z", remaining=0)
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r["remaining_count"] == 0
    assert r["projected_completion"] == NOW.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_velocity_rounded_to_two_decimals() -> None:
    # 1 completion 3 days after created → velocity = 1/3 = 0.333... → 0.33
    nodes = _nodes("2026-05-04T00:00:00Z", remaining=2)
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=None, now=NOW)
    assert r["velocity_topics_per_day"] == 0.33


def test_on_track_pace_status() -> None:
    # velocity=1.0, remaining=1 → projected = now + 1 day.
    # Deadline ~1 day away → on_track (within ±1 day).
    nodes = _nodes(
        "2026-05-02T00:00:00Z",  # 1 day after created
        remaining=1,
    )
    r = compute_pacing(
        nodes, deadline="2026-06-02T00:00:00Z", created=CREATED, profile_map=None, now=NOW,
    )
    assert r["pace_status"] == "on_track"


def test_profile_entry_without_stability_skipped() -> None:
    """Profile entries missing 'stability' are skipped (no overhead)."""
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=4)
    profile = {"topic-a": {"mastery": "solid"}}  # no stability key
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=profile, now=NOW)
    # No stale topics → no overhead → same as no profile.
    assert r["velocity_topics_per_day"] == 0.1


def test_profile_entry_non_dict_skipped() -> None:
    """Non-dict profile entries are skipped gracefully."""
    nodes = _nodes("2026-05-11T00:00:00Z", remaining=4)
    profile = {"topic-a": "not-a-dict"}  # type: ignore[dict-item]
    r = compute_pacing(nodes, deadline=None, created=CREATED, profile_map=profile, now=NOW)
    assert r["velocity_topics_per_day"] == 0.1


# ── T9: CLI integration tests ────────────────────────────────────────────


def test_cli_with_goal_file(tmp_path: object) -> None:
    tmp = tmp_path  # type: ignore[assignment]
    cur = {
        "created": CREATED,
        "deadline": "2026-08-01T00:00:00Z",
        "nodes": {
            "a": {"state": "completed", "completed_at": "2026-05-11T00:00:00Z"},
            "b": {"state": "not_started"},
            "c": {"state": "not_started"},
        },
    }
    cur_path = tmp / "curriculum.yaml"
    cur_path.write_text(yaml.dump(cur))

    rc = main(["--curriculum", str(cur_path), "--now", "2026-06-01T00:00:00Z"])
    assert rc == 0


def test_cli_missing_created_returns_error(tmp_path: object) -> None:
    tmp = tmp_path  # type: ignore[assignment]
    cur = {"nodes": {"a": {"state": "not_started"}}}
    cur_path = tmp / "curriculum.yaml"
    cur_path.write_text(yaml.dump(cur))

    rc = main(["--curriculum", str(cur_path), "--now", "2026-06-01T00:00:00Z"])
    assert rc == 1


def test_cli_with_profile(tmp_path: object) -> None:
    tmp = tmp_path  # type: ignore[assignment]
    cur = {
        "created": CREATED,
        "nodes": {
            "a": {"state": "completed", "completed_at": "2026-05-11T00:00:00Z"},
            "b": {"state": "not_started"},
        },
    }
    cur_path = tmp / "curriculum.yaml"
    cur_path.write_text(yaml.dump(cur))

    prof = {"expertise_map": {"topic-a": {"stability": 1.0}}}
    prof_path = tmp / "profile.yaml"
    prof_path.write_text(yaml.dump(prof))

    rc = main(["--curriculum", str(cur_path), "--profile", str(prof_path), "--now", "2026-06-01T00:00:00Z"])
    assert rc == 0


def test_cli_defaults_now_to_wall_clock(tmp_path: object) -> None:
    """When --now is omitted, main() uses wall clock (no crash)."""
    tmp = tmp_path  # type: ignore[assignment]
    cur = {
        "created": CREATED,
        "nodes": {"a": {"state": "not_started"}},
    }
    cur_path = tmp / "curriculum.yaml"
    cur_path.write_text(yaml.dump(cur))

    rc = main(["--curriculum", str(cur_path)])
    assert rc == 0

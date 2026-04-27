"""Tests for _states.py — curriculum-graph node-state classification sets."""

from __future__ import annotations

from sensei.engine.scripts._states import DONE_STATES, EXCLUDED_STATES


def test_done_states_membership() -> None:
    """DONE_STATES contains the two terminal-satisfaction states."""
    assert "skipped" in DONE_STATES
    assert "completed" in DONE_STATES


def test_excluded_states_membership() -> None:
    """EXCLUDED_STATES contains all four non-frontier states."""
    assert "skipped" in EXCLUDED_STATES
    assert "completed" in EXCLUDED_STATES
    assert "active" in EXCLUDED_STATES
    assert "decomposed" in EXCLUDED_STATES


def test_done_subset_of_excluded() -> None:
    """Every done state is also an excluded state."""
    assert DONE_STATES <= EXCLUDED_STATES


def test_states_are_frozenset() -> None:
    """Both sets are immutable frozensets."""
    assert isinstance(DONE_STATES, frozenset)
    assert isinstance(EXCLUDED_STATES, frozenset)

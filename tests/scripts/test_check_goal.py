"""Tests for check_goal.py — goal schema + cross-field validation."""

from __future__ import annotations

from pathlib import Path

import yaml

from sensei.engine.scripts.check_goal import main, validate_goal


def _valid_goal() -> dict:
    return {
        "schema_version": 0,
        "goal_id": "system-design",
        "expressed_as": "I want to learn system design",
        "created": "2026-04-20T10:00:00Z",
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "3 weeks",
        },
        "nodes": {
            "load-balancing": {"state": "active", "prerequisites": []},
            "caching": {"state": "collapsed", "prerequisites": []},
            "sharding": {"state": "spawned", "prerequisites": ["load-balancing"]},
        },
    }


def test_valid_goal():
    status, errors = validate_goal(_valid_goal())
    assert status == "ok"
    assert errors == []


def test_missing_required_field():
    goal = _valid_goal()
    del goal["goal_id"]
    status, errors = validate_goal(goal)
    assert status != "ok"
    assert any("goal_id" in e or "required" in e for e in errors)


def test_invalid_status():
    goal = _valid_goal()
    goal["status"] = "invalid"
    status, errors = validate_goal(goal)
    assert status != "ok"


def test_invalid_node_state():
    goal = _valid_goal()
    goal["nodes"]["load-balancing"]["state"] = "unknown"
    status, errors = validate_goal(goal)
    assert status != "ok"


def test_invalid_prior_state():
    goal = _valid_goal()
    goal["three_unknowns"]["prior_state"] = "bad"
    status, errors = validate_goal(goal)
    assert status != "ok"


def test_multiple_active_nodes():
    goal = _valid_goal()
    goal["nodes"]["caching"]["state"] = "active"
    # Now two nodes are active
    status, errors = validate_goal(goal)
    assert status != "ok"
    assert any("active" in e.lower() for e in errors)


def test_missing_prerequisite_reference():
    goal = _valid_goal()
    goal["nodes"]["sharding"]["prerequisites"] = ["nonexistent-topic"]
    status, errors = validate_goal(goal)
    assert status != "ok"
    assert any("nonexistent-topic" in e for e in errors)


def test_cycle_detection():
    goal = _valid_goal()
    # Create a cycle: A → B → A
    goal["nodes"] = {
        "topic-a": {"state": "active", "prerequisites": ["topic-b"]},
        "topic-b": {"state": "collapsed", "prerequisites": ["topic-a"]},
    }
    status, errors = validate_goal(goal)
    assert status != "ok"
    assert any("cycle" in e.lower() for e in errors)


def test_self_referencing_prerequisite():
    goal = _valid_goal()
    goal["nodes"]["load-balancing"]["prerequisites"] = ["load-balancing"]
    status, errors = validate_goal(goal)
    assert status != "ok"
    assert any("cycle" in e.lower() or "load-balancing" in e for e in errors)


def test_empty_nodes_valid():
    goal = _valid_goal()
    goal["nodes"] = {}
    status, errors = validate_goal(goal)
    assert status == "ok"


def test_no_active_node_valid():
    goal = _valid_goal()
    goal["nodes"]["load-balancing"]["state"] = "completed"
    status, errors = validate_goal(goal)
    assert status == "ok"


# --- deadline field tests ---


def test_valid_deadline():
    goal = _valid_goal()
    goal["deadline"] = "2026-06-01T00:00:00Z"
    status, errors = validate_goal(goal)
    assert status == "ok"
    assert errors == []


def test_null_deadline():
    goal = _valid_goal()
    goal["deadline"] = None
    status, errors = validate_goal(goal)
    assert status == "ok"
    assert errors == []


def test_missing_deadline_is_optional():
    """deadline is not required — omitting it is valid."""
    goal = _valid_goal()
    assert "deadline" not in goal
    status, errors = validate_goal(goal)
    assert status == "ok"
    assert errors == []


# --- require_redemonstration field tests ---


def test_require_redemonstration_true():
    goal = _valid_goal()
    goal["nodes"]["load-balancing"]["require_redemonstration"] = True
    status, errors = validate_goal(goal)
    assert status == "ok"
    assert errors == []


def test_require_redemonstration_false():
    goal = _valid_goal()
    goal["nodes"]["load-balancing"]["require_redemonstration"] = False
    status, errors = validate_goal(goal)
    assert status == "ok"
    assert errors == []


def test_missing_require_redemonstration_is_optional():
    """require_redemonstration is not required — omitting it is valid."""
    goal = _valid_goal()
    assert "require_redemonstration" not in goal["nodes"]["load-balancing"]
    status, errors = validate_goal(goal)
    assert status == "ok"
    assert errors == []


def test_main_valid_file(tmp_path: Path, capsys):
    goal = _valid_goal()
    path = tmp_path / "goal.yaml"
    path.write_text(yaml.dump(goal))
    rc = main(["--goal", str(path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert '"ok"' in out


def test_main_invalid_file(tmp_path: Path, capsys):
    path = tmp_path / "goal.yaml"
    path.write_text("{{{invalid yaml")
    rc = main(["--goal", str(path)])
    assert rc == 1


def test_main_missing_file(tmp_path: Path, capsys):
    rc = main(["--goal", str(tmp_path / "nope.yaml")])
    assert rc == 1

"""Tests for scripts/check_session_notes.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.check_session_notes import main, validate_session_notes


def _valid_session_notes() -> dict:
    return {
        "schema_version": 0,
        "sessions": [
            {
                "date": "2026-04-18T14:20:00Z",
                "observations": [
                    {
                        "type": "misconception",
                        "detail": "Confused recursion with iteration",
                    }
                ],
            }
        ],
    }


def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "session-notes.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_valid_session_notes() -> None:
    status, errors = validate_session_notes(_valid_session_notes())
    assert status == "ok"
    assert errors == []


def test_missing_required_field() -> None:
    data = _valid_session_notes()
    del data["sessions"]
    status, errors = validate_session_notes(data)
    assert status == "schema"
    assert any("sessions" in e for e in errors)


def test_wrong_type_for_field() -> None:
    data = _valid_session_notes()
    data["sessions"] = "not-a-list"
    status, errors = validate_session_notes(data)
    assert status == "schema"


def test_invalid_enum_value() -> None:
    data = _valid_session_notes()
    data["sessions"][0]["observations"][0]["type"] = "unknown"
    status, errors = validate_session_notes(data)
    assert status == "schema"


def test_main_file_not_found(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--session-notes-file", str(tmp_path / "nope.yaml")])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert any("not found" in e for e in parsed["errors"])


def test_corrupt_yaml(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("{{{", encoding="utf-8")
    rc = main(["--session-notes-file", str(path)])
    assert rc == 1
    out = capsys.readouterr().out.lower()
    assert "yaml" in out or "parse" in out


def test_non_dict_yaml(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- a list\n", encoding="utf-8")
    rc = main(["--session-notes-file", str(path)])
    assert rc == 1
    out = capsys.readouterr().out.lower()
    assert "mapping" in out


def test_main_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _valid_session_notes())
    rc = main(["--session-notes-file", str(path)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "ok"


def test_main_schema_failure(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data = _valid_session_notes()
    del data["sessions"]
    path = _write(tmp_path, data)
    rc = main(["--session-notes-file", str(path)])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "schema"

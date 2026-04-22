"""Tests for scripts/classify_confidence.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sensei.engine.scripts.classify_confidence import classify, main


def test_four_quadrants() -> None:
    assert classify("confident", "correct")["quadrant"] == "mastery"
    assert classify("confident", "incorrect")["quadrant"] == "misconception"
    assert classify("uncertain", "correct")["quadrant"] == "fragile"
    assert classify("uncertain", "incorrect")["quadrant"] == "gap"


def test_interpretation_non_empty() -> None:
    for c in ("confident", "uncertain"):
        for r in ("correct", "incorrect"):
            result = classify(c, r)
            assert result["interpretation"].strip(), f"empty interpretation for ({c}, {r})"


def test_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        classify("whatever", "correct")  # type: ignore[arg-type]


def test_invalid_correctness() -> None:
    with pytest.raises(ValueError, match="correctness"):
        classify("confident", "maybe")  # type: ignore[arg-type]


def test_main_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--confidence", "uncertain", "--correctness", "incorrect"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed == {
        "quadrant": "gap",
        "interpretation": classify("uncertain", "incorrect")["interpretation"],
    }


def test_script_runs_as_subprocess() -> None:
    """Protocols invoke helpers via shell subprocess (per ADR-0006). Verify that path works."""
    script = Path(__file__).resolve().parents[2] / "src" / "sensei" / "engine" / "scripts" / "classify_confidence.py"
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [sys.executable, str(script), "--confidence", "confident", "--correctness", "correct"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["quadrant"] == "mastery"

"""Smoke test: `sensei init` creates a complete instance."""

from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner

from sensei.cli import main
from sensei.engine.scripts.check_profile import validate_profile


def test_init_creates_instance(tmp_path: Path) -> None:
    target = tmp_path / "learner-home"
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(target)])

    assert result.exit_code == 0, result.output

    # Engine bundle copied.
    sensei_dir = target / ".sensei"
    assert sensei_dir.is_dir()
    assert (sensei_dir / "engine.md").is_file()
    assert (sensei_dir / "defaults.yaml").is_file()
    assert (sensei_dir / "scripts" / "config.py").is_file()
    assert (sensei_dir / "protocols" / "README.md").is_file()
    assert (sensei_dir / ".sensei-version").is_file()

    # Instance config and profile seeded.
    assert (target / "instance" / "config.yaml").is_file()
    profile_path = target / "instance" / "profile.yaml"
    assert profile_path.is_file()
    profile = yaml.safe_load(profile_path.read_text())
    status, errors = validate_profile(profile)
    assert status == "ok", errors
    assert profile["learner_id"] == "learner"  # default
    assert profile["expertise_map"] == {}

    # Hints ingestion directories and registry.
    assert (target / "instance" / "inbox").is_dir()
    assert (target / "instance" / "hints" / "active").is_dir()
    assert (target / "instance" / "hints" / "archive").is_dir()
    hints_reg = yaml.safe_load((target / "instance" / "hints" / "hints.yaml").read_text())
    assert hints_reg == {"schema_version": 1, "hints": []}

    # Boot document and shims.
    assert (target / "AGENTS.md").is_file()
    assert (target / "CLAUDE.md").read_text().strip() == "See @AGENTS.md"
    assert (target / ".cursor" / "rules" / "sensei.mdc").is_file()
    assert (target / ".kiro" / "steering" / "sensei.md").is_file()
    assert (target / ".github" / "copilot-instructions.md").is_file()


def test_init_accepts_learner_id(tmp_path: Path) -> None:
    target = tmp_path / "alice-home"
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(target), "--learner-id", "alice"])

    assert result.exit_code == 0, result.output
    profile = yaml.safe_load((target / "instance" / "profile.yaml").read_text())
    assert profile["learner_id"] == "alice"
    status, errors = validate_profile(profile)
    assert status == "ok", errors


def test_init_refuses_existing(tmp_path: Path) -> None:
    target = tmp_path / "learner-home"
    runner = CliRunner()
    first = runner.invoke(main, ["init", str(target)])
    assert first.exit_code == 0

    second = runner.invoke(main, ["init", str(target)])
    assert second.exit_code != 0
    assert "already exists" in second.output.lower()


def test_init_force_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "learner-home"
    runner = CliRunner()
    assert runner.invoke(main, ["init", str(target)]).exit_code == 0
    second = runner.invoke(main, ["init", str(target), "--force"])
    assert second.exit_code == 0

"""Tests for CLI commands beyond init."""

from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner

from sensei import __version__
from sensei.cli import main


def _init_instance(runner: CliRunner, target: Path) -> None:
    result = runner.invoke(main, ["init", str(target)])
    assert result.exit_code == 0, result.output


def test_status_reports_version(tmp_path: Path) -> None:
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_status_fails_without_instance(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code != 0


def test_upgrade_exits_not_implemented() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["upgrade"])
    assert result.exit_code != 0
    assert "not yet implemented" in result.output.lower()


def test_verify_exits_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["verify"])
    assert result.exit_code == 0


def test_version_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_init_force_preserves_instance_profile(tmp_path: Path) -> None:
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    profile_path = tmp_path / "instance" / "profile.yaml"
    custom_content = "schema_version: 0\nlearner_id: custom\nexpertise_map: {}\n"
    profile_path.write_text(custom_content, encoding="utf-8")

    result = runner.invoke(main, ["init", str(tmp_path), "--force"])
    assert result.exit_code == 0
    assert profile_path.read_text(encoding="utf-8") == custom_content


def test_init_learner_id_with_braces(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(tmp_path), "--learner-id", "test{1}"])
    assert result.exit_code == 0, result.output
    profile = yaml.safe_load((tmp_path / "instance" / "profile.yaml").read_text())
    assert profile["learner_id"] == "test{1}"

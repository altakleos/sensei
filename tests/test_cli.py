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


def test_upgrade_same_version_noop(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["init", str(tmp_path / "inst")])
    result = runner.invoke(main, ["upgrade", str(tmp_path / "inst")])
    assert result.exit_code == 0
    assert "Already at" in result.output


def test_upgrade_replaces_engine(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["init", str(tmp_path / "inst")])
    # Simulate old version
    (tmp_path / "inst" / ".sensei" / ".sensei-version").write_text("0.0.0\n")
    # Write custom profile to verify it's preserved
    profile_content = "schema_version: 0\nlearner_id: alice\nexpertise_map: {}\n"
    (tmp_path / "inst" / "instance" / "profile.yaml").write_text(profile_content)
    result = runner.invoke(main, ["upgrade", str(tmp_path / "inst")])
    assert result.exit_code == 0
    assert "0.0.0" in result.output
    assert "preserved" in result.output.lower()
    # Engine updated
    from sensei import __version__
    new_ver = (tmp_path / "inst" / ".sensei" / ".sensei-version").read_text().strip()
    assert new_ver == __version__
    # Instance preserved
    profile = (tmp_path / "inst" / "instance" / "profile.yaml").read_text()
    assert "alice" in profile


def test_upgrade_fails_without_instance(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["upgrade", str(tmp_path)])
    assert result.exit_code != 0


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

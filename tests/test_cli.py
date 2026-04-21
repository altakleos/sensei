"""Tests for CLI commands beyond init."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from sensei import __version__
from sensei.cli import _atomic_replace_engine, main


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


def test_verify_exits_zero(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["init", str(tmp_path / "inst")])
    result = runner.invoke(main, ["verify", str(tmp_path / "inst")])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_verify_fails_without_instance(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["verify", str(tmp_path)])
    assert result.exit_code != 0


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


# _atomic_replace_engine — atomicity contract per ADR-0004.
# The helper must never leave `.sensei/` in a corrupted or missing state
# after any failure during copy or swap.


def _fake_engine(src: Path) -> Path:
    """Build a minimal fake engine bundle to copy from."""
    src.mkdir(parents=True, exist_ok=True)
    (src / "engine.md").write_text("# fake\n", encoding="utf-8")
    (src / "scripts").mkdir()
    (src / "scripts" / "marker.py").write_text("# marker\n", encoding="utf-8")
    return src


def test_atomic_replace_happy_path(tmp_path: Path) -> None:
    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()

    _atomic_replace_engine(src, sensei_dir, "1.2.3")

    assert (sensei_dir / "engine.md").read_text() == "# fake\n"
    assert (sensei_dir / ".sensei-version").read_text() == "1.2.3\n"
    # No lingering temp or aside dirs.
    assert not (sensei_dir.parent / ".sensei.tmp").exists()
    assert not (sensei_dir.parent / ".sensei.old").exists()


def test_atomic_replace_preserves_old_on_copy_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()

    # Prime an existing `.sensei/` with a sentinel file the test can check.
    sensei_dir.mkdir()
    (sensei_dir / "SENTINEL").write_text("pre-existing", encoding="utf-8")

    def boom(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated disk failure during copy")

    monkeypatch.setattr("sensei.cli.shutil.copytree", boom)

    with pytest.raises(OSError, match="simulated disk failure"):
        _atomic_replace_engine(src, sensei_dir, "9.9.9")

    # Old .sensei/ untouched; no stale temp dirs.
    assert (sensei_dir / "SENTINEL").read_text() == "pre-existing"
    assert not (sensei_dir.parent / ".sensei.tmp").exists()


def test_atomic_replace_cleans_stale_tmp_from_prior_run(tmp_path: Path) -> None:
    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()

    # Leftover from a prior failed run.
    stale_tmp = sensei_dir.parent / ".sensei.tmp"
    stale_tmp.mkdir()
    (stale_tmp / "LEFTOVER").write_text("stale", encoding="utf-8")

    _atomic_replace_engine(src, sensei_dir, "1.2.3")

    assert (sensei_dir / "engine.md").exists()
    assert not stale_tmp.exists()


def test_atomic_replace_recovers_from_mid_swap_crash(tmp_path: Path) -> None:
    """Simulates a crash between `rename sensei_dir → .sensei.old` and
    `rename .sensei.tmp → sensei_dir`: the next invocation must restore
    the old dir rather than overwrite it blindly."""
    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()

    # Simulate the aftermath of an interrupted swap: .sensei/ is missing,
    # .sensei.old/ holds the previous contents, no .sensei.tmp/ yet.
    old_dir = sensei_dir.parent / ".sensei.old"
    old_dir.mkdir()
    (old_dir / "RECOVERED").write_text("prior-engine-survived", encoding="utf-8")

    _atomic_replace_engine(src, sensei_dir, "2.0.0")

    # Recovery completes the swap cleanly: the fresh copy wins, and the
    # old aside is removed. Crucially, the helper did NOT overwrite
    # .sensei/ while .sensei.old/ existed — it first restored the old
    # so the normal swap path could run.
    assert (sensei_dir / "engine.md").exists()
    assert (sensei_dir / ".sensei-version").read_text() == "2.0.0\n"
    assert not old_dir.exists()
    assert not (sensei_dir.parent / ".sensei.tmp").exists()


def test_atomic_replace_rollback_on_final_rename_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the final `tmp → real` rename fails, the old dir must be restored."""
    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()
    sensei_dir.mkdir()
    (sensei_dir / "SENTINEL").write_text("survive-me", encoding="utf-8")

    original_rename = Path.rename
    call_count = {"n": 0}

    def rename_once_then_fail(self: Path, target: str | Path) -> Path:
        call_count["n"] += 1
        if call_count["n"] == 2:
            # Second rename is tmp → real; fail it.
            raise OSError("simulated rename failure")
        return original_rename(self, target)

    monkeypatch.setattr(Path, "rename", rename_once_then_fail)

    with pytest.raises(OSError, match="simulated rename failure"):
        _atomic_replace_engine(src, sensei_dir, "3.0.0")

    # Old content restored; no stale temp or aside dirs.
    assert (sensei_dir / "SENTINEL").read_text() == "survive-me"
    assert not (sensei_dir.parent / ".sensei.tmp").exists()
    assert not (sensei_dir.parent / ".sensei.old").exists()


def test_upgrade_leaves_instance_intact_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: a failed `sensei upgrade` must preserve both .sensei/ and instance/."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    runner.invoke(main, ["init", str(inst)])
    (inst / ".sensei" / ".sensei-version").write_text("0.0.0\n")
    profile_path = inst / "instance" / "profile.yaml"
    profile_path.write_text("schema_version: 0\nlearner_id: preserved\nexpertise_map: {}\n")

    def fail_copy(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated")

    monkeypatch.setattr("sensei.cli.shutil.copytree", fail_copy)

    result = runner.invoke(main, ["upgrade", str(inst)])
    assert result.exit_code != 0
    # Both survive.
    assert (inst / ".sensei" / "engine.md").exists()
    assert "preserved" in profile_path.read_text()

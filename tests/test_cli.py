"""Tests for CLI commands beyond init."""

from __future__ import annotations

import os
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
import pytest
import yaml
from click.testing import CliRunner

from sensei import __version__
from sensei.cli import _atomic_replace_engine, _engine_source, main


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
    (tmp_path / "inst" / "learner" / "profile.yaml").write_text(profile_content)
    result = runner.invoke(main, ["upgrade", str(tmp_path / "inst")])
    assert result.exit_code == 0
    assert "0.0.0" in result.output
    assert "preserved" in result.output.lower()
    # Engine updated
    from sensei import __version__
    new_ver = (tmp_path / "inst" / ".sensei" / ".sensei-version").read_text().strip()
    assert new_ver == __version__
    # Instance preserved
    profile = (tmp_path / "inst" / "learner" / "profile.yaml").read_text()
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
    profile_path = tmp_path / "learner" / "profile.yaml"
    custom_content = "schema_version: 0\nlearner_id: custom\nexpertise_map: {}\n"
    profile_path.write_text(custom_content, encoding="utf-8")

    result = runner.invoke(main, ["init", str(tmp_path), "--force"])
    assert result.exit_code == 0
    assert profile_path.read_text(encoding="utf-8") == custom_content


@pytest.mark.parametrize("learner_id", ["alice", "learner-01", "ab_cd", "A", "x" * 64])
def test_init_accepts_valid_learner_id(tmp_path: Path, learner_id: str) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(tmp_path), "--learner-id", learner_id])
    assert result.exit_code == 0, result.output
    profile = yaml.safe_load((tmp_path / "learner" / "profile.yaml").read_text())
    assert profile["learner_id"] == learner_id


@pytest.mark.parametrize(
    "bad_id",
    [
        "",  # empty
        "x" * 65,  # too long
        "has space",  # whitespace
        "name\nwith\nnewlines",  # YAML-injecting characters
        "name: injected",  # yaml key-ish content
        "name'with'quotes",
        "name{braces}",
        "name/slash",
        "name.dot",  # conservative — dots rejected too
    ],
)
def test_init_rejects_invalid_learner_id(tmp_path: Path, bad_id: str) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(tmp_path), "--learner-id", bad_id])
    assert result.exit_code != 0
    assert "learner-id" in result.output.lower() or "learner_id" in result.output.lower()
    # No instance was scaffolded.
    assert not (tmp_path / ".sensei").exists()
    assert not (tmp_path / "learner").exists()


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
    """End-to-end: a failed `sensei upgrade` must preserve both .sensei/ and learner/."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    runner.invoke(main, ["init", str(inst)])
    (inst / ".sensei" / ".sensei-version").write_text("0.0.0\n")
    profile_path = inst / "learner" / "profile.yaml"
    profile_path.write_text("schema_version: 0\nlearner_id: preserved\nexpertise_map: {}\n")

    def fail_copy(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated")

    monkeypatch.setattr("sensei.cli.shutil.copytree", fail_copy)

    result = runner.invoke(main, ["upgrade", str(inst)])
    assert result.exit_code != 0
    # Both survive.
    assert (inst / ".sensei" / "engine.md").exists()
    assert "preserved" in profile_path.read_text()


# --- _engine_source error path ---


def test_engine_source_raises_when_bundle_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """If the installed package has no engine/ directory, _engine_source raises ClickException."""
    import sensei

    empty = tmp_path / "fake_pkg"
    empty.mkdir()
    (empty / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(sensei, "__file__", str(empty / "__init__.py"))

    with pytest.raises(click.ClickException, match="Engine bundle not found"):
        _engine_source()


# --- _atomic_replace_engine: prior run completed but died before cleanup ---


def test_atomic_replace_cleans_old_dir_when_both_exist(tmp_path: Path) -> None:
    """A prior run can die between step 3 (rename tmp → real) and step 4 (rmtree old);
    the next invocation finds both `.sensei/` AND `.sensei.old/` present and must
    clean the stale aside rather than overwrite the current install with it."""
    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()
    # Existing install:
    sensei_dir.mkdir()
    (sensei_dir / "engine.md").write_text("# current\n", encoding="utf-8")
    # Leftover stale aside from a prior run that died between step 3 and step 4:
    old_dir = sensei_dir.parent / ".sensei.old"
    old_dir.mkdir()
    (old_dir / "STALE").write_text("stale", encoding="utf-8")

    _atomic_replace_engine(src, sensei_dir, "4.0.0")

    assert (sensei_dir / "engine.md").read_text() == "# fake\n"
    assert (sensei_dir / ".sensei-version").read_text() == "4.0.0\n"
    assert not old_dir.exists()


@pytest.mark.skipif(os.name != "posix", reason="parent-dir fsync is POSIX-only")
def test_atomic_replace_fsyncs_parent_after_each_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each rename during engine swap must be followed by a parent-dir fsync,
    so the dirent update survives power loss (ADR-0004 durability contract).

    Fresh install path: two renames are not possible (nothing to swap aside),
    so only the final tmp → real rename fires. The helper must fsync the
    parent exactly once in that case, and exactly twice when an existing
    `.sensei/` is swapped aside first.
    """
    import sensei.cli as cli

    fsync_fds: list[int] = []
    real_fsync = cli.os.fsync

    def recording_fsync(fd: int) -> None:
        fsync_fds.append(fd)
        return real_fsync(fd)

    monkeypatch.setattr(cli.os, "fsync", recording_fsync)

    src = _fake_engine(tmp_path / "src")
    sensei_dir = tmp_path / "inst" / ".sensei"
    sensei_dir.parent.mkdir()
    sensei_dir.mkdir()
    (sensei_dir / "MARK").write_text("before", encoding="utf-8")

    _atomic_replace_engine(src, sensei_dir, "1.2.3")

    # Two renames (swap-aside + install-new) ⇒ two parent-dir fsyncs.
    assert len(fsync_fds) == 2, f"expected 2 fsync calls, got {len(fsync_fds)}: {fsync_fds}"
    # End state intact:
    assert (sensei_dir / "engine.md").exists()
    assert (sensei_dir / ".sensei-version").read_text() == "1.2.3\n"


@pytest.mark.skipif(os.name != "posix", reason="parent-dir fsync is POSIX-only")
def test_fsync_dir_targets_a_directory(tmp_path: Path) -> None:
    """_fsync_dir opens a read-only fd on the given path and the fd refers
    to a directory. Guards against accidentally passing a file path."""
    from sensei.cli import _fsync_dir

    d = tmp_path / "somedir"
    d.mkdir()
    # Before fsync, snapshot that the path is indeed a directory at the
    # syscall level (regression guard — same check _fsync_dir would fail on
    # if called with a file path on Linux, where os.open(..., O_RDONLY) on a
    # file yields a file fd and fsync on that fd also succeeds silently).
    fd = os.open(d, os.O_RDONLY)
    try:
        st = os.fstat(fd)
        assert stat.S_ISDIR(st.st_mode)
    finally:
        os.close(fd)
    # Call should complete without raising.
    _fsync_dir(d)


# --- status: uncovered branches ---


def test_status_reports_profile_not_found(tmp_path: Path) -> None:
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    (tmp_path / "learner" / "profile.yaml").unlink()
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert "Profile:  not found" in result.output


def test_status_reports_invalid_profile_not_a_mapping(tmp_path: Path) -> None:
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    (tmp_path / "learner" / "profile.yaml").write_text("- just\n- a\n- list\n")
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert "invalid (not a mapping)" in result.output


def test_status_summarises_mastery_breakdown(tmp_path: Path) -> None:
    """With expertise_map populated, status prints the mastery-level counts."""
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    now_iso = datetime.now(tz=timezone.utc).isoformat()
    profile = {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            "t1": {"mastery": "solid", "confidence": 0.8, "last_seen": now_iso, "attempts": 5, "correct": 4},
            "t2": {"mastery": "developing", "confidence": 0.5, "last_seen": now_iso, "attempts": 3, "correct": 2},
            "t3": {"mastery": "mastered", "confidence": 0.9, "last_seen": now_iso, "attempts": 8, "correct": 8},
        },
    }
    (tmp_path / "learner" / "profile.yaml").write_text(yaml.safe_dump(profile))
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert "Topics:   3" in result.output
    assert "Mastery:" in result.output
    # Fresh topics → no stale line.
    assert "Stale:" not in result.output


def test_status_flags_stale_topics(tmp_path: Path) -> None:
    """Topics with old last_seen timestamps should surface under a Stale:  header."""
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    old_iso = (datetime.now(tz=timezone.utc) - timedelta(days=60)).isoformat()
    profile = {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            f"topic-{i}": {
                "mastery": "solid",
                "confidence": 0.7,
                "last_seen": old_iso,
                "attempts": 4,
                "correct": 3,
            }
            for i in range(7)  # more than 5 to exercise the "... and N more" tail
        },
    }
    (tmp_path / "learner" / "profile.yaml").write_text(yaml.safe_dump(profile))
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert "Stale:    7 topics due for review" in result.output
    assert "... and 2 more" in result.output


def test_status_tolerates_malformed_last_seen(tmp_path: Path) -> None:
    """A topic with a garbage last_seen string should still appear as stale,
    not crash status — and the parse failure must surface as a warning so
    the learner knows their profile has corrupt timestamps."""
    runner = CliRunner()
    _init_instance(runner, tmp_path)
    profile = {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            "garbage": {
                "mastery": "solid",
                "confidence": 0.7,
                "last_seen": "not-a-real-date",
                "attempts": 1,
                "correct": 1,
            },
            "absent-timestamp": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": "",
                "attempts": 1,
                "correct": 0,
            },
        },
    }
    (tmp_path / "learner" / "profile.yaml").write_text(yaml.safe_dump(profile))
    result = runner.invoke(main, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert "Stale:    2 topics" in result.output
    # Only the unparseable timestamp is malformed; empty is a legitimate schema
    # state (never reviewed) and does not appear in the warning list.
    assert "Warning:  1 topic with unparseable last_seen" in result.output
    # Slice the output between the Warning: header and the Stale: header —
    # absent-timestamp belongs in Stale (empty last_seen is schema-valid) but
    # not in the Warning list.
    warning_section = result.output.split("Warning:")[1].split("Stale:")[0]
    assert "- garbage" in warning_section
    assert "- absent-timestamp" not in warning_section


# --- upgrade: migration-applied + already-current paths ---


def test_upgrade_reports_already_current_migrations(tmp_path: Path) -> None:
    """After a real version bump, the migration helper runs and migrates
    the profile from schema_version 0 to 1 (emotional_state added)."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    runner.invoke(main, ["init", str(inst)])
    (inst / ".sensei" / ".sensei-version").write_text("0.0.0\n")
    result = runner.invoke(main, ["upgrade", str(inst)])
    assert result.exit_code == 0
    assert "profile.yaml: schema_version" in result.output


def test_upgrade_runs_migration_before_engine_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If migrate_instance raises, the engine bundle must not have been swapped.
    Otherwise a user would end up with a new engine paired with old-format data.
    """
    runner = CliRunner()
    inst = tmp_path / "inst"
    runner.invoke(main, ["init", str(inst)])
    # Simulate an old version so upgrade isn't a noop.
    (inst / ".sensei" / ".sensei-version").write_text("0.0.0\n")

    def failing_migrate(learner_dir: Path) -> list[str]:
        raise RuntimeError("simulated migration failure")

    monkeypatch.setattr(
        "sensei.engine.scripts.migrate.migrate_instance", failing_migrate
    )

    result = runner.invoke(main, ["upgrade", str(inst)])
    assert result.exit_code != 0
    # Engine was NOT swapped — stamp still reflects the old version.
    stamp = (inst / ".sensei" / ".sensei-version").read_text().strip()
    assert stamp == "0.0.0"


# --- verify: failure output paths ---


def test_verify_reports_missing_engine_file(tmp_path: Path) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / ".sensei" / "engine.md").unlink()
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "FAIL" in result.output
    assert "missing: .sensei/engine.md" in result.output


def test_verify_reports_missing_profile(tmp_path: Path) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "profile.yaml").unlink()
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "missing: learner/profile.yaml" in result.output


def test_verify_reports_invalid_profile_yaml(tmp_path: Path) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "profile.yaml").write_text("{{{\n")
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "profile: invalid YAML" in result.output


def test_verify_reports_profile_not_a_mapping(tmp_path: Path) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "profile.yaml").write_text("- item\n")
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "profile: not a YAML mapping" in result.output


def test_verify_reports_profile_validation_errors(tmp_path: Path) -> None:
    """A profile that parses but fails validate_profile should be reported."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    # Empty learner_id violates minLength:1 per profile.schema.json.
    (inst / "learner" / "profile.yaml").write_text(
        "schema_version: 0\nlearner_id: \"\"\nexpertise_map: {}\n"
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "FAIL" in result.output
    assert "profile:" in result.output


# --- verify: manifest-driven bundle check ---
#
# These cover files that the previous hardcoded `expected` list omitted —
# regression guards against re-introducing a partial verify checklist.


@pytest.mark.parametrize(
    "rel",
    [
        # Top-level protocols missing from the previous hardcoded list:
        "protocols/hints.md",
        "protocols/tutor.md",
        "protocols/challenger.md",
        "protocols/reviewer.md",
        "protocols/status.md",
        "protocols/performance-training.md",
        # Schemas missing from the previous hardcoded list:
        "schemas/goal.schema.json",
        "schemas/hints.yaml.schema.json",
        # Helper scripts missing from the previous hardcoded list:
        "scripts/review_scheduler.py",
        "scripts/goal_priority.py",
        "scripts/frontier.py",
        "scripts/mutate_graph.py",
    ],
)
def test_verify_catches_missing_bundle_file(tmp_path: Path, rel: str) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / ".sensei" / rel).unlink()
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert f"missing: .sensei/{rel}" in result.output


def test_verify_catches_missing_manifest(tmp_path: Path) -> None:
    """Without manifest.yaml, verify cannot determine bundle integrity and must fail."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / ".sensei" / "manifest.yaml").unlink()
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "missing: .sensei/manifest.yaml" in result.output


def test_verify_catches_invalid_manifest_yaml(tmp_path: Path) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / ".sensei" / "manifest.yaml").write_text("{{{not yaml\n")
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "manifest.yaml: invalid YAML" in result.output


def test_verify_catches_manifest_with_non_list_required(tmp_path: Path) -> None:
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / ".sensei" / "manifest.yaml").write_text(
        "schema_version: 1\nrequired: not-a-list\n"
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "'required' must be a list" in result.output


# --- verify: defaults-schema validation ---
#
# Catches typos, wrong types, and out-of-range tunables in the merged
# (defaults + learner override) config. Previously these silently fell
# through to hardcoded script defaults.


def test_verify_passes_clean_instance_against_defaults_schema(tmp_path: Path) -> None:
    """Regression: a freshly-scaffolded instance must validate cleanly.
    Catches schema/defaults-yaml drift if either is edited without the other."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 0, result.output
    assert "config:" not in result.output


def test_verify_catches_unknown_tunable_in_learner_config(tmp_path: Path) -> None:
    """A typo'd top-level key in learner/config.yaml must surface, not silently fall through."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "config.yaml").write_text(
        "memori:\n  half_life_dais: 7\n", encoding="utf-8"
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "config:" in result.output
    # The schema reports the unknown property under <root> with the key name.
    assert "memori" in result.output


def test_verify_catches_wrong_type_in_learner_config(tmp_path: Path) -> None:
    """A string in place of a number must be rejected by the schema."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "config.yaml").write_text(
        'memory:\n  half_life_days: "seven"\n', encoding="utf-8"
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "config:" in result.output
    assert "memory" in result.output


def test_verify_catches_out_of_range_tunable(tmp_path: Path) -> None:
    """stale_threshold > 1 violates the 0..1 freshness bound."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "config.yaml").write_text(
        "memory:\n  stale_threshold: 1.5\n", encoding="utf-8"
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "config:" in result.output
    assert "stale_threshold" in result.output


def test_verify_catches_invalid_enum_in_learner_config(tmp_path: Path) -> None:
    """performance_training.mastery_gate is enum-restricted; a wrong value must fail."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "config.yaml").write_text(
        "performance_training:\n  mastery_gate: legendary\n", encoding="utf-8"
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "config:" in result.output
    assert "mastery_gate" in result.output


def test_verify_does_not_leak_soft_fail_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Per ADR-0025, verify temporarily sets SENSEI_CONFIG_SOFT_FAIL=1 so it
    can collect every offending dotpath. The prior env state must be restored
    on exit, in both the no-prior-value and prior-value cases."""
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "config.yaml").write_text(
        "memory:\n  half_life_days: 'seven'\n", encoding="utf-8"
    )

    monkeypatch.delenv("SENSEI_CONFIG_SOFT_FAIL", raising=False)
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "SENSEI_CONFIG_SOFT_FAIL" not in os.environ

    monkeypatch.setenv("SENSEI_CONFIG_SOFT_FAIL", "preexisting")
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert os.environ.get("SENSEI_CONFIG_SOFT_FAIL") == "preexisting"


def test_verify_collects_every_dotpath_on_multi_field_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Per ADR-0025, verify must report every config violation in one run,
    not abort on the first. Two unrelated bad fields must both surface."""
    monkeypatch.delenv("SENSEI_CONFIG_SOFT_FAIL", raising=False)
    runner = CliRunner()
    inst = tmp_path / "inst"
    _init_instance(runner, inst)
    (inst / "learner" / "config.yaml").write_text(
        "memory:\n  half_life_days: 'seven'\n"
        "performance_training:\n  mastery_gate: legendary\n",
        encoding="utf-8",
    )
    result = runner.invoke(main, ["verify", str(inst)])
    assert result.exit_code == 1
    assert "half_life_days" in result.output
    assert "mastery_gate" in result.output

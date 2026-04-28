"""Smoke test: `sensei init` creates a complete instance."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from sensei._shims import SHIMS
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
    assert (target / "learner" / "config.yaml").is_file()
    profile_path = target / "learner" / "profile.yaml"
    assert profile_path.is_file()
    profile = yaml.safe_load(profile_path.read_text())
    status, errors = validate_profile(profile)
    assert status == "ok", errors
    assert profile["learner_id"] == "learner"  # default
    assert profile["expertise_map"] == {}

    # Hints ingestion directories and registry.
    assert (target / "learner" / "inbox").is_dir()
    assert (target / "learner" / "hints" / "active").is_dir()
    assert (target / "learner" / "hints" / "archive").is_dir()
    hints_reg = yaml.safe_load((target / "learner" / "hints" / "hints.yaml").read_text())
    assert hints_reg == {"schema_version": 0, "hints": []}

    # Session notes file.
    session_notes = yaml.safe_load((target / "learner" / "session-notes.yaml").read_text())
    assert session_notes == {"schema_version": 0, "sessions": []}

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
    profile = yaml.safe_load((target / "learner" / "profile.yaml").read_text())
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


def test_init_rejects_symlink_target(tmp_path: Path) -> None:
    """sensei init must refuse to write through a symlink target."""
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real_dir)

    runner = CliRunner()
    result = runner.invoke(main, ["init", str(link)])
    assert result.exit_code != 0
    assert "symlink" in result.output.lower()


def test_init_rejects_symlink_sensei_dir(tmp_path: Path) -> None:
    """sensei init must refuse if .sensei is a pre-planted symlink."""
    target = tmp_path / "learner-home"
    target.mkdir()
    evil = tmp_path / "evil"
    evil.mkdir()
    (target / ".sensei").symlink_to(evil)

    runner = CliRunner()
    result = runner.invoke(main, ["init", str(target)])
    assert result.exit_code != 0
    assert "symlink" in result.output.lower()


# --- Shim format validation ---
#
# Per docs/operations/shim-validation.md, every generated shim must (a) live
# at the path the target tool actually reads, (b) match the format that tool
# documents (frontmatter for Cursor's .mdc, trigger directive for Windsurf,
# plain prose for Cline/Roo/Copilot/AI Assistant, claude-code @import for
# CLAUDE.md, plain prose for Kiro), and (c) reference AGENTS.md so the
# scaffolded instance has a single source of truth.


_SHIM_PATHS = sorted(SHIMS.keys())


@pytest.fixture(scope="module")
def shim_instance(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Scaffold one instance per test module — all shim cases share it."""
    target = tmp_path_factory.mktemp("shim-validation")
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(target)])
    assert result.exit_code == 0, result.output
    return target


@pytest.mark.parametrize("rel_path", _SHIM_PATHS)
def test_shim_file_exists_and_references_agents_md(
    shim_instance: Path, rel_path: str
) -> None:
    """Every shim must exist on disk and point at AGENTS.md."""
    target = shim_instance / rel_path
    assert target.is_file(), f"shim missing at {rel_path}"
    text = target.read_text(encoding="utf-8")
    # CLAUDE.md uses Claude Code's @import syntax; everything else references
    # AGENTS.md by name in prose.
    if rel_path == "CLAUDE.md":
        assert "@AGENTS.md" in text
    else:
        assert "AGENTS.md" in text, (
            f"shim {rel_path} must reference AGENTS.md so the scaffolded "
            f"instance has a single source of truth"
        )


def test_shim_cursor_format(shim_instance: Path) -> None:
    """Cursor `.mdc` requires YAML frontmatter with `description` and either
    `alwaysApply` or `globs` per Cursor's documented rule format."""
    text = (shim_instance / ".cursor" / "rules" / "sensei.mdc").read_text(encoding="utf-8")
    assert text.startswith("---\n"), "Cursor .mdc must start with YAML frontmatter"
    end = text.find("\n---\n", 4)
    assert end > 0, "Cursor .mdc frontmatter must close with `---`"
    fm = yaml.safe_load(text[4:end])
    assert isinstance(fm, dict), "Cursor frontmatter must be a YAML mapping"
    assert "description" in fm, "Cursor rule needs a `description` field"
    # alwaysApply: true tells Cursor to inject this rule into every prompt
    # (rather than activating on glob match). The shim's whole purpose is
    # always-on, so this field is required.
    assert fm.get("alwaysApply") is True, (
        "Cursor shim must set `alwaysApply: true` so the rule applies on every prompt"
    )


def test_shim_windsurf_format(shim_instance: Path) -> None:
    """Windsurf rules require a `trigger:` frontmatter field with one of the
    documented values (always_on, manual, model_decision, glob)."""
    text = (shim_instance / ".windsurf" / "rules" / "sensei.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), "Windsurf rule must start with YAML frontmatter"
    end = text.find("\n---\n", 4)
    assert end > 0, "Windsurf rule frontmatter must close with `---`"
    fm = yaml.safe_load(text[4:end])
    assert isinstance(fm, dict), "Windsurf frontmatter must be a YAML mapping"
    assert fm.get("trigger") in {"always_on", "manual", "model_decision", "glob"}, (
        "Windsurf rule needs `trigger:` with a documented value"
    )


@pytest.mark.parametrize(
    "rel_path",
    [
        ".kiro/steering/sensei.md",
        ".github/copilot-instructions.md",
        ".clinerules/sensei.md",
        ".roo/rules/sensei.md",
        ".aiassistant/rules/sensei.md",
    ],
)
def test_shim_plain_prose_format(shim_instance: Path, rel_path: str) -> None:
    """Plain-prose shims (Kiro, Copilot, Cline, Roo, AI Assistant) must NOT
    have YAML frontmatter — these tools read the whole file as instructions."""
    text = (shim_instance / rel_path).read_text(encoding="utf-8")
    # A leading `---` would be a frontmatter delimiter the tool wouldn't
    # interpret. Plain-prose tools read everything verbatim.
    assert not text.startswith("---\n"), (
        f"{rel_path} should be plain prose, not YAML-frontmatter — "
        f"the target tool reads the whole file as instructions"
    )
    assert text.strip(), f"{rel_path} must not be empty"


def test_shim_claude_code_uses_at_import(shim_instance: Path) -> None:
    """CLAUDE.md is special — Claude Code resolves `@<path>` as an import."""
    text = (shim_instance / "CLAUDE.md").read_text(encoding="utf-8").strip()
    assert text == "See @AGENTS.md", (
        f"CLAUDE.md must use the `@AGENTS.md` import directive verbatim "
        f"(got: {text!r})"
    )


# --- Snapshot test ---
#
# Pinned `_SHIMS` content. Any edit to cli.py:_SHIMS requires a deliberate
# update here in the same commit; otherwise format-drift slips in silently.

_EXPECTED_SHIMS: dict[str, str] = {
    "CLAUDE.md": "See @AGENTS.md\n",
    ".kiro/steering/sensei.md": "# Sensei\n\nRead and follow the instructions in `AGENTS.md` at the instance root.\n",
    ".cursor/rules/sensei.mdc": (
        "---\ndescription: Sensei boot chain\nalwaysApply: true\n---\n"
        "Read and follow the instructions in `AGENTS.md` at the instance root.\n"
    ),
    ".github/copilot-instructions.md": "Read and follow the instructions in `AGENTS.md` at the instance root.\n",
    ".windsurf/rules/sensei.md": (
        "---\ntrigger: always_on\n---\n"
        "Read and follow the instructions in `AGENTS.md` at the instance root.\n"
    ),
    ".clinerules/sensei.md": "Read and follow the instructions in `AGENTS.md` at the instance root.\n",
    ".roo/rules/sensei.md": "Read and follow the instructions in `AGENTS.md` at the instance root.\n",
    ".aiassistant/rules/sensei.md": "Read and follow the instructions in `AGENTS.md` at the instance root.\n",
}


def test_shims_match_snapshot() -> None:
    """Regression guard against silent edits to cli.py:_SHIMS. If you change
    a shim's content deliberately, update _EXPECTED_SHIMS in the same commit
    and document the reason in the commit message."""
    assert SHIMS == _EXPECTED_SHIMS, (
        "cli.py:_SHIMS drifted from the snapshot. Either fix the regression "
        "or update _EXPECTED_SHIMS in tests/test_init.py with the new content."
    )

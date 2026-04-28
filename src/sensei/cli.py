"""Sensei CLI.

Subcommands:
    init <target>   Scaffold a Sensei instance at <target>.
    status          Report instance state.
    upgrade         Update .sensei/ to the installed package version.
    verify          Run validators.
"""

from __future__ import annotations

import re
from pathlib import Path

import click
import yaml

from sensei import __version__
from sensei._engine import atomic_replace_engine, engine_source, install_run_script
from sensei._shims import SHIMS, write_shim

# Strict validation for --learner-id: letters, digits, underscore, hyphen;
# 1–64 characters. The value is interpolated into learner/profile.yaml and
# later embedded in LLM prompts, so we reject any character that could inject
# YAML, shell metacharacters, or prompt-steering content.
_LEARNER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_LEARNER_CONFIG_YAML = """# Learner-level overrides for Sensei defaults.
# Leave empty to use engine defaults from .sensei/defaults.yaml.
"""

_STARTER_PROFILE_HEADER = """\
# Sensei learner profile. See docs/specs/learner-profile.md for the contract.
# Validated by .sensei/scripts/check_profile.py.
"""


@click.group()
@click.version_option(__version__, prog_name="sensei")
def main() -> None:
    """Sensei — pip-installable scaffolding for LLM-operated learning environments."""


@main.command()
@click.argument("target", type=click.Path(file_okay=False, path_type=Path))
@click.option("--force", is_flag=True, help="Overwrite an existing .sensei/ directory.")
@click.option(
    "--learner-id",
    default="learner",
    show_default=True,
    help="Identifier written to learner/profile.yaml. Edit later if you prefer a different name.",
)
def init(target: Path, force: bool, learner_id: str) -> None:
    """Scaffold a new Sensei instance at TARGET."""
    if not _LEARNER_ID_RE.match(learner_id):
        raise click.BadParameter(
            "must match ^[A-Za-z0-9_-]{1,64}$ (letters, digits, underscore, hyphen; 1–64 chars)",
            param_hint="--learner-id",
        )

    # Reject symlinks before resolving — writing through a symlink could
    # redirect engine files to an attacker-controlled location.
    if target.is_symlink():
        raise click.ClickException(
            f"Target path is a symlink: {target}. "
            f"Refusing to write through symlinks for security."
        )
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)

    sensei_dir = target / ".sensei"
    if sensei_dir.is_symlink():
        raise click.ClickException(
            f".sensei is a symlink: {sensei_dir}. "
            f"Refusing to write through symlinks for security."
        )
    if sensei_dir.exists() and not force:
        raise click.ClickException(
            f"Instance already exists at {sensei_dir}. "
            f"Run `sensei upgrade` to update the engine, or re-run with --force to reinitialize."
        )

    # Install engine bundle into .sensei/ atomically.
    atomic_replace_engine(engine_source(), sensei_dir, __version__)

    # Record interpreter path and make run wrapper executable.
    install_run_script(sensei_dir)

    # Learner data directory + seed profile.
    try:
        (target / "learner").mkdir(exist_ok=True)
        (target / "learner" / "goals").mkdir(exist_ok=True)
        learner_config = target / "learner" / "config.yaml"
        if not learner_config.exists():
            learner_config.write_text(_LEARNER_CONFIG_YAML, encoding="utf-8")
        learner_profile = target / "learner" / "profile.yaml"
        if not learner_profile.exists():
            profile_body = yaml.safe_dump(
                {"schema_version": 0, "learner_id": learner_id, "expertise_map": {}},
                sort_keys=False,
            )
            learner_profile.write_text(
                _STARTER_PROFILE_HEADER + profile_body,
                encoding="utf-8",
            )

        # Session notes file.
        session_notes = target / "learner" / "session-notes.yaml"
        if not session_notes.exists():
            session_notes.write_text("schema_version: 0\nsessions: []\n", encoding="utf-8")

        # Hints ingestion directories and registry.
        (target / "learner" / "inbox").mkdir(exist_ok=True)
        gitkeep = target / "learner" / "inbox" / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text(
                "# Drop zone for raw learning hints (URLs, snippets, notes).\n", encoding="utf-8"
            )
        (target / "learner" / "hints" / "active").mkdir(parents=True, exist_ok=True)
        (target / "learner" / "hints" / "archive").mkdir(parents=True, exist_ok=True)
        hints_registry = target / "learner" / "hints" / "hints.yaml"
        if not hints_registry.exists():
            hints_registry.write_text("schema_version: 0\nhints: []\n", encoding="utf-8")
    except OSError as exc:
        raise click.ClickException(
            f"Failed to write learner files: {exc}. "
            f"Re-run with --force to complete initialization."
        ) from exc

    # AGENTS.md + tool shims (ADR-0003). The boot document is bundled in the
    # engine (see src/sensei/engine/templates/AGENTS.md) rather than baked into
    # the CLI source, so it stays in sync with engine.md / protocols / schemas
    # any time the bundle is refreshed. `.sensei/` was just written above, so
    # the template is always readable from there.
    agents_template = sensei_dir / "templates" / "AGENTS.md"
    agents_md = target / "AGENTS.md"
    if not agents_md.exists():
        agents_md.write_text(
            agents_template.read_text(encoding="utf-8"), encoding="utf-8"
        )
    for rel_path, content in SHIMS.items():
        shim_path = target / rel_path
        if not shim_path.exists():
            write_shim(target, rel_path, content)

    click.echo(f"Created .sensei/ at {sensei_dir}")
    click.echo(f"Wrote AGENTS.md and {len(SHIMS)} tool-specific shims.")
    click.echo(f"Seeded learner/profile.yaml with learner_id={learner_id!r}.")
    click.echo("Open this folder with any LLM agent to begin.")


@main.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def status(target: Path) -> None:
    """Report instance state: engine version, profile summary, stale topics."""
    target = target.resolve()
    sensei_dir = target / ".sensei"
    if not sensei_dir.exists():
        raise click.ClickException(f"Not a Sensei instance: {target} (no .sensei/ directory).")

    version_file = sensei_dir / ".sensei-version"
    engine_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"
    click.echo(f"Instance: {target}")
    click.echo(f"Engine:   {engine_version}")

    # Profile summary
    profile_path = target / "learner" / "profile.yaml"
    if not profile_path.exists():
        click.echo("Profile:  not found")
        return

    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        click.echo("Profile:  invalid (not a mapping)")
        return

    learner_id = profile.get("learner_id", "unknown")
    expertise = profile.get("expertise_map") or {}
    total = len(expertise)

    # Count by mastery level
    levels = {"mastered": 0, "solid": 0, "developing": 0, "shaky": 0, "none": 0}
    for topic_state in expertise.values():
        if isinstance(topic_state, dict):
            lvl = topic_state.get("mastery", "none")
            if lvl in levels:
                levels[lvl] += 1

    click.echo(f"Learner:  {learner_id}")
    click.echo(f"Topics:   {total}")

    if total > 0:
        parts = [f"{v} {k}" for k, v in levels.items() if v > 0]
        click.echo(f"Mastery:  {', '.join(parts)}")

        # Stale topics (due for review)
        from datetime import datetime, timezone

        from sensei.engine.scripts.decay import freshness_score

        now = datetime.now(tz=timezone.utc)
        try:
            from sensei.engine.scripts.config import load_config

            merged = load_config(sensei_dir, target)
        except Exception:  # noqa: BLE001 — fallback to defaults-only is intentional
            click.echo("Warning: could not load merged config, using engine defaults.", err=True)
            defaults_path = sensei_dir / "defaults.yaml"
            merged = yaml.safe_load(defaults_path.read_text(encoding="utf-8")) if defaults_path.exists() else {}
            if not isinstance(merged, dict):
                merged = {}
        memory_cfg = merged.get("memory", {}) if isinstance(merged, dict) else {}
        half_life = float(memory_cfg.get("half_life_days", 7))
        threshold = float(memory_cfg.get("stale_threshold", 0.5))

        stale: list[str] = []
        malformed: list[str] = []
        for slug, state in expertise.items():
            if not isinstance(state, dict):
                continue
            last_seen_str = state.get("last_seen")
            if not last_seen_str:
                stale.append(slug)
                continue
            try:
                last_seen = datetime.fromisoformat(str(last_seen_str).replace("Z", "+00:00"))
                elapsed = (now - last_seen).total_seconds() / 86400.0
                if freshness_score(elapsed, half_life) < threshold:
                    stale.append(slug)
            except (ValueError, TypeError):
                # Treat as stale (conservative), but surface it so the learner
                # knows their profile has corrupt timestamps rather than a
                # silently-growing "due for review" list.
                stale.append(slug)
                malformed.append(slug)

        if malformed:
            click.echo(
                f"Warning:  {len(malformed)} topic{'s' if len(malformed) != 1 else ''} "
                f"with unparseable last_seen (treated as stale):"
            )
            for s in malformed[:5]:
                click.echo(f"          - {s}")
            if len(malformed) > 5:
                click.echo(f"          ... and {len(malformed) - 5} more")

        if stale:
            click.echo(f"Stale:    {len(stale)} topic{'s' if len(stale) != 1 else ''} due for review")
            for s in stale[:5]:
                click.echo(f"          - {s}")
            if len(stale) > 5:
                click.echo(f"          ... and {len(stale) - 5} more")


@main.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def upgrade(target: Path) -> None:
    """Update .sensei/ engine bundle to the installed package version."""
    target = target.resolve()
    sensei_dir = target / ".sensei"
    if not sensei_dir.exists():
        raise click.ClickException(f"Not a Sensei instance: {target} (no .sensei/ directory).")

    # Read current version
    version_file = sensei_dir / ".sensei-version"
    old_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"

    from packaging.version import InvalidVersion, Version
    try:
        old_ver, new_ver = Version(old_version), Version(__version__)
    except InvalidVersion:
        old_ver = new_ver = None  # type: ignore[assignment]
    if old_ver is not None and new_ver is not None and new_ver < old_ver:
        raise click.ClickException(
            f"Installed version ({__version__}) is older than current engine "
            f"({old_version}). Downgrade is not supported — install a newer "
            f"version or use 'init --force'."
        )

    if old_version == __version__:
        click.echo(f"Already at {__version__}. Nothing to upgrade.")
        return

    # Migrate learner state files BEFORE swapping the engine. If migration
    # fails (bad YAML, permissions, failed schema transform), the existing
    # engine remains on disk and is still compatible with the unmigrated
    # data. Swapping first would leave a new engine paired with old-format
    # data if a subsequent migration failed.
    learner_dir = target / "learner"
    migrated: list[str] = []
    if learner_dir.exists() or (target / "instance").exists():
        from sensei.engine.scripts.migrate import migrate_instance

        migrated = migrate_instance(learner_dir)

    # Replace engine bundle atomically (learner/ is untouched).
    atomic_replace_engine(engine_source(), sensei_dir, __version__)

    # Refresh interpreter path and run wrapper.
    install_run_script(sensei_dir)

    # Refresh AGENTS.md + tool shims to match new engine version.
    agents_template = sensei_dir / "templates" / "AGENTS.md"
    if agents_template.exists():
        (target / "AGENTS.md").write_text(
            agents_template.read_text(encoding="utf-8"), encoding="utf-8"
        )
    for rel_path, content in SHIMS.items():
        write_shim(target, rel_path, content)

    click.echo(f"Upgraded .sensei/ from {old_version} → {__version__}")
    if learner_dir.exists():
        if migrated:
            for desc in migrated:
                click.echo(f"  Migrated: {desc}")
        else:
            click.echo("  Instance schemas already current.")
    click.echo("Learner data (learner/) preserved.")


@main.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def verify(target: Path) -> None:
    """Verify engine bundle integrity: expected files present, profile valid."""
    from sensei._verify import run_verify
    run_verify(target)


if __name__ == "__main__":
    main()

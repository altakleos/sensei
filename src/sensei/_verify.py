"""Verify engine bundle integrity."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import click
import jsonschema
import yaml

from sensei._shims import SHIMS


def run_verify(target: Path) -> None:
    target = target.resolve()
    sensei_dir = target / ".sensei"
    if not sensei_dir.exists():
        raise click.ClickException(f"Not a Sensei instance: {target} (no .sensei/ directory).")

    errors: list[str] = []

    # `.sensei-version` is generated at install time, not shipped in the engine
    # bundle, so it is checked separately from the manifest.
    if not (sensei_dir / ".sensei-version").exists():
        errors.append("missing: .sensei/.sensei-version")

    # Bundle integrity is enumerated by `manifest.yaml` shipped inside the
    # engine. Missing manifest is itself a verify failure — without it we
    # cannot determine what should be present.
    manifest_path = sensei_dir / "manifest.yaml"
    if not manifest_path.exists():
        errors.append("missing: .sensei/manifest.yaml")
    else:
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"manifest.yaml: invalid YAML — {exc}")
            manifest = None
        if isinstance(manifest, dict):
            schema_ver = manifest.get("schema_version", 1)
            required = manifest.get("required", [])
            if not isinstance(required, list):
                errors.append("manifest.yaml: 'required' must be a list")
            else:
                for entry in required:
                    if schema_ver >= 2:
                        # v2: entry is a dict with path + sha256
                        if not isinstance(entry, dict):
                            errors.append(f"manifest.yaml: expected dict entry, got {type(entry).__name__}")
                            continue
                        rel = entry.get("path", "")
                        expected_hash = entry.get("sha256", "")
                        file_path = sensei_dir / rel
                        if not file_path.exists():
                            errors.append(f"missing: .sensei/{rel}")
                            continue
                        actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                        if actual_hash != expected_hash:
                            errors.append(f"checksum mismatch: .sensei/{rel}")
                    else:
                        # v1 fallback: existence only
                        if not isinstance(entry, str):
                            errors.append(f"manifest.yaml: non-string entry {entry!r}")
                            continue
                        if not (sensei_dir / entry).exists():
                            errors.append(f"missing: .sensei/{entry}")
        elif manifest is not None:
            errors.append("manifest.yaml: not a YAML mapping")

    profile_path = target / "learner" / "profile.yaml"
    if profile_path.exists():
        try:
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            if isinstance(profile, dict):
                from sensei.engine.scripts.check_profile import validate_profile

                v_status, errs = validate_profile(profile)
                if v_status != "ok":
                    for e in errs:
                        errors.append(f"profile: {e}")
            else:
                errors.append("profile: not a YAML mapping")
        except yaml.YAMLError as exc:
            errors.append(f"profile: invalid YAML — {exc}")
    else:
        errors.append("missing: learner/profile.yaml")

    session_notes_path = target / "learner" / "session-notes.yaml"
    if session_notes_path.exists():
        try:
            notes_data = yaml.safe_load(session_notes_path.read_text(encoding="utf-8"))
            if isinstance(notes_data, dict):
                schema_path = sensei_dir / "schemas" / "session-notes.schema.json"
                if schema_path.exists():
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    validator = jsonschema.Draft202012Validator(schema)
                    for err in sorted(validator.iter_errors(notes_data), key=lambda e: list(e.absolute_path)):
                        errors.append(f"session-notes: {list(err.absolute_path) or '<root>'}: {err.message}")
            else:
                errors.append("session-notes: not a YAML mapping")
        except yaml.YAMLError as exc:
            errors.append(f"session-notes: invalid YAML — {exc}")

    # Validate the merged config (defaults + learner override) against
    # defaults.schema.json. The merged result is what scripts see at
    # runtime, so a learner-side typo or wrong type must surface here.
    # `load_config` itself hard-fails on schema errors per ADR-0025; we
    # downgrade to soft-fail in this scope so verify can collect every
    # offending dotpath rather than aborting on the first one.
    defaults_schema_path = sensei_dir / "schemas" / "defaults.schema.json"
    defaults_yaml_path = sensei_dir / "defaults.yaml"
    if defaults_schema_path.exists() and defaults_yaml_path.exists():
        prior_soft_fail = os.environ.get("SENSEI_CONFIG_SOFT_FAIL")
        os.environ["SENSEI_CONFIG_SOFT_FAIL"] = "1"
        try:
            from sensei.engine.scripts.config import load_config

            merged = load_config(sensei_dir, target)
            schema = json.loads(defaults_schema_path.read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator(schema)
            for err in sorted(validator.iter_errors(merged), key=lambda e: list(e.absolute_path)):
                errors.append(f"config: {list(err.absolute_path) or '<root>'}: {err.message}")
        except (yaml.YAMLError, ValueError) as exc:
            errors.append(f"config: {exc}")
        finally:
            if prior_soft_fail is None:
                os.environ.pop("SENSEI_CONFIG_SOFT_FAIL", None)
            else:
                os.environ["SENSEI_CONFIG_SOFT_FAIL"] = prior_soft_fail

    # Check 6: goal files.
    goals_dir = target / "learner" / "goals"
    if goals_dir.is_dir():
        from sensei.engine.scripts.check_goal import validate_goal
        for goal_path in sorted(goals_dir.glob("*.yaml")):
            try:
                goal_data = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"{goal_path.name}: invalid YAML — {exc}")
                continue
            if not isinstance(goal_data, dict):
                errors.append(f"{goal_path.name}: not a YAML mapping")
                continue
            _status, goal_errors = validate_goal(goal_data)
            for ge in goal_errors:
                errors.append(f"{goal_path.name}: {ge}")

    # Check 7: AGENTS.md exists.
    if not (target / "AGENTS.md").exists():
        errors.append("missing: AGENTS.md")

    # Check 8: tool shims.
    for rel_path in SHIMS:
        if not (target / rel_path).exists():
            errors.append(f"missing: {rel_path}")

    # Check 9: hints registry.
    hints_path = target / "learner" / "hints" / "hints.yaml"
    hints_schema_path = sensei_dir / "schemas" / "hints.yaml.schema.json"
    if hints_path.exists() and hints_schema_path.exists():
        try:
            hints_data = yaml.safe_load(hints_path.read_text(encoding="utf-8"))
            hints_schema = json.loads(hints_schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(hints_data, hints_schema)
        except yaml.YAMLError as exc:
            errors.append(f"hints.yaml: invalid YAML — {exc}")
        except jsonschema.ValidationError as exc:
            errors.append(f"hints.yaml: {exc.message}")

    if errors:
        click.echo("FAIL")
        for e in errors:
            click.echo(f"  ✗ {e}")
        sys.exit(1)
    else:
        click.echo("OK — engine bundle intact, profile valid.")

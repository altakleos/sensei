"""Validator for learner/profile.yaml (per docs/design/learner-profile-state.md).

Runs JSON Schema validation followed by cross-field invariants that JSON Schema
alone cannot express (currently only `correct <= attempts`).

Exits:
    0 — profile is valid
    1 — parse failure or schema violation
    2 — cross-field invariant violation

Always prints a single JSON line to stdout summarizing what was checked and
what failed, so protocols can surface the failure to the learner without
parsing stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as _err:  # pragma: no cover
    print(f"ERROR: Missing dependency ({_err.name}). Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "profile.schema.json"


def _load_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        schema: dict[str, Any] = json.load(fh)
    return schema


def _check_cross_field(profile: dict[str, Any]) -> list[str]:
    """Return a list of cross-field invariant violations (empty if valid)."""
    violations: list[str] = []
    expertise = profile.get("expertise_map", {}) or {}
    for slug, state in expertise.items():
        attempts = state.get("attempts", 0)
        correct = state.get("correct", 0)
        if correct > attempts:
            violations.append(
                f"topic {slug!r}: correct ({correct}) exceeds attempts ({attempts})"
            )
    return violations


def validate_profile(profile: dict[str, Any]) -> tuple[str, list[str]]:
    """Validate a parsed profile dict.

    Migrates the profile to the current schema version before validating,
    so older profiles (e.g. schema_version 0 without emotional_state) are
    accepted during the transition period.

    Returns a tuple (status, errors) where status is one of:
        "ok"           — profile is valid
        "schema"       — schema violations (also returned when required field missing)
        "cross_field"  — schema passes but cross-field invariants fail

    `errors` lists human-readable error messages.
    """
    import contextlib

    from migrate import migrate_profile  # type: ignore[import-not-found]

    # Migration may fail (bad data); fall through to schema validation which
    # will report the real error.
    with contextlib.suppress(ValueError, KeyError):
        profile = migrate_profile(dict(profile))

    schema = _load_schema()
    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(profile), key=lambda e: list(e.absolute_path))
    if schema_errors:
        return "schema", [f"{list(e.absolute_path) or '<root>'}: {e.message}" for e in schema_errors]
    cross = _check_cross_field(profile)
    if cross:
        return "cross_field", cross
    return "ok", []


def _emit(status: str, errors: list[str], path: str) -> None:
    print(json.dumps({"path": path, "status": status, "errors": errors}))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--profile", required=True, help="Path to profile.yaml")
    args = parser.parse_args(argv)

    path = Path(args.profile)
    if not path.is_file():
        _emit("schema", [f"profile file not found: {path}"], str(path))
        return 1

    try:
        with path.open("r", encoding="utf-8") as fh:
            profile = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        _emit("schema", [f"yaml parse error: {exc}"], str(path))
        return 1

    if not isinstance(profile, dict):
        _emit("schema", ["top-level yaml must be a mapping"], str(path))
        return 1

    status, errors = validate_profile(profile)
    _emit(status, errors, str(path))
    if status == "ok":
        return 0
    if status == "cross_field":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())

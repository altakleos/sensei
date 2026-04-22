"""Mastery threshold gate (per docs/design/learner-profile-state.md).

Given a learner profile, a topic slug, and a required mastery level, answer
whether the learner meets or exceeds the required level on that topic.

Invoked by protocols as:
    python mastery_check.py --profile learner/profile.yaml \\
                            --topic recursion --required solid

Exits:
    0 — learner meets the required level (pass)
    1 — profile invalid (parse / schema / cross-field failure)
    3 — learner does not meet the required level (fail)

Always prints a single JSON line describing the decision.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from sensei.engine.scripts.check_profile import validate_profile

# Ordered mastery levels; index == rank.
_LEVELS: tuple[str, ...] = ("none", "shaky", "developing", "solid", "mastered")


def rank(level: str) -> int:
    """Return the rank of a mastery level. Raises ValueError if unknown."""
    try:
        return _LEVELS.index(level)
    except ValueError:
        raise ValueError(f"unknown mastery level {level!r}; expected one of {_LEVELS}") from None


def meets(current: str, required: str) -> bool:
    """True iff `current` mastery level is at or above `required`."""
    return rank(current) >= rank(required)


def _emit(
    *,
    topic: str,
    current_mastery: str,
    required: str,
    gate: str,
    reason: str | None = None,
) -> None:
    payload: dict[str, object] = {
        "topic": topic,
        "current_mastery": current_mastery,
        "required": required,
        "gate": gate,
    }
    if reason is not None:
        payload["reason"] = reason
    print(json.dumps(payload))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--profile", required=True, help="Path to profile.yaml")
    parser.add_argument("--topic", required=True, help="Topic slug to check")
    parser.add_argument("--required", required=True, choices=list(_LEVELS), help="Required mastery level")
    args = parser.parse_args(argv)

    path = Path(args.profile)
    if not path.is_file():
        print(json.dumps({"error": f"profile file not found: {path}"}))
        return 1

    try:
        with path.open("r", encoding="utf-8") as fh:
            profile = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        print(json.dumps({"error": f"yaml parse error: {exc}"}))
        return 1

    if not isinstance(profile, dict):
        print(json.dumps({"error": "top-level yaml must be a mapping"}))
        return 1

    status, errors = validate_profile(profile)
    if status != "ok":
        print(json.dumps({"error": "invalid profile", "status": status, "errors": errors}))
        return 1

    expertise = profile.get("expertise_map", {}) or {}
    topic_state = expertise.get(args.topic)
    if topic_state is None:
        # Absent topic ≡ mastery "none" per spec invariant.
        current = "none"
        reason = "topic absent from expertise_map; treated as mastery 'none'"
    else:
        current = topic_state["mastery"]
        reason = None

    passed = meets(current, args.required)
    _emit(
        topic=args.topic,
        current_mastery=current,
        required=args.required,
        gate="pass" if passed else "fail",
        reason=reason,
    )
    return 0 if passed else 3


if __name__ == "__main__":
    sys.exit(main())

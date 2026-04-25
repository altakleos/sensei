"""Check if a topic is already mastered globally across all goals.

Reads the learner profile's expertise_map and reports whether the given
topic slug has mastery >= solid (i.e. "solid" or "mastered").  Protocols
use this to skip topics the learner already knows.

Invoked by protocols as:
    python global_knowledge.py --profile learner/profile.yaml --topic hash-maps

Exits 0 and prints a single JSON object to stdout.
Exits 1 on invalid input (missing file, bad YAML).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)

# Mastery levels in rank order; "solid" and above count as globally known.
_LEVELS: tuple[str, ...] = ("none", "shaky", "developing", "solid", "mastered")
_SCORES: dict[str, float] = {
    "none": 0.0,
    "shaky": 0.25,
    "developing": 0.5,
    "solid": 0.75,
    "mastered": 1.0,
}
_KNOWN_THRESHOLD = _LEVELS.index("solid")  # rank 3


def check(
    profile: dict[str, Any],
    topic: str,
    *,
    goal: dict[str, Any] | None = None,
    concept_peers: list[str] | None = None,
    goal_depth: str | None = None,
) -> dict[str, Any]:
    """Return knowledge status for *topic* given a parsed profile dict.

    When *goal* is provided and the topic's node has
    ``require_redemonstration: true``, the result overrides ``known`` to
    ``False`` and includes ``redemonstration_required: true``.

    When *goal_depth* is ``"deep"``, the known threshold is raised to
    ``mastered`` — a topic at ``solid`` is not auto-skipped because the
    goal demands deeper understanding. The probe-first behavior in the
    tutor protocol handles the UX: the learner is probed, not re-taught.

    When *concept_peers* is provided (list of topic slugs sharing concept
    tags, resolved by the protocol) and the topic is not directly known,
    checks if any peer is known. If so, returns ``concept_evidence: true``
    — evidence, not proof.
    """
    threshold = _LEVELS.index("mastered") if goal_depth == "deep" else _KNOWN_THRESHOLD
    expertise = profile.get("expertise_map") or {}
    entry = expertise.get(topic)
    if entry is None:
        result: dict[str, Any] = {"topic": topic, "known": False, "mastery": 0.0}
        # Concept-level evidence: topic not in profile but a peer with shared
        # concept tags is known globally.
        if concept_peers:
            for peer in concept_peers:
                peer_entry = expertise.get(peer)
                if peer_entry and _LEVELS.index(peer_entry.get("mastery", "none")) >= threshold:
                    result["concept_evidence"] = True
                    result["evidence_from"] = peer
                    break
        return result
    mastery = entry.get("mastery", "none")
    known = _LEVELS.index(mastery) >= threshold
    result = {"topic": topic, "known": known, "mastery": _SCORES.get(mastery, 0.0)}

    # Per-goal re-demonstration override (cross-goal intelligence invariant 1).
    if goal is not None and known:
        nodes = goal.get("nodes") or {}
        node = nodes.get(topic)
        if node is not None and node.get("require_redemonstration") is True:
            result["known"] = False
            result["redemonstration_required"] = True

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--profile", required=True, help="Path to profile.yaml")
    parser.add_argument("--topic", required=True, help="Topic slug to check")
    parser.add_argument("--goal", default=None, help="Optional path to goal YAML file for re-demonstration check")
    parser.add_argument(
        "--concept-peers",
        default=None,
        help="JSON list of topic slugs sharing concept tags (resolved by protocol)",
    )
    parser.add_argument(
        "--goal-depth",
        default=None,
        choices=["exposure", "functional", "deep"],
        help="Goal's target_depth. When 'deep', raises the known threshold to 'mastered'.",
    )
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

    goal = None
    if args.goal:
        goal_path = Path(args.goal)
        if not goal_path.is_file():
            print(json.dumps({"error": f"goal file not found: {goal_path}"}))
            return 1
        try:
            with goal_path.open("r", encoding="utf-8") as fh:
                goal = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            print(json.dumps({"error": f"yaml parse error: {exc}"}))
            return 1

    concept_peers = json.loads(args.concept_peers) if args.concept_peers else None
    print(
        json.dumps(
            check(
                profile,
                args.topic,
                goal=goal,
                concept_peers=concept_peers,
                goal_depth=args.goal_depth,
            )
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

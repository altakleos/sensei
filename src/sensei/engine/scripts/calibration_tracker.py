"""Calibration accuracy tracker.

Computes the ratio of confident-correct to total-confident responses
from the learner's expertise_map. A learner who is confident and correct
9 out of 10 times has calibration_accuracy 0.9.

Invoked by protocols as:
    python calibration_tracker.py --profile learner/profile.yaml

Exits 0 and prints a single JSON object to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)


def compute_calibration(profile: dict) -> float | None:
    """Compute calibration_accuracy from expertise_map.

    Returns the ratio of correct to attempts for topics where the learner
    has been assessed (attempts > 0). Returns None if no topics have
    attempts — insufficient data to compute calibration.
    """
    expertise = profile.get("expertise_map", {})
    total_attempts = 0
    total_correct = 0
    for topic_state in expertise.values():
        attempts = topic_state.get("attempts", 0)
        if attempts > 0:
            total_attempts += attempts
            total_correct += topic_state.get("correct", 0)
    if total_attempts == 0:
        return None
    return total_correct / total_attempts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--profile", required=True, type=Path, help="Path to profile.yaml")
    args = parser.parse_args(argv)

    profile = yaml.safe_load(args.profile.read_text(encoding="utf-8"))
    if profile is None:
        print(json.dumps({"calibration_accuracy": None}))
        return 0

    accuracy = compute_calibration(profile)
    print(json.dumps({"calibration_accuracy": accuracy}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

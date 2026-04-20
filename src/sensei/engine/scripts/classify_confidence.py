"""Confidence × correctness 4-quadrant classifier (per ADR-0006 § V1 scope, see docs/research/synthesis/accelerated-performance.md).

Quadrant semantics:
    confident + correct   = mastery        (stable knowledge)
    confident + incorrect = misconception  (dangerous — learner believes the wrong thing)
    uncertain + correct   = fragile        (correct answer, shaky grasp)
    uncertain + incorrect = gap            (genuine not-yet-learned)

Invoked by protocols as:
    python classify_confidence.py --confidence confident --correctness correct

Exits 0 and prints a single JSON object to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Literal

Confidence = Literal["confident", "uncertain"]
Correctness = Literal["correct", "incorrect"]
Quadrant = Literal["mastery", "misconception", "fragile", "gap"]

_QUADRANT: dict[tuple[Confidence, Correctness], Quadrant] = {
    ("confident", "correct"): "mastery",
    ("confident", "incorrect"): "misconception",
    ("uncertain", "correct"): "fragile",
    ("uncertain", "incorrect"): "gap",
}

_INTERPRETATION: dict[Quadrant, str] = {
    "mastery": "Stable knowledge. Advance.",
    "misconception": "Dangerous — learner is confidently wrong. Surface the conflict before teaching.",
    "fragile": "Correct but shaky. Reinforce before moving on.",
    "gap": "Not yet learned. Teach; prerequisites may be missing.",
}


def classify(confidence: Confidence, correctness: Correctness) -> dict[str, str]:
    """Classify a learner response into one of four quadrants.

    Raises ValueError if either input is not in the accepted set.
    """
    if confidence not in ("confident", "uncertain"):
        raise ValueError(f"confidence must be 'confident' or 'uncertain', got {confidence!r}")
    if correctness not in ("correct", "incorrect"):
        raise ValueError(f"correctness must be 'correct' or 'incorrect', got {correctness!r}")
    quadrant = _QUADRANT[(confidence, correctness)]
    return {
        "quadrant": quadrant,
        "interpretation": _INTERPRETATION[quadrant],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--confidence", required=True, choices=["confident", "uncertain"])
    parser.add_argument("--correctness", required=True, choices=["correct", "incorrect"])
    args = parser.parse_args(argv)
    result = classify(args.confidence, args.correctness)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Multi-turn capture harness for dogfood transcripts.

Invokes a real LLM (via agent_runner) to produce `.dogfood.md` files that
the transcript fixture system validates. Each protocol (hints, assess,
review) is scaffolded, seeded, and run independently.

Usage:
    python tests/e2e/capture_dogfood.py --protocol hints|assess|review|all
    python tests/e2e/capture_dogfood.py --protocol all --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is on sys.path for standalone execution.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main
from tests.e2e.agent_runner import TOOL, TOOL_AVAILABLE, run_agent

PROTOCOLS = ("hints", "assess", "review")
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "transcripts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _scaffold(tmp: Path) -> None:
    """Run `sensei init` into *tmp*."""
    result = CliRunner().invoke(sensei_main, ["init", str(tmp), "--learner-id", "e2e"])
    if result.exit_code != 0:
        raise RuntimeError(f"sensei init failed:\n{result.output}")


def _extract_mentor_text(completed) -> str:
    """Pull the pedagogical text from the agent's raw output.

    Claude (--output-format json): parse JSON, grab ``result``.
    Kiro / fallback: two-pass extraction — strip noise lines, then walk
    paragraphs from the end to find the mentor's actual speech.
    """
    raw = completed.stdout or ""
    if TOOL == "claude":
        try:
            data = json.loads(raw)
            # Claude JSON output has a `result` field with the text
            return data.get("result", raw)
        except (json.JSONDecodeError, TypeError):
            pass

    # ── Pass 1: strip ANSI codes and obvious noise lines ──

    # Strip ALL ANSI escape codes (including \x1b[K and similar)
    text = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', raw)

    # Remove <thinking>...</thinking> blocks
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)

    # Strip Kiro's "> " output prefix
    text = re.sub(r'^> ?', '', text, flags=re.MULTILINE)

    # Noise line patterns
    _NOISE = re.compile(
        r'^Batch .+ operation with'
        r'|^↱ Operation \d+'
        r'|^✓ Successfully'
        r'|^⋮'
        r'|^-?\s*Summary: \d+ operations'
        r'|^-?\s*Completed in '
        r'|^Replacing: '
        r'|^Updating: '
        r'|^I will run the following command: '
        r'|^Purpose: '
        r'|^Wrote '
        r'|^Created '
        r'|^Updated '
        r'|^Reading file: '
        r'|^Reading directory: '
        r'|^\+\s+\d+:'
        r'|^\.\.\.$'
        r'|^\d{4}-\d{2}-\d{2}T'
        r'|^\[\d*\]$'
        r'|^\[\]$'
    )

    # Diff-like lines: `- N   :`, `  N, N:`, or lines still containing \x1b
    _DIFF = re.compile(
        r'^-\s+\d+\s*:'
        r'|^\s+\d+,\s*\d+:'
        r'|\\x1b\['
    )

    # JSON blob lines: bare JSON objects on a line
    _JSON_BLOB = re.compile(r'^\s*\{.*\}\s*$')

    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if _NOISE.search(stripped):
            continue
        if _DIFF.search(stripped):
            continue
        # Drop bare JSON object lines
        if _JSON_BLOB.match(stripped):
            try:
                json.loads(stripped)
                continue
            except (json.JSONDecodeError, TypeError):
                pass
        lines.append(line)

    # Collapse multiple blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()

    # ── Pass 2: extract mentor speech from the end ──

    # Split into paragraphs (separated by one or more blank lines)
    paragraphs = re.split(r'\n\s*\n', cleaned)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return cleaned

    # Internal reasoning markers — if a paragraph matches, it's NOT mentor speech
    _REASONING_START = re.compile(
        r'^(Now I|Let me|I need to|I\'ll |I should|I must'
        r'|I have the|Good\.|Good —|Good,)'
    )
    _REASONING_CONTAINS = re.compile(
        r'Per Step|Per the protocol|Per the assessor|Per the review'
        r'|the learner\'s response|the learner said|the learner answered'
        r'|Gate not met|Gate result|This is failure'
        r'|Now update|Profile is valid'
        r'|The queue is ranked|stale topic|freshness \d'
        r'|calibration_accuracy|EXIT:\s*\d|failure count'
        r'|mastery is still|I should ask'
        r'|"If the learner'
        r'|using tool:|Reading file:|Reading directory:'
    , re.IGNORECASE)

    def _is_reasoning(para: str) -> bool:
        first_line = para.split('\n')[0].strip()
        if _REASONING_START.match(first_line):
            return True
        if _REASONING_CONTAINS.search(para):
            return True
        return False

    # Walk from the end backwards; stop at the first reasoning paragraph
    mentor_start = len(paragraphs)
    for i in range(len(paragraphs) - 1, -1, -1):
        if _is_reasoning(paragraphs[i]):
            break
        mentor_start = i

    mentor_paragraphs = paragraphs[mentor_start:]
    if not mentor_paragraphs:
        # Fallback: return the last paragraph
        return paragraphs[-1]

    return '\n\n'.join(mentor_paragraphs)


def _build_frontmatter(protocol: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    model = "unknown"
    agent = TOOL or "unknown"
    return (
        f"---\n"
        f"protocol: {protocol}\n"
        f"agent: {agent}\n"
        f"model: {model}\n"
        f"captured: {now}\n"
        f"fixture_ref: {protocol}.md\n"
        f"status: captured\n"
        f"note: Captured by capture_dogfood.py\n"
        f"---\n"
    )


def _run_turn(prompt: str, cwd: Path, timeout: int) -> str:
    """Run one agent turn and return extracted mentor text."""
    completed = run_agent(prompt, cwd=cwd, timeout=timeout)
    if completed.returncode != 0:
        raise RuntimeError(
            f"agent exited {completed.returncode}\n"
            f"stderr: {completed.stderr[:1000]}"
        )
    return _extract_mentor_text(completed)


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def _seed_hints(instance_dir: Path) -> None:
    """Create 4 inbox items matching hints.md fixture expectations."""
    inbox = instance_dir / "learner" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    # 1. Clear article — maps to an existing curriculum topic
    (inbox / "rust-ownership-guide.md").write_text(
        "# Rust Ownership Deep Dive\n\n"
        "A comprehensive guide to ownership, borrowing, and lifetimes in Rust.\n"
        "Covers move semantics, the borrow checker, and common patterns.\n",
        encoding="utf-8",
    )
    # 2. Ambiguous item — unclear relevance, should trigger clarification
    (inbox / "interesting-tweet.txt").write_text(
        "Saw this cool tweet about ML model compression techniques.\n"
        "Not sure if relevant but saving it anyway.\n",
        encoding="utf-8",
    )
    # 3. Overlaps existing curriculum topic
    (inbox / "async-runtime-notes.md").write_text(
        "# Notes on Async Runtimes\n\n"
        "Tokio vs async-std comparison. Event loop internals.\n"
        "Relates to the async-await topic in my Rust curriculum.\n",
        encoding="utf-8",
    )
    # 4. Short tip
    (inbox / "quick-tip.txt").write_text(
        "Tip: use `cargo clippy` for better lint warnings.\n",
        encoding="utf-8",
    )

    # Seed a goal with curriculum so hints can map to topics
    _seed_hints_goal(instance_dir)


def _seed_hints_goal(instance_dir: Path) -> None:
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 0,
        "goal_id": "learn-rust",
        "expressed_as": "Learn Rust for systems programming",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Self-paced",
        },
        "nodes": {
            "ownership": {"state": "active", "prerequisites": []},
            "lifetimes": {"state": "active", "prerequisites": ["ownership"]},
            "async-await": {"state": "active", "prerequisites": []},
            "traits": {"state": "active", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "learn-rust.yaml").write_text(yaml.safe_dump(goal), encoding="utf-8")


def _seed_assess(instance_dir: Path) -> None:
    """Seed profile + goal for assessment protocol."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "recursion": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": _utc_iso(now - timedelta(days=3)),
                "attempts": 6,
                "correct": 3,
            },
            "sorting-algorithms": {
                "mastery": "developing",
                "confidence": 0.4,
                "last_seen": _utc_iso(now - timedelta(days=5)),
                "attempts": 4,
                "correct": 2,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 0,
        "goal_id": "dsa-fundamentals",
        "expressed_as": "Master fundamental data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Interview prep",
        },
        "nodes": {
            "recursion": {"state": "completed", "prerequisites": []},
            "sorting-algorithms": {
                "state": "completed",
                "prerequisites": ["recursion"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-fundamentals.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _seed_review(instance_dir: Path) -> None:
    """Seed profile with stale topics + goal for review protocol."""
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "binary-search": {
                "mastery": "solid",
                "confidence": 0.7,
                "last_seen": _utc_iso(now - timedelta(days=35)),
                "attempts": 8,
                "correct": 7,
            },
            "merge-sort": {
                "mastery": "solid",
                "confidence": 0.6,
                "last_seen": _utc_iso(now - timedelta(days=30)),
                "attempts": 6,
                "correct": 5,
            },
            "hash-tables": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": _utc_iso(now - timedelta(days=2)),
                "attempts": 3,
                "correct": 2,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 0,
        "goal_id": "dsa-review",
        "expressed_as": "Review core data structures and algorithms",
        "created": _utc_iso(now - timedelta(days=30)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Ongoing review",
        },
        "nodes": {
            "binary-search": {"state": "completed", "prerequisites": []},
            "merge-sort": {"state": "completed", "prerequisites": []},
            "hash-tables": {"state": "completed", "prerequisites": ["binary-search"]},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "dsa-review.yaml").write_text(yaml.safe_dump(goal), encoding="utf-8")


# ---------------------------------------------------------------------------
# Multi-turn capture per protocol
# ---------------------------------------------------------------------------

def _capture_hints(instance_dir: Path, timeout: int) -> str:
    """Capture a hints triage session (2 turns)."""
    _seed_hints(instance_dir)

    turn1_prompt = (
        "I have new items in my inbox. Process my hints and tell me what you found."
    )
    mentor1 = _run_turn(turn1_prompt, cwd=instance_dir, timeout=timeout)

    # Turn 2: respond to the ambiguity question the mentor should ask
    history = (
        f"Previous conversation:\n"
        f"Learner: {turn1_prompt}\n"
        f"Mentor: {mentor1}\n\n"
        f"Continue the conversation. The learner says:\n"
    )
    turn2_prompt = (
        f"{history}"
        "The ML tweet is unrelated to Rust — it was just something I found interesting. "
        "You can archive it for now."
    )
    mentor2 = _run_turn(turn2_prompt, cwd=instance_dir, timeout=timeout)

    body = (
        f"[LEARNER] {turn1_prompt}\n\n"
        f"[MENTOR] {mentor1}\n\n"
        f"[LEARNER] The ML tweet is unrelated to Rust — it was just something I found "
        f"interesting. You can archive it for now.\n\n"
        f"[MENTOR] {mentor2}\n"
    )
    return _build_frontmatter("hints") + "\n" + body


def _capture_assess(instance_dir: Path, timeout: int) -> str:
    """Capture an assessment session (5 turns).

    Exercises all assess fixtures:
      - assessor-silence: correct answer → "Got it." / "One more."
      - gate-result-reported: gate progression visible
      - two-failure-diagnosis: two wrong answers → "Two misses"
    """
    _seed_assess(instance_dir)

    # Learner answers used in the conversation.
    learner_answers = [
        (  # Turn 1: correct — directly answers whatever recursion question is posed
            "def nested_sum(lst):\n"
            "    total = 0\n"
            "    for item in lst:\n"
            "        if isinstance(item, list):\n"
            "            total += nested_sum(item)\n"
            "        else:\n"
            "            total += item\n"
            "    return total\n\n"
            "Base case: the element is an integer, just add it. "
            "Recursive case: the element is a list, recurse into it. "
            "For [1, [2, [3, 4], 5], 6]: first call processes 1 (add), "
            "then [2, [3, 4], 5] (recurse), then 6 (add). The nested call "
            "processes 2 (add), [3, 4] (recurse), 5 (add). Deepest call "
            "processes 3 and 4. Total: 21."
        ),
        (  # Turn 2: wrong — vague, doesn't answer the specific question
            "I think you just call the function again with different arguments."
        ),
        (  # Turn 3: wrong again — triggers "Two misses" diagnosis
            "Something about splitting the list in half?"
        ),
    ]

    turn1_prompt = "Assess my knowledge of recursion."
    mentor1 = _run_turn(turn1_prompt, cwd=instance_dir, timeout=timeout)

    # Build turns iteratively, accumulating history.
    history_lines = [
        f"Learner: {turn1_prompt}",
        f"Mentor: {mentor1}",
    ]
    mentor_turns = [mentor1]

    for answer in learner_answers:
        history = (
            "Previous conversation:\n"
            + "\n".join(history_lines)
            + "\n\nContinue the conversation. The learner says:\n"
        )
        prompt = history + answer
        mentor_resp = _run_turn(prompt, cwd=instance_dir, timeout=timeout)
        history_lines.append(f"Learner: {answer}")
        history_lines.append(f"Mentor: {mentor_resp}")
        mentor_turns.append(mentor_resp)

    # Assemble dogfood body.
    body_parts = [f"[LEARNER] {turn1_prompt}\n"]
    for i, answer in enumerate(learner_answers):
        body_parts.append(f"[MENTOR] {mentor_turns[i]}\n")
        body_parts.append(f"[LEARNER] {answer}\n")
    # Final mentor turn after last learner answer.
    body_parts.append(f"[MENTOR] {mentor_turns[-1]}\n")

    return _build_frontmatter("assess") + "\n" + "\n".join(body_parts)


def _capture_review(instance_dir: Path, timeout: int) -> str:
    """Capture a review session (3 turns)."""
    _seed_review(instance_dir)

    turn1_prompt = "Let's do a review session."
    mentor1 = _run_turn(turn1_prompt, cwd=instance_dir, timeout=timeout)

    # Turn 2: answer the retrieval question
    history = (
        f"Previous conversation:\n"
        f"Learner: {turn1_prompt}\n"
        f"Mentor: {mentor1}\n\n"
        f"Continue the conversation. The learner says:\n"
    )
    turn2_prompt = (
        f"{history}"
        "Binary search works by dividing a sorted array in half each step. "
        "Compare the target to the middle element — go left if smaller, "
        "right if larger. Time complexity is O(log n)."
    )
    mentor2 = _run_turn(turn2_prompt, cwd=instance_dir, timeout=timeout)

    # Turn 3: end the session
    history2 = (
        f"Previous conversation:\n"
        f"Learner: {turn1_prompt}\n"
        f"Mentor: {mentor1}\n"
        f"Learner: Binary search works by dividing a sorted array in half each step.\n"
        f"Mentor: {mentor2}\n\n"
        f"Continue the conversation. The learner says:\n"
    )
    turn3_prompt = f"{history2}stop"
    mentor3 = _run_turn(turn3_prompt, cwd=instance_dir, timeout=timeout)

    body = (
        f"[LEARNER] review\n\n"
        f"[MENTOR] {mentor1}\n\n"
        f"[LEARNER] Binary search works by dividing a sorted array in half each step. "
        f"Compare the target to the middle element — go left if smaller, "
        f"right if larger. Time complexity is O(log n).\n\n"
        f"[MENTOR] {mentor2}\n\n"
        f"[LEARNER] stop\n\n"
        f"[MENTOR] {mentor3}\n"
    )
    return _build_frontmatter("review") + "\n" + body


CAPTURE_FNS = {
    "hints": _capture_hints,
    "assess": _capture_assess,
    "review": _capture_review,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _capture_one(protocol: str, output_dir: Path, timeout: int, dry_run: bool) -> bool:
    """Capture one protocol. Returns True on success."""
    tmp = tempfile.mkdtemp(prefix=f"sensei-capture-{protocol}-")
    try:
        print(f"[{protocol}] Scaffolding into {tmp}")
        _scaffold(Path(tmp))

        print(f"[{protocol}] Seeding state and running multi-turn capture...")
        content = CAPTURE_FNS[protocol](Path(tmp), timeout)

        out_path = output_dir / f"{protocol}.dogfood.md"
        if dry_run:
            print(f"[{protocol}] --dry-run: would write {out_path}")
            print("--- begin preview ---")
            print(content)
            print("--- end preview ---")
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            print(f"[{protocol}] Wrote {out_path}")
        return True
    except Exception as exc:
        print(f"[{protocol}] FAILED: {exc}", file=sys.stderr)
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture real LLM dogfood transcripts for the transcript fixture system.",
    )
    parser.add_argument(
        "--protocol",
        required=True,
        choices=[*PROTOCOLS, "all"],
        help="Which protocol to capture (or 'all').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview output without writing files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-turn timeout in seconds (default: 120).",
    )
    args = parser.parse_args()

    if not TOOL_AVAILABLE:
        print(f"No LLM tool available (detected tool: {TOOL}). Cannot capture.", file=sys.stderr)
        sys.exit(1)

    print(f"Using agent: {TOOL}")

    protocols = list(PROTOCOLS) if args.protocol == "all" else [args.protocol]
    results = {}
    for proto in protocols:
        results[proto] = _capture_one(proto, args.output_dir, args.timeout, args.dry_run)

    # Summary
    print()
    for proto, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"  {proto}: {status}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()

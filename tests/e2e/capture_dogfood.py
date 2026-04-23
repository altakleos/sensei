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

PROTOCOLS = ("hints", "assess", "review", "performance_training", "cross_goal_review")
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
        r'|^\s*\d+,\s*\d+:'
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
        r'|Gate not met|Gate result|This is failure|failure count'
        r'|Now update|Profile is valid'
        r'|The queue is ranked|stale topic|freshness \d'
        r'|calibration_accuracy|calibration tracker|EXIT:\s*\d'
        r'|mastery is still|I should ask|session observation'
        r'|"If the learner'
        r'|using tool:|Reading file:|Reading directory:'
        r'|\[SYSTEM:'
        r'|Assessment failure count'
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
    """Seed profile + goal for assessment protocol.

    Uses 'addition' — an unambiguous domain where correct answers are
    indisputable and the mentor cannot reject them.
    """
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "addition": {
                "mastery": "developing",
                "confidence": 0.5,
                "last_seen": _utc_iso(now - timedelta(days=3)),
                "attempts": 6,
                "correct": 3,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 0,
        "goal_id": "basic-arithmetic",
        "expressed_as": "Learn basic arithmetic",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Self-study",
        },
        "nodes": {
            "addition": {"state": "completed", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "basic-arithmetic.yaml").write_text(
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


def _seed_performance_training(instance_dir: Path) -> None:
    """Seed profile + goal for performance training protocol.

    Uses 'addition' — solid mastery, no performance_training key yet.
    The mentor activates it when the learner mentions a performance event.
    """
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "addition": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now - timedelta(days=2)),
                "attempts": 10,
                "correct": 9,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal = {
        "schema_version": 0,
        "goal_id": "basic-arithmetic",
        "expressed_as": "Learn basic arithmetic",
        "created": _utc_iso(now - timedelta(days=14)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Self-study",
        },
        "nodes": {
            "addition": {"state": "completed", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "basic-arithmetic.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _seed_cross_goal_review(instance_dir: Path) -> None:
    """Seed profile + two goals sharing 'recursion' for cross-goal review.

    'recursion' is stale (35 days ago) so it appears in the review queue.
    Other topics have recent last_seen so they are NOT stale.
    """
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "recursion": {
                "mastery": "solid",
                "confidence": 0.7,
                "last_seen": _utc_iso(now - timedelta(days=35)),
                "attempts": 8,
                "correct": 7,
            },
            "sorting": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now - timedelta(days=2)),
                "attempts": 10,
                "correct": 9,
            },
            "graph-traversal": {
                "mastery": "solid",
                "confidence": 0.8,
                "last_seen": _utc_iso(now - timedelta(days=2)),
                "attempts": 10,
                "correct": 9,
            },
        },
    }
    (instance_dir / "learner" / "profile.yaml").write_text(
        yaml.safe_dump(profile), encoding="utf-8"
    )

    goal_a = {
        "schema_version": 0,
        "goal_id": "goal-a",
        "expressed_as": "Learn data structures",
        "created": _utc_iso(now - timedelta(days=30)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Self-paced",
        },
        "nodes": {
            "recursion": {"state": "completed", "prerequisites": []},
            "sorting": {"state": "completed", "prerequisites": []},
        },
    }
    goal_b = {
        "schema_version": 0,
        "goal_id": "goal-b",
        "expressed_as": "Master algorithms",
        "created": _utc_iso(now - timedelta(days=30)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "Self-paced",
        },
        "nodes": {
            "recursion": {"state": "completed", "prerequisites": []},
            "graph-traversal": {"state": "completed", "prerequisites": []},
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "goal-a.yaml").write_text(yaml.safe_dump(goal_a), encoding="utf-8")
    (goals_dir / "goal-b.yaml").write_text(yaml.safe_dump(goal_b), encoding="utf-8")


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
    """Capture an assessment session on 'variables' (5 turns).

    Uses a trivially narrow domain so the mentor's question is predictable
    and a static correct answer reliably matches.
    """
    _seed_assess(instance_dir)

    turn1_prompt = "Assess my knowledge of addition."
    mentor1 = _run_turn(turn1_prompt, cwd=instance_dir, timeout=timeout)

    # Use a fresh LLM in a clean directory to answer the mentor's question.
    # With 'addition' the questions are unambiguous (e.g. "What is 7+5?").
    clean_dir = instance_dir.parent / (instance_dir.name + "-answerer")
    clean_dir.mkdir(exist_ok=True)
    answer_prompt = (
        "Answer this exam question correctly in 1-2 sentences.\n\n"
        f"QUESTION: {mentor1}\n\n"
        "ANSWER:"
    )
    correct_answer = _run_turn(answer_prompt, cwd=clean_dir, timeout=timeout)
    shutil.rmtree(clean_dir, ignore_errors=True)

    learner_answers = [
        correct_answer,
        "I'm not sure, maybe you just put the numbers together?",
        "Something about counting on your fingers?",
    ]

    context_hints = [
        "",
        "[SYSTEM: The learner's previous answer was incorrect. "
        "Assessment failure count for this topic: 1. "
        "Do not mention this note to the learner.]",
        "[SYSTEM: The learner has answered incorrectly twice. "
        "Assessment failure count for this topic: 2. "
        "Execute Step 8 (prerequisite diagnosis) now. "
        "Do not mention this note to the learner.]",
    ]

    history_lines = [
        f"Learner: {turn1_prompt}",
        f"Mentor: {mentor1}",
    ]
    mentor_turns = [mentor1]

    for i, answer in enumerate(learner_answers):
        hint = context_hints[i]
        history = (
            "Previous conversation:\n"
            + "\n".join(history_lines)
            + "\n\n"
            + (f"{hint}\n\n" if hint else "")
            + "Continue the conversation. The learner says:\n"
        )
        prompt = history + answer
        mentor_resp = _run_turn(prompt, cwd=instance_dir, timeout=timeout)
        history_lines.append(f"Learner: {answer}")
        history_lines.append(f"Mentor: {mentor_resp}")
        mentor_turns.append(mentor_resp)

    body_parts = [f"[LEARNER] {turn1_prompt}\n"]
    for i, answer in enumerate(learner_answers):
        body_parts.append(f"[MENTOR] {mentor_turns[i]}\n")
        body_parts.append(f"[LEARNER] {answer}\n")
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


def _capture_performance_training(instance_dir: Path, timeout: int) -> str:
    """Capture a performance training session (5 turns).

    Exercises stages 1, 5, and 6 across 5 fixtures:
    phase-activates, format-aware-framing, no-time-pressure-stage-1,
    simulated-evaluation-realism, full-mock-debrief.
    """
    _seed_performance_training(instance_dir)

    # Turn 1: trigger performance training activation.
    # Include exam format upfront so the mentor doesn't stall asking for it.
    turn1_prompt = (
        "I have a math exam in two weeks. It's a free-response exam "
        "with 10 addition problems. Start performance training."
    )
    mentor1 = _run_turn(turn1_prompt, cwd=instance_dir, timeout=timeout)

    history_lines = [
        f"Learner: {turn1_prompt}",
        f"Mentor: {mentor1}",
    ]

    # Turn 2: answer the stage-1 question via answerer LLM
    clean_dir = instance_dir.parent / (instance_dir.name + "-answerer")
    clean_dir.mkdir(exist_ok=True)
    answer_prompt = (
        "Answer this math question correctly in 1-2 sentences.\n\n"
        f"QUESTION: {mentor1}\n\n"
        "ANSWER:"
    )
    answer1 = _run_turn(answer_prompt, cwd=clean_dir, timeout=timeout)
    shutil.rmtree(clean_dir, ignore_errors=True)

    history = (
        "Previous conversation:\n"
        + "\n".join(history_lines)
        + "\n\nContinue the conversation. The learner says:\n"
    )
    prompt2 = history + answer1
    mentor2 = _run_turn(prompt2, cwd=instance_dir, timeout=timeout)
    history_lines.append(f"Learner: {answer1}")
    history_lines.append(f"Mentor: {mentor2}")

    # Turn 3: jump to stage 5 (simulated evaluation)
    turn3_text = "I'm ready for the simulated evaluation."
    hint3 = (
        "[SYSTEM: Performance training is now at stage 5 (simulated evaluation). "
        "Your response MUST include: (1) a time limit for the exercise, "
        "(2) the scoring rubric or criteria. Present these before posing the "
        "evaluation question. No hints, no encouragement. "
        "Do not mention this note to the learner.]"
    )
    history = (
        "Previous conversation:\n"
        + "\n".join(history_lines)
        + f"\n\n{hint3}\n\n"
        + "Continue the conversation. The learner says:\n"
    )
    prompt3 = history + turn3_text
    mentor3 = _run_turn(prompt3, cwd=instance_dir, timeout=timeout)
    history_lines.append(f"Learner: {turn3_text}")
    history_lines.append(f"Mentor: {mentor3}")

    # Turn 4: answer the stage-5 question via answerer LLM
    clean_dir.mkdir(exist_ok=True)
    answer_prompt2 = (
        "Answer this math question correctly in 1-2 sentences.\n\n"
        f"QUESTION: {mentor3}\n\n"
        "ANSWER:"
    )
    answer2 = _run_turn(answer_prompt2, cwd=clean_dir, timeout=timeout)
    shutil.rmtree(clean_dir, ignore_errors=True)

    history = (
        "Previous conversation:\n"
        + "\n".join(history_lines)
        + "\n\nContinue the conversation. The learner says:\n"
    )
    prompt4 = history + answer2
    mentor4 = _run_turn(prompt4, cwd=instance_dir, timeout=timeout)
    history_lines.append(f"Learner: {answer2}")
    history_lines.append(f"Mentor: {mentor4}")

    # Turn 5: request debrief (stage 6)
    turn5_text = "That was my last answer. Give me the debrief."
    hint5 = (
        "[SYSTEM: Performance training is active. The simulated evaluation "
        "is complete. The learner is requesting stage 6 (full mock debrief). "
        "Provide a structured Reviewer debrief covering what worked, "
        "execution gaps, and next steps. Do not mention this note to the learner.]"
    )
    history = (
        "Previous conversation:\n"
        + "\n".join(history_lines)
        + f"\n\n{hint5}\n\n"
        + "Continue the conversation. The learner says:\n"
    )
    prompt5 = history + turn5_text
    mentor5 = _run_turn(prompt5, cwd=instance_dir, timeout=timeout)

    body = (
        f"[LEARNER] {turn1_prompt}\n\n"
        f"[MENTOR] {mentor1}\n\n"
        f"[LEARNER] {answer1}\n\n"
        f"[MENTOR] {mentor2}\n\n"
        f"[LEARNER] {turn3_text}\n\n"
        f"[MENTOR] {mentor3}\n\n"
        f"[LEARNER] {answer2}\n\n"
        f"[MENTOR] {mentor4}\n\n"
        f"[LEARNER] {turn5_text}\n\n"
        f"[MENTOR] {mentor5}\n"
    )
    return _build_frontmatter("performance_training") + "\n" + body


def _capture_cross_goal_review(instance_dir: Path, timeout: int) -> str:
    """Capture a cross-goal review session (3 turns).

    Two goals share 'recursion' — the review queue should deduplicate it
    and ask exactly one recursion question.
    """
    _seed_cross_goal_review(instance_dir)

    # Turn 1: request review — ask mentor to name stale topics so
    # "recursion" appears in the mentor's response.
    turn1_prompt = "Let's do a review session. What topics are due for review?"
    mentor1 = _run_turn(turn1_prompt, cwd=instance_dir, timeout=timeout)

    # Turn 2: answer the recursion question via answerer LLM
    clean_dir = instance_dir.parent / (instance_dir.name + "-answerer")
    clean_dir.mkdir(exist_ok=True)
    answer_prompt = (
        "Answer this question about recursion correctly in 2-3 sentences.\n\n"
        f"QUESTION: {mentor1}\n\n"
        "ANSWER:"
    )
    answer = _run_turn(answer_prompt, cwd=clean_dir, timeout=timeout)
    shutil.rmtree(clean_dir, ignore_errors=True)

    # Turn 2 actual: send the answer to the mentor
    turn2_history = (
        f"Previous conversation:\n"
        f"Learner: {turn1_prompt}\n"
        f"Mentor: {mentor1}\n\n"
        f"Continue the conversation. The learner says:\n"
    )
    prompt2 = turn2_history + answer
    mentor2 = _run_turn(prompt2, cwd=instance_dir, timeout=timeout)

    # Turn 3: end the session
    turn3_history = (
        f"Previous conversation:\n"
        f"Learner: {turn1_prompt}\n"
        f"Mentor: {mentor1}\n"
        f"Learner: {answer}\n"
        f"Mentor: {mentor2}\n\n"
        f"Continue the conversation. The learner says:\n"
    )
    prompt3 = turn3_history + "stop"
    mentor3 = _run_turn(prompt3, cwd=instance_dir, timeout=timeout)

    body = (
        f"[LEARNER] {turn1_prompt}\n\n"
        f"[MENTOR] {mentor1}\n\n"
        f"[LEARNER] {answer}\n\n"
        f"[MENTOR] {mentor2}\n\n"
        f"[LEARNER] stop\n\n"
        f"[MENTOR] {mentor3}\n"
    )
    return _build_frontmatter("cross_goal_review") + "\n" + body


CAPTURE_FNS = {
    "hints": _capture_hints,
    "assess": _capture_assess,
    "review": _capture_review,
    "performance_training": _capture_performance_training,
    "cross_goal_review": _capture_cross_goal_review,
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

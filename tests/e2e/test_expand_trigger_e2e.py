"""End-to-end verification of the expand trigger against a headless LLM agent.

Scaffolds a fresh Sensei instance, pre-populates ``learner/profile.yaml``
with a single coarse topic ("caching") at mastery 'developing' with uneven
sub-mastery signals, creates a minimal goal file with that topic in 'active'
state, and invokes the detected LLM CLI tool with a prompt that triggers the
granularity check in tutor.md.

The prompt provides a stipulated learner answer that demonstrates uneven
understanding: solid on cache eviction policies but confused about cache
invalidation and consistency — signalling 3+ distinct sub-concepts with
uneven mastery within one node.

This test asserts that after the tutor cycle the original "caching" node
has been expanded (state == "expanded") and at least one new subtopic node
exists in the curriculum (state == "spawned"), proving the expand trigger
fired and ``mutate_graph.py --operation expand`` was executed.

Tier-2 test per ADR-0011. Skip conditions match the other E2E tests.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jsonschema
import pytest
import yaml
from click.testing import CliRunner

from sensei.cli import main as sensei_main
from tests.e2e.agent_runner import SKIP_REASON, TOOL_AVAILABLE, run_agent

GOAL_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "sensei"
    / "engine"
    / "schemas"
    / "goal.schema.json"
)

pytestmark = pytest.mark.skipif(not TOOL_AVAILABLE, reason=SKIP_REASON)


def _utc_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_profile(instance_dir: Path) -> None:
    now = datetime.now(timezone.utc)
    profile = {
        "schema_version": 2,
        "learner_id": "e2e",
        "expertise_map": {
            "caching": {
                "mastery": "developing",
                "confidence": 0.4,
                "last_seen": _utc_iso(now - timedelta(days=1)),
                "attempts": 3,
                "correct": 1,
            },
        },
    }
    profile_path = instance_dir / "learner" / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")


def _seed_goal(instance_dir: Path) -> None:
    now = datetime.now(timezone.utc)
    goal = {
        "schema_version": 0,
        "goal_id": "system-design",
        "expressed_as": "Learn system design for senior engineer interviews",
        "created": _utc_iso(now - timedelta(days=7)),
        "status": "active",
        "three_unknowns": {
            "prior_state": "partial",
            "target_state": "clear",
            "constraints": "8 weeks",
        },
        "nodes": {
            "caching": {
                "state": "active",
                "prerequisites": [],
                "concept_tags": ["caching", "performance"],
            },
        },
    }
    goals_dir = instance_dir / "learner" / "goals"
    goals_dir.mkdir(parents=True, exist_ok=True)
    (goals_dir / "system-design.yaml").write_text(
        yaml.safe_dump(goal), encoding="utf-8"
    )


def _build_prompt() -> str:
    return (
        "You are operating a Sensei instance. Read `AGENTS.md` at the repository root "
        "and follow the boot chain. Dispatch to the `tutor` protocol based on the "
        "learner's message below.\n\n"
        "Execute the tutor protocol in this single turn. Since headless mode cannot "
        "carry a multi-turn conversation, treat the stipulated learner answers below "
        "as the responses to whatever probes you pose.\n\n"
        "IMPORTANT: The learner's answers below demonstrate UNEVEN understanding "
        "across distinct sub-concepts within the 'caching' topic. The learner is "
        "solid on eviction policies but confused about invalidation and consistency. "
        "This is the granularity check signal from tutor.md — 3+ distinct sub-concepts "
        "with uneven mastery. You MUST trigger the expand operation per the granularity "
        "check mid-session trigger. Run mutate_graph.py --operation expand to decompose "
        "the 'caching' node into subtopics.\n\n"
        "After expanding, update the curriculum file and stop. Do not continue teaching.\n\n"
        "--- learner message begins ---\n"
        "Teach me about caching.\n\n"
        "(Treat whatever probes you pose as answered by the following — this is a "
        "single-turn E2E, so the learner can't reply twice:)\n\n"
        "**Learner's answer to probe about cache eviction (LRU, LFU, FIFO):**\n"
        "\"LRU evicts the least recently used entry when the cache is full. LFU tracks "
        "frequency counts and evicts the least frequently used. FIFO is simple — first "
        "in, first out. LRU is the most common in practice because it balances recency "
        "and implementation simplicity.\"\n"
        "**Confidence signal:** direct, assertive, correct.\n\n"
        "**Learner's answer to probe about cache invalidation:**\n"
        "\"I'm not really sure how invalidation works. I think you just... delete the "
        "key? Or maybe set a TTL? I don't know when you'd use one vs the other or how "
        "to handle write-through vs write-behind.\"\n"
        "**Confidence signal:** hedging, uncertain, incomplete.\n\n"
        "**Learner's answer to probe about cache consistency:**\n"
        "\"I have no idea how you keep caches consistent across multiple nodes. "
        "Something about eventual consistency? I really don't understand this part.\"\n"
        "**Confidence signal:** confused, no recall.\n"
        "--- learner message ends ---\n"
    )


def test_expand_trigger_decomposes_coarse_node(tmp_path: Path) -> None:
    """Verify the tutor's granularity check expands a coarse curriculum node."""
    runner = CliRunner()
    result = runner.invoke(sensei_main, ["init", str(tmp_path), "--learner-id", "e2e"])
    assert result.exit_code == 0, f"sensei init failed:\n{result.output}"

    _seed_profile(tmp_path)
    _seed_goal(tmp_path)

    completed = run_agent(_build_prompt(), cwd=tmp_path, timeout=300)
    assert completed.returncode == 0, (
        f"agent exited {completed.returncode}.\n"
        f"stdout:\n{completed.stdout[:3000]}\n\nstderr:\n{completed.stderr[:1000]}"
    )

    # --- Assertions on the curriculum file ---
    goal_path = tmp_path / "learner" / "goals" / "system-design.yaml"
    goal_after = yaml.safe_load(goal_path.read_text(encoding="utf-8"))

    # Goal file still validates against schema.
    schema = json.loads(GOAL_SCHEMA_PATH.read_text())
    jsonschema.validate(goal_after, schema)

    nodes = goal_after["nodes"]

    # The original "caching" node should now be in "expanded" state.
    assert "caching" in nodes, (
        f"original 'caching' node missing from curriculum; nodes: {list(nodes)}"
    )
    assert nodes["caching"]["state"] == "expanded", (
        f"expected 'caching' node state to be 'expanded' after granularity check; "
        f"got '{nodes['caching']['state']}'. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

    # At least one new subtopic node should exist with state "spawned".
    subtopic_nodes = {
        slug: node for slug, node in nodes.items()
        if slug != "caching" and node["state"] == "spawned"
    }
    assert len(subtopic_nodes) >= 2, (
        f"expected at least 2 spawned subtopic nodes after expansion; "
        f"found {len(subtopic_nodes)}: {list(subtopic_nodes)}. "
        f"all nodes: {list(nodes)}. "
        f"agent stdout head:\n{completed.stdout[:2000]}"
    )

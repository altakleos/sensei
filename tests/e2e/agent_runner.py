"""Tool-agnostic agent runner for Tier-2 E2E tests.

Detects available LLM CLI tools (claude, kiro-cli) and provides a
unified interface for running headless agent sessions.

Usage:
    from tests.e2e.agent_runner import run_agent, TOOL_AVAILABLE, SKIP_REASON

Environment variables:
    SENSEI_E2E_TOOL: Force a specific tool ('claude' or 'kiro'). Default: auto-detect.
    SENSEI_E2E: Set to '1' to enable E2E tests (required if no ANTHROPIC_API_KEY).
    ANTHROPIC_API_KEY: Required for Claude (unless SENSEI_E2E is set).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _detect_tool() -> str | None:
    """Return the tool name to use, or None if nothing is available."""
    forced = os.environ.get("SENSEI_E2E_TOOL", "").strip().lower()
    if forced == "kiro":
        return "kiro" if shutil.which("kiro-cli") else None
    if forced == "claude":
        return "claude" if shutil.which("claude") else None
    # Auto-detect: prefer claude (established), fall back to kiro
    if shutil.which("claude"):
        return "claude"
    if shutil.which("kiro-cli"):
        return "kiro"
    return None


def _should_skip() -> bool:
    """Return True if E2E tests should be skipped."""
    if _detect_tool() is None:
        return True
    tool = _detect_tool()
    if tool == "claude":
        return not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("SENSEI_E2E"))
    # Kiro uses its own auth (midway/login), no API key needed
    return not os.environ.get("SENSEI_E2E")


def _skip_reason() -> str:
    """Human-readable reason for skipping."""
    tool = _detect_tool()
    if tool is None:
        return "neither `claude` nor `kiro-cli` on PATH"
    if tool == "claude":
        return "set ANTHROPIC_API_KEY or SENSEI_E2E=1 to enable"
    return "set SENSEI_E2E=1 to enable Kiro E2E tests"


TOOL = _detect_tool()
TOOL_AVAILABLE = not _should_skip()
SKIP_REASON = _skip_reason()


def run_agent(
    prompt: str,
    cwd: Path,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    """Run a headless agent session and return the result."""
    tool = _detect_tool()
    if tool is None:
        raise RuntimeError("No LLM CLI tool available")

    if tool == "claude":
        cmd = [
            "claude",
            "--print",
            "--permission-mode",
            "acceptEdits",
            "--output-format",
            "json",
            prompt,
        ]
    else:
        cmd = ["kiro-cli", "chat", prompt, "--no-interactive", "--trust-all-tools"]

    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

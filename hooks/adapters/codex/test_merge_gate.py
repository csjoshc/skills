"""The Codex adapter turns the gate's verdict into Codex's deny JSON and never fails open."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ADAPTER = Path(__file__).with_name("merge-gate.py")
WRAPPER = Path(__file__).with_name("merge-gate.sh")
GATE = Path(__file__).resolve().parents[2] / "merge-gate.py"


def sandbox(tmp_path: Path, gate: str | None = None, gate_exists: bool = True) -> Path:
    """A hooks/ tree shaped like ~/.skills, so the adapter resolves the gate the same way."""
    hooks = tmp_path / "hooks"
    (hooks / "adapters" / "codex").mkdir(parents=True)
    shutil.copy2(ADAPTER, hooks / "adapters" / "codex" / "merge-gate.py")
    shutil.copy2(WRAPPER, hooks / "adapters" / "codex" / "merge-gate.sh")
    if gate_exists:
        (hooks / "merge-gate.py").write_text(gate if gate is not None else GATE.read_text())
    return hooks / "adapters" / "codex" / "merge-gate.sh"


def run(wrapper: Path, payload: dict, env: dict | None = None, timeout: int = 30):
    full = {k: v for k, v in os.environ.items() if k != "MERGE_GATE_PYTHON"} | (env or {})
    return subprocess.run(["/bin/sh", str(wrapper)], input=json.dumps(payload),
                          capture_output=True, text=True, check=False, cwd="/", env=full,
                          timeout=timeout)


def decision(proc: subprocess.CompletedProcess) -> dict:
    return json.loads(proc.stdout)["hookSpecificOutput"]


def shell_cmd(command: str) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}


@pytest.mark.parametrize("command", [
    "gh pr view 55 --json state",
    "gh pr create --draft --base main",
    "git push -u origin feat/x",
])
def test_allows_and_prints_nothing(tmp_path: Path, command: str) -> None:
    proc = run(sandbox(tmp_path), shell_cmd(command))
    assert proc.returncode == 0
    assert proc.stdout == ""


@pytest.mark.parametrize("payload", [
    shell_cmd("gh pr merge 55 --squash"),
    shell_cmd("gh pr review 55 --approve"),
    shell_cmd("git push origin HEAD:main"),
    {"tool_name": "mcp__github__merge_pull_request", "tool_input": {}},
    {"tool_name": "mcp__github__pull_request_review_write",
     "tool_input": {"event": "APPROVE"}},
    # Codex 0.163 namespaces MCP tools as mcp__<server>__<tool>; verified live.
    {"tool_name": "mcp__ghstub__merge_pull_request", "tool_input": {"pull_number": 1}},
])
def test_denies_with_the_gate_reason(tmp_path: Path, payload: dict) -> None:
    proc = run(sandbox(tmp_path), payload)
    assert proc.returncode == 0  # Codex blocks on the JSON decision, not the exit status
    out = decision(proc)
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    assert out["permissionDecisionReason"].startswith("BLOCKED [merge-gate]: ")
    assert len(proc.stdout.strip().splitlines()) == 1


@pytest.mark.parametrize("payload", [
    {"tool_name": "mcp__ghstub__get_pull_request", "tool_input": {"pull_number": 1}},
    {"tool_name": "Read", "tool_input": {"file_path": "README.md"}},
])
def test_allows_other_mcp_and_builtin_tools(tmp_path: Path, payload: dict) -> None:
    proc = run(sandbox(tmp_path), payload)
    assert proc.returncode == 0 and proc.stdout == ""


def test_missing_gate_denies(tmp_path: Path) -> None:
    proc = run(sandbox(tmp_path, gate_exists=False), shell_cmd("gh pr view 1"))
    assert proc.returncode == 0
    assert decision(proc)["permissionDecision"] == "deny"


def test_crashing_gate_denies(tmp_path: Path) -> None:
    crash = "import sys\nprint('gate exploded', file=sys.stderr)\nsys.exit(3)\n"
    proc = run(sandbox(tmp_path, gate=crash), shell_cmd("gh pr view 1"))
    assert decision(proc)["permissionDecisionReason"] == "gate exploded"


def test_silent_crash_denies_with_the_exit_status(tmp_path: Path) -> None:
    crash = "import sys\nsys.exit(3)\n"
    proc = run(sandbox(tmp_path, gate=crash), shell_cmd("gh pr view 1"))
    assert "exited 3" in decision(proc)["permissionDecisionReason"]


def test_gate_timeout_denies(tmp_path: Path) -> None:
    slow = "import time\ntime.sleep(30)\n"
    proc = run(sandbox(tmp_path, gate=slow), shell_cmd("gh pr view 1"), timeout=20)
    assert proc.returncode == 0
    assert "did not answer in time" in decision(proc)["permissionDecisionReason"]


def test_broken_path_still_fails_closed(tmp_path: Path) -> None:
    # A GUI-launched session can have a PATH without python3. Whatever still runs, the
    # answer must be deny; the wrapper's own deny covers the case where nothing does.
    proc = run(sandbox(tmp_path, gate_exists=False), shell_cmd("gh pr view 1"),
               env={"MERGE_GATE_PYTHON": "/usr/bin/false", "PATH": "/nonexistent"})
    assert proc.returncode == 0
    assert decision(proc)["permissionDecision"] == "deny"


def test_merge_gate_python_override_is_used(tmp_path: Path) -> None:
    record = tmp_path / "record.json"
    fake = tmp_path / "python3"
    fake.write_text(f"#!/bin/sh\ncat > '{record}'\n")
    fake.chmod(0o755)
    proc = run(sandbox(tmp_path), shell_cmd("gh pr view 1"),
               env={"MERGE_GATE_PYTHON": str(fake)})
    assert proc.returncode == 0 and proc.stdout == ""
    assert json.loads(record.read_text())["tool_input"]["command"] == "gh pr view 1"

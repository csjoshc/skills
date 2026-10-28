"""Regressions from Codex session cwd and the system Python runtime."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).with_name("merge-gate.py")
ENV = {key: value for key, value in os.environ.items()
       if key not in {"DEVIN_PROJECT_DIR", "CLAUDE_PROJECT_DIR"}}


@pytest.fixture
def main_and_feature(tmp_path: Path) -> tuple[Path, Path]:
    main = tmp_path / "repo"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(main)]
    subprocess.run(["git", "init", "-q", "--template=", "-b", "main", str(main)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "base"], check=True)
    subprocess.run([*git, "worktree", "add", "-q", "-b", "feat", ".worktrees/feat"], check=True)
    return main, main / ".worktrees" / "feat"


def gate(command: str, session: Path) -> subprocess.CompletedProcess[str]:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(session)}
    return subprocess.run([sys.executable, str(GATE)], input=json.dumps(payload),
                          capture_output=True, text=True, check=False, cwd="/", env=ENV)


def test_git_c_allows_history_change_in_feature_checkout(main_and_feature: tuple[Path, Path]) -> None:
    main, feature = main_and_feature
    # red-first: exempt; -C target resolution already exists and is the safe usage pattern.
    result = gate(f"git -C {feature} rebase main", main)
    assert result.returncode == 0, result.stderr


def test_git_c_keeps_primary_main_protected(main_and_feature: tuple[Path, Path]) -> None:
    main, feature = main_and_feature
    # red-first: exempt; explicit main targeting must stay blocked from a feature session.
    result = gate(f"git -C {main} merge feat", feature)
    assert result.returncode == 2


def test_protected_branch_block_reports_session_cwd(main_and_feature: tuple[Path, Path]) -> None:
    main, _ = main_and_feature
    result = gate("git merge feat", main)
    assert result.returncode == 2
    assert f"hook cwd: {main}" in result.stderr


def test_system_python_can_load_gate() -> None:
    system_python = "/usr/bin/python3"
    if not os.path.exists(system_python):
        pytest.skip("no system Python at /usr/bin/python3")
    version = subprocess.run(
        [system_python, "-c", "import json, sys; print(json.dumps(sys.version_info[:2]))"],
        capture_output=True, text=True, check=True).stdout
    if tuple(json.loads(version)) >= (3, 10):
        pytest.skip("system Python already supports evaluated union annotations")
    proc = subprocess.run([system_python, str(GATE)], input=json.dumps({"tool_name": "Read"}),
                          capture_output=True, text=True, check=False, cwd="/", env=ENV)
    assert proc.returncode == 0, proc.stderr

"""merge-gate blocks agent merges, approvals and pushes to protected branches."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).with_name("merge-gate.py")


ENV = {k: v for k, v in os.environ.items() if k not in {"DEVIN_PROJECT_DIR", "CLAUDE_PROJECT_DIR"}}


def run_result(payload: dict) -> subprocess.CompletedProcess[str]:
    # Neutral cwd so the repo the tests run from never decides the outcome.
    return subprocess.run([sys.executable, str(GATE)], input=json.dumps(payload),
                          capture_output=True, text=True, check=False, cwd="/", env=ENV)


def run(payload: dict) -> int:
    return run_result(payload).returncode


def shell(cmd: str, tool: str = "exec") -> int:
    return run({"tool_name": tool, "tool_input": {"command": cmd}})


@pytest.mark.parametrize("cmd", [
    "gh pr merge 55 --squash",
    "cd /repo && export GH_CONFIG_DIR=$HOME/x && gh pr merge 56 --squash --match-head-commit abc",
    "GH_CONFIG_DIR=~/.gh gh pr merge --auto --merge",
    "gh -R c3-e/repo pr merge 7",
    "gh pr review 57 --approve",
    "gh pr review 57 -a -b ok",
    "gh api -X PUT repos/o/r/pulls/5/merge",
    "gh api graphql -f query='mutation { mergePullRequest(input: {}) { clientMutationId } }'",
    "gh api graphql -f query='mutation { enablePullRequestAutoMerge(input: {}) { x } }'",
    "git push origin main",
    "git push -q origin HEAD:main",
    "git push origin feat/x:refs/heads/dev",
    "git -C /repo push upstream master",
    "git push origin +main",
])
def test_blocks(cmd: str) -> None:
    assert shell(cmd) == 2
    assert shell(cmd, tool="Bash") == 2


@pytest.mark.parametrize("cmd", [
    "gh pr create --draft --base main --head feat/x",
    "gh pr view 55 --json state",
    "gh pr list --state merged",
    "gh pr review 57 --comment -b 'looks off'",
    "git push -u origin feat/m2-rag-eval",
    "git push origin --delete e2e-rag-eval",
    "git merge origin/main",
    "git log --oneline origin/main",
    "echo 'never run gh pr merge yourself'",
    "rg 'gh pr merge' docs/",
    "git push origin maintenance",
])
def test_allows(cmd: str) -> None:
    assert shell(cmd) == 0


def test_skills_repo_is_not_exempt() -> None:
    skills = str(Path.home() / ".skills")
    assert shell("cd ~/.skills && git push origin main") == 2
    assert shell(f"git -C {skills} push origin HEAD:main") == 2
    assert run({"tool_name": "exec", "tool_input": {"command": "git push origin main",
                                                     "workdir": skills}}) == 2


@pytest.fixture
def primary_with_feature_worktree(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(repo)]
    subprocess.run(["git", "init", "-q", "--template=", "-b", "main", str(repo)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "base"], check=True)
    subprocess.run([*git, "worktree", "add", "-q", "-b", "feat", ".worktrees/feat"], check=True)
    return repo


def in_tool_dir(command: str, session: Path, tool_input: dict) -> int:
    return run({"tool_name": "Bash", "tool_input": {"command": command, **tool_input},
                "cwd": str(session)})


def test_merge_base_into_feature_worktree_is_allowed(primary_with_feature_worktree: Path) -> None:
    # Codex sends the active tool directory as `cwd`; the session directory is still on main.
    payload = {"tool_name": "Bash", "tool_input": {
        "command": "git merge --no-edit origin/main", "cwd": ".worktrees/feat"},
        "cwd": str(primary_with_feature_worktree)}
    result = run_result(payload)
    assert result.returncode == 0, result.stderr


def test_merge_into_primary_main_is_still_blocked(primary_with_feature_worktree: Path) -> None:
    # red-first: exempt this characterization of the protected-branch policy.
    assert in_tool_dir("git merge feat", primary_with_feature_worktree, {}) == 2


def test_github_mcp_merge_and_approve_are_blocked() -> None:
    assert run({"tool_name": "mcp__github__merge_pull_request", "tool_input": {}}) == 2
    assert run({"tool_name": "mcp_call_tool", "tool_input": {
        "server_name": "github", "tool_name": "merge_pull_request"}}) == 2
    assert run({"tool_name": "mcp_call_tool", "tool_input": {
        "server_name": "github", "tool_name": "pull_request_review_write",
        "arguments": {"method": "submit_pending", "event": "APPROVE"}}}) == 2
    assert run({"tool_name": "mcp_call_tool", "tool_input": {
        "server_name": "github", "tool_name": "get_pull_request"}}) == 0
    assert run({"tool_name": "mcp_call_tool", "tool_input": {
        "server_name": "github", "tool_name": "pull_request_review_write",
        "arguments": {"event": "COMMENT"}}}) == 0


def test_unparseable_input_does_not_block() -> None:
    proc = subprocess.run([sys.executable, str(GATE)], input="not json",
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0

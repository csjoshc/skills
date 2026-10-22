"""merge-gate blocks agent merges, approvals and pushes to protected branches."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).with_name("merge-gate.py")


def run(payload: dict) -> int:
    proc = subprocess.run([sys.executable, str(GATE)], input=json.dumps(payload),
                          capture_output=True, text=True, check=False)
    return proc.returncode


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

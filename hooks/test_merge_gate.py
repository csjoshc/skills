"""merge-gate blocks agent merges, approvals and pushes to protected branches."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).with_name("merge-gate.py")


ENV = {k: v for k, v in os.environ.items() if k not in {"DEVIN_PROJECT_DIR", "CLAUDE_PROJECT_DIR"}}


def run(payload: dict) -> int:
    # Neutral cwd so the repo the tests run from never decides the outcome.
    proc = subprocess.run([sys.executable, str(GATE)], input=json.dumps(payload),
                          capture_output=True, text=True, check=False, cwd="/", env=ENV)
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


def test_skills_repo_is_not_exempt() -> None:
    skills = str(Path.home() / ".skills")
    assert shell("cd ~/.skills && git push origin main") == 2
    assert shell(f"git -C {skills} push origin HEAD:main") == 2
    assert run({"tool_name": "exec", "tool_input": {"command": "git push origin main",
                                                     "workdir": skills}}) == 2


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    """A primary checkout on main with a linked worktree on feat under .worktrees/feat."""
    repo = tmp_path / "repo"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(repo)]
    # No template: the machine's guard hooks would refuse the commit on main.
    subprocess.run(["git", "init", "-q", "--template=", "-b", "main", str(repo)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "base"], check=True)
    subprocess.run([*git, "worktree", "add", "-q", "-b", "feat", ".worktrees/feat"], check=True)
    return repo


def in_dir(cmd: str, session: Path, tool_input: dict) -> int:
    return run({"tool_name": "Bash", "tool_input": {"command": cmd, **tool_input},
                "cwd": str(session)})


@pytest.mark.parametrize("tool_input", [{"cwd": ".worktrees/feat"}, {"workdir": ".worktrees/feat"}])
def test_tool_dir_on_a_feature_branch_allows_rebase(checkout: Path, tool_input: dict) -> None:
    # The session sits on main; the command runs in the feat worktree.
    assert in_dir("git rebase main", checkout, tool_input) == 0
    assert in_dir("git rebase main", checkout, {"cwd": str(checkout / ".worktrees/feat")}) == 0


def test_tool_dir_on_main_still_blocks_rebase(checkout: Path) -> None:
    assert in_dir("git rebase feat", checkout, {}) == 2
    assert in_dir("git rebase feat", checkout / ".worktrees/feat", {"cwd": "../.."}) == 2


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


MERGE = "gh pr merge 43 --repo o/r && GH_TOKEN=$(gh auth token --user u) gh pr merge 46"


@pytest.mark.parametrize("cmd", [
    f"~/.skills/shared/scripts/side-pane.sh stage '{MERGE}'",
    f"/Users/u/.skills/shared/scripts/side-pane.sh stage '{MERGE}'",
    f"  side-pane.sh stage '{MERGE}'  ",
    "side-pane.sh stage 'gh pr merge 45 --repo o/r && git -C ~/.skills pull --ff-only'",
])
def test_lone_stage_call_is_allowed(cmd: str) -> None:
    assert shell(cmd) == 0
    assert shell(cmd, tool="Bash") == 0


@pytest.mark.parametrize("cmd", [
    f"side-pane.sh stage '{MERGE}' && gh pr merge 1",
    f"gh pr merge 1; side-pane.sh stage '{MERGE}'",
    f"cd /repo && side-pane.sh stage '{MERGE}' | sh",
    'side-pane.sh stage "$(gh pr merge 1)"',
    f"bash -c \"side-pane.sh stage '{MERGE}'\"",
    "$(gh pr merge 1)/side-pane.sh stage 'x'",
    "side-pane.sh run 'gh pr merge 1'",
    'echo "$(gh pr merge 1)"',
    'echo "`gh pr merge 1`"',
])
def test_stage_lookalikes_still_block(cmd: str) -> None:
    assert shell(cmd) == 2


def test_side_pane_refuses_to_stage_a_newline() -> None:
    # A typed newline is an Enter: the staged command would run without the user.
    side_pane = Path(__file__).parents[1] / "shared/scripts/side-pane.sh"
    proc = subprocess.run([str(side_pane), "stage", "gh pr merge 1\n"], capture_output=True,
                          text=True, check=False, env={**ENV, "WEZTERM_PANE": "", "TMUX": ""})
    assert proc.returncode == 2 and "single line" in proc.stderr


def test_block_message_points_to_staging() -> None:
    proc = subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True, check=False,
                          input=json.dumps({"tool_name": "exec",
                                            "tool_input": {"command": "gh pr merge 1"}}),
                          cwd="/", env=ENV)
    assert proc.returncode == 2 and "side-pane.sh stage" in proc.stderr


def test_unparseable_input_does_not_block() -> None:
    proc = subprocess.run([sys.executable, str(GATE)], input="not json",
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0

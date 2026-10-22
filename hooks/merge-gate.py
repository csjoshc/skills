#!/usr/bin/env python3
"""PreToolUse (shell + MCP): agents never merge, approve, or push/merge into a protected branch.

Mode: halt (exit 2; harnesses relay stderr to the agent). Bypass is the user acting
themselves (GitHub UI or their own terminal); there is deliberately no agent-side switch.
"""

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

PROTECTED = {"main", "master", "dev"}
# ~/AGENTS.md lets agents push ~/.skills main after a clean commit (skill sync resets it).
PUSH_EXEMPT = Path.home() / ".skills"
GH = r"(?:^|[;&|(]|\s)gh(?:\s+-{1,2}\S+(?:\s+[^-\s]\S*)?)*\s+"
# Matched against the command with quoted text blanked, so `echo 'gh pr merge'` passes.
PATTERNS = [
    (re.compile(GH + r"pr\s+merge(?:\s|$)"), "gh pr merge"),
    (re.compile(GH + r"pr\s+review\b[^;&|]*\s(?:--approve|-a)(?:\s|$)"), "gh pr review --approve"),
    (re.compile(GH + r"api\b[^;&|]*?/pulls/\d+/merge\b"), "REST pull merge"),
]
GH_GRAPHQL = re.compile(GH + r"api\s+graphql\b")
GRAPHQL_MUTATION = re.compile(
    r"\b(?:mergePullRequest|enablePullRequestAutoMerge)\b|addPullRequestReview[^;&|]*APPROVE")
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
MCP_BLOCKED = {"merge_pull_request", "enable_auto_merge"}


GIT_TIMEOUT = 1  # seconds per git probe; the hook's own budget is 5s
MERGE_SAFE = {"--abort", "--quit", "--continue"}
SYNC_SAFE = {"--ff-only", "--rebase", "-r"}  # pull forms that cannot create a merge commit


def _git(repo: str, *args: str) -> str | None:
    """Stdout of a git probe, '' when git fails, None on timeout (callers fail closed)."""
    try:
        proc = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                              timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _exempt(path: str, branch: str) -> bool:
    if branch != "main":
        return False
    resolved = Path(os.path.expanduser(path)).resolve()
    skills = PUSH_EXEMPT.resolve()
    if resolved != skills and skills not in resolved.parents:
        return False
    root = _git(str(resolved), "rev-parse", "--show-toplevel")
    if not root or Path(root).resolve() != skills:
        return False
    return _git(str(resolved), "status", "--porcelain", "--untracked-files=normal") == ""


def git_commands(command: str, cwd: str):
    """Yield (repo, subcommand, args, switched_to) for each git call in a shell command line."""
    switched = None  # branch a prior `git checkout|switch` in this command moved to
    for segment in re.split(r"&&|\|\||[;|\n]", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        if words[:1] == ["cd"] and len(words) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        if "git" not in words:
            continue
        rest, repo = words[words.index("git") + 1:], cwd
        while rest and rest[0].startswith("-"):  # git -C dir push ...
            if rest[0] == "-C" and len(rest) > 1:
                repo = os.path.join(cwd, os.path.expanduser(rest[1]))
            rest = rest[2:] if rest[0] in {"-C", "-c"} else rest[1:]
        if not rest:
            continue
        yield repo, rest[0], rest[1:], switched
        if rest[0] in {"checkout", "switch"}:
            names = [w for w in rest[1:] if not w.startswith("-")]
            switched = names[0] if names else switched


def pushes_to_protected(command: str, cwd: str) -> bool:
    for repo, sub, args, _ in git_commands(command, cwd):
        if sub != "push":
            continue
        refspecs = [w for w in args if not w.startswith("-")][1:]  # drop the remote
        for spec in refspecs:
            dest = spec.lstrip("+").split(":")[-1].removeprefix("refs/heads/")
            deleting = "--delete" in args or "-d" in args or spec.startswith(":")
            if dest in PROTECTED and (deleting or not _exempt(repo, dest)):
                return True
    return False


def merges_into_protected(command: str, cwd: str) -> bool:
    """Local `git merge`, or a `git pull` that may merge, while on a protected branch."""
    for repo, sub, args, switched in git_commands(command, cwd):
        if sub == "merge":
            if MERGE_SAFE & set(args):
                continue
        elif sub == "pull":
            if SYNC_SAFE & set(args):
                continue
        else:
            continue
        branch = switched or _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        if branch is None or branch in PROTECTED:
            return True
    return False


def reason(payload: dict) -> str | None:
    tool = str(payload.get("tool_name", ""))
    args = payload.get("tool_input") or {}
    if tool.startswith("mcp") and isinstance(args, dict):
        name = tool.split("__")[-1] if tool.startswith("mcp__") else str(args.get("tool_name", ""))
        if name in MCP_BLOCKED:
            return f"MCP {name}"
        inner = args if tool.startswith("mcp__") else args.get("arguments") or {}
        if name == "pull_request_review_write" and str(inner.get("event", "")).upper() == "APPROVE":
            return "MCP review APPROVE"
        return None
    command = args.get("command") or args.get("cmd") if isinstance(args, dict) else None
    if not isinstance(command, str):
        return None
    bare = QUOTED.sub("''", command)
    for pattern, label in PATTERNS:
        if pattern.search(bare):
            return label
    if GH_GRAPHQL.search(bare) and GRAPHQL_MUTATION.search(command):
        return "GraphQL merge/approve"
    cwd = str(args.get("workdir") or payload.get("cwd") or os.environ.get("DEVIN_PROJECT_DIR")
              or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if pushes_to_protected(command, cwd):
        return "git push to a protected branch"
    return "local git merge into a protected branch" if merges_into_protected(command, cwd) else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    found = reason(payload) if isinstance(payload, dict) else None
    if not found:
        return 0
    print(f"BLOCKED [merge-gate]: {found}. Agents never merge, approve, or push/merge into "
          f"{'/'.join(sorted(PROTECTED))}. Leave the PR for the user; they merge it themselves.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

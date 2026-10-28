#!/usr/bin/env python3
"""PreToolUse (shell + MCP): agents never merge, approve, or move a protected branch.

Mode: halt (exit 2; harnesses relay stderr to the agent). Bypass is the user acting
themselves (GitHub UI or their own terminal); there is deliberately no agent-side switch.

Blocks, for main/master/dev:
- gh pr merge/approve, the REST merge, ref and contents routes, GraphQL merge mutations
- GitHub MCP merge_pull_request, enable_auto_merge, APPROVE reviews, and file writes to them
- git push to them (bare, HEAD, --all/--mirror, globs, deletes)
- on them: merge, cherry-pick, rebase, am, revert, and a pull that can merge
- elsewhere: branch -f/-M/-C, checkout -B, switch -C, update-ref, fetch|pull x:main
- setting core.hooksPath (git -c, GIT_CONFIG_* env, git config), which skips the local hooks
The same typed into a process (Devin write_to_process; unreadable key mixes block).
The same inside sh -c, eval, xargs or `side-pane.sh run` text (matched unblanked), inside
double-quoted $(...) or backticks, and via a full git path.
Allowed: git pull --ff-only|--rebase, and --abort/--quit/--continue/--skip.
Allowed: a lone `side-pane.sh stage '<cmd>'`, which types cmd unrun for the user to run.
Out of scope: programs that call git or the API themselves, and git reset --hard.
A git probe that times out blocks (fail closed).
"""

import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master", "dev"}
GH = r"(?:^|[;&|(\'\"`]|\s)gh(?:\s+-{1,2}\S+(?:\s+[^-\s]\S*)?)*\s+"
# Matched against the command with quoted text blanked, so `echo 'gh pr merge'` passes.
PATTERNS = [
    (re.compile(GH + r"pr\s+merge(?:\s|$)"), "gh pr merge"),
    (re.compile(GH + r"pr\s+review\b[^;&|]*\s(?:--approve|-a)(?:\s|$)"), "gh pr review --approve"),
    (re.compile(GH + r"api\b[^;&|]*?/pulls/\d+/merge\b"), "REST pull merge"),
    (re.compile(GH + r"api\b[^;&|]*?/merges\b"), "REST branch merge"),
    (re.compile(GH + r"api\b[^;&|]*?/git/refs/heads/(?:main|master|dev)\b"), "REST ref update"),
    (re.compile(GH + r"api\b[^;&|]*?/contents/[^;&|]*?(?:branch=|ref=)(?:main|master|dev)\b"),
     "REST commit to a protected branch"),
]
# Quoted text is blanked so `echo 'gh pr merge'` passes, except when it feeds a shell.
SHELL_WRAPPER = re.compile(
    r"\b(?:ba|z|da|k)?sh\s+-\w*c\b|\beval\b|\bxargs\b|\|\s*(?:ba|z)?sh\b|side-pane\.sh\s+run\b")
GH_GRAPHQL = re.compile(GH + r"api\s+graphql\b")
GRAPHQL_MUTATION = re.compile(
    r"\b(?:mergePullRequest|enablePullRequestAutoMerge)\b|addPullRequestReview[^;&|]*APPROVE")
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
# Double quotes still run $(...) and backticks, so those strings are never blanked.
SUBSTITUTION = re.compile(r"\$\(|`")
# Single quotes only, so nothing expands on the agent's side; side-pane.sh refuses newlines too.
STAGE_ONLY = re.compile(r"^\s*[\w~./-]*side-pane\.sh\s+stage\s+'[^'\n\r]*'\s*$")
STAGE_HINT = "~/.skills/shared/scripts/side-pane.sh stage '<cmd>'"
MCP_BLOCKED = {"merge_pull_request", "enable_auto_merge"}
# GitHub MCP tools that commit straight to args["branch"], skipping review.
MCP_BRANCH_WRITERS = {"push_files", "create_or_update_file", "delete_file"}
MCP_KNOWN = MCP_BLOCKED | MCP_BRANCH_WRITERS | {"pull_request_review_write"}


LINE_END = re.compile(r"<(?:CR|LF)>")
TYPED_KEY = re.compile(r"<[A-Za-z][A-Za-z0-9-]*>")
GIT_CONFIG_ENV = re.compile(r"GIT_CONFIG_(?:KEY_\d+|PARAMETERS)=")
GIT_TIMEOUT = 1  # seconds per git probe; the hook's own budget is 5s
# History-moving commands that import other work into the current branch.
LOCAL_MERGERS = {"merge", "cherry-pick", "rebase", "am", "revert"}
CONTINUATIONS = {"--abort", "--quit", "--continue", "--skip"}
SYNC_SAFE = {"--ff-only", "--rebase", "-r"}  # pull forms that cannot create a merge commit


def _git(repo: str, *args: str) -> str | None:
    """Stdout of a git probe, '' when git fails, None on timeout (callers fail closed)."""
    try:
        proc = subprocess.run(["git", "-C", repo, *args], check=False, capture_output=True,
                              text=True, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else ""


def git_commands(command: str, cwd: str):
    """Yield (repo, subcommand, args, switched_to) for each git call in a shell command line.

    Quoted text handed to a shell (`bash -c "git merge x"`) is parsed recursively.
    """
    switched = None  # branch a prior `git checkout|switch` in this command moved to
    if SHELL_WRAPPER.search(command):
        for quoted in QUOTED.findall(command):
            if "git" in quoted:
                yield from git_commands(quoted[1:-1], cwd)
    for segment in re.split(r"&&|\|\||[;|\n]", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        if words[:1] == ["cd"] and len(words) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        at = next((i for i, w in enumerate(words) if os.path.basename(w) == "git"), None)
        if at is None:
            continue
        rest, repo = words[at + 1:], cwd
        for assignment in words[:at]:  # GIT_CONFIG_KEY_0=core.hooksPath git ...
            if GIT_CONFIG_ENV.match(assignment):
                yield repo, "-c", [assignment], switched
        while rest and rest[0].startswith("-"):  # git -C dir push ...
            if rest[0] == "-C" and len(rest) > 1:
                repo = os.path.join(cwd, os.path.expanduser(rest[1]))
            if rest[0] == "-c" and len(rest) > 1:
                yield repo, "-c", [rest[1]], switched
            rest = rest[2:] if rest[0] in {"-C", "-c"} else rest[1:]
        if not rest:
            continue
        yield repo, rest[0], rest[1:], switched
        if rest[0] in {"checkout", "switch"}:
            names = [w for w in rest[1:] if not w.startswith("-")]
            switched = names[0] if names else switched


def overrides_hooks(command: str, cwd: str) -> bool:
    """Setting core.hooksPath (-c, env or git config) points git at a hook-less directory."""
    for _, sub, args, _ in git_commands(command, cwd):
        if sub == "-c" and "core.hookspath" in args[0].lower():
            return True
        reading = {"--get", "--get-all", "--get-regexp", "--list", "-l"} & set(args)
        if sub == "config" and not reading and any(a.lower() == "core.hookspath" for a in args):
            return True
    return False


def _dest(spec: str) -> str:
    return spec.lstrip("+").split(":")[-1].removeprefix("refs/heads/")


def _current(repo: str, switched: str | None) -> str | None:
    """Current branch, or None when it cannot be told (callers fail closed)."""
    return switched or _git(repo, "rev-parse", "--abbrev-ref", "HEAD")


def pushes_to_protected(command: str, cwd: str) -> bool:
    for repo, sub, args, switched in git_commands(command, cwd):
        if sub != "push":
            continue
        flags = {w for w in args if w.startswith("-")}
        if flags & {"--all", "--mirror"}:
            return True
        dests = [_dest(w) for w in args if not w.startswith("-")][1:]  # drop the remote
        if not dests or "HEAD" in dests:  # bare push sends the current branch
            dests.append(_current(repo, switched) or "main")
        if any(dest in PROTECTED or "*" in dest for dest in dests):
            return True
    return False


def _moves_ref(sub: str, args: list[str]) -> bool:
    """Commands that point a protected ref at other work, whatever branch is checked out."""
    flags = {w for w in args if w.startswith("-")}
    names = [w.removeprefix("refs/heads/") for w in args if not w.startswith("-")]
    short = {c for w in flags if not w.startswith("--") for c in w[1:]}
    if sub in {"fetch", "pull"}:
        return any(":" in w and _dest(w) in PROTECTED for w in names)  # fetch origin feat:main
    if sub == "branch" and names:
        moving = flags & {"--move", "--copy"} or short & {"m", "M", "c", "C"}
        forcing = flags & {"--force"} or short & {"f", "M", "C"}
        target = names[-1] if moving else names[0]  # `branch -f <name> [<start>]`
        return bool(moving or forcing) and target in PROTECTED
    if sub in {"checkout", "switch"}:
        recreating = short & {"B", "C"} or "--force-create" in flags
        return bool(recreating) and any(n in PROTECTED for n in names)
    return sub == "update-ref" and any(n in PROTECTED for n in names)


def _imports_history(sub: str, args: list[str]) -> bool:
    """Commands that pull other commits into the current branch (a merge, in effect)."""
    flags = {w for w in args if w.startswith("-")}
    if sub in LOCAL_MERGERS:
        return not CONTINUATIONS & flags
    return sub == "pull" and not SYNC_SAFE & flags


def moves_protected(command: str, cwd: str) -> bool:
    """Any local way to land unreviewed work on a protected branch (push is checked apart)."""
    for repo, sub, args, switched in git_commands(command, cwd):
        if _moves_ref(sub, args):
            return True
        if _imports_history(sub, args):
            branch = _current(repo, switched)
            if branch is None or branch in PROTECTED:
                return True
    return False


def _typed_input(args: dict) -> str | None:
    """Text Devin's write_to_process types into a shell; None when its keys cannot be read.

    <CR>/<LF> end a line. Any other key token (<ESC>, <UP>, <C-c>) is fine alone, but beside
    text it can rewrite the line, so the line that finally runs is unknowable.
    """
    text, keys = str(args.get("text_input") or ""), str(args.get("bytes_input") or "")
    typed = LINE_END.sub("\n", keys)
    if TYPED_KEY.search(typed) and (text or TYPED_KEY.sub("", typed).strip()):
        return None
    return f"{text}\n{TYPED_KEY.sub('', typed)}"


def _mcp_tool(name: str) -> str:
    """The server tool a qualified name ends in: mcp__s__t (Claude), mcp__s_t (OMP), s_t."""
    return next((t for t in MCP_KNOWN if name == t or name.endswith("_" + t)), name)


def reason(payload: dict) -> str | None:
    tool = str(payload.get("tool_name", ""))
    args = payload.get("tool_input") or {}
    if tool.startswith("mcp") and isinstance(args, dict):
        name = tool.split("__")[-1] if tool.startswith("mcp__") else str(args.get("tool_name", ""))
        name = _mcp_tool(name)
        if name in MCP_BLOCKED:
            return f"MCP {name}"
        inner = args if tool.startswith("mcp__") else args.get("arguments") or {}
        if name in MCP_BRANCH_WRITERS and str(inner.get("branch", "")) in PROTECTED:
            return f"MCP {name} to a protected branch"
        if name == "pull_request_review_write" and str(inner.get("event", "")).upper() == "APPROVE":
            return "MCP review APPROVE"
        return None
    if tool == "write_to_process" and isinstance(args, dict):
        command = _typed_input(args)
        if command is None:
            return "keystrokes typed into a process that cannot be read"
    else:
        command = args.get("command") or args.get("cmd") if isinstance(args, dict) else None
    if not isinstance(command, str) or (tool != "write_to_process" and STAGE_ONLY.match(command)):
        return None
    bare = command if SHELL_WRAPPER.search(command) else QUOTED.sub(
        lambda m: m.group(0) if m.group(0)[0] == '"' and SUBSTITUTION.search(m.group(0)) else "''",
        command)
    for pattern, label in PATTERNS:
        if pattern.search(bare):
            return label
    if GH_GRAPHQL.search(bare) and GRAPHQL_MUTATION.search(command):
        return "GraphQL merge/approve"
    # The tool's own directory wins over the session's: Codex sends `workdir`, OMP's bash `cwd`,
    # possibly relative. Reading only the session's let a feature-branch rebase in a worktree
    # look like one on the primary checkout's main.
    session = str(payload.get("cwd") or os.environ.get("DEVIN_PROJECT_DIR")
                  or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    tool_dir = args.get("workdir") or args.get("cwd")
    cwd = os.path.join(session, os.path.expanduser(str(tool_dir))) if tool_dir else session
    if pushes_to_protected(command, cwd):
        return "git push to a protected branch"
    if overrides_hooks(command, cwd):
        return "overriding core.hooksPath"
    return "local git history change on a protected branch" if moves_protected(command, cwd) else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    found = reason(payload) if isinstance(payload, dict) else None
    if not found:
        return 0
    print(f"BLOCKED [merge-gate]: {found}. Agents never merge, approve, or change "
          f"{'/'.join(sorted(PROTECTED))}. Stage it for the user instead: run `{STAGE_HINT}` "
          "as the whole command (single quotes, nothing chained, no shell wrapper), and show "
          "the command in a code block. Make no other attempt to run it. "
          "After the user reports success, verify the PR is merged into the repository's current "
          "default branch before cleanup. If it landed in an intermediate branch, leave its "
          "worktrees and branches alone. After a final merge, inspect local worktrees and branches "
          "linked to that PR's pipeline, including intermediate PRs. Establish that each "
          "candidate's changes reached the default branch and its local branch still points at "
          "the associated merged PR head. Remove only clean, unlocked worktrees that are not "
          "current or active working directories, then delete only their local branches. If "
          "activity or pipeline membership is unclear, leave the candidate untouched and report "
          "why. Never delete remote branches.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

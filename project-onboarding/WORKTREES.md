# Parallel work with git worktrees

## Contents

- Why
- Onboarding checklist (what to write into the repo)
- Operator playbook (any coding harness)
- Subagent rules
- Harness hooks (optional; prefer native when present)
- Anti-patterns
- Cleanup

---

## Why

Multiple agent sessions (or a parent + write subagents) that share **one working tree** fight over `HEAD`. A `git checkout` / `git switch` in one session moves the branch for every other session rooted in that directory. Uncommitted edits collide; smoke-test pins flip; reviews target the wrong branch.

**Linked git worktrees** give each concurrent branch its own directory while sharing object storage. That is the portable isolation model across Cursor, Claude Code, Codex, Gemini CLI, and plain terminals.

**No "quick task" exception.** A single `git checkout` / `git switch` / `git reset --hard` in the shared primary checkout is exactly as disruptive whether the task behind it is large or small — it still moves `HEAD` for every other session rooted there. "It's just a quick fix" or "one-off corrective branch" is not a reason to skip a worktree. If a task needs a different branch checked out, even briefly, cut a worktree for it.

---

## Onboarding checklist (what to write into the repo)

During `/project-onboarding`, ensure:

1. **`.gitignore`** contains `.worktrees/` (prefer that name; if `worktrees/` already exists and is ignored, keep it).
2. **`AGENTS.md`** includes the block below (merge/dedupe; do not duplicate).
3. Do **not** create worktrees during onboarding unless the user asks — only the ignore + agent rules.

### AGENTS.md block (copy verbatim when missing)

```markdown
## Parallel work (git worktrees)

- **Do not** run two write agents in the same working tree. `git checkout` / `git switch` in one session moves `HEAD` for every session sharing that directory.
- Prefer one linked worktree per concurrent branch under `.worktrees/<slug>/` (must be gitignored). Keep the primary checkout on `main` (or one stable integration branch).
- Bind each write session's cwd / workspace root to its worktree path — not the primary checkout.
- Write subagents must receive an absolute worktree path and must not `checkout` / `switch` in the parent tree. Read-only explore/review may share the parent tree.
- **No exception for quick, one-off, or corrective tasks.** A single `git checkout`/`git switch`/`git reset --hard` in the shared primary checkout is exactly as disruptive whether the task is large or small. If a task needs a different branch checked out, even briefly, cut a worktree for it.
- Prefer harness-native isolation when already present; otherwise `git worktree add`. Full playbook: skill companion `project-onboarding/WORKTREES.md` (or repo docs that mirror it).
```

Verify ignore before any later `git worktree add`:

```bash
git check-ignore -q .worktrees || git check-ignore -q worktrees
```

If neither is ignored, add `.worktrees/` to `.gitignore` and commit before creating trees.

---

## Operator playbook (any coding harness)

### Layout

```text
<repo>/                         # primary checkout — stay on main / stable
└── .worktrees/
    ├── fix-issue-9/            # session A — branch fix/issue-9
    ├── fix-issue-10/           # session B — branch fix/issue-10
    └── fix-issue-11/           # session C — branch fix/issue-11
```

### Create

From the primary checkout:

```bash
mkdir -p .worktrees
git worktree add .worktrees/<slug> -b <branch> <base>   # new branch
# or attach existing remote/local branch:
git worktree add .worktrees/<slug> <branch>
```

`<slug>` should match the branch purpose (e.g. `fix-docker-build-target`). `<base>` is usually `main`.

### Bind the session

Point **that** agent session’s working directory / workspace root at the worktree path — not at the primary checkout. How:

| Harness | Typical bind |
|---------|----------------|
| Cursor | Open folder / `move_agent_to_root` (or equivalent) to the worktree path |
| Claude Code / CLI | `cd` into the worktree (or start the session there) |
| Codex / other | Set cwd / open the worktree directory as the project root |
| Plain terminal | `cd .worktrees/<slug>` |

Two write sessions both rooted at `<repo>/` will still collide even if worktrees exist unused.

### Keep primary clean

- Primary checkout stays on `main` (or one declared integration branch).
- Feature / fix / experiment work happens only inside `.worktrees/<slug>/`.
- Merge or rebase into the integration branch **after** each worktree branch is ready; resolve conflicts intentionally.

### List / remove

```bash
git worktree list
git worktree remove .worktrees/<slug>    # after branch merged or abandoned
git worktree prune                       # if directory was deleted out-of-band
```

---

## Subagent rules

| Kind of subagent | Isolation |
|------------------|-----------|
| **Write / implement / commit** | Own worktree (absolute path in the prompt). Ban `git checkout` / `git switch` / `git worktree add` against the **parent** tree. |
| **Read-only explore / review** | Shared tree is fine; no branch changes. |
| **Harness-native isolated runner** | Prefer it when available (see below); do not also `checkout` in the parent. |

Parent prompt must include:

- Absolute worktree path as cwd for all edits and git commands
- Branch name already checked out in that worktree
- Explicit: do not change branches in `<primary-repo-path>`

---

## Harness hooks (optional; prefer native when present)

Portable baseline is always `git worktree add` + bind session cwd.

If the harness already provides isolation, **use it instead of nesting another worktree inside an isolated workspace**:

- Detect existing isolation first (`git rev-parse --git-dir` vs `--git-common-dir`; linked worktree when they differ and you are not in a submodule).
- Cursor: workspace-root move tools; Task runners that create per-agent worktrees.
- Claude Code / other: documented worktree or sandbox flags when present.

Never invent a second worktree manager when the platform already owns one.

---

## Anti-patterns

| Anti-pattern | Effect |
|--------------|--------|
| Two write agents in the same directory | Branch flip / dirty-tree races |
| Subagent `git checkout` in the parent repo | Parent + sibling sessions jump branches |
| "It's just a quick fix" branch/checkout in the primary tree | Same collision risk as any other write session; the rationalization doesn't reduce the blast radius |
| Worktree dir not gitignored | Accidental tracking of nested checkouts |
| Feature work parked on primary `main` checkout | Every new session inherits the wrong branch |
| Creating a worktree inside an already-linked worktree | Nested isolation; harness confusion |
| Parallel write agents on overlapping files without a merge plan | Silent conflict debt |

---

## Cleanup

When a branch is merged or abandoned:

1. Ensure no agent session still has that worktree as cwd.
2. `git worktree remove .worktrees/<slug>`.
3. Delete the remote branch if policy says so (`gh` / `git push --delete`).
)

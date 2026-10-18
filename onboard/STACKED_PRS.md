# Stacked PRs (opt-in playbook)

**Not part of default onboarding.** Load and apply this companion only when
the user explicitly asks for a stacked-PR strategy (e.g. "let's stack these
PRs", "split this into stacked PRs"). Onboarding itself installs nothing
from this file unless the user prompts for it.

Reference — follow GitHub's official doc for create/manage/merge mechanics:
https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
(and the CLI reference: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands)

## Tooling

- Use GitHub's native stacks via the `gh stack` CLI extension (public preview):
  `gh extension install github/gh-stack`.
- Two modes:
  - **Full local tracking** (`gh stack init` / `add` / `submit`) — when the
    stack is created fresh and one working tree owns all its branches.
  - **Link-only** (`gh stack link <bottom> <top>...`) — when PRs are already
    open and branches are managed manually (worktree-per-branch layouts,
    Jujutsu/Sapling/git-town). No local tracking state; base-branch chaining
    is corrected automatically. Prefer this in repos using the parallel-
    worktrees convention (see WORKTREES.md) since each branch lives in its
    own tree.

## Core rules

- **Change to a lower layer:** commit on that layer's branch, then
  cascade-rebase every branch above it — `gh stack rebase --upstack` +
  `gh stack push`, or manually `git rebase --onto` per branch +
  `git push --force-with-lease`.
- **After the bottom PR merges:** `gh stack sync --prune` (fetches,
  fast-forwards trunk, rebases remaining branches onto it, pushes).
- **Signed commits:** never use the website "Rebase stack" button when the
  repo requires signed commits — server-side rebase commits are unsigned;
  rebase via CLI.
- **Merge bottom-up only.** A stacked PR still obeys every merge gate on it
  (draft status, integration-gate banners, required reviews); stacking
  changes review topology, not merge discipline.
- **Duplicate-content hazard when converting parallel PRs into a stack:**
  if two open PRs both target trunk and share cherry-picked commits, first
  decide the single home for the shared commits (usually the lower PR),
  rebase the upper PR onto the lower branch dropping its duplicates
  (`git rebase --onto <lower-tip> <last-duplicate>`), then retarget the
  upper PR's base (`gh pr edit N --base <lower-branch>`) before linking.

## AGENTS.md block (merge only when the user prompts for stacked-PR support)

```markdown
## Stacked PRs (opt-in — only when the operator asks for a stacked-PR strategy)

Reference (follow this doc for create/manage/merge mechanics):
https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests

- Use GitHub's native stacks via the `gh stack` CLI extension
  (`gh extension install github/gh-stack`; public preview).
- Branches managed manually (e.g. per-worktree, as in this repo): link
  already-open PRs bottom-to-top with `gh stack link <bottom> <top>...` —
  no local tracking state required. It corrects base-branch chaining
  automatically.
- Change to a lower layer: commit on that layer's branch, then
  cascade-rebase every branch above it (`gh stack rebase --upstack` +
  `gh stack push`, or manual `git rebase --onto` + `git push
  --force-with-lease` per branch).
- After the bottom PR merges: `gh stack sync --prune` (fetches,
  fast-forwards trunk, rebases + pushes the remaining branches).
- Never use the website "Rebase stack" button when signed commits are
  required — server-side rebase commits are unsigned; rebase via CLI.
- Merge bottom-up only. A stacked PR still obeys every merge gate on it
  (e.g. draft status, integration-gate banners); stacking changes review
  topology, not merge discipline.
```

---
name: onboard
description: "Sets up or reconciles agent instruction files (AGENTS.md, Cursor rules, ignore patterns, worktree conventions) for a repo. Use when onboarding a repo to agents or standardizing its agent setup."
---

# onboard

Target the **project root** the user is onboarding (usually workspace root). **Default:** write `AGENTS.md`, `.cursorignore`, and `.cursorrules` at that root even when markers live only in subfolders (monorepo), so one workspace sees one set of rules—unless the user asks to onboard a subfolder as its own root.

**Refuse these targets.** Do not onboard `~` or `~/.skills`, or write `AGENTS.md`, `.cursorrules` or `STANDARDS.md` there.
`~/AGENTS.md` is the single global memory file; the other tools' global files are symlinks to it, and project templates must never overwrite it.
If the resolved root equals `$HOME` or sits under `~/.skills`, stop and ask for a real project path.
Their git guards are reconciled by `/sync hooks`, not here.

Memory needs no per-repo setup (rules in `~/AGENTS.md`, files made on demand by the `memory` skill).
Don't add `.agent-local/` or memory entries to a repo's `.gitignore`, and don't create memory files during onboarding.

Companion files:
- Windows notes: [WINDOWS.md](WINDOWS.md)
- Parallel worktrees: [WORKTREES.md](WORKTREES.md) — harness-agnostic isolation for concurrent agent sessions / write subagents; load when onboarding or when parallel branch work is requested.
- Stacked PRs: [STACKED_PRS.md](STACKED_PRS.md) — **opt-in, NOT default onboarding**; load only when the user explicitly prompts for a stacked-PR strategy (`gh stack` workflow, cascading rebases, AGENTS.md block to merge on request).
- Symlink map: [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md)
- Workflow routing: [WORKFLOW_GATES.md](WORKFLOW_GATES.md) — which skills and shared checks fit each phase, not an installed orchestrator. Link it from the project AGENTS.md. Load when setting up the agent loop for a repo, not for file-level onboarding.
- Hook principles: [shared/HOOK_PRINCIPLES.md](../shared/HOOK_PRINCIPLES.md) — read before adding any hook; decision rule and minimal safe catalogue.

---

## 0. Check for Global STANDARDS.md (required first)

`~/.skills/STANDARDS.md` is a thin index. The topic files live in `~/.skills/standards/`.

1. **Confirm `~/.skills/STANDARDS.md` and `~/.skills/standards/` exist.** If not, stop and tell the user; do not recreate them.
2. **Create the local `./STANDARDS.md` as a copy of the global index.**
   - Keep the topic table and rewrite its relative links to `~/.skills/standards/<file>`.
   - Add project-specific decisions under "Project-Specific Additions". Project wins on conflict; note the override.
   - If a local `STANDARDS.md` or `ARCHITECTURE.md` already exists, merge into it instead of replacing it, and keep its project sections.
   - Do not copy `standards/` into the project unless the user asks for a self-contained repo (teammates without `~/.skills` need it).
3. **Update AGENTS.md to reference both:**
   ```markdown
   ## STANDARDS.md
   - Global standards: `~/.skills/STANDARDS.md` (index; topic files in `~/.skills/standards/`)
   - Project-specific: `./STANDARDS.md` (local, authoritative for this repo)
   - Agents: read the matching topic file before blocking on architectural questions; use `standards/pre-flight.md` for blocker detection
   ```

**Why:** the index keeps every project copy small and drift-free; only project decisions live locally.

---

## 0b. Detect tech stack (required first)

Detect npm/Node and Python, including nested paths and Python without a manifest. Marker tables and merge rules: [STACK_DETECTION.md](STACK_DETECTION.md). Only npm and Python blocks are in scope; do not guess other frameworks. Record the result (npm / python / both / neither).

---

## 0c. Enforce static analysis via pre-commit hooks (required)

The repo must run static analysis as a git commit hook that blocks failing commits, and must document a "run everything" command. Extend an existing hook framework; do not add a second one. Policy placement, per-stack defaults and docs: [PRECOMMIT_HOOKS.md](PRECOMMIT_HOOKS.md).

---

## 0d. Identifier + doc-staleness audit (forks / inherited projects)

Before declaring onboarding done, run two grep scans: (1) **identifier scope scan** for ADR labels, ticket IDs and gate/slice slugs leaked into committed source; (2) **doc-staleness scan** of `docs/` and README for deleted or renamed entities. Both become handoff debt, not blockers. Add a `STANDARDS.md` / `AGENTS.md` note that planning-system IDs belong in commit messages and PR threads, never committed prose. Commands + template: [`IDENTIFIER_AND_DOC_STALENESS.md`](IDENTIFIER_AND_DOC_STALENESS.md).

---

## 0e. Parallel worktrees (required for multi-session / write-subagent safety)

Concurrent sessions (or a parent plus **write** subagents) sharing one working tree race on `HEAD`.

**Onboarding actions (do these; do not create worktrees unless the user asks):**

1. Ensure `.worktrees/` is in `.gitignore` (prefer that name; if `worktrees/` already exists and is ignored, keep it — do not invent a second location).
2. Merge the **AGENTS.md block** from [`WORKTREES.md`](WORKTREES.md) (after Engineering principles / before MCP tool lists is fine; dedupe if present).
3. Operators use the full playbook in that companion (create/bind/subagents/cleanup).

**Verify ignore before any later create:** `git check-ignore -q .worktrees || git check-ignore -q worktrees` — if that fails, add `.worktrees/` and commit before `git worktree add`.

---

## 0f. Git push discipline (required)

Onboarding must guarantee every project's `AGENTS.md` states that agents never push directly to the protected/default branch, with no exception for trivial, corrective, or "quick fix" changes.

**Onboarding actions (do these; this block is unconditional, not stack-dependent):**

1. Merge the **Git workflow block** (see section 1) into `AGENTS.md`, inserted after the stack preamble; dedupe if an equivalent rule already exists.
2. The rule holds even when a direct push would technically succeed (branch protection may not be configured to block it) — that is not permission to use it.

---

## 0g. Git guards (required, once per repo)

0f states the rule; this step makes the repo enforce it.
Do it when a commit or push is first attempted in a repo with a GitHub remote, after 0c (a hook framework can replace hooks), and stay silent when the guards are already present.

1. Resolve the effective hooks directory with `git -C <repo> rev-parse --path-format=absolute --git-path hooks`; it honours `core.hooksPath` and worktrees, and without the flag it prints a path relative to the repo.
2. Check it holds an executable copy of each stub listed in `~/bootstrap/BOM.md#git-guards`, each calling its shared guard; do not restate the list here.
3. With the default hooks directory and no hook present, run `git init` in the repo: it re-applies the template and overwrites nothing.
   With a hook present, show the integration and ask first; put the guard ahead of any `exec` or `exit` and keep pre-commit's `.legacy` chaining.
   When `core.hooksPath` points inside the repo (a tracked directory such as `.githooks`), `git init` fills `.git/hooks`, which git then ignores.
   Copy the stubs from `~/.config/git/template/hooks/` into that directory as local files and list them in `.git/info/exclude`; never commit them, because they fail closed for teammates who lack the shared guards.
4. Report it in one line.

---

## 1. `AGENTS.md` — canonical agent instructions

Record only what the code can't say (trade-offs, domain rules, external constraints, files not to touch, how to run checks); each claim cites a file or issue. Skip README content and generic advice.

This is the **single source of truth** read by every tool. All other instruction files (`.cursorrules`, `GEMINI.md`) are thin shims that reference it.

Create **`AGENTS.md`** at the project root using the appropriate stack template below.

The **Git workflow block** and **Code comments block** (below) are unconditional — always merge them into every project's `AGENTS.md`, regardless of stack.

Insertion order is mandatory:
1. stack preamble
2. Git workflow block (always)
3. Code comments block (always)
4. Engineering principles block (always)
5. Tokenify block (optional; only on request)

When merging into an existing `AGENTS.md`: keep user sections; append missing parts; deduplicate; preserve headings. Ensure exactly one Git workflow block, placed immediately after the stack preamble, and exactly one Code comments block immediately after it, then exactly one Engineering principles block.
Reconcile outdated template wording in place: replace "Prefer the shortest solution that is still correct" with the coherent-change wording in [AGENTS_BLOCKS.md](AGENTS_BLOCKS.md), without appending a second principles block or discarding project-specific constraints.

### Stack-specific preamble (pick one)

Read [STACK_PREAMBLES.md](STACK_PREAMBLES.md) once the stack is detected. It holds the verbatim `# Project Context` templates for npm only, Python only, npm + Python (with the optional monorepo subtree bullet), and neither. Copy the one that matches.

### Git workflow block (always add — copy verbatim, stack-agnostic)

Place immediately after the stack preamble in every project, regardless of stack:

```markdown
## Git workflow

- Never push directly to a protected/default branch (`main`, `master`, `trunk`), even for trivial or corrective changes, even if the push would technically succeed (branch protection may not be configured to block it). Always create a branch and open a PR.
- This applies to agents and subagents equally — a "quick fix" is not an exception.
```

### Code comments block (always add — copy verbatim, stack-agnostic)

The base comment style (plain English, 1-2 lines, why not what) lives in the global `~/AGENTS.md`. Do not restate it here. Add only the project delta, immediately after the Git workflow block, regardless of stack:

```markdown
## Code comments

Same style as the global rules. History behind odd code earns a comment too, with an issue or file pointer.
```

Cursor and Copilot have no global file. If the user targets those tools, tell them the base style will not reach them.

### Verbatim blocks (Engineering principles, Tokenify, MCP Tools)

Copy the matching blocks from `AGENTS_BLOCKS.md` verbatim. Engineering principles (always) goes right
after Code comments, then Tokenify (optional) and MCP Tools (optional).

## 2-3. Cursor files

Create `.cursor/rules/core-agent-behavior.mdc` (`alwaysApply: true`, points at `AGENTS.md`) and `.cursorignore` (Universal block plus one block per detected stack; merge, never replace). Verbatim content and merge rules: [CURSOR_FILES.md](CURSOR_FILES.md). Blocks: [cursorignore-blocks.md](cursorignore-blocks.md).

---

## 4. Tool-Specific Shims (Centralizing around AGENTS.md)

Because `AGENTS.md` is the canonical instruction file, other tools only need a minimal shim pointing to it.

If supporting these tools, create their respective files at the project root with this exact content:

```markdown
Read and follow AGENTS.md in this directory for project conventions,
context exclusions, and operational rules.
```

- **Cursor**: `.cursorrules` (Note: older `.cursorrules` that copy stack or rules blocks should be replaced with this shim).
- **Windsurf**: `.windsurfrules`
- **Cline**: `.clinerules`

### Native Support (No Shim Needed)

| Tool | How it picks up `AGENTS.md` |
|------|----------------------------|
| **OpenCode** | Reads `AGENTS.md` natively. |
| **GitHub Copilot** | Reads `AGENTS.md` natively. |
| **Claude Code** | Reads `AGENTS.md` natively (v2.1.277+) unless a `CLAUDE.md` or `CLAUDE.local.md` is in that folder or above. Add no project `CLAUDE.md` unless something needs it (then make it `@AGENTS.md`); never add `CLAUDE.local.md`. |
| **Aider** | Add `read: AGENTS.md` to `.aider.conf.yml`. |

---

## 5. Agent Synchronization & Symlinking (Multi-Tool)

`~/.skills` is the single authoritative store; tool-specific paths map to it.

- **Claude Code CLI:** the global symlink `~/.claude/skills -> ~/.skills` covers it. No project-level action.
- **Claude Desktop:** sandboxed, cannot follow external symlinks. Use the filtered `rsync` copy in [sync/skills.md](../sync/skills.md) (about 2 MB; never a plain `cp -r ~/.skills`) and re-run it when the master store changes.
- **Everything else:** audit and establish links per [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md) before completing onboarding. Link, don't copy.
- Add project-level skill folders (`.skills/`, `.claude/skills/`, etc.) to `.gitignore`.
- Use `sync` to audit and fix broken links and stale copies.

---

## 6. Verification

- [ ] Target root is not `~` or under `~/.skills`; `~/AGENTS.md` untouched.
- [ ] Stack detection recorded (npm / python / both / neither), including **nested** paths and **Python-without-manifest** when applicable.
- [ ] Global STANDARDS.md checked (`~/.skills/STANDARDS.md`)
- [ ] Project-specific STANDARDS.md merged (if exists) or section created
- [ ] Static analysis enforced via git commit hooks (use existing hook framework if present; otherwise `pre-commit` for Python and/or `husky` for npm). “Run everything” commands documented.
- [ ] `AGENTS.md` stays at or under 200 lines, with no README duplicates or uncited claims.
- [ ] `AGENTS.md` exists with the correct stack preamble, exclusion paths, STANDARDS.md reference, and section order: stack preamble -> Git workflow -> Code comments -> Engineering principles -> (optional) Tokenify.
- [ ] Git workflow block present exactly once, immediately after the stack preamble (never-push-to-protected-branch rule, no quick-fix exception).
- [ ] `core-agent-behavior.mdc` exists with `alwaysApply: true`.
- [ ] `.cursorignore` contains Universal + every block for a detected stack; Python-only includes `dist/` and `build/`. If the tool cannot write `.cursorignore`, paste the missing block(s) for the user to add manually.
- [ ] `.cursorrules` is a thin shim referencing `AGENTS.md` (no blocks copied from `AGENTS.md`).
- [ ] Cross-tool shims (`GEMINI.md`, `.cursorrules`, etc.) exist if multi-tool support was requested or defaulted.
- [ ] `.claude/skills` is a filtered copy of `~/.skills` for Claude Desktop (the `rsync` command in sync/skills.md, run from the project root). Claude Code CLI uses the global symlink.
- [ ] Global and Project symlinks audited against [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).
- [ ] The effective hooks directory has the stubs listed in `~/bootstrap/BOM.md#git-guards` (0g).
- [ ] `.worktrees/` (or existing `worktrees/`) is gitignored; `AGENTS.md` includes the Parallel work (git worktrees) block; [`WORKTREES.md`](WORKTREES.md) is the operator playbook.

---

## Notes for the agent

- `STANDARDS.md` (global: `~/.skills/STANDARDS.md`, an index into `~/.skills/standards/`) is the **architectural oracle** — agents read the matching topic file before blocking on assumptions.
- Future stacks (Rust, Go, Java, etc.) become new labeled blocks in [STACK_PREAMBLES.md](STACK_PREAMBLES.md), not ad hoc edits.
- Exact patterns live in this skill and its companions; copy blocks verbatim. The `AGENTS.md` exclusion list is a soft ignore for tools without an ignore file.
- Never replace a user's `AGENTS.md` / `.cursorignore` / `.cursorrules` / `STANDARDS.md` wholesale; merge and dedupe.
- When a user switches tools mid-session (e.g. rate-limited on Claude, jumps to Codex), the new agent reads `AGENTS.md` (or its shim) automatically — no manual re-onboarding needed for baseline project knowledge. Use `/todo` for `.agent-local/tickets/` workflow and `Stage:` transitions when continuing across sessions or agents.
- **Nested layouts:** Do not conclude "npm only" just because the workspace root lacks `package.json`; nested `package.json` still means npm. Same for Python manifests or backend `.py` trees under a subfolder.
- **STANDARDS.md lifecycle:**
  - Global index and topic files live in `~/.skills`; they are not recreated per project
  - Extended with project-specific sections per project
  - Updated when agents block on questions humans have already decided
  - Reviewed every 3 months or when onboarding to significantly different project
- **Parallel worktrees:** Onboarding installs ignore + `AGENTS.md` rules only. Creating/removing worktrees and binding session cwd is an operator/runtime step — see [`WORKTREES.md`](WORKTREES.md). Never nest a new worktree inside an already-linked worktree.

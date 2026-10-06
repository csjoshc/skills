---
name: project-onboarding
description: Creates and reconciles project agent-instruction files across tools, including AGENTS.md, Cursor rules, stack-specific ignore patterns, and parallel git-worktree conventions. Use when onboarding a repository, standardizing agent behavior files, syncing multi-tool project setup, or establishing isolated branches for concurrent agent sessions.
---

# Project Onboarding (Multi-Tool)

Target the **project root** the user is onboarding (usually workspace root). **Default:** write `AGENTS.md`, `.cursorignore`, and `.cursorrules` at that root even when markers live only in subfolders (monorepo), so one workspace sees one set of rules—unless the user asks to onboard a subfolder as its own root.

Companion files:
- Windows notes: [WINDOWS.md](WINDOWS.md)
- Parallel worktrees: [WORKTREES.md](WORKTREES.md) — harness-agnostic isolation for concurrent agent sessions / write subagents; load when onboarding or when parallel branch work is requested.
- Stacked PRs: [STACKED_PRS.md](STACKED_PRS.md) — **opt-in, NOT default onboarding**; load only when the user explicitly prompts for a stacked-PR strategy (`gh stack` workflow, cascading rebases, AGENTS.md block to merge on request).
- Symlink map: [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md)
- Workflow gates (session-level orchestration): [WORKFLOW_GATES.md](WORKFLOW_GATES.md) — which skills fire at which phase, plus the SessionStart digest. Load when setting up the agent loop for a repo, not for file-level onboarding.
- Token budget strategy: [shared/TOKEN_BUDGET.md](../shared/TOKEN_BUDGET.md) — install RTK (input-side CLI proxy) during onboarding; caveman (output-side) activates automatically above 50% context usage if hooks are installed.
- Hook principles: [shared/HOOK_PRINCIPLES.md](../shared/HOOK_PRINCIPLES.md) — read before adding any hook; decision rule and minimal safe catalogue.

---

## 0. Check for Global STANDARDS.md (required first)

Before any other onboarding steps:

1. **Check if `~/.skills/STANDARDS.md` exists**
   - If yes → read it
   - If no → create `~/.skills/STANDARDS.md` from template (use ticket-critic skill STANDARDS.md template)

2. **Establish Local STANDARDS.md**
   - **Always copy** the global `~/.skills/STANDARDS.md` to the project root as `./STANDARDS.md`.
   - If a local `STANDARDS.md` or `ARCHITECTURE.md` already exists:
     - Merge the global content with the existing local content.
     - Project-specific overrides/additions should be preserved.
     - Document that the local file is now the authoritative source for this project.

3. **Merge strategy:**
   - Global standards: architecture decisions, layer ownership, resolved questions
   - Project-specific: stack adjustments, project ADRs, custom security/perf requirements
   - Conflicts: project-specific wins (document the override)

4. **Update AGENTS.md to reference local STANDARDS.md:**
   ```markdown
   ## STANDARDS.md
   - Global standards: `~/.skills/STANDARDS.md` (authoritative for patterns)
   - Project-specific: `./STANDARDS.md` (local copy, authoritative for this repo)
   - Agents: Check STANDARDS.md before blocking on architectural questions; use pre-flight checklist for blocker detection
   ```

**Why:** STANDARDS.md is the single source of truth for architectural decisions; a local copy is stable, versionable, and extendable per project.

---

## 0b. Detect tech stack (required first)

### Where to look

Inspect **under the onboarding root at any depth**, not only the root directory. Discover markers with globs or search tools; **skip** dependency and VCS noise when scanning (`node_modules/`, `.git/`, `.venv/`, `venv/`, `env/`, `site-packages/`, `dist/`, `build/` if clearly generated-only—use judgment so you do not miss real app `dist/` layouts).

Classify:

| Stack | Treat as present if you find (any path under onboarding root) |
|--------|-------------------------------------|
| **npm / Node** | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lock`, `bun.lockb` |
| **Python (manifest)** | `pyproject.toml`, `Pipfile`, `poetry.lock`, `requirements.txt`, `requirements-*.txt`, `setup.py`, `setup.cfg`, `manage.py`, `tox.ini` |

### Python without a manifest (backend / platform code)

If **no** Python manifest row matches but you find **`.py` files that look like project source** (e.g. under `api/`, `backend/`, `server/`, `src/` of a named package, or `**/SomePackage/src/*.py`), treat **Python** as present:

- Apply the **Python** `.cursorignore` block (Block C) and the **Python-only** or **npm + Python** `AGENTS.md` preamble, consistent with npm detection.
- Do **not** treat stray scripts, vendored trees, or copies under ignored paths as sufficient unless the user says otherwise.

### Merge rules

- **Both** npm and Python (by manifest and/or the rule above) → include **both** pattern blocks in `.cursorignore` and the combined exclusion list in **`npm + Python`** `AGENTS.md`.
- **Neither** → create only the **Universal** blocks plus `core-agent-behavior.mdc`; tell the user no npm/Python markers were found.
- **Monorepo** (e.g. `apps/web/package.json` + `services/api/pyproject.toml`, or nested `package.json` + backend `.py`) → still merge **both** blocks at the **onboarding root** unless the user asks for per-package files only.

Do not guess extra frameworks beyond npm/Python for this skill; only the blocks defined below are in scope.

---

## 0c. Enforce static analysis via pre-commit hooks (required)

The repo should have **static analysis / linting checks** that run as a **git commit hook** and **block commits** when they fail (type errors, invalid returns/inputs, unreachable code, obvious null/None hazards, etc.).

### Where to encode the policy

1. **`./STANDARDS.md` (authoritative)**: Add a short section like:
   - Commits must be blocked by pre-commit hooks that run static analysis appropriate to the stack.
   - The “run everything” command(s) must be documented (see below).

2. **`AGENTS.md` (operational)**: Add a brief bullet reminding agents to ensure hooks exist and are kept passing.

### Hook mechanism defaults (use these unless the repo already has something else)

If the repo already uses a hook framework (e.g. `pre-commit`, `husky`, `lefthook`, `lint-staged`, `simple-git-hooks`), **extend the existing one**; do not introduce a second framework without a strong reason.

If the repo does not have hooks yet:

- **Python present** → use **`pre-commit`** with (at minimum):
  - `ruff` (format + lint) and
  - `mypy` (type checking).

- **npm/Node present** → use **`husky`** with (at minimum):
  - `eslint` (lint) and
  - `tsc -p <tsconfig>` (type checking) when TypeScript is present.
  - If no TypeScript config exists, run `eslint` only (do not invent `tsconfig.json`).

- **npm + Python present**:
  - Enforce both. Prefer one runner that calls both toolchains (commonly `lefthook`) if low-risk; otherwise extend the existing mechanism.

### “Run everything” documentation (required)

Ensure the repo has a documented way to run the same checks outside git hooks, ideally in one place (choose the natural home for the stack):

- **Python**: `make check`, `uv run pre-commit run -a`, `python -m ruff check . && python -m mypy ...`, etc.
- **Node**: `npm run lint`, `npm run typecheck`, or a combined `npm run check`.

Use what the repo already has; do not guess tooling beyond npm/Python detection. **Hooks enforce**; developers can run the same checks directly.

---

## 0d. Identifier + doc-staleness audit (forks / inherited projects)

Before declaring onboarding done, run two grep scans: (1) **identifier scope scan** for ADR labels, ticket IDs and gate/slice slugs leaked into committed source; (2) **doc-staleness scan** of `docs/` and README for deleted or renamed entities. Both become handoff debt, not blockers. Add a `STANDARDS.md` / `AGENTS.md` note that planning-system IDs belong in commit messages and PR threads, never committed prose. Commands + template: [`IDENTIFIER_AND_DOC_STALENESS.md`](IDENTIFIER_AND_DOC_STALENESS.md).

---

## 0e. Parallel worktrees (required for multi-session / write-subagent safety)

Concurrent sessions (or a parent plus **write** subagents) sharing one working tree race on `HEAD`.

**Onboarding actions (do these; do not create worktrees unless the user asks):**

1. Ensure `.worktrees/` is in `.gitignore` (prefer that name; if `worktrees/` already exists and is ignored, keep it — do not invent a second location).
2. Merge the **AGENTS.md block** from [`WORKTREES.md`](WORKTREES.md) (after Karpathy / before MCP tool lists is fine; dedupe if present).
3. Operators use the full playbook in that companion (create/bind/subagents/cleanup).

**Verify ignore before any later create:** `git check-ignore -q .worktrees || git check-ignore -q worktrees` — if that fails, add `.worktrees/` and commit before `git worktree add`.

---

## 0f. Git push discipline (required)

Onboarding must guarantee every project's `AGENTS.md` states that agents never push directly to the protected/default branch, with no exception for trivial, corrective, or "quick fix" changes.

**Onboarding actions (do these; this block is unconditional, not stack-dependent):**

1. Merge the **Git workflow block** (see section 1) into `AGENTS.md`, inserted after the stack preamble and before the optional MCP block; dedupe if an equivalent rule already exists.
2. The rule holds even when a direct push would technically succeed (branch protection may not be configured to block it) — that is not permission to use it.

---

## 1. `AGENTS.md` — canonical agent instructions

Record only what the code can't say (trade-offs, domain rules, external constraints, files not to touch, how to run checks); each claim cites a file or issue. Skip README content and generic advice.

This is the **single source of truth** read by every tool. All other instruction files (`.cursorrules`, `GEMINI.md`) are thin shims that reference it.

Create **`AGENTS.md`** at the project root using the appropriate stack template below.

The **Git workflow block** and **Code comments block** (below) are unconditional — always merge them into every project's `AGENTS.md`, regardless of stack.

If the project uses **`codebase-memory-mcp`** (explicitly requested by user, present in existing instructions, or available in current agent tooling), insert the **Codebase-Memory-MCP block** immediately after the Git workflow block and before broader behavior/style sections.
If none of those signals are present, do **not** add the MCP block.

Insertion order is mandatory:
1. stack preamble
2. Git workflow block (always)
3. Code comments block (always)
4. optional MCP block (only when MCP is in use)
5. Tokenify block (optional; only on request)
6. Karpathy Guidelines block (optional; only on request)

When merging into an existing `AGENTS.md`: keep user sections; append missing parts; deduplicate; preserve headings. Ensure exactly one Git workflow block, placed immediately after the stack preamble, and exactly one Code comments block immediately after it. If MCP is in use, ensure exactly one MCP block, placed immediately after the Code comments block.

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

Place immediately after the Git workflow block in every project, regardless of stack:

```markdown
## Code comments

Plain English, no AI-slop. 1–2 lines (≤100 chars), next to the code. Say why, not what. Only real footguns earn more. History behind odd code earns a comment too, with an issue or file pointer.
```

### Codebase-Memory-MCP block (add when project uses it)

Verbatim block lives in [AGENTS_BLOCKS.md](AGENTS_BLOCKS.md); read it only when MCP is in use. Place it early in `AGENTS.md` (before generic coding style rules) so it shapes tool selection first.

### Optional verbatim blocks (Tokenify, Karpathy Guidelines, graphify, MCP Tools)

Append the matching blocks from `AGENTS_BLOCKS.md` in that order: Tokenify (optional, after the
optional MCP block), Karpathy Guidelines (optional, after Tokenify), graphify (if present),
MCP Tools (optional). Copy them verbatim.

## 2. Core agent behavior rule (Cursor-specific)

Create **`.cursor/rules/core-agent-behavior.mdc`** with exactly this content:

```markdown
---
description: Core agent behavior — concise replies and minimal code surface
alwaysApply: true
---

# CORE DIRECTIVES

- **Read and follow \`AGENTS.md\`** in the project root for all project conventions, context exclusions, and operational rules.
- Be extremely concise.
- Do not explain code unless explicitly asked.
- NO pleasantries (e.g., 'Sure!', 'I can help').
- Provide only the code or the direct answer.
- For small changes, provide snippets, not the whole file.
```

If `.cursor/rules/` does not exist, create it.

---

## 3. `.cursorignore` — use only the blocks for detected stacks

Cursor reads **`.cursorignore`** at the project root for indexing and `@` context. It is **not** `.gitignore`; duplicate patterns when needed. Most other tools only respect `.gitignore`, which is why `AGENTS.md` embeds the exclusion list directly.

**Always include** the **Universal** block. **Add npm block** if npm/Node detected. **Add Python block** if Python detected.

When merging into an existing `.cursorignore`: keep user lines; append missing patterns; deduplicate exact lines; preserve section comments.

Verbatim Universal / npm / Python blocks live in [cursorignore-blocks.md](cursorignore-blocks.md). Copy what applies to the detected stack.

---

## 4. Tool-Specific Shims (Centralizing around AGENTS.md)

Because `AGENTS.md` is the canonical instruction file, other tools only need a minimal shim pointing to it.

If supporting these tools, create their respective files at the project root with this exact content:

```markdown
Read and follow AGENTS.md in this directory for project conventions,
context exclusions, and operational rules.
```

- **Cursor**: `.cursorrules` (Note: older `.cursorrules` with full Tokenify/stack blocks should be replaced with this shim).
- **Gemini CLI**: `GEMINI.md`
- **Windsurf**: `.windsurfrules`
- **Cline**: `.clinerules`

### Native Support (No Shim Needed)

| Tool | How it picks up `AGENTS.md` |
|------|----------------------------|
| **OpenCode** | Reads `AGENTS.md` natively. |
| **GitHub Copilot** | Reads `AGENTS.md` natively. |
| **Claude Code** | Reads `AGENTS.md` when no `CLAUDE.md` exists. If one is needed, make it `@AGENTS.md`. |
| **Aider** | Add `read: AGENTS.md` to `.aider.conf.yml`. |

---

## 5. Agent Synchronization & Symlinking (Multi-Tool)

`~/.skills` is the single authoritative store; tool-specific paths map to it.

- **Claude Code CLI:** the global symlink `~/.claude/skills -> ~/.skills` covers it. No project-level action.
- **Claude Desktop:** sandboxed, cannot follow external symlinks. Use a recursive copy and re-run it (or `skill-sync`) when the master store changes:
  `rm -rf /path/to/project/.claude/skills && cp -r ~/.skills /path/to/project/.claude/skills`
- **Everything else:** audit and establish links per [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md) before completing onboarding. Link, don't copy.
- Add project-level skill folders (`.skills/`, `.gemini/skills/`, `.claude/skills/`, etc.) to `.gitignore`.
- Use `skill-sync` to audit and fix broken links and stale copies.

---

## 6. Verification

- [ ] Stack detection recorded (npm / python / both / neither), including **nested** paths and **Python-without-manifest** when applicable.
- [ ] Global STANDARDS.md checked (`~/.skills/STANDARDS.md`)
- [ ] Project-specific STANDARDS.md merged (if exists) or section created
- [ ] Static analysis enforced via git commit hooks (use existing hook framework if present; otherwise `pre-commit` for Python and/or `husky` for npm). “Run everything” commands documented.
- [ ] `AGENTS.md` stays at or under 200 lines, with no README duplicates or uncited claims.
- [ ] `AGENTS.md` exists with the correct stack preamble, exclusion paths, STANDARDS.md reference, and section order: stack preamble -> Git workflow block -> optional MCP block -> (optional) Tokenify -> (optional) Karpathy.
- [ ] Git workflow block present exactly once, immediately after the stack preamble (never-push-to-protected-branch rule, no quick-fix exception).
- [ ] MCP conditional inclusion enforced: include MCP block only when MCP is in use (explicit request, existing instructions, or active tooling); otherwise omit it.
- [ ] If included, MCP block appears exactly once, immediately after the Git workflow block, with mandatory discovery order, fallback boundaries, and completion self-check.
- [ ] `core-agent-behavior.mdc` exists with `alwaysApply: true`.
- [ ] `.cursorignore` contains Universal + every block for a detected stack; Python-only includes `dist/` and `build/`. If the tool cannot write `.cursorignore`, paste the missing block(s) for the user to add manually.
- [ ] `.cursorrules` is a thin shim referencing `AGENTS.md` (no duplicated Tokenify).
- [ ] Cross-tool shims (`GEMINI.md`, `.cursorrules`, etc.) exist if multi-tool support was requested or defaulted.
- [ ] `.claude/skills` is a recursive copy of `~/.skills` for Claude Desktop (run `cp -r ~/.skills /path/to/project/.claude/skills`). Claude Code CLI uses the global symlink.
- [ ] Global and Project symlinks audited against [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).
- [ ] `.worktrees/` (or existing `worktrees/`) is gitignored; `AGENTS.md` includes the Parallel work (git worktrees) block; [`WORKTREES.md`](WORKTREES.md) is the operator playbook.

---

## Notes for the agent

- `STANDARDS.md` (global: `~/.skills/STANDARDS.md`) is the **architectural oracle** — agents check this before blocking on assumptions.
- Future stacks (Rust, Go, Java, etc.) become new labeled blocks in [STACK_PREAMBLES.md](STACK_PREAMBLES.md), not ad hoc edits.
- Exact patterns live in this skill and its companions; copy blocks verbatim. The `AGENTS.md` exclusion list is a soft ignore for tools without an ignore file.
- Never replace a user's `AGENTS.md` / `.cursorignore` / `.cursorrules` / `STANDARDS.md` wholesale; merge and dedupe.
- When a user switches tools mid-session (e.g. rate-limited on Claude, jumps to Gemini CLI), the new agent reads `AGENTS.md` (or its shim) automatically — no manual re-onboarding needed for baseline project knowledge. Use the **orchestrate** skill for `.tickets/` workflow and `Stage:` transitions when continuing across sessions or agents.
- **Nested layouts:** Do not conclude "npm only" just because the workspace root lacks `package.json`; nested `package.json` still means npm. Same for Python manifests or backend `.py` trees under a subfolder.
- **STANDARDS.md lifecycle:**
  - Created once (globally) on first onboarding
  - Extended with project-specific sections per project
  - Updated when agents block on questions humans have already decided
  - Reviewed every 3 months or when onboarding to significantly different project
- **Parallel worktrees:** Onboarding installs ignore + `AGENTS.md` rules only. Creating/removing worktrees and binding session cwd is an operator/runtime step — see [`WORKTREES.md`](WORKTREES.md). Never nest a new worktree inside an already-linked worktree.

---
name: project-onboarding
description: Creates and reconciles project agent-instruction files across tools, including AGENTS.md, Cursor rules, and stack-specific ignore patterns. Use when onboarding a repository, standardizing agent behavior files, or syncing multi-tool project setup.
---

# Project Onboarding (Multi-Tool)

Target the **project root** the user is onboarding (usually workspace root). **Default:** write `AGENTS.md`, `.cursorignore`, and `.cursorrules` at that root even when markers live only in subfolders (monorepo), so one workspace sees one set of rules—unless the user asks to onboard a subfolder as its own root.

Companion files:
- Windows notes: [WINDOWS.md](WINDOWS.md)
- Symlink map: [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md)
- Workflow gates (session-level orchestration): [WORKFLOW_GATES.md](WORKFLOW_GATES.md) — defines which skills fire at which phase (spec, implement, test, done, PR) and provides the SessionStart digest the agent emits on open. Load this when setting up the agent loop for a repo, not for file-level onboarding.
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

**Why:** STANDARDS.md is the single source of truth for architectural decisions. Copying it locally ensures the project has a stable, versionable set of rules that can be extended without affecting other projects.

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

Some repos ship Python **application or platform code** (e.g. C3 types, server modules) **without** a `pyproject.toml` or `requirements.txt` at rest in the tree.

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
  - Prefer keeping both checks enforced. If adopting two hook frameworks would be messy, prefer a single hook runner that can call both toolchains (commonly `lefthook`), but only if adding it is low-risk for the repo. Otherwise, use the repo’s existing mechanism and add the missing checks there.

### “Run everything” documentation (required)

Ensure the repo has a documented way to run the same checks outside git hooks, ideally in one place (choose the natural home for the stack):

- **Python**: `make check`, `uv run pre-commit run -a`, `python -m ruff check . && python -m mypy ...`, etc.
- **Node**: `npm run lint`, `npm run typecheck`, or a combined `npm run check`.

The exact commands depend on what the repo already uses; do not guess package manager or tooling beyond “npm/Python present” detection. The goal is: **hooks enforce**, and **developers can run the same checks directly**.

---

## 1. `AGENTS.md` — canonical agent instructions

This is the **single source of truth** read by every tool. All other instruction files (`.cursorrules`, `CLAUDE.md`, `GEMINI.md`) are thin shims that reference it.

Tools that auto-read `AGENTS.md`: OpenCode, GitHub Copilot (`.github/copilot-instructions.md` can reference it), and any agent given a cold-start prompt.

Create **`AGENTS.md`** at the project root using the appropriate stack template below.

If the project uses **`codebase-memory-mcp`** (explicitly requested by user, present in existing instructions, or available in current agent tooling), insert the **Codebase-Memory-MCP block** immediately after the stack preamble and before broader behavior/style sections.
If none of those signals are present, do **not** add the MCP block.

Insertion order is mandatory:
1. stack preamble
2. optional MCP block (only when MCP is in use)
3. Tokenify block
4. Karpathy Guidelines block

When merging into an existing `AGENTS.md`: keep user sections; append missing parts; deduplicate; preserve headings. If MCP is in use, ensure exactly one MCP block and place it immediately after the stack preamble.

### Stack-specific preamble (pick one)

**npm only:**

```markdown
# Project Context

- **Stack:** npm / Node
- Prefer app source under `src/` or this repo's layout.
- Commits must be blocked by pre-commit hooks running static analysis (e.g. `eslint`, `tsc` where applicable).
- **Do not read** these paths unless they are the direct subject of the task:
  `node_modules/`, `dist/`, `build/`, `out/`, `.next/`, `.nuxt/`, `.svelte-kit/`,
  `.parcel-cache/`, `.vite/`, `.cache/`, `.turbo/`, `storybook-static/`,
  `coverage/`, `.nyc_output/`, lock files (`package-lock.json`, `pnpm-lock.yaml`,
  `yarn.lock`, `bun.lock`), `*.tsbuildinfo`, `*.log`.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).
```

**Python only:**

```markdown
# Project Context

- **Stack:** Python
- Prefer package/app source directories.
- Commits must be blocked by pre-commit hooks running static analysis (e.g. `ruff`, `mypy`).
- **Do not read** these paths unless they are the direct subject of the task:
  `.venv/`, `venv/`, `env/`, `__pycache__/`, `*.py[cod]`, `*.so`,
  `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.tox/`, `.hypothesis/`,
  `.pytype/`, `.ipynb_checkpoints/`, `*.egg-info/`, `.eggs/`, `.uv/`,
  `htmlcov/`, `conda-meta/`, `dist/`, `build/`, lock files.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).
```

**npm + Python:**

```markdown
# Project Context

- **Stack:** npm / Node + Python
- Prefer app/package source directories.
- Commits must be blocked by pre-commit hooks running static analysis (e.g. `eslint`/`tsc`, `ruff`/`mypy` as applicable).
- **Do not read** these paths unless they are the direct subject of the task:
  `node_modules/`, `dist/`, `build/`, `out/`, `.next/`, `.nuxt/`, `.svelte-kit/`,
  `.parcel-cache/`, `.vite/`, `.cache/`, `.turbo/`, `storybook-static/`,
  `coverage/`, `.nyc_output/`, `*.tsbuildinfo`,
  `.venv/`, `venv/`, `__pycache__/`, `*.py[cod]`, `*.so`,
  `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.tox/`, `.hypothesis/`,
  `.pytype/`, `.ipynb_checkpoints/`, `*.egg-info/`, `.eggs/`, `.uv/`,
  `htmlcov/`, `conda-meta/`, lock files, `*.log`.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).
```

**Optional (monorepos, `npm + Python` only):** After the line `Prefer app/package source directories.`, add one bullet listing top-level subtrees you actually found (e.g. ``- Main subtrees: `apps/web/` (npm), `services/api/` (Python).``). Use real directory names from the repo, not placeholders.

**Neither** (no npm/Python markers):

```markdown
# Project Context

- Prefer source directories; avoid large or generated trees.
- **Do not read** build output, dependency caches, lock files, or log files
  unless they are the direct subject of the task.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).
```

### Codebase-Memory-MCP block (add when project uses it)

Place this block early in `AGENTS.md` (before generic coding style rules) so it shapes tool selection first:

```markdown
## Codebase-Memory-MCP

- **Critical rule:** For code discovery, navigation, and impact analysis, use `codebase-memory-mcp` first. Do not start with grep/glob for code symbols.

### Discovery Order (Mandatory)

1. `search_graph` — find functions, classes, routes, and variables by name/pattern
2. `trace_call_path` — identify callers/callees and impact
3. `get_code_snippet` — read implementation for exact qualified names
4. `query_graph` — use for multi-hop or aggregate questions
5. `get_architecture` — use for high-level structure when needed

### Fallback Rules (Only When Needed)

Use grep/glob/file search only for:

- string literals, error messages, and config values
- non-code files (`Dockerfile`, YAML/TOML/JSON configs, shell scripts, docs)
- cases where MCP returns insufficient results

### Required Self-Check Before Finalizing

- Confirm MCP graph tools were used for code discovery
- If fallback search was used, explicitly state why MCP was insufficient
- Keep evidence concise: symbol queried, tool used, and result

### MCP Query Tips (Tests)

- In many repos, code files (including tests) are represented primarily as `Module` nodes rather than `File` nodes.
- For test discovery, start with:
  - `search_graph(label="Module", name_pattern=".*test.*")`
  - `search_graph(label="Function", name_pattern="test_.*")`
- `search_code` is content-based grep; it is not a filename index.
- If `label="File"` looks sparse, retry with `label="Module"` before using grep/glob fallback.
```

### Tokenify block (append after optional MCP block; otherwise after stack preamble — copy verbatim)

```markdown
# Tokenify — Context & Token Optimization

## Goal
Minimize token consumption and prevent context window pollution while maintaining high accuracy in code generation and task execution.

## Operational Rules

### 1. Context Minimization (Surgical Mentions)
- **Do not read entire directories** unless specifically instructed.
- **Selective Reading:** Before reading a file, check if a summary or the file structure (tree) is sufficient.
- **Exclude Noise:** Automatically ignore lock files (`package-lock.json`, `pnpm-lock.yaml`), build artifacts, and large static assets unless they are the direct subject of the task.

### 2. Information Density
- **Log Pruning:** When analyzing errors, do not ingest entire terminal outputs. Extract only the stack trace and the specific error message.
- **Concise Responses:** Avoid conversational filler ("Certainly!", "I have updated the file..."). Provide the direct solution or the diff.
- **Diffs over Rewrites:** Whenever possible, output only the modified lines (diff format) rather than rewriting a 500-line file to change two variables.

### 3. Task Segmentation
- **Sub-tasking:** If a request is complex (e.g., "Build the API and the UI"), decompose it. Propose to handle the API first, then "Reset" or start a new context for the UI.
- **The "Clean Slate" Protocol:** If a bug remains unresolved after 3 attempts, signal the user to "Hard Reset" the chat to purge the accumulated "hallucination debt" in the current context.

### 4. Modular Thinking
- **Encourage Refactoring:** If a file exceeds 300 lines, proactively suggest breaking it into smaller modules. This makes future edits cheaper and more accurate.
- **Spec-First Workflow:** Always request or generate a minimal test case/spec before implementation. This prevents "shotgun debugging" which wastes thousands of tokens.

### 5. Resource Allocation (Model Matching)
- **Tiered Processing:**
    - Use "Flash" or smaller models for boilerplate, documentation, and simple refactors.
    - Reserve "Pro/Sonnet" models for architectural changes and complex logic.
- **MCP Management:** Deactivate Model Context Protocol (MCP) tools that are not relevant to the current file type (e.g., disable SQL tools when editing CSS).

## Trigger Phrases
- "Applying Tokenify Protocol": When the agent starts pruning context.
- "Context Warning": When the agent detects the chat history is becoming too "heavy" and suggests a new session.
```


### Karpathy Guidelines block (append after Tokenify — copy verbatim)

```markdown
# Behavioral Guidelines (Karpathy)

## 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.

## 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
- Transform tasks into verifiable goals (e.g. "Add validation" → "Write tests for invalid inputs, then make them pass").
- For multi-step tasks, state a brief plan and verify each step.
```

### graphify (if present)

If `graphify-out/` exists, add this block to `AGENTS.md`:

```markdown
## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
```

### MCP Tools (optional)

Add any Model Context Protocol tools available in your workflow:

```markdown
## Available MCP Tools

- **mcp-cli** - CLI facade for accessing MCP servers dynamically
- **[your-mcp-name-1]** - [brief description of what it does]
- **[your-mcp-name-2]** - [brief description]
```

If you use mcp-cli, include it so agents know to use `mcp-cli <server> <command>` for tasks involving those tools.

---

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
- **Claude Code**: `CLAUDE.md`
- **Gemini CLI**: `GEMINI.md`
- **Windsurf**: `.windsurfrules`
- **Cline**: `.clinerules`

### Native Support (No Shim Needed)

| Tool | How it picks up `AGENTS.md` |
|------|----------------------------|
| **OpenCode** | Reads `AGENTS.md` natively. |
| **GitHub Copilot** | Reads `AGENTS.md` natively. |
| **Aider** | Add `read: AGENTS.md` to `.aider.conf.yml`. |

---

## 5. Agent Synchronization & Symlinking (Multi-Tool)

To ensure consistency across Cursor, Gemini CLI, Claude Code, and other agents, we use a single authoritative store (\`~/.skills\`) and map all tool-specific paths to it via symlinks.

### Claude Code CLI (global symlink)

The global symlink at `~/.claude/skills → ~/.skills` gives Claude Code CLI access to all skills. No project-level action needed for CLI sessions.

### Claude Desktop (project-level recursive copy)

Claude Desktop is sandboxed and cannot follow symlinks outside the workspace. Ensure it has access to skills via a **recursive copy**:

```bash
rm -rf /path/to/project/.claude/skills
cp -r ~/.skills /path/to/project/.claude/skills
```

Re-run `cp -r` (or use the `skill-sync` skill) whenever the master store is updated to keep the project copy current.

### Multi-Tool Symlink Mapping

Before completing onboarding, audit and establish symlinks according to these references:

- **Symlinks:** See [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md) for global and project-level mappings.

### Symlinking Principles

1. **Link, Don't Copy** (default): Symlink to the master store at \`~/.skills\`.
   - **Exception — Claude Desktop:** Use \`cp -r ~/.skills .claude/skills\` instead of a symlink (sandbox cannot follow external symlinks). Re-copy when the master store changes. Claude Code CLI uses the global symlink and needs no project-level copy.
2. **Ignore Local Shims:** Always add project-level skill folders (\`.skills/\`, \`.gemini/skills/\`, \`.claude/skills/\`, etc.) to \`.gitignore\`.
3. **Automate Sync:** Use the \`skill-sync\` skill to audit and fix broken or missing links (and stale copies for Claude Desktop) across all platforms.

---

## 6. Verification

- [ ] Stack detection recorded (npm / python / both / neither), including **nested** paths and **Python-without-manifest** when applicable.
- [ ] Global STANDARDS.md checked (`~/.skills/STANDARDS.md`)
- [ ] Project-specific STANDARDS.md merged (if exists) or section created
- [ ] Static analysis enforced via git commit hooks (use existing hook framework if present; otherwise `pre-commit` for Python and/or `husky` for npm). “Run everything” commands documented.
- [ ] `AGENTS.md` exists with the correct stack preamble, exclusion paths, STANDARDS.md reference, and section order: stack preamble -> optional MCP block -> Tokenify -> Karpathy.
- [ ] MCP conditional inclusion enforced: include MCP block only when MCP is in use (explicit request, existing instructions, or active tooling); otherwise omit it.
- [ ] If included, MCP block appears exactly once, immediately after the stack preamble, with mandatory discovery order, fallback boundaries, and completion self-check.
- [ ] `core-agent-behavior.mdc` exists with `alwaysApply: true`.
- [ ] `.cursorignore` contains Universal + every block for a detected stack; Python-only includes `dist/` and `build/`. If the tool cannot write `.cursorignore`, paste the missing block(s) for the user to add manually.
- [ ] `.cursorrules` is a thin shim referencing `AGENTS.md` (no duplicated Tokenify).
- [ ] Cross-tool shims (`CLAUDE.md`, `GEMINI.md`) exist if multi-tool support was requested or defaulted.
- [ ] `.claude/skills` is a recursive copy of `~/.skills` for Claude Desktop (run `cp -r ~/.skills /path/to/project/.claude/skills`). Claude Code CLI uses the global symlink.
- [ ] Global and Project symlinks audited against [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).

---

## Notes for the agent

- `AGENTS.md` is the **canonical source of truth** for project conventions. All other instruction files are shims or references.
- `STANDARDS.md` (global: `~/.skills/STANDARDS.md`) is the **architectural oracle** — agents check this before blocking on assumptions.
- Exact patterns live only in this skill—copy blocks verbatim so onboarding stays consistent.
- When `codebase-memory-mcp` is in use, place its block near the top of `AGENTS.md` so it is not diluted by lower-priority style guidance.
- Do not add the MCP block to projects where MCP is not in use.
- Future stacks (Rust, Go, Java, etc.) should be new labeled blocks in this skill, not ad hoc edits during a run.
- Never replace a user's `AGENTS.md` / `.cursorignore` / `.cursorrules` / `STANDARDS.md` wholesale; merge and dedupe.
- When a user switches tools mid-session (e.g. rate-limited on Claude, jumps to Gemini CLI), the new agent reads `AGENTS.md` (or its shim) automatically — no manual re-onboarding needed for baseline project knowledge. Use the **orchestrate** skill for `.tickets/` workflow and `Stage:` transitions when continuing across sessions or agents.
- The exclusion list in `AGENTS.md` serves as a "soft ignore" for tools without a dedicated ignore file. It tells the agent what not to read, even though the tool has no `.cursorignore` equivalent.
- **Nested layouts:** Do not conclude "npm only" just because the workspace root lacks `package.json`; nested `package.json` still means npm. Same for Python manifests or backend `.py` trees under a subfolder.
- **STANDARDS.md lifecycle:**
  - Created once (globally) on first onboarding
  - Extended with project-specific sections per project
  - Updated when agents block on questions humans have already decided
  - Reviewed every 3 months or when onboarding to significantly different project

---
name: project-onboarding
description: Creates and reconciles project agent-instruction files across tools, including AGENTS.md, Cursor rules, and stack-specific ignore patterns. Use when onboarding a repository, standardizing agent behavior files, or syncing multi-tool project setup.
---

# Project Onboarding (Multi-Tool)

Target the **project root** the user is onboarding (usually workspace root). **Default:** write `AGENTS.md`, `.cursorignore`, and `.cursorrules` at that root even when markers live only in subfolders (monorepo), so one workspace sees one set of rules—unless the user asks to onboard a subfolder as its own root.

Companion files:
- Windows notes: [WINDOWS.md](WINDOWS.md)
- Global symlink map: [GLOBAL_SYMLINKS.md](GLOBAL_SYMLINKS.md)
- Project symlink map: [PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md)

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

## 1. `AGENTS.md` — canonical agent instructions

This is the **single source of truth** read by every tool. All other instruction files (`.cursorrules`, `CLAUDE.md`, `GEMINI.md`) are thin shims that reference it.

Tools that auto-read `AGENTS.md`: OpenCode, GitHub Copilot (`.github/copilot-instructions.md` can reference it), and any agent given a cold-start prompt.

Create **`AGENTS.md`** at the project root using the appropriate stack template below, followed by the Tokenify block.

When merging into an existing `AGENTS.md`: keep user sections; append missing parts; deduplicate; preserve headings.

### Stack-specific preamble (pick one)

**npm only:**

```markdown
# Project Context

- **Stack:** npm / Node
- Prefer app source under `src/` or this repo's layout.
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

### Tokenify block (append after stack preamble — copy verbatim)

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

### Block A — Universal (always)

```
# --- cursorignore: universal ---
.git/

.env
.env.*
!.env.example

*.log
.DS_Store
Thumbs.db

# Local skill shims (symlinks to ~/.skills)
.skills/
.gemini/skills/
```

### Block B — npm / Node (if stack detected)

Use this block verbatim (do not omit entries; paths are chosen for size and low signal for LLM context):

```
# --- cursorignore: npm / Node ---
node_modules/
jspm_packages/

.pnp/
.pnp.*
**/.pnpm-store/

dist/
build/
out/
.next/
.nuxt/
.svelte-kit/
storybook-static/
.parcel-cache/
.vite/

.cache/
.turbo/
*.tsbuildinfo

coverage/
.nyc_output/

npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*
```

### Block C — Python (if stack detected)

Use this block verbatim:

```
# --- cursorignore: python ---
.venv/
venv/
env/
ENV/
.virtualenv/

__pycache__/
*.py[cod]
*$py.class
*.so

.mypy_cache/
.pytest_cache/
.ruff_cache/
.tox/
.hypothesis/
.pytype/
.ipynb_checkpoints/

*.egg-info/
.eggs/
*.egg
pip-wheel-metadata/

.uv/

htmlcov/

# Common large local env trees (conda/miniconda layouts sometimes copied into repo)
conda-meta/
```

**Note:** `dist/` and `build/` appear in the npm block. If **Python-only** (no npm), add these two lines under the Python section so packaging artifacts are still ignored:

```
dist/
build/
```

---

## 4. `.cursorrules` — thin shim (Cursor-specific)

`.cursorrules` no longer holds the full instructions. It references `AGENTS.md` and adds Cursor-specific notes.

Write the following (pick the stack variant that matches detection):

**npm only:**

```markdown
# Project context (npm / Node)

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

**Python only:**

```markdown
# Project context (Python)

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

**npm + Python:**

```markdown
# Project context (npm / Node + Python)

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

**Neither:**

```markdown
# Project context

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

When merging into an existing `.cursorrules` that already contains a full Tokenify block or stack preamble: replace the old preamble with the shim; remove the duplicated Tokenify block (it now lives in `AGENTS.md`).

---

## 5. Cross-tool shims (optional — generate when asked or by default)

These files let other agents pick up project context automatically on cold start. Generate them at the project root. If the user only uses Cursor, these can be skipped.

### `CLAUDE.md` (Claude Code)

Claude Code auto-reads `CLAUDE.md` at the project root and `~/.claude/CLAUDE.md` globally.

```markdown
Read and follow AGENTS.md in this directory for project conventions,
context exclusions, and operational rules.
```

### `GEMINI.md` (Gemini CLI)

Gemini CLI auto-reads `GEMINI.md` at the project root.

```markdown
Read and follow AGENTS.md in this directory for project conventions,
context exclusions, and operational rules.
```

### Other tools

| Tool | How it picks up `AGENTS.md` |
|------|----------------------------|
| **OpenCode** | Reads `AGENTS.md` natively — no shim needed. |
| **GitHub Copilot** | Reads `AGENTS.md` natively. Optionally reference it from `.github/copilot-instructions.md`. |
| **Windsurf** | Create `.windsurfrules` with the same shim text as above. |
| **Aider** | Add `read: AGENTS.md` to `.aider.conf.yml`. |
| **Cline** | Create `.clinerules` with the same shim text as above. |

---

## 5b. Agent Synchronization & Symlinking (Multi-Tool)

To ensure consistency across Cursor, Gemini CLI, Claude Code, and other agents, we use a single authoritative store (\`~/.skills\`) and map all tool-specific paths to it via symlinks.

### Multi-Tool Symlink Mapping

Before completing onboarding, audit and establish symlinks according to these references:

- **Global Symlinks:** See [GLOBAL_SYMLINKS.md](GLOBAL_SYMLINKS.md) for \`~/\` home directory mappings.
- **Project Symlinks:** See [PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md) for local repo mappings.

### Symlinking Principles

1. **Link, Don't Copy:** Never duplicate skill folders; always symlink to the master store at \`~/.skills\`.
2. **Ignore Local Shims:** Always add project-level symlink folders (\`.skills/\`, \`.gemini/skills/\`, etc.) to \`.gitignore\`.
3. **Automate Sync:** Use the \`skill-sync\` skill to audit and fix broken or missing links across all platforms.

---

## 6. Verification

- [ ] Stack detection recorded (npm / python / both / neither), including **nested** paths and **Python-without-manifest** when applicable.
- [ ] Global STANDARDS.md checked (`~/.skills/STANDARDS.md`)
- [ ] Project-specific STANDARDS.md merged (if exists) or section created
- [ ] `AGENTS.md` exists with the correct stack preamble, exclusion paths, Tokenify block, and STANDARDS.md reference
- [ ] `core-agent-behavior.mdc` exists with `alwaysApply: true`.
- [ ] `.cursorignore` contains Universal + every block for a detected stack; Python-only includes `dist/` and `build/`. If the tool cannot write `.cursorignore`, paste the missing block(s) for the user to add manually.
- [ ] `.cursorrules` is a thin shim referencing `AGENTS.md` (no duplicated Tokenify).
- [ ] Cross-tool shims (`CLAUDE.md`, `GEMINI.md`) exist if multi-tool support was requested or defaulted.
- [ ] Global and Project symlinks audited against [GLOBAL_SYMLINKS.md](GLOBAL_SYMLINKS.md) and [PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md).

---

## Notes for the agent

- `AGENTS.md` is the **canonical source of truth** for project conventions. All other instruction files are shims or references.
- `STANDARDS.md` (global: `~/.skills/STANDARDS.md`) is the **architectural oracle** — agents check this before blocking on assumptions.
- Exact patterns live only in this skill—copy blocks verbatim so onboarding stays consistent.
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

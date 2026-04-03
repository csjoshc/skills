# AGENTS.md Stack Preambles

Pick the preamble matching the detected stack. Append the Tokenify block after it.

## npm only

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

## Python only

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

## npm + Python

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

## Neither (no npm/Python markers)

```markdown
# Project Context

- Prefer source directories; avoid large or generated trees.
- **Do not read** build output, dependency caches, lock files, or log files
  unless they are the direct subject of the task.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).
```

## Windows (Add-on)

```markdown
# Windows Compatibility (Git Bash)

- **Environment:** running in MINGW64 / MSYS2 (Git Bash).
- **Path Rules:** 
  - Use POSIX-style paths: `/c/Users/...` instead of `C:\Users\...`.
  - Drive letters are lowercase: `/c/`.
  - MSYS_NO_PATHCONV=1 for native Windows binaries (or double the leading slash: `//`).
- **Commands:** Unix commands (`ls`, `grep`, `sed`, `find`) work; PowerShell cmdlets do NOT.
- See [WINDOWS.md](./WINDOWS.md) for full shell and path reference.
```

## Tokenify block (append after stack preamble — copy verbatim)

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

### 5. Post-Implementation Validation
- **Mandatory Verification:** After modifying any code, identify and execute the most relevant unit or integration tests to verify the change. 
- **Continuous Feedback:** If a modification causes a test failure, prioritize fixing the regression before proceeding or finishing the task.

## Trigger Phrases
- "Applying Tokenify Protocol": When the agent starts pruning context.
- "Context Warning": When the agent detects the chat history is becoming too "heavy" and suggests a new session.
```

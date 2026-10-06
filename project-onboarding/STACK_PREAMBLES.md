# Stack-specific AGENTS.md preambles

Verbatim `# Project Context` templates. Extracted from `SKILL.md`; pick one after stack detection.

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


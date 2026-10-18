# Stack Detection

## Contents

- Where to look (manifest markers)
- Python without a manifest
- Merge rules

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

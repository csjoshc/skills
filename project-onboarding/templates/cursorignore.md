# .cursorignore Blocks

Always include the **Universal** block. Add npm block if npm/Node detected. Add Python block if Python detected.

If a `.cursorignore` already exists, **append the missing patterns** to the bottom. Do not aggressively deduplicate or reshape existing sections.

## Block A — Universal (always)

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

## Block B — npm / Node (if stack detected)

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

## Block C — Python (if stack detected)

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

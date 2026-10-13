# Documentation Cross-Reference Scrub (Phase 3C)

## 3C: Documentation cross-references (deletion or rename)

**Goal:** Catch orphaned references when a package, module, public function, or endpoint is removed. The diff shows the deletion; what it doesn't show is every doc/diagram/CI filter that still points at the deleted thing.

**Trigger:** the PR deletes any of:
- A directory under `packages/`, `src/`, `lib/`, `apps/`
- A top-level public function, class, or exported symbol
- An HTTP endpoint (route handler) or its docstring
- A config file (whose name appears in `.env.example`, docs, or scripts)

**Required checks** before opening the PR:

```bash
# Substitute <removed-name> with the deleted package/symbol/route
NAME=<removed-name>

# Docs + diagrams + READMEs
git grep -nE "\\b${NAME}\\b" -- '*.md' '*.mmd' '*.rst' || true

# CI path filters + workflow refs
git grep -nE "\\b${NAME}\\b" -- '.github/workflows/' || true

# Helm values + manifests + Compose
git grep -nE "\\b${NAME}\\b" -- 'helm/' 'k8s/' 'manifests/' '*.yaml' '*.yml' 'docker-compose*' || true

# Package manifests (project-specific names: pyproject.toml, package.json, Cargo.toml)
git grep -nE "\\b${NAME}\\b" -- '*.toml' '*.json' || true
```

Every hit must be:
- **Removed** if it was the only thing the doc/filter described.
- **Updated** if it referenced the replacement (link / name).
- **Escalated** to the user if ambiguous (e.g., a diagram that includes the old + new side-by-side).

Add a final check to the PR description: `Cross-reference scrub: ran for <NAME>; N hits, all resolved.`

This is the rule that catches "the package was deleted but README/architecture-diagram/CI-filter still mentions it" — the same pattern that produced 5 stale docs + 1 workflow filter + 1 manifest description in a recent cycle.

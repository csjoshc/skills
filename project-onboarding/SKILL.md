---
name: project-onboarding
description: >-
  Onboards a project root by creating AGENTS.md, .cursorignore, .cursorrules, CLAUDE.md, GEMINI.md,
  and symlink infrastructure for multi-tool agent consistency. Detects npm/Python stacks, applies
  stack-specific templates, and establishes STANDARDS.md. Use when starting a new project or
  adding AI tooling to an existing repo.
---

# Project Onboarding (Multi-Tool)

## TL;DR (Quick Start)

Onboards a project root by creating AI-compatible infrastructure (`AGENTS.md`, `.cursorignore`, `CLAUDE.md`). Detects stack (npm, Python), applies templates, and establishes local `STANDARDS.md`.

**When to use:** "setup project", "onboard repo", "add AI rules".

**Invocation:**
```bash
npx project-onboarding
```

## Decision Tree

1. **What is the environment?**
   - Windows → **MANDATORY** Inject `WINDOWS.md` and Windows-specific preamble.
   - POSIX (macOS/Linux) → Use standard templates.

2. **Is a local `STANDARDS.md` present?**
   - YES → Skip creation; audit for existing patterns.
   - NO → Symlink or copy global `STANDARDS.md`.

3. **What is the project stack?**
   - npm/Node → Apply React/Next.js/Node templates.
   - Python → Apply Pytest/Uvicorn templates.

## Workflow

Target the **project root** the user is onboarding (usually workspace root). Create `AGENTS.md`, `.cursorignore`, and `.cursorrules` at that root even when markers live only in subfolders (monorepo), unless the- Future stacks (Rust, Go, Java, etc.) should be new labeled blocks in this skill, not ad hoc edits.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing `.cursorignore` pattern — proceed, append to list in next pass.
- **Tier 2 (conflict):** Existing `AGENTS.md` contradicts new standards — **STOP**, ask user to merge manually or override.
- **Tier 3 (security):** Local `STANDARDS.md` includes credentials — **STOP**, block and alert immediately.

## 0. Check for Global STANDARDS.md
... (rest of the file)

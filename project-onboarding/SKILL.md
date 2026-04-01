---
name: project-onboarding
description: >-
  Onboards a project root by creating AGENTS.md, .cursorignore, .cursorrules, and symlinks for CLAUDE.md/GEMINI.md
  pointing to AGENTS.md (OS-specific symlinks). Detects npm/Python stack, applies stack-specific templates,
  and establishes local STANDARDS.md index. Use when starting a new project or adding AI tooling to an existing repo.
---

# Project Onboarding (Multi-Tool)

## TL;DR (Quick Start)

Onboards a project root by creating AI-compatible infrastructure (`AGENTS.md`, `.cursorignore`, `CLAUDE.md`). Detects stack (npm, Python), applies templates, and establishes local `STANDARDS.md` index.

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
   - NO → Create local STANDARDS.md index pointing to `~/.skills/STANDARDS.md`.

3. **What is the project stack?**
   - npm/Node → Apply React/Next.js/Node templates.
   - Python → Apply Pytest/Uvicorn templates.

## Workflow

Target the **project root** the user is onboarding (usually workspace root). Create `AGENTS.md`, `.cursorignore`, and `.cursorrules` at that root even when markers live only in subfolders (monorepo), unless the user specifies otherwise.

**Future stacks (Rust, Go, Java, etc.)** should be new labeled blocks in this skill, not ad hoc edits.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing `.cursorignore` pattern — proceed, append to list in next pass.
- **Tier 2 (conflict):** Existing `AGENTS.md` contradicts new standards — **STOP**, ask user to merge manually or override.
- **Tier 3 (security):** Local `STANDARDS.md` includes credentials — **STOP**, block and alert immediately.

## 0. Check for Global STANDARDS.md Index

The global `~/.skills/STANDARDS.md` is now an **index** pointing to specialized skills (progressive disclosure).

**When creating local STANDARDS.md:**
1. Create a thin index file (not a full copy)
2. Point to `~/.skills/STANDARDS.md` for global standards
3. Reserve local file for project-specific patterns only

**Template:**
```markdown
# Project Standards — {ProjectName} (Local Additions)

**Location:** This file (`./STANDARDS.md`) is for **{ProjectName}-specific** standards only.

**Global standards:** See `~/.skills/STANDARDS.md` (index pointing to skills)

---

## Global Standards Reference

For architecture decisions, blocker patterns, and quality rubrics, check these skills:

| Topic | Location |
|-------|----------|
| Architecture Decisions | `~/.skills/shared/ARCHITECTURE_DECISIONS.md` |
| Blocker Patterns | `~/.skills/ticket-critic/SKILL.md` |
| State Machine | `~/.skills/orchestrate/SKILL.md` |
| Quality Rubric | `~/.skills/cleanup/QUALITY_RUBRIC.md` |
| PR Review | `~/.skills/pr-review/SKILL.md` |

---

## {ProjectName}-Specific Standards

_(Add project-specific patterns below this line)_

```

**Note:** The local STANDARDS.md should remain thin (<100 lines) to minimize token consumption.

## 1. Symlink Setup

See [`~/.skills/shared/SYMLINK_MAP.md`](~/.skills/shared/SYMLINK_MAP.md) for the authoritative global and project-level symlink map. Create all symlinks listed there.

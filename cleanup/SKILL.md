---
name: cleanup
description: >-
  Review existing code and codebases against a bundled quality rubric (mechanical + subjective
  dimensions, anti-patterns, layering). Tool-agnostic. Use when running audits, PR review prep,
  holistic code-health checks, or remediation planning. Does NOT edit tickets—use ticket-critic
  for .tickets/.
---

# Cleanup — existing codebase review

## TL;DR (Quick Start)
Review source code against a quality rubric with file-cited evidence. Maps observations to rubric dimensions (M1-M12 patterns, subjective tiers, anti-patterns).

**When to use:** Code audits, PR review prep, holistic code health checks. NOT for editing tickets — use ticket-critic for that.

**Invocation:** Apply QUALITY_RUBRIC.md to named paths, PR diffs, or project scope.

## Purpose

Apply **[`QUALITY_RUBRIC.md`](~/.skills/cleanup/QUALITY_RUBRIC.md)** to **source code already in the repo**: structure, contracts, tests, security hygiene, and subjective dimensions (with **file-cited evidence**).

**Out of scope:** Editing **`.tickets/*.md`**, epic splits, or implementation-ready spec shaping → **ticket-critic** skill.

## Mandatory pre-reads

1. **`AGENTS.md`** — exclusions, layout, agent rules.
2. **Architecture Decisions** (in `~/.skills/shared/ARCHITECTURE_DECISIONS.md`) — resolve ambiguities; do not invent policy.
3. **`~/.skills/cleanup/QUALITY_RUBRIC.md`** — full criteria (mechanical **M1–M12**, subjective tiers, anti-patterns, layers).

## Workflow

1. **Scope** — paths, package, or PR diff the user named; default to project source per `AGENTS.md`.
2. **Phase 0 — Mechanical pass (deterministic first).** Run the tool matrix below and collect all findings before any subjective review. Do NOT skip to rubric mapping until the mechanical pass is complete. This prevents the LLM from rationalizing mechanical violations away.
3. **Map** observations to rubric **§Part 2–4** (which dimension or M-pattern).
4. **Evidence** — every finding: **file path**, symbol or line region, **why** it violates the rubric, **suggested fix** (or "needs Architecture Decisions" if policy gap).
5. **Output** — structured review (markdown sections per dimension/pattern, or org-required JSON).
6. **Prioritize** — address **Tier A–C** subjective issues and **M** patterns that affect reliability/security first.

## Phase 0 — Mechanical pass

Run these deterministic checks on the changed/reviewed files before any
LLM-driven reasoning. Every finding from Phase 0 is non-negotiable — it
cannot be dismissed by a later subjective judgment.

| Check | Python | TypeScript/JS | Notes |
|---|---|---|---|
| Unused imports / vars | `ruff check --select F401,F841` | `npx eslint --rule 'no-unused-vars: error'` | Fail = delete |
| Unused exports | `vulture --min-confidence 80` | `npx ts-prune`, `npx knip` | Fail = delete or justify |
| File size | `wc -l` vs 300/500 thresholds in STANDARDS.md | same | Over cap = split |
| Cyclomatic complexity | `radon cc -n C` | `npx complexity-report` | > 10 = refactor |
| Dup detection | `jscpd .` | same | > 5% = consolidate |
| Import cycles | `pycycle` / `importlinter` | `npx madge --circular` | Any cycle = break |
| Layer boundaries | invoke `layer-boundary-critic` | same | Any BLOCK = fix |
| Dead code | `vulture` / grep `if False` / `# TODO someday` | `knip` / grep | Review list |
| Dead branches | `# pragma: no cover` without reason | `istanbul ignore` without reason | Justify or remove |
| Commented-out blocks | `grep -En '^\s*(#\|//)[^!]'` runs | same | Remove |

Emit Phase 0 output before Phase 1:

```markdown
## Phase 0 — Mechanical findings (N)

| Check | File | Line | Finding |
|---|---|---|---|
| F401 | src/auth.py | 4 | unused `from os import path` |
| file-size | src/ui/Dashboard.tsx | 847 | exceeds 500 LOC cap |
```

If Phase 0 is non-empty, resolve those findings (or get explicit override)
before proceeding to subjective rubric mapping.

## Persona

**Principal Staff Engineer:** favor **deletion** of redundant AI slop; **pragmatic** modularity (no speculative abstractions); **explicit** edge cases; **one** standard per cross-cutting concern (logging, config, errors, file IO).

## Optional cross-skills

- **arch-review** — when checking architecture patterns (bounded contexts, hexagonal, vertical slices, module boundaries)
- **make-ui** — when reviewing frontend visuals if the project uses it.  
- **chrome-devtools** / **test-ui** — when validating UI behavior after fixes (not required to *invoke* for a read-only audit).

## Do not

- Edit ticket files or handoff plans unless the user explicitly switches to **ticket-critic**.  
- Cite proprietary scanner brands as mandatory; verification is **project commands** (pytest, ruff, bandit, etc.).  
- Score from vibes without paths/symbols.

## Related

| File | Role |
|------|------|
| [`QUALITY_RUBRIC.md`](~/.skills/cleanup/QUALITY_RUBRIC.md) | Full merged rubric |
| [`WRITE_TIME_GUARD.md`](./WRITE_TIME_GUARD.md) | Blocks duplication and "just in case" code at write time (invoked on any new file or new export) |
| [`LAYER_ENFORCEMENT.md`](./LAYER_ENFORCEMENT.md) | Enforces downward-only dependencies from AGENTS.md layer cake (invoked during Phase 0 on every import change) |
| **arch-review** | Architecture pattern enforcement and review |
| **ticket-critic** | Ticket markdown, blast radius, TDD/verification in specs |

**When to load companions:**
- Load `WRITE_TIME_GUARD.md` before any `Write` of a new file or new exported symbol.
- Load `LAYER_ENFORCEMENT.md` during Phase 0 whenever the changed files add or modify an import statement.

## Examples

**Example 1: Basic code audit**
Input: "Review the auth/ directory for code quality issues"
Output: Structured findings mapped to rubric dimensions with file paths and suggested fixes.

**Example 2: PR review prep**
Input: "Audit the changes in PR #42 for security and maintainability"
Output: Findings categorized by severity (Tier A-C), M-patterns violated, and priority recommendations.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for cleanup:**
- **Tier 1 (reversible):** Minor style issues — proceed, flag for post-review
- **Tier 2 (architecture):** Design concerns blocking — check Architecture Decisions, block if unresolved
- **Tier 3 (security):** Security vulnerabilities — always block for human confirmation

## Decision Tree

Use this skill when you need to:

1. **What is the scope?**
   - PR diff review → Focus on changed files, M-patterns in diff
   - Full codebase → Use AGENTS.md exclusions, scan systematically
   - Specific directory → Scope to named path

2. **What type of issues matter most?**
   - Security focus → Check M1-M4 (vulnerabilities)
   - Maintainability → Check M5-M8 (code structure)
   - Testing → Check M9-M12 (test quality)
   - General → Address all, prioritize Tier A + M1-M4

3. **Need visual validation?**
   - YES → Pair with chrome-devtools or test-ui
   - NO → Standalone audit

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.

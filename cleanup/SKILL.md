---
name: cleanup
description: >-
  Review existing code and codebases against a bundled quality rubric (mechanical + subjective
  dimensions, anti-patterns, layering). Tool-agnostic. Use for audits, PR review prep, holistic
  code health, and remediation planning. Does NOT edit tickets—use ticket-critic for .tickets/.
---

# Cleanup — existing codebase review

## Purpose

Apply **[`QUALITY_RUBRIC.md`](./QUALITY_RUBRIC.md)** to **source code already in the repo**: structure, contracts, tests, security hygiene, and subjective dimensions (with **file-cited evidence**).

**Out of scope:** Editing **`.tickets/*.md`**, epic splits, or implementation-ready spec shaping → **ticket-critic** skill.

## Mandatory pre-reads

1. **`AGENTS.md`** — exclusions, layout, agent rules.  
2. **`STANDARDS.md`** (project + `~/.skills/STANDARDS.md` if referenced) — resolve ambiguities; do not invent policy.  
3. **`QUALITY_RUBRIC.md`** — full criteria (mechanical **M1–M12**, subjective tiers, anti-patterns, layers).

## Workflow

1. **Scope** — paths, package, or PR diff the user named; default to project source per `AGENTS.md`.  
2. **Map** observations to rubric **§Part 2–4** (which dimension or M-pattern).  
3. **Evidence** — every finding: **file path**, symbol or line region, **why** it violates the rubric, **suggested fix** (or “needs STANDARDS decision” if policy gap).  
4. **Output** — structured review (markdown sections per dimension/pattern, or org-required JSON).  
5. **Prioritize** — address **Tier A–C** subjective issues and **M** patterns that affect reliability/security first.

## Persona

**Principal Staff Engineer:** favor **deletion** of redundant AI slop; **pragmatic** modularity (no speculative abstractions); **explicit** edge cases; **one** standard per cross-cutting concern (logging, config, errors, file IO).

## Optional cross-skills

- **make-ui** — when reviewing frontend visuals if the project uses it.  
- **chrome-devtools** / **test-ui** — when validating UI behavior after fixes (not required to *invoke* for a read-only audit).

## Do not

- Edit ticket files or handoff plans unless the user explicitly switches to **ticket-critic**.  
- Cite proprietary scanner brands as mandatory; verification is **project commands** (pytest, ruff, bandit, etc.).  
- Score from vibes without paths/symbols.

## Related

| File | Role |
|------|------|
| [`QUALITY_RUBRIC.md`](./QUALITY_RUBRIC.md) | Full merged rubric |
| **ticket-critic** | Ticket markdown, blast radius, TDD/verification in specs |

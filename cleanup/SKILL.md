---
name: cleanup
description: >-
  Review existing code and codebases against a bundled quality rubric (mechanical + subjective
  dimensions, anti-patterns, layering). Tool-agnostic. Use for audits, PR review prep, holistic
  code health, and remediation planning. Does NOT edit tickets—use ticket-critic for .tickets/.
---

# Cleanup — existing codebase review

## TL;DR (Quick Start)
Review source code against a quality rubric with file-cited evidence. Maps observations to rubric dimensions (M1-M12 patterns, subjective tiers, anti-patterns).

**When to use:** Code audits, PR review prep, holistic code health checks. NOT for editing tickets — use ticket-critic for that.

**Invocation:** Apply QUALITY_RUBRIC.md to named paths, PR diffs, or project scope.

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

## Examples

**Example 1: Basic code audit**
Input: "Review the auth/ directory for code quality issues"
Output: Structured findings mapped to rubric dimensions with file paths and suggested fixes.

**Example 2: PR review prep**
Input: "Audit the changes in PR #42 for security and maintainability"
Output: Findings categorized by severity (Tier A-C), M-patterns violated, and priority recommendations.

## Assumptions & Escalation

- **Tier 1 (reversible):** Minor style issues — proceed, flag for post-review
- **Tier 2 (architecture):** Design concerns blocking — check STANDARDS.md, block if unresolved
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

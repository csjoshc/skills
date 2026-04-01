# Skill Conventions

Distilled from context engineering research (Anthropic 2025, ETH Zurich 2026, Addy Osmani 2026).
All skills in `~/.skills/` follow these conventions.

## Core Principle

**Find the smallest possible set of high-signal tokens that maximize the likelihood of your desired outcome.**

Context is finite. Every token competes with every other token for attention. More context often degrades performance.

---

## 1. Progressive Disclosure

**Rule:** SKILL.md is the lightweight protocol. Depth lives in companion files loaded on-demand.

| Threshold | Action |
|-----------|--------|
| SKILL.md < 200 lines | No companions needed |
| SKILL.md 200-400 lines | 1-3 focused companions |
| SKILL.md > 400 lines | Must split into companions |

**Companion file naming:**
- `templates/` — output templates, block messages, formatters
- `reference/` — cross-skill references, integration guides
- `examples/` — few-shot examples, audit findings, session transcripts
- `*.md` — domain-specific depth (e.g., `TESTS.md`, `MOCKING.md`, `QUALITY_RUBRIC.md`)

**SKILL.md must reference companions explicitly** with clear "when to load" guidance.

---

## 2. Token Budgets

| Component | Budget | Rationale |
|-----------|--------|-----------|
| SKILL.md TL;DR | ≤ 10 lines | Quick scan, no bloat |
| SKILL.md total | ≤ 200 lines (ideal), ≤ 400 lines (max) | Attention budget |
| Companion file | No hard limit, but progressive disclosure required | Loaded only when needed |
| Total skill (SKILL.md + all companions) | No limit | Only SKILL.md loads every invocation |

---

## 3. No Redundancy

**Rule:** If content appears in 2+ skills, extract to `shared/`.

**Current shared files:**
- `shared/ASSUMPTION_TIERS.md` — canonical Tier 1/2/3 definitions (referenced by 7 skills)
- `shared/ARCHITECTURE_DECISIONS.md` — API patterns, auth, data layer, testing, code org (referenced by spec-writer, ticket-critic, cleanup, tdd)
- `shared/SYMLINK_MAP.md` — global and project-level symlink maps (referenced by project-onboarding, skill-sync)
- `shared/SKILL_CONVENTIONS.md` — this file

**Check before adding content to a skill:**
1. Does another skill already define this?
2. Is this a shared concept that multiple skills reference?
3. If yes to either → put in `shared/`, reference from skills.

---

## 4. Non-Discoverable Content Only

**Rule:** Every line must represent information the agent cannot discover by reading the codebase.

**Belongs in skills:**
- Tool gotchas (`uv` vs `pip`, Git Bash path conversion)
- Non-obvious conventions (custom middleware patterns, deprecated directories)
- Cross-component contracts (API schemas, dependency edges)
- Process rules (state transitions, stage enums)

**Does NOT belong in skills:**
- Directory structure (agent can `ls`)
- Tech stack (agent can read `package.json` / `pyproject.toml`)
- Module explanations (agent can read the code)
- README content (agent can read README.md)

**Test:** "Can the agent find this by reading the repo?" If yes → delete it.

---

## 5. Cross-Reference Requirements

**Rule:** Skills must reference each other rather than re-defining concepts.

**Required references:**
- Stage enum → reference `orchestrate` skill
- Assumption tiers → reference `shared/ASSUMPTION_TIERS.md`
- Architecture decisions → reference `shared/ARCHITECTURE_DECISIONS.md`
- TDD principles → reference `tdd` skill
- Quality rubric → reference `cleanup/QUALITY_RUBRIC.md`
- Ticket format → reference `spec-writer` skill output contract

**Forbidden:** Re-defining another skill's core concepts.

---

## 6. Architecture Decisions Location

**Rule:** Architecture Decisions live in `shared/ARCHITECTURE_DECISIONS.md`, NOT embedded in skills.

**Why:** Embedded Architecture Decisions become stale. If the project switches from REST to GraphQL, every agent invocation carries misleading context. The "pink elephant" problem.

**Pattern:**
```markdown
## Architecture Decisions

See [`~/.skills/shared/ARCHITECTURE_DECISIONS.md`](~/.skills/shared/ARCHITECTURE_DECISIONS.md)
for canonical API patterns, auth, data layer, testing strategy, and code organization.

**Project-specific overrides:** See `./STANDARDS.md` in the target project.
```

---

## 7. Shared File Conventions

Files in `shared/` are cross-cutting references used by multiple skills.

**Requirements:**
- Self-contained (no references back to individual skills)
- Project-agnostic (no project-specific patterns)
- Version-stable (changes affect all consumers)
- Well-structured with clear section headers

**When to add to `shared/`:**
- Referenced by 2+ skills
- Domain knowledge, not process knowledge
- Unlikely to change frequently

---

## 8. Skill Structure

Every SKILL.md must have:

```markdown
---
name: <skill-name>
description: <one-line description for skill discovery>
---

## TL;DR (Quick Start)
≤ 10 lines. When to use, invocation pattern.

## Assumptions & Escalation
Reference shared/ASSUMPTION_TIERS.md + domain-specific examples.

## Decision Tree
Numbered branching logic for when/how to use the skill.

## Workflow
Core operating principles and step-by-step process.

## Examples (Few-Shot)
2+ diverse examples showing expected behavior.

## Quality Rules
Hard constraints, non-negotiables.
```

**Optional sections:** Architecture Decisions reference, Layer Ownership, companion file references.

---

## 9. Maintenance

**Update this file when:**
- New convention identified from skill audit
- Context engineering research adds new principles
- Skill validator gains new checks

**Validation:** Run `./skill-validator.sh` before committing skill changes.

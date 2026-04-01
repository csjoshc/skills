# Project Standards — Index

**Status:** DEPRECATED — Knowledge moved to skills (progressive disclosure)

**Purpose:** This file previously contained architectural decisions and blocker patterns. All content has been migrated to specialized skills for token efficiency.

---

## Where to Find Standards

### Architecture Decisions
**Location:** `~/.skills/shared/ARCHITECTURE_DECISIONS.md`

**Contains:**
- API patterns (REST, endpoints, error format, status codes)
- Authentication & authorization (JWT, sessions, rate limiting)
- Data layer (database, ORM, migrations)
- Testing strategy (frameworks, coverage targets)
- Code organization (backend/frontend structure)
- File size limits (300/500 line thresholds)
- Layer ownership (domain, service, application, infrastructure)
- Resolved Q&A (endpoints, validation, tests, file uploads, subprocess, state management)
- Security checklist
- Performance budgets
- Decision framework (when to block vs. proceed, assumption tiers)

**When to check:** Writing specs, making architecture decisions, resolving assumptions

---

### Blocker Patterns & Pre-Flight Checklist
**Location:** `~/.skills/ticket-critic/SKILL.md` — "Pre-Flight Checklist" section

**Contains:**
- Dependency detection patterns
- Redesign/redarchitecture triggers
- Contradicting ticket detection
- Research/vagueness detection
- Quick reference table (8 blocker patterns)
- 10 blocking patterns audit
- Stage header gate validation

**When to check:** Auditing tickets before implementation, writing ticket specs

---

### State Machine & Ticket Routing
**Location:** `~/.skills/orchestrate/SKILL.md`

**Contains:**
- Stage enum (NEW, SPEC, SPEC_SPLIT, BUILD, REVIEW, COMPLETE, BLOCKED, FAILED)
- State transition rules
- Ticket splitting policy (blast radius control)
- Inter-agent communication patterns

**When to check:** Transitioning ticket states, understanding orchestration flow

---

### Quality Rubric (Code Review)
**Location:** `~/.skills/cleanup/QUALITY_RUBRIC.md`

**Contains:**
- Mechanical dimensions (M1-M12)
- Subjective tiers (A-C)
- Anti-patterns catalog
- Layer analysis

**When to check:** Auditing existing code, PR review prep

---

### PR Review Standards
**Location:** `~/.skills/pr-review/SKILL.md`

**Contains:**
- Bug detection checklist
- Standards compliance patterns
- Error handling audit
- Test analyzer criteria

**When to check:** Reviewing pull requests

---

## Migration History

**Date:** 2026-03-31

**Reason:** Token optimization — prevent context window pollution by moving 710-line monolithic file behind progressively disclosed skills.

**Token savings:** ~4,000 tokens per agent invocation (80-90% reduction for most tasks)

**Skills updated:**
- `spec-writer` — Architecture Decisions embedded
- `ticket-critic` — Blocker patterns embedded
- `cleanup` — References updated
- `pr-review` — References updated
- `orchestrate` — Already focused on state machine

**Files updated:**
- `orchestra/prompts.py` — Removed STANDARDS.md from `_ctx()`
- `orchestra/expansion/facets.py` — Removed direct file read

---

## For Historical Reference

The full content of this file has been distributed as follows:

| Original Section | New Location |
|-----------------|--------------|
| Pre-Flight Checklist | `ticket-critic/SKILL.md` |
| Architecture Decisions | `spec-writer/SKILL.md` |
| Layer Ownership | `spec-writer/SKILL.md` |
| Resolved Questions | `spec-writer/SKILL.md` |
| Security Checklist | `spec-writer/SKILL.md` |
| Performance Budgets | `spec-writer/SKILL.md` |
| Decision Framework | `spec-writer/SKILL.md` |
| Project-Specific (Orchestra) | `orchestrate/SKILL.md` |

---

## What to Do

**As an agent:**
1. Check the specific skill for your task (see table above)
2. Do NOT read this file — it's an index only
3. Skills are loaded on-demand, saving tokens

**As a human:**
1. Update the relevant skill when making new decisions
2. Do not add content to this file
3. Use this file only as a navigation aid

---

**Previous location:** `~/.skills/STANDARDS.md` (now this index)
**Project-level:** `./STANDARDS.md` (still used for project-specific additions)

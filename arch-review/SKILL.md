---
name: arch-review
description: Architectural pattern enforcement and review. Use when reviewing code for architecture compliance, writing architecture sections in specs, making pattern selection decisions, or validating ADRs. Provides centralized knowledge of macro-architecture (microservices, modular monoliths), micro-architecture (hexagonal, vertical slices), and DDD patterns.
---

# Arch Review

## TL;DR (Quick Start)

Provides architectural pattern knowledge for code review and spec writing. Enforces established patterns (hexagonal, vertical slices, DDD bounded contexts) and detects drift.

**When to use:** Code audits, spec writing, ADR validation.

**Invocation:** Load skill, then reference pattern guides in `references/` directory.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for arch-review:**
- **Tier 1 (reversible):** Missing pattern documentation — proceed, add in next pass.
- **Tier 2 (conflict):** Pattern conflict with cleanup/spec-writer — **STOP**, resolve before proceeding.
- **Tier 3 (security):** Architecture allows security bypass — **STOP**, block and alert.

## Overview

Provides architectural pattern knowledge for code review and spec writing. Ensures architecture consistency across the codebase by enforcing established patterns and detecting drift.

## When to Use

- **cleanup skill** invokes this when checking `cross_module_architecture`, `high_level_elegance`, `abstraction_fitness`
- **spec-writer skill** invokes this when writing architecture sections or making pattern decisions
- User asks to "review architecture", "check pattern compliance", or "validate architectural decisions"
- Writing or reviewing ADRs (Architecture Decision Records)

## Workflow Decision Tree

1. **What type of review?**
   - Code audit → Start with Pattern Checklist, then deep-dive specific patterns
   - Spec writing → Use pattern selection guidance, reference examples
   - ADR validation → Check against Pattern Checklist and bounded contexts

2. **Which architecture level?**
   - System-level (services, boundaries) → See [MACRO_ARCHITECTURE.md](references/MACRO_ARCHITECTURE.md)
   - Code-level (organization, layering) → See [MICRO_ARCHITECTURE.md](references/MICRO_ARCHITECTURE.md)
   - Domain-level (bounded contexts, entities) → See [DDD_PATTERNS.md](references/DDD_PATTERNS.md)

3. **What pattern applies?**
   - See [PATTERN_CHECKLIST.md](references/PATTERN_CHECKLIST.md) for quick reference

## Review Dimensions

| Key | Checks |
|-----|--------|
| `macro_pattern` | Correct use of microservices/modular monolith |
| `micro_pattern` | Hexagonal/vertical slice compliance |
| `bounded_contexts` | DDD context boundaries clear |
| `module_boundaries` | Imports acyclic, responsibilities split |
| `adapter_isolation` | External concerns behind interfaces |
| `pattern_drift` | Code deviates from chosen architecture |

## Integration Notes

### cleanup skill
When reviewing code, use the review dimensions above. Map findings to rubric dimensions:
- `cross_module_architecture` → `bounded_contexts` + `module_boundaries`
- `high_level_elegance` → `micro_pattern` + `adapter_isolation`
- `abstraction_fitness` → `micro_pattern` compliance

### spec-writer skill
When writing architecture sections:
1. Select macro pattern (microservices vs modular monolith)
2. Define bounded contexts for the domain
3. Choose micro pattern per context (hexagonal vs vertical slices)
4. Document decisions in ADR format

## Evidence Requirements

Every finding must include:
- **File path** + symbol/line region
- **Pattern violated** (cite specific pattern rule)
- **Why** it violates (specific evidence)
- **Suggested fix** or "needs Architecture Decisions update"

## Resources

### references/
- [MACRO_ARCHITECTURE.md](references/MACRO_ARCHITECTURE.md) — System-level patterns
- [MICRO_ARCHITECTURE.md](references/MICRO_ARCHITECTURE.md) — Code organization patterns
- [DDD_PATTERNS.md](references/DDD_PATTERNS.md) — Domain-Driven Design
- [PATTERN_CHECKLIST.md](references/PATTERN_CHECKLIST.md) — Quick reference for reviewers

## Examples (Few-Shot)

**Example 1: Code audit for architecture compliance**
Input: "Review the payment module for hexagonal architecture compliance"
Output: Check domain layer has zero external dependencies, all I/O through ports, adapters implement port interfaces. Findings mapped to review dimensions.

**Example 2: Spec writing with pattern selection**
Input: "Write the architecture section for a new order management service"
Output: Select modular monolith (vs microservices), define bounded contexts, choose vertical slices per context, document in ADR format.

**Example 3: Detecting pattern drift**
Input: "The checkout feature is importing the database adapter directly"
Output: Flag as `adapter_isolation` violation. Evidence: `checkout.py` imports `SqlAlchemyAdapter`. Fix: route through outbound port interface.

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.

---
name: skillsmith
description: >-
  Guides creation and editing of AI skills following context engineering principles.
  Enforces progressive disclosure, token budgets, no-redundancy rules, and non-discoverable content only.
  Use when creating a new skill, refactoring an existing skill, or auditing skills for compliance.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for skillsmith:**
- **Tier 1 (reversible):** Missing companion file — proceed, add in next pass.
- **Tier 2 (conflict):** New skill overlaps with existing skill — **STOP**, merge or clarify boundaries.
- **Tier 3 (security):** Skill includes credentials or secrets — **STOP**, redact immediately, block and alert.

## TL;DR (Quick Start)

Pre-flight checklist and conventions for creating/editing AI skills. Ensures skills follow context engineering principles: progressive disclosure, token budgets, no redundancy, non-discoverable content only.

**When to use:** "create a new skill", "refactor skill X", "audit all skills".

**Invocation:**
```bash
# Before creating a skill
/skillsmith create <skill-name> <purpose>

# Before editing a skill
/skillsmith edit <skill-name> <change>

# Audit all skills
/skillsmith audit
```

## Decision Tree

1. **Does a skill already cover this?**
   - YES → Extend existing skill, don't create new one.
   - NO → Proceed to creation checklist.

2. **Is this project-specific or universal?**
   - Project-specific → Put in project's `./STANDARDS.md`, not `~/.skills/`.
   - Universal → Create skill in `~/.skills/`.

3. **Is this process knowledge or domain knowledge?**
   - Process (how to work) → Superpowers skill.
   - Domain (what to do) → `~/.skills/` skill.

4. **Will this skill exceed 200 lines?**
   - YES → Plan companion files for progressive disclosure.
   - NO → Single SKILL.md is sufficient.

## Workflow

### Creating a New Skill

**Pre-flight checklist:**

1. **Redundancy check** — Does another skill already cover this? Search `~/.skills/*/SKILL.md` for overlapping content.
2. **Discoverability check** — Can the agent discover this by reading the codebase? If yes, don't create a skill.
3. **Scope check** — Is this one focused responsibility, or multiple concerns? Split if multiple.
4. **Shared content check** — Does this skill need content from `shared/`? Reference, don't duplicate.

**Structure:**
```
~/.skills/<skill-name>/
├── SKILL.md              # ≤ 200 lines (ideal), ≤ 400 lines (max)
├── companion1.md         # Only if SKILL.md > 200 lines
├── companion2.md         # Only if needed
└── templates/            # Output templates (optional)
```

**SKILL.md must have:**
- YAML front matter with `name:` and `description:`
- `## TL;DR (Quick Start)` — ≤ 10 lines
- `## Assumptions & Escalation` — reference shared/ASSUMPTION_TIERS.md
- `## Decision Tree` — numbered branching logic
- `## Workflow` — core operating principles
- `## Examples (Few-Shot)` — 2+ diverse examples

**After creation:**
1. Run `./skill-validator.sh` to check structure
2. Update `skill-discovery-index.md` with the new skill
3. Create symlinks via `skill-sync` or `project-onboarding`

### Editing an Existing Skill

**Rules:**
1. **Don't embed shared content** — reference `shared/` files instead.
2. **Don't re-define another skill's concepts** — cross-reference instead.
3. **Keep SKILL.md thin** — move depth to companions.
4. **Update all consumers** — if you change a shared file, check all referencing skills.

### Auditing Skills

Run these checks:
1. **Redundancy scan** — grep for duplicated text blocks (>50 lines identical across skills)
2. **Shared file references** — check that `shared/` files are referenced by all consumers
3. **Token budget** — flag SKILL.md files over 200 lines without companion references
4. **Architecture Decisions** — flag embedded project-specific patterns that should be in `shared/`
5. **Assumption tiers** — check planning skills reference `shared/ASSUMPTION_TIERS.md`

## Quality Rules

- **Progressive disclosure:** SKILL.md < 200 lines (ideal), companions for depth
- **No redundancy:** If content appears in 2+ skills, extract to `shared/`
- **Non-discoverable only:** Every line must be information the agent cannot find by reading the repo
- **Cross-reference:** Reference other skills, don't re-define their concepts
- **Shared files:** Self-contained, project-agnostic, version-stable
- **Token budget:** TL;DR ≤ 10 lines, SKILL.md ≤ 200 lines (ideal), ≤ 400 lines (max)

## Conventions

See [`~/.skills/shared/SKILL_CONVENTIONS.md`](~/.skills/shared/SKILL_CONVENTIONS.md) for the full set of distilled context engineering principles.

## Examples (Few-Shot)

**Example 1: Creating a new skill**
Input: "Create a skill for database migration patterns"
Output: `~/.skills/db-migrations/SKILL.md` with TL;DR, decision tree, workflow, examples. Companion file `MIGRATION_PATTERNS.md` for detailed pattern catalog.

**Example 2: Refactoring a bloated skill**
Input: "spec-writer is 575 lines, too long"
Output: Extract Architecture Decisions to `shared/ARCHITECTURE_DECISIONS.md`, replace with reference. SKILL.md reduced to ~350 lines.

**Example 3: Detecting redundancy**
Input: "Both project-onboarding and skill-sync have GLOBAL_SYMLINKS.md"
Output: Extract to `shared/SYMLINK_MAP.md`, both skills reference it. Eliminates 84 lines of duplication.

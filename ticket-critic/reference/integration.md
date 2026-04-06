# Integration with Other Skills

## With spec-writer

With missing/invalid `Stage:` header, ticket-critic must block and route remediation to the **spec-writer** skill.

**Flow:**
1. User provides feature request
2. **ticket-critic runs first** → audits request for blockers
3. If cleared → spec-writer generates spec
4. If blocked → human resolves blockers, re-run critic

## With tdd

**Flow:**
1. User provides bug fix or feature
2. **ticket-critic runs first** → audits for blockers
3. If cleared → tdd starts planning
4. If blocked → human resolves blockers

## With project-onboarding

**Flow:**
1. project-onboarding checks for `~/.skills/STANDARDS.md` (now an index)
2. If exists → creates local STANDARDS.md index pointing to global skills
3. ticket-critic uses Architecture Decisions in spec-writer skill for auto-resolution

**Note:** The global `STANDARDS.md` is now a thin index (~100 lines) pointing to specialized skills. Local STANDARDS.md files should follow the same pattern.

## With cleanup (QUALITY_RUBRIC only)

The **cleanup** skill reviews **existing code**, not tickets. When **hardening ticket acceptance criteria** or mapping work to quality dimensions, read **`~/.cursor/rules/cleanup/QUALITY_RUBRIC.md`** (mechanical M1–M12, subjective tiers, anti-patterns). Use it to make AC **checkable** and aligned with layering/contracts/tests—**do not** conflate with the cleanup *workflow* (codebase audit).

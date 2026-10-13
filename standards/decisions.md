# Decision Framework

## When to Block vs. Proceed

**Proceed without blocking if:**
- Question answered in STANDARDS.md or companion files
- Assumption is Tier 1 (reversible, low impact)
- Change is behind feature flag
- Test coverage exists to catch mistakes

**Block for human clarification if:**
- Security vulnerability possible
- Architecture contradiction (conflicting tickets)
- Dependency not implemented/merged
- Success criteria undefined
- Tier 3 assumption (auth, data model, public API)

## Assumption Tiers

Tier 1 (reversible), Tier 2 (architecture) and Tier 3 (safety/security) are defined in [`../shared/ASSUMPTION_TIERS.md`](../shared/ASSUMPTION_TIERS.md). Tier 3 always blocks for human confirmation.

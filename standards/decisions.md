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

### Tier 1: Reversible (LOW impact)
- Naming conventions, file locations, UI copy
- Library choices with easy migration path
- **Action:** Proceed, flag for post-review

### Tier 2: Architecture (MEDIUM impact)
- API patterns, data model structure, layer ownership
- Harder to change but not breaking
- **Action:** Check STANDARDS.md, block if unresolved

### Tier 3: Safety/Security (HIGH impact)
- Authentication, authorization, data sensitivity
- Public API contracts, database schema
- **Action:** Always block for human confirmation

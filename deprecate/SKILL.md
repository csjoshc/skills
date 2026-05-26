---
name: deprecate
description: >-
  Plan deprecation and migration. Use when removing or replacing a feature,
  library, or API. Covers strangler/adapter/feature-flag patterns and
  zombie-code detection. Not for routine refactoring (use cleanup) or
  one-shot code removal (just edit).
---

<!-- imported from addyosmani/agent-skills deprecation-and-migration -->

# Deprecation and Migration

Code is a liability. Every line carries ongoing cost: bugs, deps, patches, onboarding overhead. Deprecation removes code that no longer earns its keep; migration moves users safely.

## When to Use

| Trigger | Note |
|---|---|
| Replacing system/API/library | Build replacement first |
| Sunsetting a feature | Quantify users |
| Consolidating duplicates | One-version rule |
| Dead code nobody owns | Zombie code |
| Lifecycle planning of new system | Plan removal at design time |

## Core Principles

| Principle | Meaning |
|---|---|
| Code is a liability | Value = functionality, not LOC |
| Hyrum's Law makes removal hard | Every observable behavior is depended on |
| Plan deprecation at design time | Ask "how would we remove this in 3 years?" |

## Decision Questions

```
1. Does it still provide unique value? → no: continue
2. How many consumers depend on it?     → quantify
3. Does a replacement exist?             → no: build it first
4. What's the migration cost per consumer?
5. What's the maintenance cost of NOT deprecating?
```

## Advisory vs Compulsory

| Type | When | Mechanism |
|---|---|---|
| Advisory | Migration optional, old system stable | Warnings + docs + nudges |
| Compulsory | Security risk, blocks progress, unsustainable | Hard deadline + migration tooling |

Default to advisory. Compulsory requires you to provide migration tooling, docs, support — not just announce a deadline.

## Migration Process

### Step 1 — Build the replacement

Must cover all critical use cases, have docs/migration guides, be production-proven (not theoretically better).

### Step 2 — Announce and document

```markdown
## Deprecation Notice: OldService
**Status:** Deprecated as of 2025-03-01
**Replacement:** NewService
**Removal date:** Advisory — no hard deadline
**Reason:** OldService requires manual scaling, lacks observability.
### Migration Guide
1. Replace `import { client } from 'old-service'` with `import { client } from 'new-service'`
2. Update configuration
3. Run `npx migrate-check`
```

### Step 3 — Migrate incrementally

One consumer at a time:

```
1. Identify all touchpoints
2. Update to replacement
3. Verify behavior matches
4. Remove old references
5. Confirm no regressions
```

**Churn Rule.** If you own infrastructure being deprecated, you migrate users — or provide backward-compat updates that need no migration.

### Step 3b — Repo-wide scrub (before Step 4)

Before you delete the thing, audit *every* place its name appears in
the long-lived tree. Code-only grep is not enough; deletions
classically leave doc/diagram/CI/manifest debris behind. Run the
substitution `NAME=<thing-being-removed>` and then:

```bash
# Markdown, RST, plain text
git grep -nE "\\b${NAME}\\b" -- '*.md' '*.rst' '*.txt'

# Diagrams (Mermaid + PlantUML + dot)
git grep -nE "\\b${NAME}\\b" -- '*.mmd' '*.puml' '*.dot' '*.drawio'

# CI / CD path filters and workflow refs
git grep -nE "\\b${NAME}\\b" -- '.github/workflows/' '.gitlab-ci.yml' '.circleci/' 'azure-pipelines.yml'

# Container / orchestration
git grep -nE "\\b${NAME}\\b" -- 'helm/' 'k8s/' 'manifests/' 'kustomize/' 'docker-compose*' 'Dockerfile*'

# Package / project manifests (substitute per stack)
git grep -nE "\\b${NAME}\\b" -- '*.toml' 'package.json' '*.csproj' 'Cargo.toml' 'go.mod' '*.c3pkg.json'

# .env examples + generated config
git grep -nE "\\b${NAME}\\b" -- '.env*' 'config/'

# Tests that test the deleted thing's existence (these become positive tests)
git grep -nE "\\b${NAME}\\b" -- 'tests/' 'test/' '__tests__/'
```

Every hit must be:

- **Removed** if the doc/filter/test described only the deleted thing.
- **Updated** if it referenced the replacement (link, name, path).
- **Inverted into a regression test** if it asserted the deleted thing's *absence* (e.g. a test that imports the deleted module and asserts `ImportError`).
- **Escalated to the user** if ambiguous — most often happens with architecture diagrams that show old + new side-by-side during a transition.

Manual diagram audit: SVG / PNG architecture diagrams won't be caught
by `git grep`. If your `docs/` tree contains image-format diagrams,
open each and look for the deleted entity. Re-render with the new
shape before Step 4.

The Step 3b scrub is what catches "the package was deleted but the
README/architecture-diagram/CI-filter still mentions it" — the same
pattern that leaves a deletion looking half-done in PR review.

### Step 4 — Remove

Only after zero active usage (verified by metrics/logs):

```
1. Verify zero usage
2. Remove code
3. Remove tests, docs, config
4. Remove deprecation notices
```

## Migration Patterns

**Strangler.** Run old + new in parallel, route traffic incrementally.

```
0% → 10% canary → 50% → 100% → remove old
```

**Adapter.** Old interface, new implementation:

```typescript
class LegacyTaskService implements OldTaskAPI {
  constructor(private newService: NewTaskService) {}
  getTask(id: number): OldTask {
    const task = this.newService.findById(String(id));
    return this.toOldFormat(task);
  }
}
```

**Feature Flag.** Switch one consumer at a time:

```typescript
function getTaskService(userId: string): TaskService {
  if (featureFlags.isEnabled('new-task-service', { userId })) {
    return new NewTaskService();
  }
  return new LegacyTaskService();
}
```

## Zombie Code

Code nobody owns but everybody depends on. Signs:

- No commits in 6+ months, active consumers exist
- No assigned maintainer
- Failing tests nobody fixes
- Vulnerable deps nobody updates
- Docs reference systems that no longer exist

Response: assign an owner OR deprecate with concrete migration plan. No limbo.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It still works, why remove it?" | Unmaintained code accumulates security debt silently. |
| "Someone might need it later" | If needed, rebuild. Keeping unused code costs more. |
| "Migration is too expensive" | Compare to 2-3 years of maintenance. |
| "We'll deprecate after we finish the new system" | Plan now, or it never happens. |
| "Users will migrate on their own" | They won't. Churn Rule applies. |
| "We can maintain both indefinitely" | Double the maintenance/testing/docs/onboarding. |

## Red Flags

- Deprecated systems with no replacement
- Announcement without migration tooling
- "Soft" deprecation advisory for years with no progress
- Zombie code with no owner
- New features added to a deprecated system
- Deprecation without measuring usage
- Removing code without verifying zero consumers

## Verification

- [ ] Replacement is production-proven
- [ ] Migration guide exists with concrete steps
- [ ] All consumers migrated (verified)
- [ ] Old code, tests, docs, config fully removed
- [ ] No references in codebase
- [ ] Deprecation notices removed

## See Also

- `api-design` — designing for future removal

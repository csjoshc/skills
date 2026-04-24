---
name: layer-boundary-critic
description: >-
  Enforces the layer cake documented in AGENTS.md — dependencies must flow
  downward only. Parses the layer list on session start and validates every
  new import in changed files. Violations emit a diff-style patch with a
  concrete fix. Use on any code change that adds or modifies imports, before
  running pr-review, and during cleanup Phase 0.
---

# layer-boundary-critic

Architectural fitness function at the import level. Dependencies must flow
downward through the documented layer cake; sideways imports require a shared
sublayer; upward imports are always a violation.

## Contents

- When to invoke
- Phase 1 — Load the layer map
- Phase 2 — Classify changed files and imports
- Phase 3 — Rule matrix
- Phase 4 — Suggest the fix
- Phase 5 — Sideways imports
- Hard rules
- Output contract

---

## When to Invoke

Invoke:

- On any `Write` or `Edit` that adds/changes an `import` / `from ... import`
  / `require(...)` / `use ...::` line
- Before running `pr-review`
- During `cleanup` Phase 0 (called by cleanup — do not re-run manually)
- When the user asks "is this in the right place?"

Skip only for:

- Test files (test imports of production code are always downward by definition)
- Generated code
- Node built-ins / stdlib imports

---

## Phase 1 — Load the Layer Map

On first invocation in a session, read `AGENTS.md` and extract the layer list.

Accepted format:

```markdown
## Layer cake (dependencies flow downward only)

1. app — user-facing UI, pages, CLI entrypoints
2. features — feature-scoped orchestration
3. services — cross-feature business logic
4. domain — pure types, invariants, policies
5. infra — I/O, HTTP clients, DB drivers, FS, time
6. util — stateless helpers, no I/O
```

Persist to `.claude/cache/layer-map.json`:

```json
{
  "layers": [
    { "name": "app", "rank": 1, "paths": ["src/app/**", "src/pages/**"] },
    { "name": "features", "rank": 2, "paths": ["src/features/**"] },
    { "name": "services", "rank": 3, "paths": ["src/services/**"] },
    { "name": "domain", "rank": 4, "paths": ["src/domain/**"] },
    { "name": "infra", "rank": 5, "paths": ["src/infra/**", "src/lib/**"] },
    { "name": "util", "rank": 6, "paths": ["src/util/**", "src/shared/**"] }
  ]
}
```

If `AGENTS.md` has no layer list, emit a warning and skip enforcement —
do not fabricate layers.

---

## Phase 2 — Classify Changed Files and Imports

```bash
IMPORTER_LAYER=$(match_layer_by_path "$file" layer-map.json)
git diff HEAD "$file" | grep -E '^\+\s*(import|from|require)'
```

For each new import, resolve the importee's file and its layer.

---

## Phase 3 — Rule Matrix

| Importer layer                                       | Importee layer | Verdict                           |
| ---------------------------------------------------- | -------------- | --------------------------------- |
| `rank(importer) < rank(importee)`                    | lower layer    | **OK** — downward                 |
| `rank(importer) == rank(importee)`, different module | same layer     | **WARN** — prefer shared sublayer |
| `rank(importer) > rank(importee)`                    | higher layer   | **BLOCK** — upward import         |

Additional blocks (from `AGENTS.md` anti-patterns):

- `infra/*` importing `domain/*` business rules → BLOCK
- `util/*` importing anything non-util → BLOCK
- `domain/*` importing I/O, HTTP, FS, time → BLOCK (domain must be pure)

---

## Phase 4 — Suggest the Fix

On **BLOCK**, emit a diff-style suggestion:

```diff
# BLOCK — upward import

File: src/infra/http/userClient.ts
Importing: src/services/userService.ts (services, rank 3) from infra (rank 5)

Reason: infra must not depend on services. Services orchestrate; infra is a leaf.

Suggested fix — dependency inversion:

1. Define the contract in domain:
   src/domain/user.ts
   +  export interface UserFetcher { fetch(id: string): Promise<User>; }

2. Have services depend on domain's interface:
   src/services/userService.ts
   -  import { fetchUser } from '../infra/http/userClient';
   +  import { UserFetcher } from '../domain/user';
   +  constructor(private users: UserFetcher) {}

3. Infra implements the domain interface:
   src/infra/http/userClient.ts
   -  import { userService } from '../../services/userService';
   +  import { UserFetcher, User } from '../../domain/user';
   +  export class HttpUserFetcher implements UserFetcher { ... }
```

---

## Phase 5 — Sideways Imports

Sideways imports within the same layer get WARN, not BLOCK:

```markdown
## SIDEWAYS IMPORT (warn)

`src/features/checkout/Cart.tsx` imports `src/features/profile/Avatar.tsx`.

Features shouldn't know about each other's internals. Options:

1. Move the shared piece to a lower layer (`domain`, `services`, or a
   new `shared/ui` package).
2. If intentional and documented, annotate the import:
   `// cross-feature: approved by <ADR-###>`
```

---

## Hard Rules

- Never weaken the layer map to allow an import. The map comes from
  `AGENTS.md`; changing it requires editing that file with an ADR.
- Never suggest `// eslint-disable` or equivalent pragma.
- Never BLOCK without a concrete fix suggestion.
- Upward imports are never OK, even "just this once."

---

## Output Contract

Exactly one of:

1. `LAYERS OK: N imports checked, 0 violations.`
2. `LAYER WARN: K sideways imports. <list>`
3. `LAYER BLOCK: J upward imports. See emitted fix suggestions.`

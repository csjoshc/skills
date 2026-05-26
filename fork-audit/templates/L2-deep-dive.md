# L2 — Deep Dive

**Repo:** `<owner/repo>` (head)
**Base:** `<upstream owner/repo>@<sha>`
**Head:** `<head ref>@<sha>`
**Audience:** engineer doing implementation review / onboarding

Walk the divergent commits in chronological order, file-group by file-group. Skip to the section you care about:

- [Commit/PR <n> — <title>](#commit-n--title-sha)
- [Commit/PR <n+1> — <title>](#commit-n1--title-sha)
- [Commit/PR <n+2> — <title>](#commit-n2--title-sha)

---

## Commit/PR <n> — <title> (`<sha>`)

**<files-changed> files, +<adds> / −<dels>. Merged <date>.**

<One-line summary of what this commit did at the user-visible level.>

> When a single squash carries multiple intents, decompose **before** writing the file table. PR bodies often self-describe ("three commits inside this squash"). Honor that decomposition.

If this is a squash with multiple logical changes, split into sub-sections:

### N.1 — <App-specific concern>

| Layer | Files | Notes |
|---|---|---|
| App skeleton | `<paths>` | <one phrase> |
| Backend HTTP | `<paths>` | <one phrase> |
| Backend services | `<paths>` | <one phrase> |
| Backend ingestion / domain | `<paths>` | <one phrase> |
| Backend models | `<paths>` | <one phrase> |
| Backend storage | `<paths>` | <one phrase> |
| Frontend skeleton | `<paths>` | <one phrase> |
| Frontend routes | `<paths>` | <one phrase> |
| Frontend components | `<paths>` | <one phrase> |
| E2E / scripts | `<paths>` | <one phrase> |
| Docs | `<paths>` | <one phrase> |

### N.2 — <Platform ride-along, if present>

These are upstream platform features that landed in the same squash but are **not app-specific**:

| Toolkit change | Files | Purpose |
|---|---|---|
| <change name> | `<paths>` | <one paragraph: what / why / signature> |
| … | … | … |

> **Architectural note.** Single-squash mixing of app + platform is unusual scoping. Call it out so reviewers can split mental models.

### N.3 — CI / workflows / containers / root

| Change | File | Notes |
|---|---|---|
| Added | `<file>` | <triggers + jobs> |
| Removed | `<file>` | <why> |
| Modified | `<file>` | <delta> |

---

## Commit/PR <n+1> — <title> (`<sha>`)

**<files-changed> files, +<adds> / −<dels>. Merged <date>.**

PR body inner decomposition (if present): <list>.

### N+1.1 — The feature

| File | Change | Key adds |
|---|---|---|
| `<path>` | +<a> / −<d> | <what this file gained — schemas, methods, branches, prompts> |
| `<path>` | +<a> / −<d> | … |

Include key code snippets where the design choice isn't obvious from the diff (e.g. a sparse-result branching rule, a retry/timeout config, an unusual schema). Otherwise the file table is enough.

```python
# Operational knobs (only include if there are tuned constants worth surfacing)
FOO_TIMEOUT_S = 8.0
FOO_MAX_RETRIES = 1
…
```

### N+1.2 — Secondary concern (if present)

Smaller change that rode along — fail-fast Makefile, formatter pass, etc. Document the bug + fix in one paragraph.

### N+1.3 — What the commit deliberately did NOT change

| Deferred | Why |
|---|---|
| <feature> | <rationale from PR body> |

---

## Commit/PR <n+2> — <title> (`<sha>`)

**<files-changed> files, +<adds> / −<dels>. Merged <date>.**

<PR body summary.>

| File | Change | Notes |
|---|---|---|
| `<path>` | +<a> / −<d> | <delta> |

### Cross-commit dependencies

Mention here if a file added in an earlier commit was only **wired** in this one (DB migrations created in PR N but the storage layer to write them lands in PR N+2, etc.). Readers need that pointer.

---

## Quick navigation

| If you're investigating… | Read |
|---|---|
| The medallion / pipeline / orchestration architecture | [topics/<novel-pattern>.md](./topics/<novel-pattern>.md) |
| The distinctive feature in detail | [topics/<distinctive-feature>.md](./topics/<distinctive-feature>.md) |
| What changed inside the shared `packages/*` | [topics/<package-diff>.md](./topics/<package-diff>.md) |
| The architect's-eye view | [L1 — Technical Overview](./L1-technical-overview.md) |
| The exec summary | [L0 — Executive Summary](./L0-executive-summary.md) |

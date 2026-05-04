# Refactor Mode

## Contents

- When to load
- Interview process
- GitHub issue template

---

## When to load

Load this file when the user's request is a **refactor**, not a feature.
Trigger words: "refactor," "clean up," "restructure," "RFC," "reorganize,"
"extract," "consolidate."

For refactoring work, replace the standard three-section spec-writer output
with the interview process below. The deliverable is a GitHub issue, not
a ticket.

---

## Interview process

Work through these steps in order. Skip a step only when genuinely not
applicable.

1. **Describe the problem** — ask for a long, detailed description of the
   pain and any candidate solutions. Don't limit the response.

2. **Verify assertions** — explore the repo to confirm their claims and
   understand the current state of the code.

3. **Alternatives** — ask whether other approaches were considered; surface
   any alternatives they may have missed.

4. **Detailed interview** — ask thorough questions about the implementation.
   Leave nothing ambiguous.

5. **Scope** — pin down exactly what will change and what won't. A refactor
   with undefined scope is a rewrite.

6. **Test coverage** — check the codebase for test coverage of the affected
   area. If insufficient, ask what their testing plan is before proceeding.

7. **Tiny commit plan** — break the implementation into the smallest possible
   commits. Each commit must leave the codebase in a working state.
   Martin Fowler: _"make each refactoring step as small as possible, so
   that you can always see the program working."_

8. **File the issue** — create a GitHub issue using the template below.

---

## GitHub issue template

```markdown
## Problem Statement

The problem from the developer's perspective.

## Solution

The proposed solution from the developer's perspective.

## Commits

A detailed implementation plan broken into the tiniest commits possible.
Each commit leaves the codebase in a working state.

## Decision Document

Implementation decisions reached during the interview. Include:
- Modules to build or modify
- Interface changes
- Technical clarifications
- Architectural decisions
- Schema changes
- API contracts

**Do NOT include specific file paths or code snippets — they become
outdated quickly.**

## Testing Decisions

- What makes a good test for this refactor (behavior, not implementation
  details)
- Which modules will be tested
- Prior art: similar tests already in the codebase

## Out of Scope

What is explicitly not part of this refactor.

## Further Notes (optional)

Any remaining context that didn't fit above.
```

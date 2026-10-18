# Scaled Audit: Subagent Delegation and Pattern Relevance

## Contents

- Delegating per-ticket audits when N > 5
- Pattern relevance by ticket surface

## Delegating per-ticket audits when N > 5

A single-context audit of 18 patterns × N tickets has context-rot
cost above ~5 tickets. For ticket sets larger than 5, delegating is
suggested (policy: `~/.skills/shared/SUBAGENTS.md`). Inline, audit in batches of about 5 with the
same verdict format. When delegating:

```
For each ticket (in parallel where possible):
  Spawn a general-purpose subagent whose prompt contains:
    - The ticket file (absolute path)
    - The relevant PATTERNS.md subset (patterns whose detection
      signals match the ticket's surface — see "Pattern
      relevance" below)
    - PRD.md and brownfield-context.md for cross-reference
    - The lint output for that ticket (run once by the parent)
    - Return contract: findings only, BLOCKER or WARN per pattern
      with ≤2-line evidence and the fix; no PASS lines.

Parent ticket-review aggregates verdicts into a single
`.plan/critic-report.md`. Subagents that return BLOCKER halt the
parent until the user resolves.
```

## Pattern relevance by ticket surface

**Pattern relevance** — not every ticket needs every pattern. The
parent ticket-review picks the relevant subset per ticket based on
declared `Files:`:

| Ticket surface | Always-relevant patterns | Conditionally relevant |
|---|---|---|
| Code-only | 1–10, 15, 16, 18 | — |
| Dockerfile / image | 1–10, 11, 12, 14, 15, 16, 18 | 13 if NetworkPolicy |
| helm / k8s | 1–10, 11–14, 15, 16, 18 | — |
| Makefile / wrapper script | 1–10, 15, 16, 17, 18 | 11, 12 if image touched |
| Compose | 1–10, 15, 16, 17, 18 | — |
| CI workflow | 1–10, 15, 16, 18 | 11, 23 if publishes images |
| Docs only | 1–7, 15 | — |
| Integration gate | 1–10, 15, 16, 17, 18 | full container set if Docker invoked |

The parent ticket-review includes the relevance table in the
subagent's brief so each subagent has tight scope.

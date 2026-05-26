# Topic: <Name>

**Where it lives:** `<path glob in the repo>`.
**Introduced in:** Commit/PR #<n> (`<sha>`, `<date>`) [— and refined in PR #<m> if applicable].
**Why it exists:** <one paragraph stating the design driver — what constraint or opportunity forced this design choice; what the obvious alternative would have been and why it was rejected>.

---

## Diagram

See [<diagram-name>](../diagrams/<diagram-name>.svg) for the visualization (or describe inline if no diagram).

---

## Anatomy

<Table mapping the concept to concrete files / tables / functions. Use the language the codebase uses, not invented terms.>

| Element | Files / Tables | Role |
|---|---|---|
| <name> | `<path>` | <one phrase> |
| <name> | `<path>` | <one phrase> |

---

## Detailed behavior

<For each major subcomponent, one short section. Keep prose minimal — favor tables + code snippets.>

### <Subcomponent>

| Column | Type | Description |
|---|---|---|
| <col> | <type> | <one phrase> |

```python
# Include a code snippet only if the design choice isn't obvious from the schema or table
```

### <Subcomponent>

…

---

## Operational notes

| Concern | Detail |
|---|---|
| Throughput | <numbers, or "METRICS NEEDED"> |
| Concurrency | <coordination posture — in-process vs distributed> |
| Storage caps / limits | <bounds> |
| Recoverability | <idempotency, cascade-deletes, etc.> |
| Re-running a single stage | <CLI / make target if it exists> |

---

## Why this pattern was chosen

<2–4 sentences. Quote the design spec or PR body if one exists. If not, infer the reason from the constraints visible in the code (e.g. "USPTO surfaces split bulk vs per-patent — no single API gives both").>

---

## Risk surface

- **<risk 1>** — <one phrase mitigation in place> · <follow-up>
- **<risk 2>** — …

---

## See also

- [L2 — <relevant PR section>](../L2-deep-dive.md#<anchor>)
- [L1 — <relevant slide>](../L1-technical-overview.md#<anchor>)
- `<in-repo canonical doc>` — DEVGUIDE.md / README.md if one exists

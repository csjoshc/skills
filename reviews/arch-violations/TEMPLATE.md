# <section name>

> Template for every file in `arch-violations/`. Copy verbatim, fill the
> slots, delete this blockquote. Keep under ~200 lines.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (N)

Prioritize the 3–5 most *compounding* violations in this category. Each
smell follows the same four-line shape:

### <violation name>

**Shape (language-agnostic):** 1–2 sentences describing the architectural
relationship, not the token pattern. No Python/TS/Java syntax.

**Decidable at:** `design` | `diff` | `both`

**Why it compounds:** One sentence on what gets worse if unfixed.

**Category mapping:** `<REVIEW-FINDINGS category>` / typical severity
`<LOW|MEDIUM|HIGH|CRITICAL>` / `rule_code: <stable-identifier>`

---

## Proof recipes

What counts as reproducible evidence for each smell.

| Smell | Proof recipe |
| --- | --- |
| <smell-1> | Command, graph query, log pattern, or failing-test type that demonstrates it |
| <smell-2> | ... |

Rules:
- Prose alone is never proof.
- Prefer commands a reviewer can run (`madge --circular`, `rg "..."`, etc.)
  over references to manual inspection.
- For CRITICAL findings, proof must be a concrete reproduction path.

---

## Few-shot: good finding

A populated `REVIEW-FINDINGS` block that would pass `reviews/validate.py`.
Every required field present; `proof:` populated; realistic content.

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: <category>
  lens: <lens-name>
  file: <realistic/path.ext>
  line: <integer>
  rule_code: <stable-identifier>
  severity: <severity>
  source: <source-tag>
  decidable_at: <design|diff|both>
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    <quoted code or concrete relationship>
  proof: |
    <reproducible command / test / log excerpt>
  suggested_fix: |
    <concrete remediation>
```
````

---

## Few-shot: good dismissal

Describe a concrete situation where code *looks like* this smell but is
actually fine. Prevents false positives on similar-shaped code. Include:

- What a reviewer would first see.
- Why it's benign (the invariant or context that makes it safe).
- What makes it different from the real smell above.

---

## Decidable-at matrix

Which skill/stage catches each smell in this file.

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| <smell-1> | ✅ / ❌ / partial | ✅ / ❌ | ✅ / ❌ |
| <smell-2> | ... | ... | ... |

Legend:
- ✅ — should catch
- ❌ — out of scope
- partial — catches only if linked context is available (e.g., plan file)

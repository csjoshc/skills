# Generator prompt — populate arch-violations stub files

Paste this prompt into a fresh session along with the section of the
11-point violation catalog you want to populate. Run once per stub file
(or once for all 10 if you trust the session to hold consistent shape).

---

```
I'm extending the `pr-review` and `cleanup` skills in ~/.skills with a
catalog of architecturally relevant violations. The goal is generalizable,
language-agnostic few-shot examples that raise finding quality for a
reviewing LLM — not a lint rulebook.

Context files to read first (READ-ONLY):
- ~/.skills/reviews/schemas.md                  (REVIEW-FINDINGS block shape, severity, source tags)
- ~/.skills/reviews/runbook.md                  (phase sequence)
- ~/.skills/reviews/arch-violations/README.md   (index + decidable-at legend)
- ~/.skills/reviews/arch-violations/TEMPLATE.md (per-file shape to copy)
- ~/.skills/reviews/arch-violations/01-dependency-direction.md
                                                (fully worked exemplar — MATCH this quality)
- ~/.skills/pr-review/reference/review-lenses.md (lens checklists)
- ~/.skills/shared/QUALITY_RUBRIC.md             (M1–M12, Tiers A–I)

Task: overwrite the target stub file <arch-violations/NN-name.md> with a
fully populated version following TEMPLATE.md exactly.

Rules (every rule matters — do not relax any):

  1. LANGUAGE-AGNOSTIC. Every "shape" description must describe an
     architectural relationship, not a token pattern. No Python, TypeScript,
     Java, Go, or Rust syntax anywhere in the shape sentence.

  2. REPRODUCIBLE PROOF. Every proof recipe must cite a command, graph
     query, log pattern, or failing-test type a reviewer can actually run.
     Prose alone is not proof. For CRITICAL findings, proof must be a
     concrete reproduction path.

  3. YAML THAT PASSES THE VALIDATOR. Every few-shot REVIEW-FINDINGS block
     must be valid against ~/.skills/reviews/schemas.md and pass
     ~/.skills/reviews/validate.py. Include `proof:` when severity is
     CRITICAL. Include `decidable_at:` on every row.

  4. GOOD DISMISSAL IS MANDATORY. Describe a concrete situation where the
     smell-shape appears but is benign. Without this, reviewers
     false-positive on similar-looking code.

  5. SEVERITY DISCIPLINE.
     - LOW    = style / nit
     - MEDIUM = maintainability
     - HIGH   = reliability
     - CRITICAL = security / data loss / production outage risk
     Most architectural smells are HIGH or MEDIUM. Reserve CRITICAL.

  6. PRIORITIZE COMPOUNDING VIOLATIONS. If the catalog section has many
     smells, keep only the 3–5 most compounding ones. Exhaustiveness is
     anti-goal — few-shot quality degrades with quantity.

  7. FILE UNDER 200 LINES. Trim prose if you approach the cap.

  8. FILL THE DECIDABLE-AT MATRIX HONESTLY.
     - `design` means /antiplan Phase 2 should catch it.
     - `diff`   means only visible in code.
     - `both`   means /antiplan sets policy, pr-review/cleanup enforces.

After writing, verify the embedded REVIEW-FINDINGS block parses:

    python3 ~/.skills/reviews/validate.py --transcript <target-file>.md

The few-shot YAML inside the file must itself validate. Fix and retry
until it does.

Target stub: <arch-violations/NN-name.md>

Catalog section to work from:

[PASTE THE SECTION OF THE 11-POINT CATALOG HERE]
```

---

## Variant: generate all 10 stubs in one session

Higher drift risk; lower wall-clock. Use when you want consistent voice
across files and are willing to review each for schema compliance after:

```
Same rules as above. Target: populate arch-violations/02-*.md through
11-*.md using the full 11-point catalog below. After generating each
file, run the validator against it. Do not move on until the previous
file passes. Stop and report if any file fails after two retries.

[PASTE FULL 11-POINT CATALOG HERE]
```

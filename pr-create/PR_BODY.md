# PR Body Template (Phase 4)

Section shape adapted from Matt Pocock's `pr` skill (MIT).

## Contents

- PR creation
- Writing each section
- Editing PR body after creation (for attaching evidence)

## PR creation

````bash
gh pr create --title "<type>(<scope>): <summary>" --body "$(cat <<'EOF'
## Summary

<why and the actual behavioral delta; add a small visual only when it clarifies relationships or sequencing>

## Evidence

- **Before:** <screenshot, output, or the failing test run>
  **After:** <screenshot, output, or the passing test run>

### Test Results
```
<paste from /tmp/test-results.txt>
```

### Coverage
```
<paste from /tmp/coverage.txt>
```

## Merge Danger

**Door:** <one-way or two-way>

<optional: why, and how to walk it back>

**Blast Radius:** <one word, e.g. none, layout, consumers, data>

<optional: what could break and for whom>

## Not Doing

- <what was left out on purpose, and why>

## Test Plan

- [ ] <specific thing for the reviewer to verify>

EOF
)"
````

## Writing each section

Skip preambles and keep prose brief.
Use the repo's domain terms from `GLOSSARY.md` when it has one.
Present the author's updated account under the [shared contract](../shared/QUALITY_RUBRIC.md#change-quality-pass), using the existing sections below.
Do not add a second checklist or repeat the original prompt.

### Summary

Apply the contract's Mental map guidance; if a visual helps, pick the smallest useful view and place it next to the point it supports.
- Logic or an algorithm: pseudocode.
- Runtime control flow: a call tree (`submitForm` > `createSession` > `persistPrompt`).
- UI structure: a component tree with the state and module boundaries that matter.
- File responsibility or a broad refactor: a shallow file tree with a short comment per entry.
- Interaction or data flow between parts: a Mermaid sequence or flowchart.
- What changes inside a shape that already exists: a `diff` block of that tree, call stack or state flow, with `+` and `-` lines.
- Most of the block is new, or the reader needs a copyable target: show the whole block.

Keep only the calls, files, props and states needed to make the point.
One visual is usually enough; use more only when each answers a different question.

### Evidence

Show a before and an after.
Screenshots are the strongest evidence when the change is visual and the environment can take them ([EVIDENCE_UI.md](EVIDENCE_UI.md)).
Execution evidence comes next: name the relevant checks and before/after outcomes under the contract's Evidence obligation, with runner output ([EVIDENCE_BACKEND.md](EVIDENCE_BACKEND.md)).
Test Results and Coverage hold the pasted logs from `/tmp/`; drop either sub-section only when there is nothing to paste and say why.
A bug fix with no correct test seam states that here, as the finding (see verify's regression test rule).

### Merge Danger

A two-way door can be walked back cheaply, for example a revert or a flag flip.
A one-way door cannot: destructive migrations, deleted data, published APIs, or anything a consumer will build on before you notice.
Blast radius is the scope of what could break if the change is wrong: layout shift, consumer breakage, mobile layout, data, other services.
Consider every path, not just the one you tested.
A production-bound PR also carries the rollback plan from [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) here.

## Editing PR body after creation (for attaching evidence)

If you need to create the PR first then add evidence:

```bash
# Create PR first
gh pr create --title "..." --body "## Summary\n\n..."

# Collect evidence...

# Then update the body
gh pr edit <PR_NUMBER> --body "$(cat <<'EOF'
<full updated body with evidence>
EOF
)"
```

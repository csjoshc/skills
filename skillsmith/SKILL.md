---
name: skillsmith
description: "Audits, creates and refactors skills against ~/.skills conventions. Use when creating a skill, reviewing skill quality, or fixing a non-compliant SKILL.md."
---

# Skillsmith

Skillsmith is the enforcement skill for `~/.skills` quality.
It converts principle-level guidance into concrete checks and repeatable remediation steps.
Apply it to requests that create or edit a skill; leave other files to their own conventions.

## Quick Start

1. Run the audit:
```bash
python3 ~/.skills/skillsmith/scripts/skill_audit.py ~/.skills
```

2. Fix all `FAIL` items first.

Evals: optional; the audit does not warn when they are missing. A skill can have `evals/evals.json` (format in `reference/evals.md`). Run one with `python3 ~/.skills/skillsmith/scripts/run_evals.py <skill>`. It costs tokens, so run it by hand.

3. Resolve `WARN` items when they affect discovery, clarity, or token hygiene.
4. Re-run the audit and include a short compliance report.

Use the report template: [templates/compliance-report.md](templates/compliance-report.md)

## Companion References

- Rules (frontmatter, invocation, structure, writing): [../shared/SKILL_CONVENTIONS.md](../shared/SKILL_CONVENTIONS.md)
- Why the rules hold (two loads, information hierarchy, pruning): [reference/context-hygiene.md](reference/context-hygiene.md)
- Specialized review rules: [reference/specialized-review.md](reference/specialized-review.md)

## Workflow

### Step 1: Baseline extraction

Load only the reference the current fix needs:

- Metadata, invocation or structure issue -> `SKILL_CONVENTIONS.md`
- Bloat or stale context issue -> context-hygiene reference
- Review quality issue -> specialized-review reference

Done when you can name the rule each planned change enforces.

### Step 2: Mechanical validation

Run the audit script and capture failures by file.
Done when every `FAIL` and `WARN` is listed against its file.

### Step 3: Branching refactor

A branch is a distinct case the skill handles, so different runs take different paths through it.
Inline what every branch needs, and put behind a pointer what only some branches reach.

1. Keep in SKILL.md the steps, decision logic and hard constraints every run uses.
2. Move material only some branches reach (long examples, templates, mode-specific checklists) to a companion file.
3. Link each companion directly from SKILL.md, worded with the condition for reaching it.

Done when every section of SKILL.md is used on every branch, or is a one-line pointer.

### Step 4: Workflow ergonomics (multi-stage skills only)

For a skill that routes or runs work across multiple stages, make one run contract easy to find:

1. **Entry:** give the workflow one obvious invocation. Add modes only when they change who advances the stages; keep the choice explicit and small.
2. **Happy path:** show the normal stage order once. Auto mode advances and re-detects durable state after each stage; Manual mode names the next action and gives a paste-ready prompt.
3. **Escalation:** name the conditions that require a person. At a pause, show the evidence, ask one focused question or action, and say how execution resumes.
4. **Authority:** state the workflow's write, commit, publish, and external-action boundaries. Do not infer broad authority from an Auto label.
5. **Recovery:** define how the workflow recognizes an interrupted stage from durable artifacts and resumes without repeating completed work.

Keep routing in the entry skill and branch-specific procedures in linked references. Do not add an orchestration layer to a single-stage skill.

Done when a reader can identify the entry point, normal path, pause conditions, permitted side effects, and resume point without reconciling contradictory instructions.

### Step 5: Writing lenses

Read the body sentence by sentence through three lenses:

1. **No-op hunt**: delete each sentence the model already obeys by default. Delete the whole sentence, not words from it.
2. **Negation**: rewrite each prohibition as the target behaviour. Keep a "don't" only as a hard guardrail, paired with its positive.
3. **Completion criterion**: give every step a checkable condition that tells the agent it is done.

Done when every sentence passes all three lenses.

### Step 6: Review-skill hardening (review, audit and critique skills only)

Enforce:

1. Deterministic checks before LLM review.
2. Specialist lens vocabulary and named anti-patterns.
3. Evidence requirements for each finding.
4. Role separation between generator and reviewer.

Done when each of the four is present in the skill's steps.

### Step 7: Stop-slop and caveman integration (prose-producing skills only)

For skills that generate prose output (specs, PRDs, docs, briefs, handoffs):
- **stop-slop** is mandatory in the skill's Quality Rules or final step: call the Skill tool with `stop-slop` on all prose output.
- **caveman** is selective: use it only when the skill's output is long agent prose (500+ lines), or the skill's own instructions are verbose enough that token cost matters.

Done when every prose-producing skill ends on a stop-slop call.

### Step 8: Verify and report

Re-run the audit on every amended skill, including amendments to an existing one.
Done when:

1. The audit shows no new `FAIL`, and SKILL.md stays under 500 lines; overflow moves to a companion behind a one-line pointer.
2. New rule codes (`AP-NN`, `DC-NN`, `Pattern N`) are counted in `~/.skills/shared/SKILL_NOISE_TERMS.md`.
3. New prose has passed stop-slop.
4. If a file under `~/.skills/shared/` changed, every skill that points at it (`grep -rl '<shared-file>' ~/.skills`) still matches its own scope.
5. The report lists scope audited, rules enforced, files changed, and remaining risk or deferred warnings.

## Hard Constraints

- Every SKILL.md starts with frontmatter.
- SKILL.md bodies stay under 500 lines.
- Descriptions are written in the third person.
- Required instructions sit in SKILL.md or one link away from it.
- Canonical files carry only current guidance; superseded and contradictory rules are deleted.

## Example Use Cases

- "Review all skills and bring them into compliance"
- "This SKILL.md is too long; split it without losing behavior"
- "Make our review skill follow specialist-review principles"

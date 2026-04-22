---
name: skillsmith
description: Audits, creates, and refactors skills to meet context hygiene, specialized review, and Claude skill authoring standards. Use when creating a new skill, reviewing skill quality, or remediating non-compliant SKILL.md and companion files.
---

# Skillsmith

Skillsmith is the enforcement skill for `~/.skills` quality.
It converts principle-level guidance into concrete checks and repeatable remediation steps.

## Quick Start

1. Run the audit:
```bash
python3 /Users/joshchiu/.skills/skillsmith/scripts/skill_audit.py /Users/joshchiu/.skills
```

2. Fix all `FAIL` items first.
3. Resolve `WARN` items when they affect discovery, clarity, or token hygiene.
4. Re-run the audit and include a short compliance report.

Use the report template: [templates/compliance-report.md](templates/compliance-report.md)

## Companion References

- Context hygiene rules: [reference/context-hygiene.md](reference/context-hygiene.md)
- Specialized review rules: [reference/specialized-review.md](reference/specialized-review.md)
- Claude best-practice requirements: [reference/claude-skill-best-practices.md](reference/claude-skill-best-practices.md)

## Decision Tree

1. Is the request about creating or editing a skill?
- Yes -> Apply this workflow.
- No -> Do not force skill restructuring.

2. Is the target SKILL.md over 500 lines?
- Yes -> Split into companion files before content expansion.
- No -> Keep SKILL.md concise and route depth to companions.

3. Is the skill a review/audit skill?
- Yes -> Enforce specialist lenses, deterministic checks first, and evidence-backed findings.
- No -> Skip review-only constraints.

## Workflow

### Step 1: Baseline extraction

Load only the reference needed for the current fix:

- Metadata or structure issue -> Claude best-practices reference
- Bloat or stale context issue -> context-hygiene reference
- Review quality issue -> specialized-review reference

### Step 2: Mechanical validation

Run the audit script and capture failures by file.

### Step 3: Progressive-disclosure refactor

When needed:

1. Keep SKILL.md as routing, decision logic, and constraints.
2. Move large examples/templates/checklists to companion docs.
3. Link companions directly from SKILL.md (one level deep).
4. Add `## Contents` to long companion files.

### Step 4: Review-skill hardening (conditional)

For review skills, enforce:

1. Deterministic checks before LLM review.
2. Specialist lens vocabulary and named anti-patterns.
3. Evidence requirements for each finding.
4. Role separation between generator and reviewer.

### Step 5: Stop-slop and caveman integration (conditional)

For skills that generate prose output (specs, PRDs, docs, briefs, handoffs, reframes):
- **stop-slop** should be mandatory in the skill's Quality Rules or final step — invoke `/stop-slop` on all prose output to remove AI writing patterns.
- **caveman** is NOT for all skills. Use only when: (1) the skill's output is long agent prose (500+ lines) that needs token compression, OR (2) the skill's instructions themselves are verbose and token optimization matters.

**Guidance**: Stop-slop is a quality gate (all prose skills); caveman is a token optimization tool (selective, for specific compression contexts).

### Step 6: Verify and report

Re-run audit until no failures remain.
Return a concise report with:

- Scope audited
- Rules enforced
- Files changed
- Remaining risk or deferred warnings

## Hard Constraints

- Do not leave SKILL.md without frontmatter.
- Do not exceed 500 SKILL.md body lines.
- Do not use second-person or first-person descriptions in frontmatter.
- Do not hide required instructions behind nested companion links.
- Do not keep stale or contradictory guidance that can poison context.

## Example Use Cases

- "Review all skills and bring them into compliance"
- "This SKILL.md is too long; split it without losing behavior"
- "Make our review skill follow specialist-review principles"


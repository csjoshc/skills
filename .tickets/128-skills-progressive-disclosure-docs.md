---
Title: Expand Progressive Disclosure Patterns to All Skills
Stage: BUILD
Type: Documentation + Infrastructure
Effort: Medium
---

## Summary

Extend the [progressive disclosure patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) from Claude's documentation to all 23 skills in `~/.skills/`. Currently, only a subset of skills use structured disclosure levels (e.g., `handoff`, `spec-writer`, `pr-fix`). This ticket ensures every skill follows a consistent pattern for revealing complexity based on user intent.

**Additional improvements from best practices:**
- Few-shot examples for output style
- Reference file organization (one-level deep, domain-specific)
- Structured output templates
- Decision trees with degrees of freedom
- Escalation/feedback loops
- Naming conventions
- Evaluation harness for skill quality

## Problem

Skills vary widely in structure and disclosure depth:

| Skill | Current State |
|-------|---------------|
| `handoff` | ✅ Has clear sections: "What to summarize", "Plan file (conditional)", templates |
| `spec-writer` | ✅ Three-section structure (SPEC/PLAN/TASKS), assumption flagging, PDCA-T alignment |
| `pr-fix` | ✅ Step-by-step workflow with fix-verify cycles, safety rules |
| `pr-review` | ✅ Parallel agent workflow with checklists, validation gates |
| `cleanup` | ⚠️ References external rubric, minimal workflow detail |
| `cmd-cli` | ⚠️ Tool reference table only, no workflow |
| `confluence-diagrams` | ✅ Detailed workflow but no progressive structure |
| `create-pr` | ✅ Four-phase workflow with conditional paths |
| `make-ui` | ⚠️ Two modes defined but consultation flow abbreviated |
| `mcp-sync` | ⚠️ Workflows listed but no disclosure levels |
| `orchestrate` | ✅ State machine well-defined, but no tiered guidance |
| `project-onboarding` | ✅ Step-by-step but dense, no quick-start path |
| `run-ticket` | ✅ Interactive prompts documented, but no escalation path |
| `tdd` | ✅ Workflow exists but anti-patterns buried |
| `test-ui` | ⚠️ Two approaches but no decision tree |
| `ticket-critic` | ⚠️ 10 patterns listed but no quick-reference summary |
| `write-prd` | ⚠️ Pipeline stages documented but HITL flow separate |
| `chrome-devtools` | ⚠️ Tool list + examples, no workflow tiers |
| `codex` | ✅ Config fixed, no skill doc yet |
| `skill-sync` | ⚠️ Script exists, no progressive doc |
| `spec-writer` | ✅ Comprehensive (gold standard) |
| `tdd` | ✅ Solid workflow |
| `write-prd` | ⚠️ Role distinction clear, HITL detailed |

**Gaps:**
1. No consistent "Quick Start" vs "Deep Dive" separation
2. Assumption flagging only in `spec-writer`
3. Decision trees missing from most skills
4. No "When to Escalate" guidance (when to involve human vs proceed)
5. Risk-tier assumptions only in `spec-writer` and `ticket-critic`

## Goals

### Core Structure
1. **Standardize skill structure** across all 23 skills using progressive disclosure
2. **Add quick-reference summaries** for time-pressed users (TL;DR under 10 lines)
3. **Make assumption flagging explicit** in all planning/spec skills with `[ASSUMPTION: ...]`
4. **Add decision trees** for skills with multiple modes/paths
5. **Document escalation thresholds** (when to block for human input vs proceed)

### Best Practices Integration
6. **Few-shot examples** — Add 2-3 input/output pairs per skill showing expected output style
7. **Reference file organization** — Split large skills into domain-specific reference files (one-level deep)
8. **Structured output templates** — YAML frontmatter, checklists, copyable templates
9. **Degrees of freedom guidance** — Match instruction specificity to task fragility
10. **Validation scripts** — Add skill-validator tool for automated structure compliance
11. **Naming conventions** — Standardize on gerund form (`processing-x`, `analyzing-y`)
12. **Evaluation harness** — Create 3+ test scenarios per skill for quality baseline

## Non-Goals

- Rewriting skill functionality — only documentation structure
- Adding new skills
- Changing skill invocation patterns
- Modifying Claude's platform documentation

## Success Criteria

### Functional
- [ ] All 23 skills have consistent top-level structure
- [ ] Each skill has a "Quick Start" or "TL;DR" section (≤10 lines)
- [ ] Planning/spec skills (`spec-writer`, `handoff`, `write-prd`, `ticket-critic`) use `[ASSUMPTION: ...]` flagging
- [ ] Skills with multiple modes have decision trees (e.g., `make-ui`, `test-ui`, `run-ticket`)
- [ ] All skills document "When to Block" thresholds
- [ ] Each skill has 2-3 few-shot input/output examples
- [ ] Reference files are one-level deep (no nested references)
- [ ] All skills with >100 lines have table of contents
- [ ] File paths use forward slashes only (no Windows backslashes)
- [ ] Skill names use gerund form consistently (`processing-x`, not `process-x`)

### Quality
- [ ] No skill exceeds 500 lines without subsections or reference file splits
- [ ] All workflows use numbered steps with verification gates
- [ ] Cross-references between skills use absolute paths
- [ ] Examples are copy-paste runnable where applicable
- [ ] All configuration values have justification comments (no magic numbers)
- [ ] Consistent terminology throughout (no mixing "API endpoint"/"URL"/"route")
- [ ] Third-person descriptions ("Processes files" not "I can help you process files")

### Verification
```bash
# Count lines per skill — flag any >500 without subsections
wc -l ~/.skills/*/SKILL.md | sort -n

# Check for assumption flagging in planning skills
rg "\[ASSUMPTION:" ~/.skills/{spec-writer,handoff,write-prd,ticket-critic}/SKILL.md

# Check for few-shot examples (look for "Example" or "Input/Output")
for dir in ~/.skills/*/; do
  count=$(grep -c "Example\|Input:\|Output:" "$dir/SKILL.md" 2>/dev/null || echo 0)
  if [ "$count" -lt 2 ]; then
    echo "Missing examples: $(basename $dir) ($count found)"
  fi
done

# Find skills without decision trees
for dir in ~/.skills/*/; do
  if ! grep -q "Decision\|when to use\|if.*then" "$dir/SKILL.md" 2>/dev/null; then
    echo "Missing decision tree: $(basename $dir)"
  fi
done

# Check for Windows backslashes in paths
rg '\\\\' ~/.skills/*/SKILL.md

# Check for magic numbers (unjustified constants)
rg '[A-Z_]+ = [0-9]+' ~/.skills/*/SKILL.md | grep -v "// " | grep -v "# "
```

## Implementation Approach

### Phase 1: Define Standard Structure (Task 1-3)

Create templates in `~/.skills/templates/`:

**1. `skill-structure.md`** — Main template:
```markdown
---
name: <skill-name>
description: <one-liner, third-person>
---

# <Skill Name>

## TL;DR (Quick Start)
<5-10 lines: when to use, how to invoke, what you get>

## When to Use
- Trigger phrase 1
- Trigger phrase 2
- NOT for X (use Y skill instead)

## Invocation
```bash
<command examples>
```

## Decision Tree (if applicable)
<flowchart or numbered decisions with degrees of freedom>
- High freedom: multiple approaches valid (text instructions)
- Medium freedom: preferred pattern exists (pseudocode/templates)
- Low freedom: consistency critical (specific scripts)

## Workflow
### Step 1: ...
### Step 2: ...

## Assumptions & Escalation
- Tier 1 (reversible): proceed, flag for post-review
- Tier 2 (architecture): check STANDARDS.md, block if unresolved
- Tier 3 (security/safety): always block

## Examples (Few-Shot)
**Example 1:**
Input: <example input>
Output: <expected output style>

**Example 2:**
...

## Related Skills
| Skill | When to use instead |
|-------|---------------------|
| ... | ... |
```

**2. `reference-file-pattern.md`** — For skills needing >500 lines:
- One-level deep references only (`SKILL.md → forms.md`, not `SKILL.md → forms.md → validation.md`)
- Domain-specific splits (`finance.md`, `sales.md`)
- TOC for files >100 lines
- Descriptive names (`form-validation-rules.md`, not `doc2.md`)

**3. `evaluation-template.md`** — Test scenarios per skill:
- 3+ test scenarios minimum
- Baseline behavior without skill
- Expected behavior with skill
- Edge cases and error handling

### Phase 2: Audit & Categorize (Task 4-6)

Categorize skills by complexity:

| Tier | Skills | Treatment |
|------|--------|-----------|
| **Simple** (reference only) | `cmd-cli`, `cleanup`, `chrome-devtools` | Add TL;DR + examples |
| **Medium** (workflow) | `create-pr`, `pr-fix`, `test-ui`, `mcp-sync`, `skill-sync` | Add decision tree + escalation |
| **Complex** (planning/spec) | `spec-writer`, `handoff`, `write-prd`, `ticket-critic`, `orchestrate`, `project-onboarding`, `run-ticket`, `make-ui`, `pr-review`, `tdd` | Full progressive disclosure + assumption flagging |

### Phase 3: Incremental Updates (Task 7-20)

Update skills in batches of 3-5, testing readability after each:

1. **Batch 1 (Simple):** `cmd-cli`, `cleanup`, `chrome-devtools`
2. **Batch 2 (Simple):** `confluence-diagrams`, `skill-sync`
3. **Batch 3 (Medium):** `create-pr`, `test-ui`, `mcp-sync`
4. **Batch 4 (Medium):** `pr-fix`, `make-ui`, `pr-review`
5. **Batch 5 (Complex):** `handoff`, `ticket-critic`, `write-prd`
6. **Batch 6 (Complex):** `spec-writer` (already good — validate template), `orchestrate`, `project-onboarding`, `run-ticket`, `tdd`

### Phase 4: Create Validation Infrastructure (Task 21-23)

1. **`skill-validator.sh`** — Automated structure compliance checker:
   - Line count validation (flag >500 without subsections)
   - Forward slash path check
   - Few-shot example count
   - Decision tree presence
   - Magic number detection
   - Terminology consistency

2. **`evaluation-harness/`** — Test scenarios per skill:
   - Run skill with sample input
   - Compare output against expected pattern
   - Score: structure compliance, example quality, clarity

3. **`skill-discovery-index.md`** — Use case → skill mapping table

4. **Git hook integration:**
   - Install `skill-validator.sh` as `.git/hooks/pre-commit` in `~/.skills`
   - Blocks commits that fail validation
   - Provides specific error messages for each failure
   - Can be bypassed with `--no-verify` for emergency commits

### Phase 5: Validation & Polish (Task 24-26)

1. Read all 23 skills end-to-end for consistency
2. Cross-reference check: verify all inter-skill links work
3. Test decision trees: walk through 2-3 paths per skill
4. Run skill-validator on all skills, fix any failures
5. Run evaluation harness with 3+ test scenarios per skill

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-standardization | Skills lose unique voice | Template is guidance, not straitjacket |
| Bloat | Skills exceed 500 lines | Enforce subsections, extract to reference files |
| Broken cross-references | Links to other skills break | Validation task includes link audit |
| Assumption flagging feels verbose | Slows down simple tasks | Only required for Tier 2/3 decisions |
| Examples become outdated | Misleading output expectations | Add "last verified" date, review quarterly |

## Open Questions

1. **Decision tree format:** Mermaid diagrams vs text? (Trade-off: visual vs plain text portability)
2. **Skill discovery UI:** Static markdown table or interactive tool?
3. **Evaluation automation:** Run evaluations in CI or manual only?

## Related Files

- `~/.skills/STANDARDS.md` — Global standards (assumption tier definitions)
- `~/.skills/templates/` — Template directory (to be created)
- `~/.skills/*/SKILL.md` — All 23 skill files
- `~/.skills/evaluation-harness/` — Test scenarios (to be created)
- `~/.skills/skill-validator.sh` — Validation script (to be created)
- `~/.skills/.git/hooks/pre-commit` — Git hook integration (to be installed)

## Verification Commands

```bash
# Count lines per skill — flag any >500 without subsections
wc -l ~/.skills/*/SKILL.md | sort -n

# Check for assumption flagging in planning skills
rg "\[ASSUMPTION:" ~/.skills/{spec-writer,handoff,write-prd,ticket-critic}/SKILL.md

# Check for few-shot examples (look for "Example" or "Input/Output")
for dir in ~/.skills/*/; do
  count=$(grep -c "Example\|Input:\|Output:" "$dir/SKILL.md" 2>/dev/null || echo 0)
  if [ "$count" -lt 2 ]; then
    echo "Missing examples: $(basename $dir) ($count found)"
  fi
done

# Find skills without decision trees
for dir in ~/.skills/*/; do
  if ! grep -q "Decision\|when to use\|if.*then" "$dir/SKILL.md" 2>/dev/null; then
    echo "Missing decision tree: $(basename $dir)"
  fi
done

# Check for Windows backslashes in paths
rg '\\\\' ~/.skills/*/SKILL.md

# Check for magic numbers (unjustified constants)
rg '[A-Z_]+ = [0-9]+' ~/.skills/*/SKILL.md | grep -v "// " | grep -v "# "

# Check for consistent terminology (no mixing terms)
# Example: check for mixed "API endpoint"/"URL"/"route"
for term in "endpoint" "URL" "route" "path"; do
  echo "=== $term ==="
  rg "$term" ~/.skills/*/SKILL.md | head -5
done

# Check for third-person descriptions (flag first-person "I can", "I will")
rg "\bI (can|will|help)\b" ~/.skills/*/SKILL.md
```

---

**Handoff Notes:**
- This is a **documentation restructuring** ticket, not a functional change
- Follow the batch approach — do not update all 23 skills in one context
- After each batch, run the verification commands to catch drift
- Use `spec-writer` skill if you need to create sub-tickets for large batches
- Validation scripts (`skill-validator.sh`, `evaluation-harness/`) are infrastructure deliverables
- Git hook (`~/.skills/.git/hooks/pre-commit`) auto-validates on commit — can bypass with `--no-verify`

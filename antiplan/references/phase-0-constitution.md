# Phase 0: Constitution & Context

Loaded when entering Phase 0. Establishes non-negotiable principles and the
existing-code baseline before any feature discussion begins.

---

## Purpose

Phase 0 is the only phase that runs on every antiplan invocation regardless of
scale classification. It produces the two artifacts every later phase depends
on: the project constitution (user-declared principles) and the brownfield
research artifact (verified existing-code inventory).

---

## Phase 0 Steps

### 1. Constitution

Ask the user to declare 3–5 immutable project principles. Examples:
"no new runtime dependencies", "TDD strictly", "offline-capable", "single
binary deploy". These become project-specific challenge criteria used by the
Constitution Gate in Phase 2.

If the user declines to declare principles, record `constitution: none
declared` explicitly — silence is not a valid answer.

### 2. Brownfield Scan

If an existing codebase is detected, scan it automatically. Tag discovered
patterns, conventions, and architecture as `Observed` in the Assumption
Register. In Phase 2, the burden of proof **inverts** — the user must justify
deviations from existing architecture, not justify the architecture itself.

### 3. Research Artifact (brownfield only)

Write the brownfield scan to a structured `research.md` file (or a
brownfield-context section of the PRD). This is NOT optional — verbal
summaries disappear on context compaction.

Required contents:
- Existing package inventory (see hard rule below)
- Naming conventions
- Key function signatures at boundaries the feature touches
- Pre-existing behaviors that must not break
- The agent's interpretation of the architecture

The user then annotates disagreements or corrections before Phase 1 begins.
This catches AP-9 (Greenfield Hallucination) at the earliest possible moment —
if the agent misunderstands the existing codebase, better to discover it here
than in a failed integration gate.

**Hard rule — ls-verified paths:** Every directory path in the package
inventory MUST be the verbatim output of `ls` (or equivalent filesystem
listing), not a conceptual or abbreviated name. Use the template:

```
| Package | Directory (exact, ls-verified) | Import name (exact) | Key modules |
```

The research artifact is not ready for user review if any path is inferred
rather than observed from the filesystem.

### 4. Implementation Topology Mapping (brownfield only)

For each feature area the user mentions, identify the existing file(s) that
would change. Produce a preliminary MODIFY/CREATE inventory. If the user
proposes creating a new package and an existing package has overlapping
responsibility, challenge immediately with AP-9. This mapping becomes PRD §8b.

### 5. Scale Classification

Determine Light / Standard / Heavy using the Decision Tree in SKILL.md. For
Light projects, compress the remaining phases per the classification rules.

---

## Phase 0 Output Contract

The Phase 0 exit response must contain a fenced `BROWNFIELD-CONTEXT:` block
(or `GREENFIELD-CONTEXT:` for greenfield work). See
`~/.skills/shared/PRD_TEMPLATES.md` → Phase-Block Contracts for the exact shape.

---

## Phase 0 Hard Gates

- Constitution is declared (or `none declared` recorded explicitly)
- For brownfield: research artifact is written and reviewed by the user
  before Phase 1
- Any user corrections to the agent's understanding of existing architecture
  are tagged `User-stated` in the Assumption Register
- The `BROWNFIELD-CONTEXT:` / `GREENFIELD-CONTEXT:` block is present in the
  Phase 0 exit response

## Phase-Gate Audit Line

Before advancing to Phase 1, emit:

```
PHASE-GATE: Phase 0 → 1. Criteria: [constitution declared: <met|not met>; research artifact written: <met|not met|n/a greenfield>; ls-verified paths: <met|not met>]. Proceeding: <yes|no>.
```

If `Proceeding: no`, surface the specific blocker and stay in Phase 0.

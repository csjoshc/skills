# Output Templates

Templates for the deliverables produced by the challenge skill. These are
populated after Phase 3 completes and the DAG is approved by the user.

---

## PRD Template

```markdown
# PRD: [Product Name]

## Status: APPROVED | DRAFT
## Date: [date]
## Author: [user] + challenge skill

---

## 1. Problem Statement

[What problem exists for what user. 2-3 sentences max. No implementation.]

## 2. Constitution

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | [e.g., "No new runtime dependencies"] | [why this is non-negotiable] |
| 2 | [principle] | [rationale] |
| 3 | [principle] | [rationale] |

Amendments: [list any amendments made during Phase 2, with justification]

## 3. Users

| User | Role | Primary workflow | Pain without this system |
|------|------|-----------------|-------------------------|
| [name/type] | [role] | [what they do] | [what hurts] |

## 4. Minimum Testable Product (MTP)

The smallest set of features that proves the design works end-to-end:

1. [Feature A] — [1-sentence description]
2. [Feature B] — [1-sentence description]

**MTP validation:** After [ticket IDs], integration gate IG-1 confirms:
- [given/when/then]
- [given/when/then]

## 5. Features

### 5.1 [Feature Name]

**Priority:** P1 | P2
**User story:** As a [user], I want [action] so that [outcome].

**Acceptance criteria:**
- [ ] Given [precondition], when [action], then [result]
- [ ] Given [precondition], when [action], then [result]

**Out of scope:** [what this feature explicitly does NOT do]

**Ticket(s):** T-[N], T-[M]
**Gate:** IG-[K]

### 5.2 [Feature Name]
[repeat structure]

## 6. Success Criteria

| ID | Criterion | Target | Measurement method |
|----|-----------|--------|--------------------|
| SC-001 | [e.g., "Response latency"] | [e.g., "<2s p95"] | [how measured] |
| SC-002 | [e.g., "First-attempt task completion"] | [e.g., ">90%"] | [how measured] |

## 7. Architecture Decisions

| Decision | Options considered | Chosen | Justification |
|----------|-------------------|--------|---------------|
| [decision] | [A, B, C] | [B] | [why B, from Phase 2] |

## 8. Component Map

| Component | Responsibility (one sentence, no 'and') | Owner tickets |
|-----------|------------------------------------------|---------------|
| [name] | [what it does] | T-[N] |

## 8b. Implementation Topology (required for brownfield)

*Maps every ticket to concrete file paths. Prevents AP-9 (Greenfield Hallucination).*

| Ticket | Action | Path | What changes |
|--------|--------|------|-------------|
| T-[N] | MODIFY | `packages/[pkg]/src/.../[file].py` | [function/class-level change description] |
| T-[N] | MODIFY | `packages/[pkg]/tests/test_[module].py` | [new test cases for ...] |
| — | CREATE | (none — or justify each CREATE) | |

**Validation rules:**
- Every ticket must have at least one MODIFY or CREATE line
- For brownfield: if a ticket has ONLY CREATE lines and zero MODIFY lines,
  it must pass an AP-9 review ("why can't this live in an existing module?")
- For greenfield: CREATE lines are expected; this section still anchors file paths

## 9. API Contracts

### [Component A] → [Component B]

```
[method] [path]
Request: [type signature]
Response: [type signature]
Errors: [error types and when]
```

## 10. Explicitly Out of Scope

1. [thing] — deferred because [reason]
2. [thing] — not requested by any identified user
3. [thing] — cut during Phase 2 architecture interrogation

## 11. Risks and Open Questions

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [risk] | H/M/L | H/M/L | [what we do] |

## 12. Ticket Dependency Graph

[paste DAG from Phase 3]

## 13. Convergence Ledger (Final)

- Resolved: [count]
- Cut: [count]
- Deferred: [count] — [items with justification]

## 14. Assumption Register

| ID | Statement | Source | Confidence | Impact if wrong | Validation method | Blocking? |
|----|-----------|--------|------------|----------------|-------------------|-----------|
| A-1 | [assumption] | Observed / User-stated / Inferred / Deferred | HIGH/MED/LOW | [consequence] | [how to validate] | Yes/No |

All Inferred assumptions that are blocking were explicitly accepted by user
before ticket generation.

## 15. Artifact Ingestion Log

*Omit this section if no reference artifacts were provided.*

| Artifact | Type | Items enumerated | Items adopted | Items rejected |
|----------|------|-----------------|--------------|----------------|
| [repo/link/screenshot] | git repo / screenshot / docs / API spec | [count] | [list with justification] | [list with reason] |

## 16. Complexity Justification Register

*Record when a user successfully defends a complex choice during Phase 2.*

| Violation | Why needed | Simpler alternative rejected because |
|-----------|-----------|--------------------------------------|
| [e.g., "4th microservice"] | [current need] | [why fewer services insufficient] |

## 17. Implementation Readiness Checklist

*Final gate before handoff to an implementing agent. All must be checked.*

- [ ] Every ticket specifies MODIFY or CREATE for each file it touches
- [ ] No ticket creates a new package without passing the Merge Test
  against ALL existing packages with overlapping responsibility
- [ ] Tool/API definitions include verified field names from the real
  upstream (not LLM-generated guesses)
- [ ] API contracts show what changed vs pre-existing state (not just
  final state)
- [ ] Plan explicitly states which existing tests must still pass
- [ ] Plan names the test runner, framework conventions, and import
  patterns used by the existing codebase
- [ ] For brownfield: existing behaviors that must NOT break are enumerated
- [ ] For interactive systems: statefulness model is explicitly resolved
- [ ] Every MODIFY path in §8b verified to exist on target commit
  (`test -d` / `test -f` or equivalent)
- [ ] Every import name in brownfield scan verified
  (`python -c "import {name}"` or equivalent)
- [ ] No ticket's dependency file adds a runtime dependency not present at
  baseline (Constitution compliance)
```

---

## Ticket templates

Ticket files (feature, integration gate, infrastructure) follow one contract: [`TICKET_CONTRACT.md`](TICKET_CONTRACT.md).
challenge's task-sequence stubs use the same frontmatter (`id`, `title`, `Stage: NEW`, `Depends-On`, `Blocks`, `Gate`, `Files`) plus a short scope and two or three invariant ACs; spec turns each stub into a full ticket and runs `spec/scripts/tickets_lint.py`.

---

## Phase-Block Contracts (Structural Output Requirements)

Every phase exit must emit a fenced block the user can spot on sight. Missing
blocks are malformed-on-sight. Downstream tools (`validate.py --transcript`,
`/todo`) grep for these markers.

### Header YAML Ledger (every response)

```yaml
ledger:
  phase: 0 | 1 | 2 | signoff | 3 | fast
  resolved: <int>
  contested: <int>
  unresolved: <int>
  cut: <int>
  confidence: LOW | MEDIUM | HIGH
  reclassified: false | "Light→Standard: <reason>"
```

### Phase 0 Exit

````
```BROWNFIELD-CONTEXT
constitution:
  - "<principle 1>"
packages:
  | Package | Directory (ls-verified) | Import name | Key modules |
conventions:
  - <convention>
must_not_break:
  - <behavior>
architecture_interpretation: |
  <agent's written understanding>
history_and_owners:          # optional; why things are this way, each with an issue/file pointer
  - <fact> (<pointer>)
open_questions:               # optional; surfaced by /todo until resolved
  - <question>
topology_preview:
  - feature: <name>
    files_to_modify: [<paths>]
    files_to_create: [<paths or none>]
```
````

Greenfield projects emit `GREENFIELD-CONTEXT` with `constitution` and
`architecture_interpretation` only.

### Phase 1 Exit

````
```PROBLEM-STATEMENT
users:
  - name: <role>
    workflow: <1 line>
mtp: <1–2 sentences>
features:
  - id: F-1
    name: <feature>
    user: <named user>
    priority: P1 | P2 | P3
    acs:
      - given: <state>
        when: <action>
        then: <observable outcome>
        verify: <grep/test/curl command>
success_criteria:
  - id: SC-001
    metric: <name>
    threshold: <number + unit>
non_goals:
  - <explicit cut>
```
````

### Phase 2 Exit

````
```ARCHITECTURE-DECISIONS
components:
  - name: <component>
    justification: <why; which Phase 1 feature requires it>
    deletion_test: <what breaks if removed>
    merge_test: <why it can't be absorbed>
    contracts:
      - boundary: <A → B>
        shape: <type signature or OpenAPI ref>
        errors: <status codes / exception types>
topology:
  - ticket: T-1
    action: MODIFY | CREATE
    files: [<paths>]
    exemplar: <pre-existing file demonstrating pattern>
risk_surface_ref: §8c
```
````

### Sign-off Exit

````
```SIGNOFF-APPROVALS
problem_statement: /approve | /reject
mtp: /approve | /reject
non_goals: /approve | /reject
architecture: /approve | /reject
ig1_scope: /approve | /reject
topology: /approve | /reject | n/a  # brownfield only
```
````

### Phase 3 Exit

````
```TICKET-DAG
<text DAG with execution modes; see convergence-engine.md § DAG Text Format>
```

```INTEGRATION-GATES
- id: IG-1
  validates: [T-1]
  scope: <flow>
  proof_artifact: <curl transcript | Playwright run | etc.>
```
````

---

## PRD §8c Risk Surface

Every PRD must include this section. It is the PRD-fallback source consumed
by `/tdd` Phase 0 ([SCOPING.md](../tdd/SCOPING.md)) when a repo has no
`.risk-registry.yaml`. Tiers are path-based, not component-based, so they
survive renames.

```markdown
## §8c Risk Surface

### Tier map (globs)
- T1 (harm on failure — auth, payments, writes, migrations, schema, security):
  - <glob>
- T2 (core flows, API surface, user-visible behavior):
  - <glob>
- T3 (cosmetic, docs, tooling):
  - <glob>

### Critical flows
- <name>: <1-line scope> — paths: [<glob>, <glob>]

### Expected blast radius
- <feature/ticket>: touches <modules>; downstream consumers: <modules>
```

Rules:
- Every ticket in the DAG must have ≥1 glob in the tier map covering its
  touch points. If not, trigger the Assumption Approval Gate — planning work
  with unknown risk.
- Critical flows promote any touched path under their globs to T1 regardless
  of tier map.

---

## prd-specific templates

### PRD Output Template

<!-- PRD-CONTRACT-VERSION: 1 -->

# <Feature Title>

## Problem Statement
<Brief context about the "Why">

## Goals
- <High-level objective 1>
- <High-level objective 2>

## Requirements
- <Requirement 1>
  ### Acceptance Criteria
  - <AC 1.1>
  - <AC 1.2>
- <Requirement 2>
- ## Integration Gate
- <Requirement 3>

## Verification
<Recommended manual verification steps>

---

### PRD Template (Concise)
*Use this when the user wants a lighter-weight PRD.*
*Adapted from mattpocock/skills to-spec (MIT).*

Before writing, sketch the seams the feature will be tested at.
Prefer existing seams to new ones, and use the highest seam possible.
If a new seam is needed, propose it at the highest point you can.
Fewer seams is better; the ideal is one.
Confirm the seams with the user.

1. **Problem Statement**: the problem from the user's perspective.
2. **Solution**: the solution from the user's perspective.
3. **User Stories**: a long numbered list covering every aspect of the feature, each as "As an <actor>, I want <feature>, so that <benefit>".
4. **Implementation Decisions**: modules built or changed and their interfaces, architectural decisions, schema changes, API contracts, notable interactions.
   Use the project's domain vocabulary and respect existing ADRs.
   Leave out file paths and code snippets, which go stale fast.
   Exception: a prototype snippet that pins a decision better than prose (state machine, reducer, schema, type shape), trimmed to the decision-rich part and marked as from a prototype.
5. **Testing Decisions**: the chosen test seams, which modules get tested, prior art in the codebase, and what makes a good test here (external behaviour, not implementation details).
6. **Out of Scope**: what this spec deliberately leaves out.
7. **Further Notes**: anything else a builder needs.

### Ticket Template

Each ticket is a vertical slice: a narrow but complete path through every layer it needs, demoable or verifiable on its own, sized for one fresh context window.
Its file format is [`TICKET_CONTRACT.md`](TICKET_CONTRACT.md); write it there, not from a list here.

### Final Synthesis Checklist

1. Assumptions are explicit.
2. Unresolved questions are isolated and minimal.
3. AC is concrete and testable.
4. Dependencies are acyclic and clear.
5. Rollout and recovery are covered when needed.

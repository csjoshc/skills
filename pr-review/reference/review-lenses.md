# review-lenses

Specialist review lenses for the `pr-review` skill. Each lens has a narrow
domain, explicit checklist threshold, and evidence requirements.

## Contents

- Lens design rules
- Lens 1 — Bug hunter
- Lens 2 — Standards compliance
- Lens 3 — Error handling auditor
- Lens 4 — Test analyzer
- Lens 5 — Spec-traceability auditor
- Lens 6 — Architectural-drift auditor
- Lens 7 — Dead-weight & workaround apology
- Validation pass
- Deduplication rules
- Issue output format
- False-positive filters

---

## Lens Design Rules

Use specialist review, not a single-pass generalist review.

- Scope each lens to one domain
- Use concise, real reviewer roles
- Run deterministic checks first when available
- Reject findings without file/line/code-path evidence
- Separate generation and review roles

---

## Lens 1 — Bug Hunter

**Role:** Senior application reliability engineer

**Focus:** Runtime bugs and security defects in changed code only

**Look for:**

- Null/undefined dereferences
- Off-by-one errors
- Race conditions
- Resource leaks
- Wrong-result logic errors
- Missing returns or incorrect operators
- Type coercion bugs
- SQL injection, XSS, command injection, path traversal
- Hardcoded secrets
- Missing auth checks

**Do not flag:**

- Style preferences
- Purely hypothetical issues
- Missing tests
- Architectural opinions outside the diff

**Checklist — report only if 4 of 5 are YES:**

| #   | Criterion                                              |
| --- | ------------------------------------------------------ |
| 1   | Can trace the exact code path to the failure           |
| 2   | Failure occurs regardless of incidental external state |
| 3   | No defensive code in the diff prevents the scenario    |
| 4   | The issue is in changed code, not pre-existing         |
| 5   | A concrete failing input or test case can be described |

---

## Lens 2 — Standards Compliance

**Role:** Staff engineer for code standards

**Focus:** Violations of documented coding standards only

For each finding, quote the exact rule code and text from
`review-standards.md` or repo-local standards.

**Check for:**

- Naming violations
- Logging violations
- Missing type/interface declarations
- Banned patterns
- Documentation formatting issues
- Unbounded queries
- Required tests for new public functions

**Do not flag:**

- Subjective preferences
- Pre-existing violations
- Linter-catchable issues
- Rules not documented anywhere

**Checklist — report only if 4 of 4 are YES:**

| #   | Criterion                                      |
| --- | ---------------------------------------------- |
| 1   | The exact rule code and text can be quoted     |
| 2   | The rule applies to this file type and context |
| 3   | The violation is in changed code               |
| 4   | No documented exception applies                |

---

## Lens 3 — Error Handling Auditor

**Role:** Production incident reviewer

**Focus:** Silent failures and diagnosability gaps

**Check for:**

- Errors not logged with useful context
- User-facing failures without actionable feedback
- Over-broad catch blocks
- Fallbacks that mask the root cause

**Do not flag:**

- Project-standard error handling
- Intentional documented fallbacks
- Test-only error paths

**Checklist — report only if 3 of 4 are YES:**

| #   | Criterion                                           |
| --- | --------------------------------------------------- |
| 1   | The handler exists in changed code                  |
| 2   | A concrete silent-failure scenario exists           |
| 3   | No upstream handler logs or surfaces the error      |
| 4   | A production debugger would struggle to diagnose it |

**Severity labels:**

- CRITICAL: 4/4 YES
- HIGH: 3/4 YES
- MEDIUM: below threshold, do not report

---

## Lens 4 — Test Analyzer

**Role:** Test strategy reviewer

**Focus:** Critical test coverage gaps in changed code

**Check for:**

- New public functions without tests
- Missing edge/error path coverage
- Violations of project test conventions
- Weak assertions
- Test data leakage

**Do not flag:**

- Trivial getters/setters
- Academic completeness concerns
- Behavior already covered by integration or e2e tests

**Checklist — report only if 3 of 4 are YES:**

| #   | Criterion                                                     |
| --- | ------------------------------------------------------------- |
| 1   | A new or modified public function lacks corresponding tests   |
| 2   | A specific bug or regression this gap would miss can be named |
| 3   | No integration or e2e coverage appears elsewhere              |
| 4   | The gap is in changed code                                    |

---

## Lens 5 — Spec-Traceability Auditor

**Role:** Delivery scope reviewer

**Focus:** Scope integrity between acceptance criteria and diff hunks

**Inputs:**

- Linked ticket(s) and acceptance criteria
- PR diff hunks
- `CLAIM_UNVERIFIED.md` if present
- `layer-boundary-critic` output if present

**Checks:**

- Hunks with no acceptance criterion
- Acceptance criteria with no hunk
- Scope creep outside ticket intent
- Missing claim verification
- Any layer BLOCK finding

**Do not flag:**

- Supporting tests for claimed behavior
- Tiny typo fixes under 3 lines
- Mechanical refactors explicitly authorized by the ticket

**Checklist — report only if 3 of 4 are YES:**

| #   | Criterion                                      |
| --- | ---------------------------------------------- |
| 1   | The hunk/AC mismatch is clear and unambiguous  |
| 2   | No other lens already caught it                |
| 3   | Fixing it is cheap                             |
| 4   | Leaving it hurts reviewability or completeness |

---

## Lens 6 — Architectural-Drift Auditor

**Role:** Staff engineer enforcing the project's declared architecture

**Focus:** Diff-level issues that *should* have been decided at PRD/plan
stage. A finding here means the diff contradicts (or exposes a gap in)
the linked plan's `ARCHITECTURE-DECISIONS` block.

**Inputs:**

- PR diff
- Linked plan/PRD if `plan_present: true` (from the pre-flight)
- [`~/.skills/reviews/arch-violations/README.md`](../../reviews/arch-violations/README.md)
  and the specific catalog file relevant to the detected smell (e.g.,
  [01-dependency-direction](../../reviews/arch-violations/01-dependency-direction.md))

**Check for:**

- Upward/sideways imports or cycles contradicting a declared layer topology
- Public APIs leaking implementation types when domain types were specified
- Authorization logic scattered despite a "single policy layer" decision
- Validation at the wrong boundary relative to the plan
- Any diff choice that made a decision the plan reserved for later review

**Do not flag:**

- Decisions the plan explicitly delegated to the implementing engineer
- Violations already caught by another lens (dedup in report phase)
- Issues when `plan_present: false` — instead emit a note in the summary
  that architectural drift cannot be assessed without a linked plan
- Code shapes that *look* architectural but are actually style (handled
  by Standards lens)

**Checklist — report only if 4 of 5 are YES:**

| #   | Criterion                                                                                                                                 |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | The linked plan contains a decision the diff contradicts or skirts                                                                        |
| 2   | The evidence is an import edge, API signature, or topology fact                                                                           |
| 3   | A reviewer could verify by reading both the plan and the diff                                                                             |
| 4   | Fixing at code-only is incomplete — the plan or policy must update                                                                        |
| 5   | `suggested_fix` eliminates the quoted evidence pattern — it does not rename it, relocate it, inject it, or wrap it behind a new parameter |

Criterion #5 closes the *fix-preserves-the-bug* pathology: a reviewer
names the violation but proposes a rewrite that keeps the same shape.
Canonical failure mode — `cart.total_cents -= discount` "fixed" by
changing the discount parameter type, or `order.user.address.get_zip()`
"fixed" by injecting the validator while keeping the attribute chain.
If the fix requires the reader to trace identifiers to confirm the
violation is gone, the criterion is NO.

**Finding shape:** always `category: Architectural Drift` with
`decidable_at` set (typically `design` or `both`). `proof:` must cite the
plan artifact (`.tickets/PRD.md §ARCHITECTURE-DECISIONS`, PR body link,
or similar) or contain `no-plan-available` verbatim.

---

## Lens 7 — Dead-weight & Workaround Apology

**Role:** Operational hygiene reviewer — compose-and-config archaeologist

**Focus:** Diff-time evidence that the system has drifted from its
canonical operator flow. Idle services kept "for completeness", config
defaults the operator path never uses, override files that apologize
for diverging from the base, and `depends_on` edges that no longer
gate anything. This lens is the PR-time counterpart of antiplan
**AP-21 (Requirement Drift / Apologetic Workaround)**: AP-21 is the
design-time gate, Lens 7 is the after-the-fact evidence detector.

This lens fires on PRs that touch `docker-compose*.{yml,yaml}`,
`Dockerfile`, Helm charts, env files (`.env*`, `*.env.example`),
service definitions, `vite.config.*`, `next.config.*`, `nginx.conf`,
or any "stack-up" / "local-stack" script. It also fires on PRs whose
description claims to "improve the dev loop" or "fix the demo"
without removing the cruft that caused the original drift.

**Check for:**

- Service / container / process declared in the default boot path
  (no profile gate, no env flag) but never targeted by the canonical
  operator flow (no env var resolves to it, no client URL points at
  it, no curl in the README references it)
- Override / overlay file (`docker-compose.override.yaml`, `*.local.*`,
  `*.example` next to a committed `*.real`) whose comments explain
  how to "restore", "fall back to", or "re-enable" the base design
- `depends_on` / `requires` / `blocks` edge in the base config that
  an override silently removes, reroutes, or breaks — and the PR does
  not fold the override into the base
- Config default whose value the canonical operator path doesn't use
  (base file says `OLLAMA_BASE_URL=http://ollama:11434`; every actual
  run uses `host.docker.internal:11434` via override)
- Gitignored file in the working tree that documents how the system
  actually works — the divergence is load-bearing but unversioned
- Comment block ≥5 lines explaining "why we keep X", "this is no
  longer used but…", "for an earlier attempt", or "harmless to leave
  in case"
- Healthcheck whose success doesn't imply participation (e.g.
  `ollama list >/dev/null` passes even when no model is loaded and
  no client is connected)
- Constants, classes, or imports kept "for compat" with no named
  consumer in the diff or in `git log`

**Do not flag:**

- Optional features behind explicit `--profile <X>`, env opts, or
  feature flags the operator must enable
- Migration-window code with a dated removal note
  (`// remove after 2026-Q3 cutover` or a linked deprecation ticket)
- Test fixtures, fakes, or mocks intentionally kept for tests
- Logging / instrumentation that observes a flow without joining it
- Standby / failover services that the README documents as
  intentionally idle with a named trigger (e.g. "promoted on primary
  health failure")
- Code paths whose only consumer is a CI job named in the PR

**Checklist — report only if 4 of 5 are YES:**

| #   | Criterion                                                                                                                                                                                |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | The dead-weight artifact is in the PR diff, OR the PR claims to improve this code path while leaving the artifact untouched                                                              |
| 2   | The canonical operator flow (per README, PR description, or stack-up script) does not traverse the flagged artifact                                                                      |
| 3   | No env var / profile selection / config flag ties the artifact to a named operator persona today (the diff or README cites a CI job by file, a teammate by handle, or a deployment env)  |
| 4   | The artifact's comment block, healthcheck, boot order, or `depends_on` edge misleads a future reader about its participation                                                             |
| 5   | `suggested_fix` removes the artifact, profile-gates it, or folds the override back into the base — it does not paper over with a longer comment, a stricter healthcheck, or a TODO note  |

Criterion #5 closes the *apology-deepens-the-debt* pathology: a
reviewer flags the dead container; the author responds by adding three
more lines of comment explaining why it's kept. That's AP-21 squared.
Acceptable fixes: delete the service, gate it behind its own profile
with a named operator persona for the profile, or roll the override
into the base so the topology is honest.

**Severity labels:**

- CRITICAL: 5/5 YES — the artifact runs, passes healthcheck, and
  misleads operators (the canonical AP-21 case)
- HIGH: 4/5 YES
- MEDIUM: below threshold, do not report

**Finding shape:** `category: Operational Hygiene` with
`decidable_at: design` (the design-time gate is antiplan AP-21).
`proof:` must cite the specific override/base/comment pair as a
quoted excerpt plus a one-line reproducer (e.g. "with `--profile chat
up` and override applied, `docker inspect --format
'{{.NetworkSettings.Networks}}' ollama-1` shows the service running;
`docker exec c3-chat env | grep OLLAMA_BASE_URL` shows
`host.docker.internal`, so the network the container joins serves no
client").

---

## Validation Pass

Every issue that passed a lens threshold gets a second validation pass.

1. Re-check every YES criterion independently.
2. Flip YES to NO if evidence does not hold.
3. Keep only findings that still meet the threshold after validation.

When in doubt, validate rather than dismiss.

---

## Deduplication Rules

1. Remove issues that failed validation.
2. Merge duplicates across lenses. If the Architectural-Drift lens and
   another lens both flagged the same hunk, prefer the Drift finding
   when `plan_present: true` (higher signal for antiplan feedback).
3. Sort by category:
   - Bug
   - Error Handling
   - Architectural Drift
   - Operational Hygiene
   - Standards
   - Test Gap
   - Scope/Traceability

   When Lens 7 (Operational Hygiene) and Lens 6 (Architectural Drift)
   flag the same artifact, prefer Drift if a plan link is present and
   the plan made a topology decision; prefer Operational Hygiene if
   the divergence is between the base config and an override file
   with no plan involvement.

---

## Issue Output Format

Every validated finding is serialized into a `REVIEW-FINDINGS` fenced
block (schema in [`~/.skills/reviews/schemas.md`](../../reviews/schemas.md)):

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Bug
  lens: bug-hunter
  file: src/api/user.py
  line: 142
  rule_code: N/A
  severity: CRITICAL
  source: lens-derived
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    response.json()["user"] dereferenced without checking status_code
  proof: |
    curl -X GET /users/0 returns 404; code path at line 142 runs unconditionally
  suggested_fix: |
    guard with `if response.ok:` before `.json()`
```
````

Required fields per row: `id`, `category`, `lens`, `file`, `line`,
`rule_code`, `severity`, `source`, `status`, `evidence`, `suggested_fix`.
CRITICAL + VALIDATED findings additionally require `proof:` — the
validator rejects the transcript without it.

Multiple blocks are allowed (e.g., one block per category). Inline PR
comments are rendered from these blocks during the posting step.

Every posted PR comment still ends with:

```markdown
---

_Generated by Claude_
```

---

## False-Positive Filters

Do not flag:

- Pre-existing issues not introduced by this PR
- Code that appears odd but is correct
- Pedantic nitpicks
- Linter-only issues
- General quality concerns without a documented rule
- Explicitly silenced issues such as `lint-ignore` or `noqa`
- PR-author intent as a substitute for code evidence

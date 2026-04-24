# Pattern cross-reference

Single index mapping the three taxonomies that live in this repository.
Each row is one underlying pattern; columns show how it manifests at
each altitude. Blank cells are real gaps — not all patterns have a
counterpart at every altitude, and the asymmetries are informative.

**Audience:** `/antiplan`, `pr-review`, and `cleanup` skills. Any
finding that cites a code from one column can be enriched with the
sibling codes from the same row.

**Source taxonomies:**

- **AP-1..AP-16** — [`antiplan/references/anti-patterns.md`](../antiplan/references/anti-patterns.md) (design altitude)
- **ARCH-\*-\*** — [`reviews/arch-violations/`](arch-violations/README.md) (diff / both altitudes)
- **M1..M12** + **P5-1..P5-12** — [`cleanup/quality-rubric.md`](../cleanup/quality-rubric.md) (mechanical / subjective)

## Contents

- How to use
- Reading the table
- Index
- Gaps surfaced by this table
- Skills that reference this table
- Open questions

---

## How to use

1. Finding surfaces with a `rule_code` from one taxonomy.
2. Grep this file for that code; the row gives the sibling codes.
3. Include them in `evidence` or `suggested_fix` when they sharpen the
   claim — e.g., a diff-level `ARCH-MOD-GOD` finding may cite AP-4 as
   the design-time decision that should have prevented it, and M9 as
   the mechanical symptom a linter could have flagged.

Do **not** emit a finding under two codes. Pick the altitude closest to
where the reviewer can act. Cross-references go in prose, not in the
`rule_code` field.

---

## Reading the table

- **design (AP)** — catchable before code exists; `/antiplan` Phase 2.
- **structural (ARCH)** — catchable from diff or codebase topology.
- **mechanical (M / P5)** — catchable from a single file, usually by
  a tool or a syntactic check.
- **notes** — explains asymmetries, false-positive flavors, or which
  skill owns the pattern.

"—" means no entry at that altitude. A gap is not automatically a
missing entry; some patterns genuinely live at one altitude only.

---

## Index

| Pattern | design (AP) | structural (ARCH) | mechanical (M / P5) | notes |
| --- | --- | --- | --- | --- |
| God module / function | AP-4 | ARCH-MOD-GOD | M9, P5-1 | Same concept at three altitudes. AP-4 is the prevention; ARCH-MOD-GOD is the detection; M9 is the syntactic shadow. |
| Silent failure / swallowed errors | AP-10 | ARCH-ERR-SWALLOW | M1, M7, P5-2 | AP-10 is the design-time temptation; M1/M7 are single-site forms; ARCH-ERR-SWALLOW is the structural version (error strategy that guarantees silence). |
| Greenfield hallucination / reinventing the wheel | AP-9 | ARCH-AI-PARALLEL, ARCH-MOD-DUP | P5-8 | AP-9 is the upstream failure to scan existing utilities; ARCH-AI-PARALLEL is its AI-specific diff signature; ARCH-MOD-DUP is the generic duplicate-cross-cutting-concern. |
| Premature abstraction | — | ARCH-MOD-PREMATURE | P5-5 | No AP — the seam emerges after code exists; not predictable from a plan. |
| Mock-validated integration | AP-5 | ARCH-TEST-MOCK-WORLD, ARCH-TEST-MOCK-CONTRACT | — | AP-5 is "tests mock the thing under test"; ARCH-TEST-MOCK-WORLD is "tests mock the universe"; different failures, both indict the test shape. |
| Untestable abstraction | AP-6 | ARCH-TEST-IMPL-ASSERT | — | AP-6: design made behavior unobservable. ARCH-TEST-IMPL-ASSERT: tests asserted on implementation details because that was all that was reachable. |
| Exemplar blindness / rejected pattern | AP-13 | ARCH-AI-REJECTED-PATTERN | — | Model reintroduces a pattern the repo has explicitly rejected; AP-13 is the plan-time precursor. |
| Happy-path only / defensive dead code | — | ARCH-AI-DEAD-DEFENSE | P5-4, P5-6 | AI-shaped: either no error path at all (P5-4) or a defensive branch for a case that cannot occur (P5-6). |
| Type illusion | — | — | M10, P5-3 | Mechanical only: `Any`/`any`, unchecked cast. No architectural counterpart. |
| Post-hoc rationalization | AP-2 | — | — | Plan-document smell. Detectable only by reading the plan; no code fingerprint. |
| Speculative architecture / premature horizontal expansion | AP-1, AP-7 | ARCH-MOD-PREMATURE (partial) | P5-5 | AP-1 and AP-7 are design-time; ARCH-MOD-PREMATURE catches the structural form once code exists. |
| Ceremony as rigor substitute | AP-8 | — | — | Plan-time — lengthy document substituting for actual decisions. No diff manifestation. |
| Ticket-closure loop | AP-3 | — | — | Process-level — checkbox-driven planning. No code signature. |
| Completion drive | AP-11 | — | — | Model behavior — tendency to finish even when the plan should abort. Prevented by Phase-0 contract, not by code review. |
| Context rot | AP-12 | — | — | Session-level pathology — older context displacing current requirements. Detectable only in planning state. |
| Orchestrator observability blindspot | AP-14 | ARCH-OBS-NO-TRACE | — | AP-14: multi-agent spans untraceable by design; ARCH-OBS-NO-TRACE: diff ships a new boundary without propagation. |
| Business logic coupled to transport | — | ARCH-BND-TRANSPORT | — | Policy ("domain rules live in domain/") is design-time but the violation is a diff fact. |
| Validation at wrong boundary | — | ARCH-BND-VALIDATION | — | Either missing at the edge or re-validated internally. |
| Missing anti-corruption layer | — | ARCH-BND-ACL | — | Vendor types / error codes flow unchanged through callers. |
| Public surface leaks internals | — | ARCH-BND-LEAK | — | ORM rows, internal enums, storage shape exposed on the API boundary. |
| Law of Demeter (reaching through collaborators) | — | ARCH-BND-DEMETER | — | Deep `a.b.c.d` attribute chains in callers. The fingerprint is nested mock structures in tests. Distinct from BND-LEAK: LEAK exposes internals outward; DEMETER reaches through collaborators inward. Covers W9006. |
| Eager construction of infrastructure at init | AP-16 | ARCH-BND-EAGER-INIT | P5-13 | `def __init__(self, db=None): self.db = db or PostgresClient()` and module-level client construction. No DI seam; import has side effects. Covers W9301. |
| Upward import / wrong-direction dependency | — | ARCH-DEP-UP | — | Pure layer imports infrastructure or transport. |
| I/O primitive inside a pure module | AP-15 | ARCH-DEP-IO-IN-PURE | — | `open()`, `requests`, `subprocess`, socket, clock inside a pure/domain module. Distinct from DEP-UP: no upward import is required — the *use* of the primitive is the violation. Covers W9004 and the AI-specific flavor of W9010. |
| Dependency cycle | — | ARCH-DEP-CYCLE | — | Mutually-importing modules; blocks isolation testing. |
| Cross-package side-importing (peer reach-across) | — | ARCH-DEP-SIDE | — | Feature A imports Feature B's internals. |
| Shared mutable state across requests/threads | — | ARCH-STATE-SHARED | P5-9 | Module-level cache mutated per-request; P5-9 is the same smell phrased as a code-review heuristic. |
| Mutable domain entity with in-place mutation | — | ARCH-STATE-DOMAIN-MUTATION | P5-14 | Within-flow aliasing of a mutable value type (mutable `@dataclass`, method that mutates `self` without returning). Distinct from STATE-SHARED: this bug fires in a single thread. Covers W9401. |
| Race on shared resource (check-then-act) | — | ARCH-STATE-RACE | — | Emerges from interleaving; no design-time equivalent. |
| Resource leak — no guaranteed cleanup | — | ARCH-STATE-LEAK | — | |
| Transactional boundary mistake | — | ARCH-STATE-TXN | — | External I/O inside transaction, or partial writes without transaction. |
| Unbounded queue / retry / recursion | — | ARCH-STATE-UNBOUNDED | — | No back-pressure; amplifies under load. |
| Error: broad catch | — | ARCH-ERR-BROAD | M1 (partial) | |
| Error: untranslated domain | — | ARCH-ERR-UNTRANSLATED | — | Vendor error shapes reach UI/domain callers unchanged. |
| Error: masking fallback | — | ARCH-ERR-MASKING-FALLBACK | — | Default/fallback values hide real failures from telemetry. |
| Error: conflated categories | — | ARCH-ERR-CONFLATE | — | One exception type covers unrelated failure modes. |
| Duplicate cross-cutting concern | AP-9 (partial) | ARCH-MOD-DUP | — | |
| Flag sprawl with no retirement path | — | ARCH-MOD-FLAG-SPRAWL, ARCH-EVO-FLAG-PARTIAL | — | FLAG-SPRAWL: many flags accumulating. FLAG-PARTIAL: a partial rollout whose long tail was never closed. |
| Data: unbounded query | — | ARCH-DATA-UNBOUNDED | — | |
| Data: N+1 | — | ARCH-DATA-N-PLUS-ONE | — | |
| Data: unstable ordering assumptions | — | ARCH-DATA-ORDER | — | |
| Data: non-idempotent write on retry-prone path | — | ARCH-DATA-NON-IDEMPOTENT | — | |
| Data: missing timeout on outbound call | — | ARCH-DATA-TIMEOUT | M2 | M2 is the same smell for `subprocess`; ARCH-DATA-TIMEOUT covers HTTP/DB/queue. |
| Security: scattered authorization | — | ARCH-SEC-AUTHZ-SCATTERED | — | |
| Security: trust boundary violation | — | ARCH-SEC-TRUST | — | |
| Security: secret leakage path | — | ARCH-SEC-SECRET | — | |
| Security: auth gap (endpoint without check) | — | ARCH-SEC-AUTH-GAP | — | |
| Security: IDOR / object-level authorization | — | ARCH-SEC-IDOR | — | |
| Observability: no distributed trace propagation | — | ARCH-OBS-NO-TRACE | — | |
| Observability: log shape drift | — | ARCH-OBS-LOG-SHAPE | — | |
| Observability: metric shape drift | — | ARCH-OBS-METRIC-SHAPE | — | |
| Observability: health/readiness unclear | — | ARCH-OBS-HEALTH | — | |
| Evolution: irreversible change | — | ARCH-EVO-IRREVERSIBLE | — | |
| Evolution: breaking change to published contract | — | ARCH-EVO-BREAK | — | |
| Evolution: orphaned temporary scaffolding | — | ARCH-EVO-ORPHAN-TEMP | — | |
| Testing: mock-the-world | — | ARCH-TEST-MOCK-WORLD | — | |
| Testing: asserting implementation | — | ARCH-TEST-IMPL-ASSERT | — | |
| Testing: drifted mock contract | — | ARCH-TEST-MOCK-CONTRACT | — | |
| Testing: no failure-path test on high-blast-radius boundary | — | ARCH-TEST-NO-FAILURE-PATH | M12 | |
| AI: shim around a library the repo doesn't need | — | ARCH-AI-SHIM | — | |
| AI: compat cruft for callers that don't exist | — | ARCH-AI-COMPAT-CRUFT | — | |
| Subprocess without timeout | — | (part of ARCH-DATA-TIMEOUT family) | M2 | |
| Subprocess / URL audit (shell=True, http) | — | — | M3 | Purely mechanical; `bandit` territory. |
| `sys.exit` outside CLI boundary | — | — | M4 | |
| Non-atomic file write | — | — | M5 | |
| Dict dead writes / overwritten keys | — | — | M6 | |
| Optional parameter sprawl | — | — | M8 | Gets promoted to AP-4-adjacent if the function is also god-sized. |
| Weak hash | — | — | M11 | Purely mechanical. |
| Coverage gaps / orphaned entry | — | — | M12 | |
| Primitive obsession | — | — | P5-7 | Magic numbers, string statuses; no ARCH counterpart unless domain-critical. |
| Redundant / line-by-line comments | — | — | P5-10 | Style-only. |
| Dead code graveyards (commented-out blocks) | — | — | P5-6 | Style-only unless large; large graveyards become AP-4-adjacent. |
| State entanglement (deep prop-drill, effect chains) | — | ARCH-STATE-SHARED (adjacent) | P5-9 | Frontend-specific flavor of state smell; ARCH-STATE-SHARED is its backend cousin. |
| Semantic naming drift (AI-specific) | — | — | P5-11 | Names look valid but obscure intent; requires domain vocabulary review. |
| Documentation drift | — | — | P5-12 | Docs describe behavior that changed; catchable by diffing docs vs. diff. |

---

## Gaps surfaced by this table

The five Josh-quiz examples (W-coded violations from the adversarial
test repository) each have a catalog entry at the structural altitude.
Each was added as a new smell in its owning file, not as a new file.

| W-code | Pattern | ARCH | Lives in |
| --- | --- | --- | --- |
| W9004 | I/O primitive (`open`, `requests`, socket) in pure/domain layer | ARCH-DEP-IO-IN-PURE | [`arch-violations/01-dependency-direction.md`](arch-violations/01-dependency-direction.md) |
| W9010 | Cross-context HTTP call (`requests.post`) in a use-case module | ARCH-DEP-IO-IN-PURE | [`arch-violations/01-dependency-direction.md`](arch-violations/01-dependency-direction.md) |
| W9301 | Constructor-time side effect / direct instantiation of infrastructure | ARCH-BND-EAGER-INIT | [`arch-violations/02-boundary-contracts.md`](arch-violations/02-boundary-contracts.md) |
| W9401 | Domain-entity mutability (mutable `@dataclass`, in-place mutation inside a single flow) | ARCH-STATE-DOMAIN-MUTATION | [`arch-violations/03-state-concurrency.md`](arch-violations/03-state-concurrency.md) |
| W9006 | Law of Demeter / deep attribute chains (`order.user.address.get_zip()`) | ARCH-BND-DEMETER | [`arch-violations/02-boundary-contracts.md`](arch-violations/02-boundary-contracts.md) |

Each new entry was landed at the level of detail house style
requires (Shape / Decidable-at / Why it compounds / Category mapping,
a row in the file's proof-recipe table, and a row in the file's
Decidable-at matrix). Smell-specific good-finding / good-dismissal
few-shots have been added inline with the smell definitions for each
of the four new codes, matching the exemplar pattern in
`01-dependency-direction.md`.

Remaining gap at the **mechanical (M)** altitude: an M-code for
Demeter (`rg`-detectable chain depth) is borderline — depth > 2 is a
weak heuristic by itself. Better left at the structural altitude where
the tests-as-X-ray reasoning lives.

---

## Skills that reference this table

- **`/antiplan`** — Phase 2 challenge loop. When a speculative shape is
  surfaced, cross-reference the structural (ARCH) column to name the
  diff-time consequence the plan is flirting with. Makes the challenge
  concrete: "this AP-1 speculative seam is the design-time precursor
  of ARCH-MOD-PREMATURE; ship the smallest concrete thing first."
- **`pr-review` Lens 6** — Architectural-Drift auditor. When a finding
  is emitted at diff altitude and `plan_present: true`, the AP column
  provides the design-time counterpart to cite — tightens the
  `decidable_at: design` claim.
- **`cleanup`** — Phase 0 + lens mapping. When a mechanical tool (M-code)
  flags a pattern, the structural column tells you whether the finding
  is architectural enough to escalate to a lens, or stays mechanical.

---

## Open questions

These are deferred decisions. None of them blocks daily use of this
table; they shape its next revision.

- **Alias metadata (Stage 2).** Should each source entry carry an
  explicit `aliases:` field (`ARCH-MOD-GOD → aliases: [AP-4, M9, P5-1]`)?
  Benefit: findings become navigable without grepping this file.
  Cost: ~60 entries to touch across three files. Deferred.
- **Physical consolidation (Stage 3).** Move all taxonomies into
  `~/.skills/patterns/{design,structural,mechanical}/`. Breaks existing
  skill loaders; forces shape unification that degrades each category.
  Almost certainly not worth it. Documented here so the question does
  not re-open later.

## Resolved

- **Proof requirement widening (item 2, resolved).** `schemas.md`
  now requires `proof:` for `severity: CRITICAL`, `category:
  Architectural Drift`, or `category: Layer` with `severity: HIGH` or
  `CRITICAL`. Validator function renamed
  `critical_findings_have_proof → structural_findings_have_proof`
  and extended accordingly.
- **Fix-removes-evidence criterion (item 3, resolved).** Lens 6
  checklist widened from 3-of-4 to 4-of-5 with criterion #5:
  "`suggested_fix` eliminates the quoted evidence pattern — it does
  not rename it, relocate it, inject it, or wrap it behind a new
  parameter." `schemas.md` `suggested_fix` bullet updated with the
  same rule for `category: Architectural Drift` and `category: Layer`.
- **AP / P5 counterparts for the new structural codes (resolved).**
  `AP-15` ("I/O in the pure layer") and `AP-16` ("eager construction
  of infrastructure") added to `antiplan/references/anti-patterns.md`.
  `P5-13` ("eager construction at init") and `P5-14` ("mutable domain
  entity / in-place mutation") added to
  `cleanup/quality-rubric.md` Part 5. Demeter left without an M-code
  (documented above).
- **Per-smell good-finding / good-dismissal few-shots (resolved).**
  `ARCH-DEP-IO-IN-PURE`, `ARCH-BND-DEMETER`, `ARCH-BND-EAGER-INIT`,
  and `ARCH-STATE-DOMAIN-MUTATION` now carry their own in-file
  few-shot pair, matching the 01-dependency-direction exemplar.

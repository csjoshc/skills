# Plan — populate arch-violations catalog (files 02–11)

## Context

`~/.skills/reviews/arch-violations/` contains an index, a template, a
saved generator prompt, and one fully-worked exemplar
(`01-dependency-direction.md`). Files 02 through 11 are stubs. This plan
populates them.

The catalog is shared between `pr-review` (Lens 6 — Architectural-Drift
Auditor) and `cleanup` (4 parallel lenses, each owning 2 catalog files).

## Ground rules (do not skip)

Every populated file must:

1. Follow [`TEMPLATE.md`](../reviews/arch-violations/TEMPLATE.md) exactly:
   Smells / Proof recipes / Few-shot: good finding / Few-shot: good
   dismissal / Decidable-at matrix.
2. Match the quality of the exemplar
   [`01-dependency-direction.md`](../reviews/arch-violations/01-dependency-direction.md).
3. Be **language-agnostic** in every "Shape" description. No
   Python/TS/Java/Go/Rust syntax. Describe architectural relationships,
   not token patterns.
4. Carry **reproducible proof recipes** — a command, graph query, log
   pattern, or failing-test type. Prose alone is never proof.
5. Contain a `REVIEW-FINDINGS` YAML block that passes
   `reviews/validate.py --transcript <file>` (fragment mode
   auto-detects). CRITICAL findings require `proof:`.
6. Include a **"good dismissal"** — a realistic situation where the smell
   shape appears but is benign. Prevents reviewer false positives.
7. Stay under **200 lines**. If a category has many smells, keep the 3–5
   most compounding, not all of them.

Severity discipline: reserve CRITICAL for security, data loss, or
production outage risk. Most architectural smells are HIGH or MEDIUM.

## Per-file step sequence

For each of files 02–11:

1. Read these first (READ-ONLY):
   - `/Users/joshc/.skills/reviews/schemas.md`
   - `/Users/joshc/.skills/reviews/runbook.md`
   - `/Users/joshc/.skills/reviews/arch-violations/README.md`
   - `/Users/joshc/.skills/reviews/arch-violations/TEMPLATE.md`
   - `/Users/joshc/.skills/reviews/arch-violations/01-dependency-direction.md`
2. Read the current stub (it has a placeholder structure).
3. Overwrite the stub using the *Catalog section* for that file below.
4. Validate:
   ```
   python3 /Users/joshc/.skills/reviews/validate.py \
     --transcript /Users/joshc/.skills/reviews/arch-violations/<file>.md
   ```
   Fragment mode auto-detects. Must exit 0 before moving to the next file.
5. Never invent catalog content not derived from the source section below.

### Order (suggested, but any order is fine)

The 4 cleanup lenses each own 2 files; completing both files for a lens
before moving to the next keeps context coherent:

- Layer & Dependency lens: 02
- Redundancy & Modularity lens: 08, 11
- Error Handling & State lens: 03, 04
- Data & Security lens: 05, 06
- Shared / pr-review only: 07, 09, 10

---

## Catalog source material (11-point list)

Use the subsection matching each stub file as the *Catalog section* in
the generator prompt.

### 02 — Boundary and contract violations

- **Business logic coupled to transport** — validation, authorization, or
  domain rules living inside HTTP handlers, GraphQL resolvers, or message
  consumers. Can't be reused, can't be tested without the framework.
- **Validation at the wrong boundary** — trusting internal callers (no
  validation at system edge) or re-validating trusted data on every call
  (no edge validation, defensive everywhere).
- **Missing anti-corruption layer around a third-party API or legacy
  system** — vendor types / external schemas flowing directly through the
  codebase. When the vendor changes, the blast radius is the whole app.
- **Public API surface that exposes internals** — optional parameters
  that only make sense given implementation knowledge; return types that
  reveal storage shape; error types that leak stack-trace-level detail.

### 03 — State, concurrency, and lifecycle

- **Shared mutable state across requests/threads/actors** —
  module-level dicts, singletons holding request data, caches without
  invalidation semantics.
- **Race conditions on shared resources** — check-then-act patterns,
  non-atomic read-modify-write, missing locks or transactional boundaries.
- **Resource leaks** — connections/files/sockets opened without
  guaranteed cleanup; background tasks without cancellation;
  subscriptions without teardown.
- **Transactional boundary mistakes** — multi-step operations without a
  transaction, or a transaction that holds a lock across an I/O call to
  an external system.
- **Unbounded queues / retries / recursion** — anything that can grow
  without back-pressure. Silent scalability failure mode.

### 04 — Error handling as architecture

- **Swallowed errors** — `catch { log }`, `except: pass`, `.catch(() =>
  null)` at a layer that can't actually recover. Silent data corruption
  downstream.
- **Catching too broadly** — catching the base exception type and
  proceeding as if nothing happened. Hides bugs that should crash.
- **Fallback-on-failure that masks the root cause** — returning empty
  list on fetch error, returning cached-stale without signaling staleness.
- **Errors crossing a boundary without translation** — raw database
  exceptions bubbling to HTTP layer, vendor SDK errors surfacing to UI.
- **No distinction between expected and unexpected failures** — `AuthError`
  and `NullPointerException` handled by the same catch block.

### 05 — Data layer and integration

- **Unbounded queries** — no LIMIT, no pagination, no cursor. Works in
  dev, breaks at scale.
- **N+1 query patterns** — loops issuing per-row queries. Invisible
  until production data volume.
- **Missing indexes implied by query shape** — filtering or joining on
  unindexed columns in code paths hot enough to matter.
- **Implicit ordering assumptions** — code that depends on row order
  without `ORDER BY`.
- **No idempotency on write paths exposed to retry** — message
  handlers, webhooks, payment flows that can double-apply.
- **Missing timeouts on outbound calls** — any network/subprocess/disk
  call without a bounded deadline.

### 06 — Security at the architectural level

Not CVE-spotting — architectural smells.

- **Authorization logic scattered** — every handler re-implements "can
  this user do this?" instead of a single policy layer. Guaranteed to
  diverge.
- **Trust-boundary confusion** — treating authenticated-user input as
  trusted; passing user-controlled data into templates, shells, queries
  without marking it untrusted.
- **Secrets in code or config committed to the repo** — not just
  hardcoded passwords; also API keys, signing keys, cloud credentials.
- **Missing auth check on a new endpoint** — architecturally
  interesting when the pattern of "every endpoint has X middleware" has
  a gap.
- **Privilege escalation through object references** — endpoints that
  trust an ID from the client without verifying the user owns that
  resource.

### 07 — Observability and operability

- **No correlation ID / trace ID through the request path** — can't
  debug cross-service issues.
- **Logs that don't identify the actor, resource, and outcome** — logs
  useless at 2am during an incident.
- **Metrics at the wrong granularity** — per-request counters where p99
  latency is needed, or vice versa.
- **Missing or misleading health checks** — endpoints that return 200
  while the process is actually broken (e.g. checks DB but not the queue
  it depends on).

### 08 — Modularity, cohesion, and reuse

- **Premature abstraction** — an interface with one implementation,
  defended as "for flexibility." Creates two places to change for every
  change.
- **Duplicate implementations of a cross-cutting concern** — two logger
  setups, two retry policies, two date formatters. Guaranteed drift.
- **God modules / god types** — files or classes that own unrelated
  responsibilities. Merge conflicts, test coupling, unclear ownership.
- **Speculative generality** — parameters no caller uses, strategy
  patterns with one strategy, plugins with one plugin.
- **Feature-flag / config sprawl with no retirement path** — flags
  accumulate forever; the code is simultaneously all versions of itself.

### 09 — Evolution and reversibility

- **Irreversible migrations without a rollback plan** — schema change
  that requires data loss to undo, or a rename deployed to multiple
  services simultaneously.
- **Backwards-incompatible API change without a deprecation path** —
  clients break silently, or have to coordinate deploys atomically.
- **Feature flags without a kill switch path in all dependent layers**
  — can turn it off in the UI but the backend still does the work.
- **"Temporary" solutions with no owner or sunset date** — the ones
  that outlive the team.

### 10 — Testing as a design signal

Not coverage. Testability as an architectural signal.

- **Behavior untestable without mocking the world** — indicates the
  unit under test has too many collaborators; architectural smell, not
  a test smell.
- **Tests that pass by asserting the implementation, not the behavior**
  — any refactor breaks them; the tests prevent change rather than
  enable it.
- **Integration boundaries asserted only in unit tests with mocks** —
  the contract is a fiction; mock drift = production bug.
- **No test covers the failure path a production incident would hit**
  — happy-path-only coverage at a critical boundary.

### 11 — AI-specific architectural violations

Worth calling out because agents produce these at unusually high rates.

- **Parallel implementations** — agent writes a new helper for a job
  the codebase already has, because it didn't search first. Drift
  guaranteed.
- **Shim/adapter layers with no justification** — defensive wrapping
  "just in case." Dead abstraction.
- **Defensive code for scenarios that can't happen** — null checks on
  values the type system guarantees, try/catch around code that can't
  throw. Signals the agent didn't read the surrounding invariants.
- **Re-introducing patterns the project has explicitly rejected** —
  using `any`/`unknown` where the codebase bans it, adding a logger the
  codebase doesn't use, bypassing an established error type.
- **Backwards-compatibility cruft for code that has no users yet** —
  deprecating things that were never published.

---

## Verification

Per file: validator exits 0 in fragment mode.

End-to-end, after all 10 files populated:

```bash
# All catalog files must validate.
for f in /Users/joshc/.skills/reviews/arch-violations/[01][0-9]-*.md; do
  python3 /Users/joshc/.skills/reviews/validate.py --transcript "$f" \
    || { echo "FAIL: $f"; exit 1; }
done

# Skillsmith audit must stay clean (only unrelated orchestrate FAIL).
python3 /Users/joshc/.skills/skillsmith/scripts/skill_audit.py /Users/joshc/.skills
```

Inspect 2–3 populated files manually to confirm:
- "Shape" sentences contain no language-specific syntax.
- "Proof recipes" table cites commands/tests, not prose.
- "Good dismissal" is concrete and contrastive, not generic.
- Severity assignments follow the discipline (CRITICAL reserved for
  security/data/outage).

## Open risks

- **Drift across files if generated in one batch**. If you generate all 10
  in one session, re-read the exemplar between files to anchor quality.
- **Severity inflation**. Architectural smells feel important; resist
  marking everything HIGH+. Revisit the severity column after writing
  each `REVIEW-FINDINGS` block.
- **Proof recipe fabrication**. Don't cite tools you haven't confirmed
  exist (`madge`, `jscpd`, etc. are real — `git scan-auth-deps` is not).
  If uncertain, use a grep/ripgrep pattern.

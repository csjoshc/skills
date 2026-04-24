# Observability and operability

Smells where code looks correct but is operationally dark — an
incident cannot be diagnosed, a deployment cannot be verified, a
dependency cannot be traced. These are architectural because telemetry
is either structurally present or structurally absent; retrofitting is
expensive and almost always incomplete.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (4)

### No correlation or trace ID through the request path

**Shape (language-agnostic):** A request enters at one edge and
traverses multiple internal services or async steps with no identifier
that lets an investigator join logs across hops. Each service's logs
are a separate island.

**Decidable at:** `design` — /antiplan should set the tracing contract
at Phase 2. Emergent correlation-ID plumbing in individual PRs is
always incomplete.

**Why it compounds:** As the number of internal hops grows, the
probability of reconstructing a specific incident drops toward zero.
Each new service inherits the missing-header shape.

**Category mapping:** `category: Architectural Drift` / severity `MEDIUM`
/ `rule_code: ARCH-OBS-NO-TRACE`

---

### Logs missing actor, resource, or outcome

**Shape (language-agnostic):** Log lines describe what code ran
("processing request") without stating who invoked it, what resource
was touched, and what the terminal outcome was (success, which
specific failure class). An incident responder reading the logs at 2am
learns nothing they can act on.

**Decidable at:** `both` — /antiplan should set the structured-log
schema; diff catches violations.

**Why it compounds:** Log formats proliferate as each new code path
invents its own. A future search for "all actions taken by user X"
requires a full re-instrumentation pass.

**Category mapping:** `category: Architectural Drift` / severity `MEDIUM`
/ `rule_code: ARCH-OBS-LOG-SHAPE`

---

### Metrics at the wrong granularity

**Shape (language-agnostic):** A system reports per-request counters
where a percentile is needed (e.g., counting total requests without a
latency histogram), or reports aggregate latency summaries where
per-event granularity is needed. The metric shape does not answer the
questions the system is asked about it.

**Decidable at:** `design` — /antiplan should state what questions the
metrics must answer and choose the matching shape.

**Why it compounds:** Dashboards built on the wrong shape feel
"covered" but cannot detect the actual failure modes. Adding the right
metric later requires a re-deploy and a historical-data gap.

**Category mapping:** `category: Architectural Drift` / severity `LOW` /
`rule_code: ARCH-OBS-METRIC-SHAPE`

---

### Misleading health check

**Shape (language-agnostic):** An endpoint returns 200 while a
dependency the process actually requires is unreachable — the health
check asserts only that the HTTP server is up, or checks one
dependency but not others. Load balancers and deploy health gates
believe the process is healthy when it is not.

**Decidable at:** `diff`

**Why it compounds:** Bad instances stay in rotation during incidents.
Deploys proceed past real failures. Eventual oncall trust in the
health check drops to zero, and it becomes a ritual rather than a
signal.

**Category mapping:** `category: Bug` / severity `MEDIUM` / `rule_code: ARCH-OBS-HEALTH`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| No correlation / trace ID | `rg -n "X-Request-Id\|trace_id\|correlation_id" <dir>/` showing zero matches in outbound-call plumbing, inbound-log emission, or async-enqueue code; OR distributed trace showing broken spans. |
| Log shape missing actor/resource/outcome | `rg -n "log\.\|logger\.\|console\." <dir>/` sampled for presence of `user_id=\|actor=\|resource=\|outcome=`; OR a sample incident transcript where the log cannot answer "who did what?" |
| Wrong metric granularity | Dashboard audit: one `requests_total` counter with no latency histogram; OR `rg -n "\.inc\(\)\|\.incr\(\)\|\.count\(" <dir>/` with no matching histogram instrumentation. |
| Misleading health check | `rg -n "/health\|/healthz\|/livez\|/readyz" <dir>/` showing the handler body; cross-reference with the process's real dependencies (DB, queue, cache). A curl showing 200 while a dependency is down. |

Prose alone never satisfies proof.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Architectural Drift
  lens: observability
  file: src/http/middleware.py
  line: 1
  rule_code: ARCH-OBS-NO-TRACE
  severity: MEDIUM
  source: lens-derived
  decidable_at: design
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    The inbound HTTP middleware does not extract or generate a
    correlation ID, and the outbound HTTP client in
    src/clients/http.py does not propagate one. No log line emitted
    from the worker service references a request ID. An incident
    spanning api → worker cannot be stitched together.
  proof: |
    Plan ARCHITECTURE-DECISIONS block (.plans/observability.md §2)
    specifies "every request carries an X-Request-Id; all services
    log it under `trace_id`; outbound clients forward it." No code
    in this PR implements any part of that contract.
    Reproduce: `rg -n "X-Request-Id|trace_id|correlation_id" src/`
    → zero matches.
  suggested_fix: |
    Add middleware that accepts X-Request-Id on inbound, generates one
    if missing, stores it in request-scoped context, and logs it with
    every record. Have src/clients/http.py forward it on every
    outbound call. Assert presence in one end-to-end test.
```
````

---

## Few-shot: good dismissal

A reviewer sees a handler that logs `log.info("processing")` without
an actor field and flags "log shape missing actor/resource/outcome."
It is **not** a violation when the handler is a pre-authentication
path (e.g., health check, public static file) where the concept of
"actor" doesn't apply, or when the log line is a low-level debug
breadcrumb emitted under a flag that is off in production. The smell
applies to log records that describe business-meaningful operations on
identifiable resources. Similarly, a plain 200 from `/health` is fine
when the check is explicitly a liveness probe (process alive) rather
than a readiness probe (able to serve traffic) — provided the
readiness probe exists separately and is the one the load balancer
consults.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| No correlation / trace ID | ✅ — must mandate tracing contract | ✅ | ✅ |
| Log shape missing actor/resource/outcome | partial — should set log schema | ✅ | ✅ |
| Wrong metric granularity | ✅ — must match metrics to questions | ✅ | ✅ |
| Misleading health check | ❌ — emerges from implementation choices | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot see the code.
When `plan_present: true` and the plan specified the log schema or
tracing contract, pr-review/cleanup emit `category: Architectural Drift`
with `decidable_at: design`.

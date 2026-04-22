# spec-writer Example Outputs

---

## Example A: Ralph-eligible ticket (Orchestra codebase)

**Input:**
`/spec-writer Add a JSONL self-assessment parser for the reflection-3 plugin output`

**Output (abbreviated — shows Ralph-eligible ticket shape):**

```yaml
---
Stage: BUILD
Type: feature
Ralph: true
Ralph-Reason: "7 additive ACs: new parser module + wiring into BUILD event consumer + tests, each grep/pytest-checkable, no bootstrap or cross-cutting changes"
---
```

### SPEC

**One-line purpose**
Parse the reflection-3 JSONL output emitted by opencode subprocesses into a structured self-assessment schema usable by Orchestra's observability layer.

**Requirements**
1. New module `orchestra/observability/self_assessment_parser.py` exposes `parse_self_assessment(events: list[dict]) -> dict | None`
2. Parser extracts `stuck`, `status`, `confidence`, `missing_work` fields from JSONL events matching the reflection-3 schema
3. Returns `None` if no matching event is found (non-fatal)
4. Called from `build_node` after runtime invocation; result recorded via `SelfAssessmentEvent`
5. No mocks — tests use a fixture JSONL file

### Acceptance Criteria → Tests

| AC | Test file / Command | Assertion shape |
|---|---|---|
| AC-1 | `grep -nE '^def parse_self_assessment' orchestra/observability/self_assessment_parser.py` | exit 0 |
| AC-2 | `pytest tests/test_self_assessment_parser.py -k test_parses_valid_reflection3_event` | `result["stuck"] == False` |
| AC-3 | `pytest tests/test_self_assessment_parser.py -k test_returns_none_on_empty_events` | `result is None` |
| AC-4 | `pytest tests/test_self_assessment_parser.py -k test_returns_none_on_missing_schema_key` | `result is None` |
| AC-5 | `grep -nE 'parse_self_assessment' orchestra/nodes/build.py` | exit 0 (wired in) |
| AC-6 | `grep -nE 'class SelfAssessmentEvent' orchestra/observability/gate_events.py` | exit 0 |
| AC-7 | `ruff check orchestra/observability/self_assessment_parser.py orchestra/nodes/build.py` | exit 0 |

**Ralph note:** Each AC is independently verifiable. AC-1 through AC-4 can be checked before AC-5 is wired. No AC depends on a later AC running first. Failure Protocol does NOT mandate full revert — `self_assessment_parser.py` is additive and can be left in place on failure.

---

## Example B: Ralph-ineligible ticket (same codebase)

**Input:**
`/spec-writer Add --plugin flag to opencode wrapper cmd construction`

```yaml
---
Stage: BUILD
Type: feature
Ralph: false
Ralph-Reason: "5 ACs below threshold; 2-file change (wrappers.py + test), one-shot BUILD faster"
---
```

**Ralph note:** Small change, 5 ACs, single logical unit. One-shot BUILD is appropriate. No Ralph overhead justified.

---

## Example C: Generic ticket (non-Orchestra)

**Input:**
`/spec-writer Add a way for users to export their order history as CSV`

### SPEC

**One-line purpose**
Users can download their complete order history as a CSV file from their account settings.

**Users and use cases**
- As a customer, I want to export my order history so that I can keep records for expense reporting.
- As a customer, I want to filter the export by date range so that I only download what I need. `[ASSUMPTION: date range filter is required — remove if out of scope]`

**Requirements**
1. Authenticated users can trigger a CSV export from their account
2. The export includes all orders `[ASSUMPTION: or filtered by date — clarify scope]`
3. The CSV downloads directly to the user's device
4. Large exports do not block the UI `[ASSUMPTION: async generation for exports over 1,000 rows]`

**Acceptance criteria**
```
Given an authenticated user on the account settings page
When they click "Export order history"
Then a CSV file downloads containing all their orders with columns: order_id, date, items, total, status

Given an authenticated user requesting an export
When the export contains more than 1,000 rows [ASSUMPTION]
Then the export is generated asynchronously and the user is notified by email when ready

Given an unauthenticated user
When they attempt to access the export endpoint directly
Then they receive a 401 response
```

### PLAN

**Stack and architecture**
`[ASSUMPTION: REST API with a relational database — adjust endpoint pattern to your framework]`

**API contracts**
- `GET /account/orders/export?from=YYYY-MM-DD&to=YYYY-MM-DD`
- Returns: CSV file stream or 202 Accepted with job ID for async
- Errors: 401 (unauthenticated), 400 (invalid date range), 500 (generation failure)

### TASKS

**Task 1: Export endpoint — synchronous path**

**What to build:** A GET endpoint that accepts optional date range parameters, queries the authenticated user's orders, and streams a CSV response.
**Files likely affected:** `routes/account.js`, `services/orderExport.js` (create), `tests/orderExport.test.js` (create)
**Acceptance criteria:**
1. Returns CSV with correct headers and one row per order
2. Returns 401 if user is not authenticated
3. Returns 400 if date range is invalid
**Dependencies:** none

### Assumptions to review

1. Date range filter is required — Impact: MEDIUM
   Correct this if: the first version should export all orders with no filtering
2. Async generation for exports over 1,000 rows — Impact: HIGH
   Correct this if: your order volumes are low and synchronous is fine
3. REST API pattern — Impact: HIGH
   Correct this if: you're using GraphQL, tRPC, or another pattern

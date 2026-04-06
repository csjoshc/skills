# spec-writer Example Output

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

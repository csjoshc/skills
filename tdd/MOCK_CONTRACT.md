---
name: mock-contract
description: >-
  Catches boundary-mock drift. Every mock of an external dependency (HTTP
  client, DB driver, FS, time, process, queue) must reference a real
  contract artifact — OpenAPI/JSON-schema spec, type definition file,
  recorded trace, or SDK declaration. Also enforces SDK-style mocks (one
  function per operation) over generic conditional mocks. Use on any test
  file that introduces a mock.
---

# mock-contract

Mocks that drift from the real contract cause silent production failures.
A test can stay green for months while the real API evolves underneath.
This skill requires every boundary mock to point at an authoritative
contract source, and re-validates the mock against that source.

## When to invoke

- On any `Write` or `Edit` of a test file that introduces a new mock
- During `tdd` when the red test mocks a boundary
- During `pr-review` Test Analyzer when changed tests include mocks
- On a scheduled cadence via `schedule` skill (nightly contract re-check)

## Which mocks are boundary mocks

Mock these:

- HTTP clients (fetch, axios, httpx, requests)
- DB drivers (pg, mongo, sqlalchemy, prisma)
- File system (fs, pathlib)
- Time sources (Date.now, datetime.now)
- Process spawn (child_process, subprocess)
- Message queues (kafka, rabbitmq, sqs)
- External SDKs (stripe, twilio, aws-sdk)

Do NOT mock these (per `tdd/MOCKING.md`):

- Your own classes or modules
- Internal collaborators
- Pure functions

## Required contract reference

Every boundary mock must have a contract comment immediately above it:

```ts
// contract: ./specs/openapi.yaml#/paths/~1users~1{id}/get
// contract-version: 2026-03-15
vi.mock('@/api/users', () => ({
  getUser: vi.fn().mockResolvedValue({ id: '1', name: 'Alice' })
}));
```

Accepted contract sources (in priority order):

1. OpenAPI / AsyncAPI / GraphQL schema in the repo
2. `*.d.ts` type declaration from the real SDK
3. Recorded HTTP trace (`./traces/*.json` — VCR style)
4. Pact / consumer-driven contract file
5. Explicit TS/Python interface owned by the team
6. Upstream SDK's public type (e.g., `@types/stripe`)

Block any mock with none of these.

## SDK-style mocks required

Prefer per-operation mocks. Reject conditional-logic mocks.

```ts
// BAD — one function, branching per URL
vi.mock('fetch', () => (url) => {
  if (url.includes('/users')) return users;
  if (url.includes('/orders')) return orders;
});

// GOOD — per-operation, each independently replaceable
vi.mock('@/api', () => ({
  getUser: vi.fn(),
  getOrders: vi.fn(),
  createOrder: vi.fn(),
}));
```

Flag any mock whose body contains > 1 `if`/`switch` branching on the
input. That shape is a sign of drift risk — each branch can rot
independently.

## Workflow

### Phase 1: Scan changed test files

```bash
git diff --name-only HEAD~1 | grep -E '\.test\.|test_|_test\.'
```

For each changed test, extract every mock declaration via AST or
regex (`vi.mock`, `jest.mock`, `monkeypatch.setattr`, `patch`,
`unittest.mock.patch`).

### Phase 2: Classify each mock

| Target | Boundary? | Contract required? |
|---|---|---|
| `@/api/*`, `@/services/http/*` | yes (HTTP) | yes |
| `fs`, `pathlib`, `open()` | yes (FS) | yes |
| `Date`, `time.time` | yes (time) | yes — doc the frozen value |
| `@/utils/*` | no (internal) | reject the mock, test the real fn |
| `./helpers/*` | no (internal) | reject the mock |

### Phase 3: Validate contract

For each boundary mock:

1. Locate the contract comment; fail if missing.
2. Resolve the contract path. Fail if the file does not exist.
3. For OpenAPI/JSON-schema: parse, find the operation, validate the
   mock's return shape against the schema.
4. For `.d.ts`: compile the test file with `tsc --noEmit`; shape
   mismatches surface as type errors.
5. For recorded traces: diff the mock response against the trace.

### Phase 4: Report

```markdown
## MOCK-CONTRACT REPORT

| Test | Target | Contract | Status |
|---|---|---|---|
| users.test.ts:42 | @/api/users.getUser | openapi.yaml#/paths/~1users~1{id}/get | OK |
| orders.test.ts:12 | fetch | (missing) | BLOCK — no contract |
| utils.test.ts:8 | @/utils/fmt | (not a boundary) | BLOCK — remove mock, test real fn |
```

## Integration points

- `tdd`: boundary mocks in the red step must pass mock-contract before
  the green step begins.
- `pr-review` Test Analyzer: incorporates mock-contract findings.
- `mutation-critic`: over-mocked tests often survive all mutants; when
  both skills flag the same test, the signal is very strong.
- `schedule`: nightly job re-runs mock-contract across the suite so
  upstream schema changes are caught before they hit prod.

## Hard rules

- Never accept a mock without a contract reference.
- Never accept a mock of internal code. Test the real thing.
- Never silently skip a boundary mock because "the contract file isn't
  there yet." File a ticket to create the contract, block merge.
- Never let conditional-branch mocks ship unless the branching is a
  single line and documented.

## Output contract

```
MOCK-CONTRACT: N mocks scanned, K OK, J blocked, V internal-mock removed
```

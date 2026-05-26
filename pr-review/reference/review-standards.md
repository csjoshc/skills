# review-standards

Project coding standards reference for `pr-review`. Each rule has a code for
citation in review comments.

## Contents

- 1. Function Declarations (FN)
- 2. Data Access (DA)
- 3. Runtime & Language (RT)
- 4. Logging (LG)
- 5. Testing (TS)
- 6. Documentation (DC)
- 7. Naming Conventions (NM)
- 8. React & Frontend (FE)
- 9. Display & Formatting (DD)
- 10. Type Definition Files (TD)
- References

---

## 1. Function Declarations (FN)

**FN-001 — Functions must match interface definitions**
Every new function in an implementation file must have a matching signature
in the corresponding type/interface/header definition file.

**FN-002 — No orphan top-level functions**
All functions must be methods of a class, type, or module — not standalone
functions at file scope, except type definition files or scripts.

**FN-003 — Destructure complex parameters early**
When a function receives an options/config/spec object, destructure it on the
first line after the signature.

**FN-004 — Avoid redundant data fetches**
Flag functions that query the same source multiple times in one function body.

**FN-005 — Spec/options parameter conventions**

- The options/spec parameter should be last and named `spec` or `options`
- Spec types should end in `Spec`; result types should end in `Result`
- Untyped options must have docstrings describing fields, types, and defaults

---

## 2. Data Access (DA)

**DA-001 — No unbounded queries**
Database or API fetch calls must never use unlimited result sets.

**DA-002 — UI-driven limits**
Functions supplying UI grids/tables should receive requested count from the UI,
not hard-code a limit.

**DA-003 — Externalize lookup tables when branches grow**
Mapping logic with more than three case branches that maps stable data
(runtime × role × alias → ref, model_id → endpoint, error_code → message)
must live in a structured data file (`.json` / `.yaml` / `.toml`),
not in inline `case` statements, `match` blocks, or dict literals embedded
in shell / Python / TS source.

The data file is the operator-visible surface: edits land there without
touching the dispatch logic, schema can be linted independently, and
diffs read cleanly during review. Loaders should fail loudly on missing
keys with the available-keys hint.

Bad:

```bash
catalog_source() {
  case "$1,$2,$3" in
    dmr,chat,gemma4-e2b-64k)        echo "hf.co/unsloth/...:Q3_K_M" ;;
    ollama,chat,gemma4-e2b-64k)     echo "gemma4:e2b" ;;
    # … 6 more cases
  esac
}
```

Good — `config/llm-catalog.json` holds the rows; the script reads it via
`python3 -c 'json.load(...)'` and fails with "available aliases for
<runtime>/<role>: …" on miss.

---

## 3. Runtime & Language (RT)

**RT-001 — Target runtime compatibility**
Code must match the project's target runtime compatibility.

**RT-002 — Arrow functions for callbacks**
Use arrow functions for callbacks unless the framework requires `this`.

**RT-003 — Avoid regular expressions**
If the project prohibits regex for security reasons, avoid regex entirely.

**RT-004 — No hardcoded env-specific or cycle-coupled paths in production code**
String literals used as filesystem paths, artifact directories, or proof
roots in production code (not tests) must come from environment variables
or constructor arguments with a stable default — not from inline cycle
slugs, gate IDs, or ticket-named directories.

The failure mode is path rot: a `proof/4G-ui-cycle/` constant works for
one cycle and becomes wrong (or confusing) the moment the gate is
renamed or the ticket closes. Test fixtures inside `tests/` are exempt
(the path *is* the test scope).

Bad:

```ts
const PROOF_DIR = "../proof/4G-ui-cycle";
mkdirSync(PROOF_DIR, { recursive: true });
```

Good:

```ts
const PROOF_DIR = process.env.PROOF_DIR ?? "../proof/chat-stack-smoke";
mkdirSync(PROOF_DIR, { recursive: true });
```

The default name describes the test scope, not the gate that birthed it,
and the env var lets CI / orchestration override per-cycle without
re-editing the source.

Also flag: runtime-specific tokens baked into config filenames that
should be runtime-agnostic — e.g. `agent.local-dmr.yaml` for a config
whose only DMR-specific thing is the current default `base_url`. Rename
to `agent.local.yaml` and let `LLM_RUNTIME` / `LLM_BASE_URL` carry the
runtime distinction.

---

## 4. Logging (LG)

**LG-001 — Use the project logger**
Backend logging must use the designated project logger.

**LG-002 — Frontend logging**
Frontend components must use the project's logging utility.

---

## 5. Testing (TS)

**TS-001 — Test coverage required**
Each new public/exported function must have a corresponding test.

**TS-002 — Test file organization**
Use project naming and location conventions for tests.

**TS-003 — Test data isolation**
Every test creates isolated data and avoids shared mutable state.

**TS-004 — Happy path + error path**
Include both happy-path and error/edge-case tests.

**TS-005 — Specific assertions**
Assert count plus specific values, or error type/message.

**TS-006 — Cleanup after tests**
Tests must clean up created data.

**TS-007 — No mock types**
Use real project types rather than invented mock/stub types.

**TS-008 — Test structure conventions (JavaScript / Jasmine)**

- One `describe`, one `beforeAll`, one `afterAll` per file
- Setup in `beforeAll`
- Store context on `this.ctx`
- Register/unregister spies correctly
- Wait for async queues after mutations

**TS-009 — Test structure conventions (Python / pytest)**

- Plain `def test_*` functions
- Module-level bootstrap fixture
- `try / finally` cleanup
- Descriptive plain `assert` messages

---

## 6. Documentation (DC)

**DC-001 — Docstring formatting**
Docstrings must render descriptions cleanly in tooling.

**DC-002 — Parameter documentation style**
`@param` and `@return` descriptions use sentence fragments, first word
capitalized, ending with a period.

**DC-003 — Untyped parameters**
Untyped parameters must document expected fields, types, and defaults.

**DC-004 — Docstrings explain *why*, not just label**
When a docstring references an internal artifact (ADR ID, design doc,
spec, ticket), the reference must be accompanied by prose that explains
the *rationale* — what the code is doing differently and why — not just
the label. The label alone is unreadable for anyone who doesn't have the
artifact open.

For ADR labels specifically: `ADR-XXX` is a doc *filename* identifier,
not a source-comment identifier. Either drop the label and explain the
rationale, or pair the label with a stable pointer (`docs/ADR-XXX.md`)
plus a one-sentence summary so a cold reader doesn't have to chase the
link to understand the code.

Bad — label-drop:

```python
"""ADR-CHAT-1: ``POST /v1/chat`` returns ``text/event-stream``."""
```

The reader can see the endpoint shape from the signature; the docstring
adds zero information beyond a token they don't know.

Good — rationale-first:

```python
"""Single SSE chat endpoint.

``POST /v1/chat`` emits the locked event-name set
``{text, tool_start, tool_end, done}``. The prior trio (`/v1/chat` JSON,
`/v1/chat/full` JSON, `/v1/chat/stream` SSE) was collapsed into this one
route so the SPA has a single stable target and the SSE framing is
exhaustive.
"""
```

Now the reader understands *why* it's structured this way without
needing the ADR open.

Coverage: this rule applies to docstrings on public surfaces (any
exported function/class/module). Internal helpers can be terser, but
must not contain bare label drops either.

---

## 7. Code Hygiene (HY)

**HY-001 — No dev-workstream artifact references in source comments.**

Source-code comments on a PR targeting `main` must not reference internal
development labels. Forbidden patterns (case-insensitive):

- Ticket numbers: `ticket \d+`, `tickets \d+(-\d+)?`, "per ticket", "this
  ticket"
- Acceptance criteria: `AC-\d+`, `AC \d+`, `AC\d+`
- Gate / orch IDs: `\d+G\d*`, `\d+A\d*`, `\(\d+G\)`, "demo gate"
- Slice IDs: `Slice \d+`, `slice-\d+`, `slice_\d+`
- Anti-pattern codes: `AP-\d+`
- Ticket-file paths: `\.tickets/[^ )"]+`

These labels are temporary local artifacts that point nowhere from a
public branch; they rot as soon as the slice ships. When the rationale is
load-bearing — a divergence from a core package, template, or legacy
implementation — replace the artifact reference with a stable pointer: a
path to an ADR under `docs/`, an RFC URL, or a spec filename. The prose
that remains must pass `/caveman` (no fluff) and `/stop-slop` (no AI
tells).

**Scope:** source-code files only — `.ts`, `.tsx`, `.js`, `.mjs`, `.py`,
`.go`, `.rs`, `.java`, `.kt`, and similar. Comments include line comments,
block comments, docstrings, and JSDoc.

**Excluded from this rule (these legitimately reference the dev workstream):**

- `docs/ADR-*.md` and other ADR / RFC files under `docs/`
- PR descriptions and commit messages
- Files under `.tickets/`, `.plan/`, `.handoff/`
- Filenames or path-string literals that include `ADR-` or `RFC-` (e.g.
  references like `docs/ADR-divergence-slice-3.md` are stable pointers,
  not artifacts)
- Test data fixtures and golden files

**Example violations:**

```python
# BAD: ticket reference in comment
"""Audit logger tests (ticket 250 / ADR-AUDIT-1)."""

# GOOD: stable ADR pointer only
"""Audit logger tests (see ``docs/ADR-AUDIT-1.md``)."""
```

```typescript
// BAD: AC code in comment
// Each row above has a vitest case asserting the error class (AC-2).

// GOOD: rationale only, no AC tag
// Each row is exercised by a forced-failure case in tests/flight-client.test.ts.
```

---

## 8. Naming Conventions (NM)

**NM-001 — Type/class names**
CamelCase with initial capital.

**NM-002 — Field/method names**
camelCase with initial lowercase.

**NM-003 — Acronyms as words**
Spell acronyms as words.

**NM-004 — No redundant prefixes**
Avoid repeating the type name in a field name.

**NM-005 — Verb conventions**

- `create` = persistent state
- `make` = in-memory instance
- `to` / `from` = conversion
- `as` = casting
- `is` = predicate methods
- `for` = lookup methods

**NM-006 — Singular vs plural**
Singular for one value, plural for collections.

---

## 9. React & Frontend (FE)

**FE-001 — One component per file**
Each React component lives in its own file.

**FE-002 — Styling**
Use colocated SCSS, avoid inline styles, and consolidate duplicate classes.

**FE-003 — Icons**
Use the project icon library instead of inline SVG or HTML entities.

**FE-004 — Hooks and memoization**
Minimize hooks; explain why `useCallback` or `useMemo` is needed.

**FE-005 — Component documentation**
Comment interfaces, hooks, and non-obvious logic blocks.

---

## 10. Display & Formatting (DD)

**DD-001 — Decimal rounding**
User-facing decimal metrics must be rounded to 2 decimal places in the backend
unless another format is explicitly required.

---

## 11. Type Definition Files (TD)

**TD-001** — 2-space indentation, no tabs  
**TD-002** — Wrap lines at 120 characters  
**TD-003** — One blank line between declarations  
**TD-004** — Non-private types and fields need `/**` docs  
**TD-005** — Provide `finalVersion` and replacement with `@deprecated`  
**TD-006** — Prefer lambdas over loop blocks; lambda params last  
**TD-007** — Prefer member methods over static methods when the first arg is an instance

---

## References

- C3 Platform Coding Standards
- C3 Coding Guidelines

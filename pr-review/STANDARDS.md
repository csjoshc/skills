# Project Coding Standards

Standards reference for PR review. Each rule has a code for easy citation
in review comments (e.g., "Violates FN-001"). Organized by category.

Adapt this file for your project: remove rules that don't apply, add
project-specific rules in the same format.

---

## 1. Function Declarations (FN)

**FN-001 — Functions must match interface definitions**
Every new function in an implementation file must have a matching signature
in the corresponding type/interface/header definition file.
If a function exists in the implementation but not the definition, flag it
and request it be added. The declaration can be `private` and/or `inline`
if appropriate.

**FN-002 — No orphan top-level functions**
All functions must be methods of a class, type, or module — not standalone
functions at file scope (does not apply to type definition files or scripts).

**FN-003 — Destructure complex parameters early**
When a function receives an options/config/spec object, destructure its
fields on the first line after the signature.

```javascript
// Bad
function process(options) {
  doSomething(options.input, options.format);
}

// Good
function process(options) {
  const { input, format, validate } = options;
  doSomething(input, format);
}
```

**FN-004 — Avoid redundant data fetches**
Flag functions that call fetch/query on the same data source multiple times
within a single function body. Consolidate into a single call.

**FN-005 — Spec/options parameter conventions**
- The options/spec parameter should be last and named `spec` or `options`
- Spec type names should end in "Spec"; result types should end in "Result"
- If an options parameter is untyped (e.g., `json`, `any`), the docstring
  must describe all expected fields, types, and defaults

---

## 2. Data Access (DA)

**DA-001 — No unbounded queries**
Database or API fetch calls must never use unlimited result sets
(e.g., `limit: -1`, no LIMIT clause). Always specify a finite limit.

**DA-002 — UI-driven limits**
Functions that supply data to a UI grid/table should receive the requested
count from the UI component (page size), not hard-code a limit.

---

## 3. Runtime & Language (RT)

**RT-001 — Target runtime compatibility**
Code must be compatible with the project's target runtime. Avoid language
features not supported by the target environment (e.g., ES5 restrictions,
Python 3.8 compatibility).

**RT-002 — Arrow functions for callbacks**
Use arrow functions for callbacks and lambdas.

```javascript
// Good
arr.forEach((v) => { ... });

// Bad
arr.forEach(function(v) { ... });
```

**Exception:** Test framework callbacks that rely on `this` context binding
(e.g., Jasmine `describe`, `it`, `beforeAll`) must use `function() {}`.

**RT-003 — Avoid regular expressions**
If the project prohibits regex for security reasons, avoid regex entirely.
Use string methods or dedicated parsing libraries.

---

## 4. Logging (LG)

**LG-001 — Use the project logger**
All backend logging must use the project's designated logger
(e.g., PerLogger, winston, pino, structlog). Direct `console.log`,
`console.error`, `print()`, or raw `log()` calls are not allowed.

**LG-002 — Frontend logging**
Frontend components must use the project's logging utility (e.g.,
`initLogger`). No `console.log` or `console.error`.

---

## 5. Testing (TS)

**TS-001 — Test coverage required**
Each new public/exported function must have a corresponding test. Generate
tests only for functions defined in the type/interface — not internal helpers.

**TS-002 — Test file organization**
- Naming: `test_<Type>_<function>.<ext>` or `<function>.test.<ext>`
- Location mirrors source structure: `<package>/test/<runtime>/<Type>/`
- Each function gets its own test file (or describe block)

**TS-003 — Test data isolation**
Every test must create its own isolated data. Never rely on pre-existing
seed data or shared mutable state between tests.

**TS-004 — Happy path + error path**
Include both a "happy path" test and at least one error/edge-case test per
function.

**TS-005 — Specific assertions**
- For collections: verify both count and specific values
- For errors: verify the error type/message, not just that an error occurred
- Use descriptive assertion messages

```python
# Bad
assert result is not None

# Good
assert len(result) == 2, f"Expected 2 rows, got {len(result)}"
assert result[0]["id"] == expected_id
```

**TS-006 — Cleanup after tests**
Tests must clean up all created data in teardown (`afterAll`, `finally`).
Never leave test data behind.

**TS-007 — No mock types**
Do not create mock/stub types. Use real types from the project. If testing
a derived type, use an existing type that already extends it.

**TS-008 — Test structure conventions (JavaScript / Jasmine)**
- One `describe`, one `beforeAll`, one `afterAll` per file
- All data setup in `beforeAll` — no entity creation inside `it` blocks
- Store test context on `this.ctx` in `beforeAll`
- Create spies in `beforeAll`, unregister in `afterAll`
- After mutations triggering async processing, wait for queues before asserting

**TS-009 — Test structure conventions (Python / pytest)**
- Use plain `def test_*` functions (no classes)
- Include module-level bootstrap fixture
- Use `try / finally` to guarantee cleanup
- Assertions use plain `assert` with descriptive failure messages

---

## 6. Documentation (DC)

**DC-001 — Docstring formatting**
Docstrings must be formatted so descriptions appear in tooling/IDE output.
Do not include inline type annotations that suppress description display.

```
// Bad — description hidden in some tools
@param {string} modelRunId - id of the model run

// Good — description always visible
@param modelRunId
   Id of the model run.
```

**DC-002 — Parameter documentation style**
- `@param` and `@return` descriptions: sentence fragments, first word
  capitalized, ending with a period
- Do not repeat "required/optional" — the signature conveys that
- Place `@see` declarations last, after `@return`
- Use `@link` for inline references

**DC-003 — Untyped parameters**
If a parameter is untyped (e.g., `spec: json`, `options: any`), the
docstring must describe all expected fields, their types, and defaults.

---

## 7. Naming Conventions (NM)

**NM-001 — Type/class names**: CamelCase with initial capital.
`ModelRun`, `FetchSpec`

**NM-002 — Field/method names**: camelCase with initial lowercase.
`modelRunId`, `fetchData`

**NM-003 — Acronyms as words**: Spell acronyms as words.
`TsNormalizer` not `TSNormalizer`

**NM-004 — No redundant prefixes**: Don't repeat the type name in fields.
`person.name` not `person.personName`

**NM-005 — Verb conventions**:
- `create` = persistent state (database record, file)
- `make` = in-memory instance
- `to` / `from` = conversion between types
- `as` = casting
- `is` prefix for predicate methods; no prefix for boolean data fields
- `for` prefix for lookup methods

**NM-006 — Singular vs plural**: Singular for single values, plural for
collections.

---

## 8. React & Frontend (FE)

**FE-001 — One component per file**
Every React component in its own file. Before creating a new component,
check if an existing one covers the use case.

**FE-002 — Styling**
- Use SCSS files colocated with the component in a folder
- No inline styles
- No duplicate CSS classes — combine into a single reusable class

**FE-003 — Icons**
Use the project's icon library (e.g., FontAwesome) instead of inline SVGs
or HTML symbol entities.

**FE-004 — Hooks and memoization**
- Minimize hook usage; prefer prop drilling over new hooks when reasonable
- When using `useCallback` or `useMemo`, include a comment explaining why
  memoization is needed

**FE-005 — Component documentation**
Interfaces, hooks, and non-obvious logic blocks within React components
should be commented.

---

## 9. Display & Formatting (DD)

**DD-001 — Decimal rounding**
User-facing decimal metrics must be rounded to 2 decimal places in the
backend, unless a different format is explicitly specified.

---

## 10. Type Definition Files (TD)

**TD-001** — 2-space indentation, no tabs

**TD-002** — Wrap lines at 120 characters

**TD-003** — One blank line between field/function declarations

**TD-004** — All non-private types and fields must have a `/**` doc comment

**TD-005** — Provide `finalVersion` and replacement with `@deprecated`

**TD-006** — Prefer lambdas over loop blocks; place lambda parameters last

**TD-007** — Prefer member methods over static methods when the first
argument is an instance of the type

---

## References

- [C3 Platform Coding Standards (PS codes)](https://docs.c3.ai/docs/platform/8.8/topic/coding-standards)
- [C3 Coding Guidelines (prose)](https://docs.c3.ai/docs/platform/8.8/topic/coding-guidelines)

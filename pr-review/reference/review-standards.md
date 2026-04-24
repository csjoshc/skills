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

---

## 3. Runtime & Language (RT)

**RT-001 — Target runtime compatibility**
Code must match the project's target runtime compatibility.

**RT-002 — Arrow functions for callbacks**
Use arrow functions for callbacks unless the framework requires `this`.

**RT-003 — Avoid regular expressions**
If the project prohibits regex for security reasons, avoid regex entirely.

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

---

## 7. Naming Conventions (NM)

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

## 8. React & Frontend (FE)

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

## 9. Display & Formatting (DD)

**DD-001 — Decimal rounding**
User-facing decimal metrics must be rounded to 2 decimal places in the backend
unless another format is explicitly required.

---

## 10. Type Definition Files (TD)

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

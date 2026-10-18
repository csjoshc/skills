# UI Testing Guide

Project-agnostic workflow for testing web UIs with Playwright and documenting defects.

## When to Use

- Testing frontend UI functionality
- Documenting visual bugs and usability issues
- Verifying state synchronization across views
- Checking form inputs, tabs, and navigation

For live inspection of console, network and rendering in a real browser, use `browser`.

## Approach

### Option A: run existing E2E tests (preferred)

Most projects already have Playwright tests. Run those first.

```bash
cd react-app  # or frontend/, ui/
npm run e2e
```

Accessibility audit:
```bash
env -u CI npm run e2e:audit
```

Environment variables:
```bash
PLAYWRIGHT_FRONTEND_URL=http://localhost:3000  # frontend URL
PLAYWRIGHT_BACKEND_URL=http://localhost:8000   # backend API URL
```

### Option B: write a custom Playwright script

Only when existing tests do not cover the requested behavior. Setup order: discover the frontend URL from project config, start required services, then verify the frontend responds. Playwright commands and a script skeleton: [SETUP.md](SETUP.md). Selector patterns: [SELECTORS.md](SELECTORS.md).

## Test artifact naming

Proof directories, screenshot folders, and console-log dumps for
playwright/cypress/jest e2e tests are committed-tree paths the moment
a config or spec hardcodes them. Pick names by these rules:

- **Name the test scope, not the gate.** `proof/stack-smoke/`
  not `proof/gate-7-cycle/`. The directory tells a future reader
  *what the test does*; gate slugs rot the moment the gate is
  renamed.
- **Make the root env-overridable.** The default is the
  scope-based name; CI / orchestration sets `PROOF_DIR=...` to
  land per-cycle archival paths without re-editing source.
  ```ts
  const PROOF_DIR = process.env.PROOF_DIR ?? "../proof/stack-smoke";
  ```
- **Mirror this in the smoke script.** If a shell harness drives
  the e2e, it reads `${PROOF_ROOT:-…}` with the same scope-based
  default and exports `PROOF_DIR="${PROOF_ROOT}"` for the
  child playwright run.
- **Filenames inside the dir describe the artifact**, not the
  cycle. `login-flow.png`, `playwright.json`, `console.txt` — not
  `gate-7-cycle-login-flow.png`.

A playwright config with a hardcoded gate-slug `PROOF_DIR` is the
canonical AP-24 failure (see `~/.skills/challenge/references/anti-patterns.md`).

## Bug documentation

When the user requests a persistent defect report, write it to `fixes/NN-bug-description.md` using [BUG_REPORT.md](BUG_REPORT.md). Otherwise report concise evidence in the response.

## Companion files

Read only when the situation matches:

- [SETUP.md](SETUP.md): starting services and custom Playwright scripts
- [SELECTORS.md](SELECTORS.md): writing locators
- [BUG_REPORT.md](BUG_REPORT.md): documenting a defect
- [CHECKLIST.md](CHECKLIST.md): coverage checklist (navigation, forms, display, interactions) and troubleshooting table

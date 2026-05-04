---
name: ci-cd
description: >-
  CI/CD pipeline design and triage. Use when setting up GitHub Actions,
  fixing a broken pipeline, or tuning quality gates and deploy strategy.
  Not for one-off command runs (use cmd-cli).
---

<!-- imported from addyosmani/agent-skills ci-cd-and-automation -->

# CI/CD and Automation

Automate quality gates so no change reaches production without passing tests, lint, types, and build.

**Shift Left.** A bug caught in lint costs minutes; in prod, hours. Move checks upstream.

**Faster is Safer.** Smaller batches reduce risk. 3 changes are easier to debug than 30.

## When to Use

| Trigger | Action |
|---|---|
| New project | Set up CI from day one |
| Adding a check | Wire it into the existing pipeline |
| CI failure | Triage; don't disable |
| Deploy strategy | Staging + rollback + flags |

## Quality Gate Pipeline

```
PR opened → LINT → TYPE CHECK → UNIT TESTS → BUILD → INTEGRATION → E2E (optional) → SECURITY AUDIT → BUNDLE SIZE → ready for review
```

No gate is skipped. Lint fails → fix lint, don't disable the rule. Test fails → fix the code, don't skip the test.

## GitHub Actions — Basic CI

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm test -- --coverage
      - run: npm run build
      - run: npm audit --audit-level=high
```

### With Postgres integration tests

```yaml
integration:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_DB: testdb
        POSTGRES_USER: ci_user
        POSTGRES_PASSWORD: ${{ secrets.CI_DB_PASSWORD }}
      ports: ['5432:5432']
      options: >-
        --health-cmd pg_isready --health-interval 10s
        --health-timeout 5s --health-retries 5
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with: { node-version: '22', cache: 'npm' }
    - run: npm ci
    - run: npx prisma migrate deploy
      env:
        DATABASE_URL: postgresql://ci_user:${{ secrets.CI_DB_PASSWORD }}@localhost:5432/testdb
    - run: npm run test:integration
      env:
        DATABASE_URL: postgresql://ci_user:${{ secrets.CI_DB_PASSWORD }}@localhost:5432/testdb
```

> Use GitHub Secrets even for CI-only test DBs.

### E2E

```yaml
e2e:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with: { node-version: '22', cache: 'npm' }
    - run: npm ci
    - run: npx playwright install --with-deps chromium
    - run: npm run build
    - run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: playwright-report
        path: playwright-report/
```

## Feeding Failures to Agents

| Failure | Agent action |
|---|---|
| Lint | `npm run lint --fix` and commit |
| Type | Read error location, fix the type |
| Test | Follow `debug` skill |
| Build | Check config and dependencies |

Paste the specific error, not 500 lines of log.

## Deployment

**Preview deploys per PR** (Vercel/Netlify/etc.).

**Feature flags** decouple deploy from release:

```typescript
if (featureFlags.isEnabled('new-checkout-flow', { userId })) {
  return renderNewCheckout();
}
return renderLegacyCheckout();
```

Lifecycle: create → test → canary → full → remove flag + dead code. Set a cleanup date at creation.

**Staged rollout:** PR merged → staging (auto) → manual verification → production → 15-min error window → rollback if needed.

**Rollback workflow:**

```yaml
name: Rollback
on:
  workflow_dispatch:
    inputs:
      version: { description: 'Version to rollback to', required: true }
jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - run: npx vercel rollback ${{ inputs.version }}
```

## Environment

```
.env.example  → committed (template)
.env          → NOT committed
.env.test     → committed (no real secrets)
CI secrets    → GitHub Secrets / vault
Prod secrets  → deployment platform / vault
```

CI never holds production secrets.

## Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule: { interval: weekly }
    open-pull-requests-limit: 5
```

**Build Cop.** When CI breaks, the Build Cop fixes or reverts — not the original author. Prevents broken-build accumulation.

**PR checks.** Required reviews, required status checks, no force-push to main, auto-merge when approved + green.

## Optimization (when pipeline >10 min)

| Strategy | Impact |
|---|---|
| Cache dependencies | High |
| Parallel jobs (lint/typecheck/test/build split) | High |
| Path filters (skip unrelated jobs) | Medium |
| Matrix shard test suites | Medium |
| Drop slow tests from critical path | Medium |
| Larger runners | Low |

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "CI is too slow" | Optimize, don't skip. 5 min prevents hours of debugging. |
| "This change is trivial, skip CI" | Trivial changes break builds. CI is fast for them anyway. |
| "Test is flaky, just re-run" | Flaky tests mask real bugs. Fix the flake. |
| "We'll add CI later" | Projects without CI accumulate broken states. Day one. |
| "Manual testing is enough" | Doesn't scale, isn't repeatable. |

## Red Flags

- No CI pipeline
- Failures ignored or silenced
- Tests disabled to make pipeline pass
- Production deploys without staging
- No rollback mechanism
- Secrets in code or CI config
- Long CI times with no optimization effort

## Verification

- [ ] All gates present (lint, types, tests, build, audit)
- [ ] Runs on every PR and push to main
- [ ] Failures block merge (branch protection)
- [ ] Failures feed back into the loop
- [ ] Secrets in vault, not code
- [ ] Rollback exists
- [ ] Pipeline under 10 min

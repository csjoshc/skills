---
name: test-ui
description: Tests web application UIs and documents functional or visual defects across forms, tabs, navigation, and stateful interactions. Use when validating frontend behavior, reproducing UI bugs, or running manual/e2e verification workflows.
---

# Test UI Skill

## Overview

Testing web application UIs requires proper service setup and using Playwright. This skill provides a project-agnostic workflow.

## When to Use

- Testing frontend UI functionality
- Documenting visual bugs and usability issues
- Verifying state synchronization across views
- Checking form inputs, tabs, and navigation

## Two Approaches

### Option A: Run Existing E2E Tests (Preferred)

Most projects have existing Playwright tests. Run those first.

```bash
cd react-app  # or frontend/, ui/
npm run e2e
```

For accessibility audit:
```bash
env -u CI npm run e2e:audit
```

**Environment variables:**
```bash
PLAYWRIGHT_FRONTEND_URL=http://localhost:3000  # frontend URL
PLAYWRIGHT_BACKEND_URL=http://localhost:8000   # backend API URL
```

### Option B: Write Custom Playwright Script

When existing tests don't cover what you need.

## Prerequisites

### Playwright Availability

**If project uses Playwright (has it in node_modules):**
```bash
cd /path/to/project
node -e "require('playwright')" && echo "Playwright available"
```

**If not installed, install it:**
```bash
npm install -D playwright
npx playwright install chromium  # install browser
```

## Setup Workflow

### Step 1: Discover Service URLs

Find the frontend URL from project config:

```bash
# Check vite.config, package.json scripts, .env
grep -r "localhost" package.json vite.config.* .env* 2>/dev/null | head -10
```

Common ports: `3000`, `5173`, `8080`, `5174`

### Step 2: Start Backend Services

```bash
# Check for startup scripts first
ls dev.py start.py main.py server.py 2>/dev/null

# Or start directly (adapt to project)
cd src
python -m uvicorn src.server:app --port 8000 &
```

### Step 3: Start Frontend

```bash
cd /path/to/project
npm run dev   # or: vite, next dev, npm start, etc.
```

### Step 4: Verify

```bash
curl http://localhost:3000 | head -5
```

## Testing with Playwright

### Run Existing Tests First

Always check if the project already has tests:

```bash
cd react-app
npm run e2e              # standard tests
npm run e2e:audit        # with accessibility audit
```

### Custom Test Script

When existing tests don't cover what you need:

```javascript
// test-ui.mjs - create in project root
import { chromium } from 'playwright';

const FRONTEND_URL = 'http://localhost:3000';  // UPDATE THIS

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

await page.goto(`${FRONTEND_URL}/route`, { 
  waitUntil: 'networkidle',
  timeout: 30000 
});

await page.screenshot({ path: '/tmp/screenshot.png', fullPage: true });

// Interact with UI
await page.getByLabel('Field Name').fill('value');
await page.locator('button').filter({ hasText: 'Submit' }).click();

await browser.close();
```

```bash
cd /path/to/project
node test-ui.mjs
```

## LLM Prompting Template

When asking an LLM to run e2e tests:

```
Run the e2e tests for this project.

Prerequisites:
1. Backend running on port 8000 (or set PLAYWRIGHT_BACKEND_URL)
2. Frontend on port 3000 (or set PLAYWRIGHT_FRONTEND_URL)

Commands:
cd react-app
npm run e2e

For accessibility audit:
env -u CI npm run e2e:audit

Expected output:
- Test results (pass/fail)
- Screenshots on failure
- Console error report
```

## Playwright Selectors Reference

```javascript
// By label (best for forms)
page.getByLabel('Email')
page.getByLabel('Password', { exact: true })

// By placeholder
page.getByPlaceholder('Search...')

// By text
page.locator('button').filter({ hasText: 'Submit' })
page.locator('summary').filter({ hasText: 'Advanced' })

// By role
page.getByRole('button', { name: 'Save' })
page.getByRole('heading', { name: 'Dashboard' })
page.getByRole('option', { name: 'Dark Mode' })

// By test ID
page.getByTestId('submit-btn')

// CSS
page.locator('.card-header')
page.locator('#main-content')

// Details/Summary (collapsible sections)
page.locator('details').filter({ hasText: 'Section Title' }).locator('summary').click()
```

## Bug Documentation Format

Create bug reports in `fixes/` directory:

**Filename:** `NN-bug-description.md`

```markdown
# Bug Report: [Short Title]

**Date:** YYYY-MM-DD
**Severity:** Critical/High/Medium/Low
**Component:** [Component Name]
**Route:** /page-route

## Summary

One paragraph description.

## Screenshots

See `/tmp/screenshot-name.png`

## Current Behavior

What happens now.

## Expected Behavior

What should happen.

## Steps to Reproduce

1. Navigate to page
2. Click element
3. Observe bug

## Code Reference

```tsx
// File.tsx:line
```

## Impact

Who is affected.

## Suggested Fix

(Optional)
```

## Testing Checklist

### Navigation
- [ ] All routes load
- [ ] Menu/sidebar navigation works
- [ ] Tab switching preserves state
- [ ] Browser back/forward

### Forms
- [ ] Text inputs
- [ ] Select dropdowns
- [ ] Range sliders
- [ ] Checkboxes/toggles
- [ ] Form validation

### Display
- [ ] Empty states
- [ ] Loading states
- [ ] Error handling
- [ ] Data lists

### Interactions
- [ ] Buttons trigger actions
- [ ] Modals
- [ ] Tooltips
- [ ] Theme toggle
- [ ] Collapsible sections (details/summary)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Cannot find module 'playwright'` | `npm install -D playwright` |
| Browser not installed | `npx playwright install chromium` |
| Page blank | Check frontend is running (`curl <url>`) |
| API 404 | Start backend, check CORS settings |
| Timeout | Increase `timeout: 60000` |
| Selector not found | Use more specific locator |
| Test hangs | Check backend is running |

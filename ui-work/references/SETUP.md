# Test UI Setup

## Contents

- Playwright availability
- Step 1-4: discover URLs, start backend and frontend, verify
- Custom Playwright script
- LLM prompting template

## Playwright availability

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

## Custom Playwright script

When existing tests don't cover what you need:

```javascript
// ui-check.mjs - create in project root
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
node ui-check.mjs
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

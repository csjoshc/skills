---
name: chrome-devtools
description: Test, validate, and debug frontend changes in a real browser. Take screenshots, measure performance, check accessibility, automate interactions, and capture network traffic.
license: MIT
compatibility: opencode
metadata:
  audience: frontend-developers
  use-case: browser-testing
---

## TL;DR (Quick Start)

Use Chrome DevTools for browser-based testing, debugging, and validation of frontend changes. Requires chrome-devtools-mcp installed in opencode.json.

**When to use:** Browser testing, UI validation, performance measurement, accessibility checks, network analysis.

**Invocation:** Configure MCP server, then use tool calls like `navigate_page`, `take_screenshot`, `click`.

## Decision Tree

Use this skill when you need to:

1. **Is this a browser-based task?**
   - YES → Continue
   - NO → Use other testing skills

2. **What type of browser task?**
   - Visual validation → `take_screenshot`, `resize_page`
   - Accessibility → `take_snapshot`
   - Performance → `performance_start_trace`, `performance_analyze_insight`
   - Network → `list_network_requests`, `get_network_request`
   - Interaction → `click`, `fill`, `hover`
   - Debugging → `evaluate_script`, `get_console_message`

3. **Isolate mode required?**
   - YES → Use `--isolated=true` flag
   - NO → Standard connection

## Overview

This skill enables browser-based testing and validation of frontend changes using Chrome DevTools Protocol through the chrome-devtools-mcp server.

## Prerequisites

Ensure the chrome-devtools-mcp server is installed. Add this to your `opencode.json`:

```json
{
  "mcp": {
    "chrome-devtools": {
      "type": "local",
      "command": ["npx", "chrome-devtools-mcp@latest", "--isolated=true", "--viewport=1920x1080"]
    }
  }
}
```

## Available Tools

### Input Automation
- `click` - Click elements
- `drag` - Drag and drop
- `fill` - Fill input fields
- `fill_form` - Fill entire forms
- `hover` - Hover over elements
- `press_key` - Press keyboard keys
- `upload_file` - Upload files

### Navigation
- `navigate_page` - Go to a URL
- `new_page` - Open new tab
- `close_page` - Close tabs
- `select_page` - Switch tabs
- `list_pages` - List all tabs
- `wait_for` - Wait for elements/conditions

### Screenshot & Visual
- `take_screenshot` - Full page screenshot
- `take_snapshot` - Accessibility tree snapshot

### Performance
- `performance_start_trace` - Start performance trace
- `performance_stop_trace` - Stop trace
- `performance_analyze_insight` - Analyze Core Web Vitals

### Network
- `list_network_requests` - List all network requests
- `get_network_request` - Get request/response details

### Emulation
- `resize_page` - Resize viewport
- `emulate_network` - Throttle network (3G, 4G)
- `emulate_cpu` - Throttle CPU

### Debugging
- `evaluate_script` - Run JavaScript
- `get_console_message` - Get console logs
- `list_console_messages` - List all console messages
- `handle_dialog` - Handle alerts/confirms

## Usage Examples

### Test a URL
```
Navigate to http://localhost:3000 and take a screenshot
```

### Measure Performance
```
Run a performance trace on the homepage and identify bottlenecks
```

### Check Accessibility
```
Take an accessibility snapshot of the login form
```

### Validate UI Changes
```
Click the submit button, wait for the response, and take a screenshot
```

### Network Analysis
```
Navigate to the dashboard and export all network requests as HAR
```

## Core Web Vitals Targets

| Metric | Good | Poor |
|--------|------|------|
| INP | ≤200ms | >500ms |
| LCP | ≤2.5s | >4s |
| CLS | ≤0.1 | >0.25 |

## Best Practices

- Use `--isolated=true` for security (temporary browser profile)
- Test on multiple viewport sizes (mobile, tablet, desktop)
- Always check console for JavaScript errors
- Validate accessibility on every major UI change

## Assumptions & Escalation

- **Tier 1 (reversible):** Page rendering differences — proceed, capture screenshot, flag for review
- **Tier 2 (performance):** Performance regressions — check baseline, block if budget exceeded
- **Tier 3 (security):** Navigating to suspicious third-party domains — always block

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.

# UI Evidence (Phase 3A)

## Contents

- When to capture
- In Cursor (IDE browser)
- Screen recording
- Screenshot requirements
- Ephemeral commit pattern
- Terminal agent
- Minimum UI evidence

## 3A: UI Evidence (frontend changes)

**Goal:** Attach visual documentation of the UI changes to the PR. This is MANDATORY for UI-heavy PRs — an agent MUST NOT skip this step.

> ⚠️ **CRITICAL:** If the PR touches any UI (components, styles, pages, themes), you MUST capture visual evidence. Skipping this makes review harder and delays merging.

**When to capture:**
- Any visual change (new component, style change, theme change)
- Form/input changes (empty, filled, error states)
- Modal/dialog changes
- Navigation/flow changes
- Dark mode/light mode changes
- Responsive layout changes

**In Cursor (IDE browser available):**

```
Checklist:
- [ ] Navigate to the running app using browser tools (browser_navigate)
- [ ] Lock browser (browser_lock)
- [ ] Walk through each affected user flow, taking screenshots at key states
- [ ] For theme changes: capture both light and dark mode
- [ ] For form changes: show empty, filled, and error states
- [ ] For new components: show all visual states
- [ ] Unlock browser (browser_unlock)
- [ ] Collect screenshots into PR description as inline images
```

**Screen recording (preferred for complex flows):**
```bash
# Use Chrome DevTools MCP or cursor's built-in recording
# Capture: full user flow from start to finish
# Include: all interactions, state changes, edge cases
```

**Screenshot requirements:**
1. Screenshot of change in default state (REQUIRED)
2. Dark mode screenshot if theme exists (REQUIRED if applicable)
3. Interactive states: empty → filled → error (REQUIRED for forms)
4. Before/after comparison if refactoring

Upload screenshots to the PR using the **ephemeral commit** pattern:

```bash
# The ephemeral commit pattern:
# 1. Commit evidence files to .evidence/ and push
# 2. Capture the commit SHA (pinned URL survives forever)
# 3. Remove .evidence/ in the next commit and push
# 4. Use raw.githubusercontent.com/{owner}/{repo}/{SHA}/.evidence/{file} in PR body
#
# Why it works: the "add" commit is an ancestor of HEAD, so GitHub never
# garbage-collects it. The SHA-pinned URL renders images inline permanently,
# even after the file is deleted from the branch tip.

# Step 1: Save screenshots to .evidence/ in the repo root
mkdir -p .evidence
cp /tmp/screenshot-dark.png .evidence/
cp /tmp/screenshot-light.png .evidence/

# Step 2: Force-add (overrides .gitignore) and commit
git add -f .evidence/
git commit -m "evidence: PR screenshots [skip ci]"

# Step 3: Capture the SHA and push
EVIDENCE_SHA=$(git rev-parse HEAD)
git push

# Step 4: Remove evidence and push again
git rm -r .evidence/
git commit -m "chore: remove evidence files"
git push

# Step 5: Build image URLs from the pinned SHA
# Pattern: https://raw.githubusercontent.com/{owner}/{repo}/{EVIDENCE_SHA}/.evidence/{filename}
# Example:
#   https://raw.githubusercontent.com/acme/app/a1b2c3d/.evidence/dashboard-dark.png

# Step 6: Embed in PR body
gh pr edit <PR_NUMBER> --body "$(cat <<'EOF'
## Evidence
![Dark mode](https://raw.githubusercontent.com/{owner}/{repo}/${EVIDENCE_SHA}/.evidence/dashboard-dark.png)
![Light mode](https://raw.githubusercontent.com/{owner}/{repo}/${EVIDENCE_SHA}/.evidence/dashboard-light.png)
EOF
)"
```

> **Tip:** Add `.evidence/` to `.gitignore` so evidence files are ignored by default.
> The flow uses `git add -f` to override the ignore for the ephemeral commit.

**In terminal agent (no IDE browser):**

```bash
# Start a recording session with Chrome DevTools Protocol
# Or use the harness's chrome-devtools MCP tools
# CRITICAL: Do NOT skip this step - start dev server if needed
# Save screenshots to /tmp/, then use the ephemeral commit pattern above.
```

**Minimum UI evidence for ANY frontend PR:**
1. Screenshot or description of the change in default state (REQUIRED)
2. If dark mode exists: both themes shown (REQUIRED if applicable)
3. If interactive: key interaction states documented (REQUIRED if applicable)
4. Screen recording for complex flows (RECOMMENDED)

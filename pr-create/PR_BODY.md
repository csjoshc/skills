# PR Body Template (Phase 4)

## PR creation

```bash
gh pr create --title "<type>(<scope>): <summary>" --body "$(cat <<'EOF'
## Summary

<1-3 bullet points explaining WHAT changed and WHY>

## Changes

<grouped list of file changes by category>

## Evidence

## UI Validation
<screenshots, recordings, or manual validation steps>

## Test Results
```
<paste from /tmp/test-results.txt>
```

## Coverage
```
<paste from /tmp/coverage.txt>
```

## Test Plan

- [ ] <specific thing to verify>
- [ ] <specific thing to verify>

EOF
)"
```

## Editing PR body after creation (for attaching evidence)

If you need to create the PR first then add evidence:

```bash
# Create PR first
gh pr create --title "..." --body "## Summary\n\n..."

# Collect evidence...

# Then update the body
gh pr edit <PR_NUMBER> --body "$(cat <<'EOF'
<full updated body with evidence>
EOF
)"
```

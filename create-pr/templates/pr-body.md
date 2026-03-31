# PR Body Template

## Standard PR Body

```markdown
## Summary

<1-3 bullet points explaining WHAT changed and WHY>

## Changes

<grouped list of file changes by category>

## Evidence

### UI Validation
<screenshots, recordings, or manual validation steps>

### Test Results
```
<test output>
```

### Coverage
```
<coverage output>
```

## Test Plan

- [ ] <specific thing to verify>
- [ ] <specific thing to verify>
```

## Ephemeral Commit Pattern

Use to embed images in PR description without polluting the codebase:

```bash
# 1. Save screenshots to .evidence/ in repo root
mkdir -p .evidence
cp /tmp/screenshot.png .evidence/

# 2. Force-add and commit
git add -f .evidence/
git commit -m "evidence: PR screenshots [skip ci]"

# 3. Capture SHA and push
EVIDENCE_SHA=$(git rev-parse HEAD)
git push

# 4. Remove evidence and push again
git rm -r .evidence/
git commit -m "chore: remove evidence files"
git push

# 5. Build image URLs from pinned SHA
# Pattern: https://raw.githubusercontent.com/{owner}/{repo}/{EVIDENCE_SHA}/.evidence/{filename}

# 6. Embed in PR body
gh pr edit <PR_NUMBER> --body "$(cat <<'EOF'
## Evidence
![Screenshot](https://raw.githubusercontent.com/{owner}/{repo}/${EVIDENCE_SHA}/.evidence/screenshot.png)
EOF
)"
```

Add `.evidence/` to `.gitignore` so evidence files are ignored by default.

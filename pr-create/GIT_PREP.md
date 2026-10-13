# Git Preparation and Commit Details (Phases 1-2)

## Branch from dirty main

When on `main` (or `master`) with local changes not on remote:

```bash
# Stage changes
git add -A

# Create descriptive branch name from the changes
# Pattern: <type>/<short-description>
# Types: feat, fix, refactor, style, docs, test, chore
git checkout -b <type>/<short-description>
```

Branch name rules:
- Lowercase, hyphens only (no spaces, underscores, or uppercase)
- Max 50 chars
- Derive from the actual diff content, not a generic name
- Examples: `feat/theme-migration`, `fix/date-picker-dark-mode`, `refactor/api-error-handling`

## Already on feature branch

If already on a feature branch, just verify it's up to date with remote main:

```bash
git fetch origin
git log --oneline origin/main..HEAD  # show what will be in the PR
```

## Commit and push

```bash
git add -A
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<body — explain WHY, not WHAT>
EOF
)"
git push -u origin HEAD
```

Commit message conventions:
- First line: `type(scope): summary` under 72 chars
- Body: explain the motivation, not a line-by-line changelog
- Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`

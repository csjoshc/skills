# Git Preparation and Commit Details (Phases 1-2)

## Portable GitHub authentication

`github-second` is machine-local, not mandatory.
`Could not resolve hostname github-second` does not prove GitHub access is unavailable.

1. Check the actual Git, SSH and `gh` executables and homes where Git runs.
   Windows and WSL need not share aliases, keys or sessions; verify only the execution environment.
2. Confirm intended host, account, owner/repository, visibility and feature branch.
   Inspect effective fetch/push URLs with `git remote get-url --all origin` and `git remote get-url --push --all origin`; redact credentials.
   Check `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT`; changing URLs can change alias-based `includeIf` identity selection.
3. Reuse working access; a missing alias permits existing HTTPS or SSH access to the same verified target.
   For HTTPS/`gh`, check `gh api user --jq .login` and `gh repo view OWNER/REPO --json nameWithOwner,isPrivate,viewerPermission` against the intended account, repository, visibility and required write permission.
   Verify Git's credential helper uses that account, or command-scope a helper reset plus `gh auth git-credential`; a `gh` login alone is insufficient.
   For SSH, verify the authenticated GitHub user; `ssh -T` may return 1 with a successful greeting.
   Check `git ls-remote <verified-url>` through the chosen transport; public read access proves neither identity nor write permission.
4. Keep account selection, including `GH_CONFIG_DIR`, scoped consistently across verification and Git/`gh` operations, using native shell syntax.
   Never globally switch accounts or copy credentials between machines/environments; ask before login, persistent Git/SSH edits or remote changes.
   Never print secrets.
5. Push only the feature branch with explicit approval; retain hooks and default-branch/force-push protections.
   A one-shot URL avoids remote edits but leaves the stored remote/upstream unchanged.
   Use `--repo OWNER/REPO` for PR operations in the verified account context.

Public-repo testing must not require private work skills, credentials, VPN or accounts.
Keep private overlays, internal instructions and work-only logs out of public commits, forks and PR evidence.
If publishing is blocked, continue credential-free tests, preserve the branch/evidence, report work-only checks as not run, and request only the missing auth/configuration action.
Reverify access afterward; testing success is not push/PR completion.

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

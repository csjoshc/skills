#!/usr/bin/env bash
# PreToolUse (shell): halt git commit / gh pr create while CLAIM_UNVERIFIED.md exists at repo root
# Mode: halt (exit 2; harnesses relay stderr to the agent)
. "$(dirname "$0")/lib/hook-input.sh"
CMD=$(hook_field command)

# Match real invocations (incl. `git -C dir commit`), not `git commit-tree` or quoted text.
GIT_COMMIT='(^|[;&|(]|[[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+commit([[:space:]]|$)'
GH_PR='(^|[;&|(]|[[:space:]])gh[[:space:]]+pr[[:space:]]+create([[:space:]]|$)'
printf '%s' "$CMD" | grep -Eq "$GIT_COMMIT|$GH_PR" || exit 0

hooks_disabled && exit 0

ROOT=$(git -C "$(hook_project_root)" rev-parse --show-toplevel 2>/dev/null || hook_project_root)
CLAIM="$ROOT/CLAIM_UNVERIFIED.md"
if [ -f "$CLAIM" ]; then
  echo "BLOCKED [verify-claim-gate]: $CLAIM exists (a verify-claim run found unproven claims)." >&2
  echo "Produce the evidence and re-run verify-claim, or ask the user for 'override: <reason>'." >&2
  exit 2
fi
exit 0

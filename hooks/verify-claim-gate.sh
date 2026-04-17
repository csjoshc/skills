#!/usr/bin/env bash
# PreToolUse: Bash — halt if CLAIM_UNVERIFIED.md exists before git commit or gh pr create
# Mode: halt (exit 2)
INPUT=$(cat)
CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

# Only gate on commit / pr create
case "$CMD" in
  *"git commit"*|*"gh pr create"*) ;;
  *) exit 0 ;;
esac

# Bypass
[ -f ".claude/hooks-disabled" ] && exit 0

CLAIM=$(find "${CLAUDE_PROJECT_DIR:-.}" -name "CLAIM_UNVERIFIED.md" -maxdepth 4 2>/dev/null | head -1)
if [ -n "$CLAIM" ]; then
  echo "BLOCKED [verify-claim-gate]: CLAIM_UNVERIFIED.md found at $CLAIM"
  echo "Run /verify-claim to clear it. Type 'override: <reason>' to bypass."
  exit 2
fi
exit 0

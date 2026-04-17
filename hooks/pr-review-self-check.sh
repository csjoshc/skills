#!/usr/bin/env bash
# PreToolUse: Bash — advisory reminder to run /pr-review before gh pr create
# Mode: advisory (exit 0, prints message)
INPUT=$(cat)
CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

case "$CMD" in
  *"gh pr create"*) ;;
  *) exit 0 ;;
esac

[ -f ".claude/hooks-disabled" ] && exit 0

echo "ADVISORY [pr-review-self-check]: About to create PR. Have you run /pr-review on this branch?"
exit 0

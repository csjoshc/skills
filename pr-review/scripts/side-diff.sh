#!/usr/bin/env bash
# Open a git diff beside the agent's pane so the user can read it while the agent talks.
# Usage: side-diff.sh <rev-range>   (run from inside the repo, e.g. side-diff.sh main...)
# Uses difftastic when installed, else plain git diff. Output and exit codes are side-pane.sh's.
set -euo pipefail

range=${1:?usage: side-diff.sh <rev-range>}
cd "$(git rev-parse --show-toplevel)"
git rev-parse "$range" >/dev/null 2>&1 || { echo "side-diff: unknown revision in '$range'" >&2; exit 1; }

view="git diff $(printf %q "$range")"
# GIT_EXTERNAL_DIFF, not difftool: it works without any gitconfig and keeps git's pager.
command -v difft >/dev/null && view="GIT_EXTERNAL_DIFF=difft $view"
# -P resolves the skill-dir symlinks (~/.claude/skills/pr-review) back to ~/.skills.
exec "$(cd -P "$(dirname "$0")/../../shared/scripts" && pwd)/side-pane.sh" run "$view"

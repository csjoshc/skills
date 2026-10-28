#!/usr/bin/env bash
# Open a git diff beside the agent's pane so the user can read it while the agent talks.
# Usage: side-diff.sh <rev-range>   (run from inside the repo, e.g. side-diff.sh main...)
# Uses difftastic when installed, else plain git diff. Output and exit codes are side-pane.sh's.
set -euo pipefail

# --view runs inside the new pane. difft lays out columns once at its start width, so a resized
# pane keeps the old layout under less; re-render on SIGWINCH instead (scroll resets to the top).
if [ "${1:-}" = --view ]; then
	range=$2 pager='' resized=0
	trap 'resized=1; [ -n "$pager" ] && kill "$pager" 2>/dev/null' WINCH
	while :; do
		resized=0
		DFT_COLOR=always DFT_WIDTH=$(tput cols) GIT_EXTERNAL_DIFF=difft \
			git --no-pager diff "$range" | less -R &
		pager=$!
		# wait returns early on a trapped signal; keep waiting until less really exits.
		while kill -0 "$pager" 2>/dev/null; do wait "$pager" || true; done
		[ "$resized" = 1 ] || exit 0
		sleep 0.2 # a divider drag sends a burst of resizes; let it settle first
	done
fi

range=${1:?usage: side-diff.sh <rev-range>}
cd "$(git rev-parse --show-toplevel)"
git rev-parse "$range" >/dev/null 2>&1 || { echo "side-diff: unknown revision in '$range'" >&2; exit 1; }

# Plain git diff output reflows in less on its own; only difft needs the re-render loop.
view="git diff $(printf %q "$range")"
command -v difft >/dev/null && view="$(printf %q "$(cd -P "$(dirname "$0")" && pwd)/side-diff.sh") --view $(printf %q "$range")"
exec "$(cd -P "$(dirname "$0")" && pwd)/side-pane.sh" run "$view"

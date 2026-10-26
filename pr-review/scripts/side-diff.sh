#!/usr/bin/env bash
# Open a git diff beside the agent's pane so the user can read it while the agent talks.
# Usage: side-diff.sh <rev-range>   (run from inside the repo, e.g. side-diff.sh main...)
# Uses difftastic when installed, else plain git diff. Prints where it opened; exit 1 = nothing opened.
set -euo pipefail

range=${1:?usage: side-diff.sh <rev-range>}
repo=$(git rev-parse --show-toplevel)
git rev-parse "$range" >/dev/null 2>&1 || { echo "side-diff: unknown revision in '$range'" >&2; exit 1; }

view="git diff $(printf %q "$range")"
# GIT_EXTERNAL_DIFF, not difftool: it works without any gitconfig and keeps git's pager.
command -v difft >/dev/null && view="GIT_EXTERNAL_DIFF=difft $view"
sh=${SHELL:-/bin/sh}
# The trailing shell keeps the pane open after the pager quits.
run="cd $(printf %q "$repo") && $view; exec $(printf %q "$sh")"

if [ -n "${WEZTERM_PANE:-}" ] && command -v wezterm >/dev/null; then
  pane=$(wezterm cli split-pane --pane-id "$WEZTERM_PANE" --right --percent 50 -- "$sh" -lc "$run")
  wezterm cli activate-pane --pane-id "$WEZTERM_PANE"
  echo "side-diff: WezTerm pane $pane"
elif [ -n "${TMUX:-}" ]; then
  tmux split-window -h -d -c "$repo" "$sh -lc $(printf %q "$run")"
  echo "side-diff: tmux pane"
elif [ -n "${ITERM_SESSION_ID:-}" ]; then
  # ITERM_SESSION_ID is "w0t0p0:<uuid>"; the uuid is the AppleScript session id.
  osascript - "${ITERM_SESSION_ID##*:}" "$run" <<'EOF'
on run argv
  tell application "iTerm2"
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          if id of s is (item 1 of argv) then
            tell s to set p to (split vertically with default profile)
            tell p to write text (item 2 of argv)
            tell s to select
            return
          end if
        end repeat
      end repeat
    end repeat
  end tell
end run
EOF
  echo "side-diff: iTerm2 split"
elif [ "$(uname)" = Darwin ]; then
  # Outside a known terminal (IDE, desktop app): a new Terminal.app window.
  osascript -e 'on run argv' -e 'tell application "Terminal" to do script (item 1 of argv)' -e 'end run' "$run" >/dev/null
  echo "side-diff: Terminal.app window"
else
  echo "side-diff: no supported terminal; run this yourself:" >&2
  echo "  $run" >&2
  exit 1
fi

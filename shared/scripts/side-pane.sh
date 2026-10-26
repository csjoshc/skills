#!/usr/bin/env bash
# Open a pane beside the agent's, starting in $PWD.
#   run   <cmd>  runs cmd there and keeps the pane open afterwards.
#   stage <cmd>  types cmd without Enter, so the user reviews and runs it (merges, sudo, auth).
# Prints "side-pane: <where>"; exit 1 = nothing opened (the command is printed instead).
set -euo pipefail

mode=${1:-} cmd=${2:-}
case $mode in run|stage) ;; *) echo "usage: side-pane.sh run|stage <cmd>" >&2; exit 2 ;; esac
[ -n "$cmd" ] || { echo "side-pane: empty command" >&2; exit 2; }
# A typed newline is an Enter, so staged text must be one line or it would run unreviewed.
if [ "$mode" = stage ] && [[ $cmd == *$'\n'* || $cmd == *$'\r'* ]]; then
  echo "side-pane: stage takes a single line" >&2; exit 2
fi
sh=${SHELL:-/bin/sh}
held="$cmd; exec $(printf %q "$sh")"

# Typing before the prompt draws makes the tty echo the text once above it; wait up to 3s.
wait_for_prompt() {
  for _ in $(seq 30); do "$@" 2>/dev/null | grep -q '[^[:space:]]' && return; sleep 0.1; done
}

if [ -n "${WEZTERM_PANE:-}" ] && command -v wezterm >/dev/null; then
  split=(wezterm cli split-pane --pane-id "$WEZTERM_PANE" --right --percent 50 --cwd "$PWD")
  if [ "$mode" = run ]; then
    pane=$("${split[@]}" -- "$sh" -lc "$held")
  else
    pane=$("${split[@]}")
    wait_for_prompt wezterm cli get-text --pane-id "$pane"
    printf '%s' "$cmd" | wezterm cli send-text --pane-id "$pane" --no-paste
  fi
  wezterm cli activate-pane --pane-id "$WEZTERM_PANE"
  echo "side-pane: WezTerm pane $pane ($mode)"
elif [ -n "${TMUX:-}" ]; then
  if [ "$mode" = run ]; then
    tmux split-window -h -d -c "$PWD" "$sh -lc $(printf %q "$held")"
  else
    pane=$(tmux split-window -h -d -c "$PWD" -P -F '#{pane_id}')
    wait_for_prompt tmux capture-pane -p -t "$pane"
    tmux send-keys -t "$pane" -l "$cmd"
  fi
  echo "side-pane: tmux pane ($mode)"
elif [ -n "${ITERM_SESSION_ID:-}" ]; then
  # ITERM_SESSION_ID is "w0t0p0:<uuid>"; the uuid is the AppleScript session id.
  osascript - "${ITERM_SESSION_ID##*:}" "cd $(printf %q "$PWD") && clear" "$cmd" "$mode" <<'EOF'
on run argv
  tell application "iTerm2"
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          if id of s is (item 1 of argv) then
            tell s to set p to (split vertically with default profile)
            tell p to write text (item 2 of argv)
            tell p to write text (item 3 of argv) newline ((item 4 of argv) is "run")
            tell s to select
            return
          end if
        end repeat
      end repeat
    end repeat
  end tell
end run
EOF
  echo "side-pane: iTerm2 split ($mode)"
elif [ "$(uname)" = Darwin ] && [ "$mode" = run ]; then
  # Outside a known terminal (IDE, desktop app): a new Terminal.app window.
  osascript -e 'on run argv' -e 'tell application "Terminal" to do script (item 1 of argv)' -e 'end run' \
    "cd $(printf %q "$PWD") && $cmd" >/dev/null
  echo "side-pane: Terminal.app window (run)"
elif [ "$(uname)" = Darwin ]; then
  # Terminal.app can only run a command, never type one, so staging falls back to the clipboard.
  printf '%s' "$cmd" | pbcopy
  echo "side-pane: copied to clipboard (stage); paste it into a terminal"
else
  echo "side-pane: no supported terminal; run this yourself:" >&2
  echo "  $cmd" >&2
  exit 1
fi

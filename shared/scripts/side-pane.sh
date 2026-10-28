#!/usr/bin/env bash
# Open a pane beside the agent's, starting in $PWD.
#   run   <cmd>  runs cmd there and keeps the pane open afterwards.
#   stage <cmd>  types cmd without Enter, so the user reviews and runs it (merges, sudo, auth).
#   close <id>   closes a pane an earlier call opened, in the same terminal; quiet if it is gone.
# Prints "side-pane: <terminal> <id> (<mode>)"; exit 1 = nothing opened (the command is printed).
set -euo pipefail

mode=${1:-} cmd=${2:-}
case $mode in run|stage|close) ;; *) echo "usage: side-pane.sh run|stage <cmd> | close <id>" >&2; exit 2 ;; esac
[ -n "$cmd" ] || { echo "side-pane: empty command" >&2; exit 2; }
# A typed newline is an Enter, so staged text must be one line or it would run unreviewed.
if [ "$mode" = stage ] && [[ $cmd == *$'\n'* || $cmd == *$'\r'* ]]; then
  echo "side-pane: stage takes a single line" >&2; exit 2
fi

if [ "$mode" = close ]; then
  if [ -n "${WEZTERM_PANE:-}" ]; then wezterm cli kill-pane --pane-id "$cmd"
  elif [ -n "${TMUX:-}" ]; then tmux kill-pane -t "$cmd"
  elif [ -n "${ITERM_SESSION_ID:-}" ]; then
    osascript - "$cmd" <<'EOF'
on run argv
  tell application "iTerm2"
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          if id of s is (item 1 of argv) then
            close s
            return
          end if
        end repeat
      end repeat
    end repeat
  end tell
end run
EOF
  fi 2>/dev/null || true
  exit 0
fi

sh=${SHELL:-/bin/sh}
held="$cmd; exec $(printf %q "$sh")"

# Typing before the prompt draws makes the tty echo the text once above it; wait up to 3s.
wait_for_prompt() {
  for _ in $(seq 30); do "$@" 2>/dev/null | grep -q '[^[:space:]]' && return; sleep 0.1; done
}

if [ -n "${WEZTERM_PANE:-}" ] && command -v wezterm >/dev/null; then
  # The split focuses the new pane and activate-pane also switches tabs, so remember where the
  # user really was (maybe another tab) and go back there, not to the agent's pane.
  focused=$(wezterm cli list-clients --format json 2>/dev/null | sed -n 's/.*"focused_pane_id": *\([0-9]*\).*/\1/p' | head -1)
  split=(wezterm cli split-pane --pane-id "$WEZTERM_PANE" --right --percent 50 --cwd "$PWD")
  if [ "$mode" = run ]; then
    pane=$("${split[@]}" -- "$sh" -lc "$held")
  else
    pane=$("${split[@]}")
    wait_for_prompt wezterm cli get-text --pane-id "$pane"
    printf '%s' "$cmd" | wezterm cli send-text --pane-id "$pane" --no-paste
  fi
  wezterm cli activate-pane --pane-id "${focused:-$WEZTERM_PANE}"
  echo "side-pane: WezTerm pane $pane ($mode)"
elif [ -n "${TMUX:-}" ]; then
  if [ "$mode" = run ]; then
    pane=$(tmux split-window -h -d -c "$PWD" -P -F '#{pane_id}' "$sh -lc $(printf %q "$held")")
  else
    pane=$(tmux split-window -h -d -c "$PWD" -P -F '#{pane_id}')
    wait_for_prompt tmux capture-pane -p -t "$pane"
    tmux send-keys -t "$pane" -l "$cmd"
  fi
  echo "side-pane: tmux pane $pane ($mode)"
elif [ -n "${ITERM_SESSION_ID:-}" ]; then
  # ITERM_SESSION_ID is "w0t0p0:<uuid>"; the uuid is the AppleScript session id.
  pane=$(osascript - "${ITERM_SESSION_ID##*:}" "cd $(printf %q "$PWD") && clear" "$cmd" "$mode" <<'EOF'
on run argv
  tell application "iTerm2"
    -- Splitting selects the new session and select also switches tabs, so put focus back
    -- where the user was, not on the agent session.
    set orig to current session of current window
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          if id of s is (item 1 of argv) then
            tell s to set p to (split vertically with default profile)
            tell p to write text (item 2 of argv)
            tell p to write text (item 3 of argv) newline ((item 4 of argv) is "run")
            tell orig to select
            return id of p
          end if
        end repeat
      end repeat
    end repeat
  end tell
end run
EOF
)
  echo "side-pane: iTerm2 session $pane ($mode)"
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

#!/usr/bin/env bash
# Stop hook: when a worktree has unpushed commits the user has not seen, open its diff beside the
# agent (side-diff.sh). One pane per worktree: a newer commit replaces the old pane in place.
# Never blocks the agent: always exits 0 and does the work in the background.
# Off: AGENT_DIFF_PANE=0. Skips sessions outside WezTerm, tmux or iTerm2.
[[ -z ${DIFF_PANE_CWD:-} ]] && input=$(cat)
[[ ${AGENT_DIFF_PANE:-1} == 0 ]] && exit 0
[[ -n ${WEZTERM_PANE:-}${TMUX:-}${ITERM_SESSION_ID:-} ]] || exit 0

scripts=$(cd -P "$(dirname "$0")/../shared/scripts" && pwd)
side_diff=${DIFF_PANE_SIDE_DIFF:-$scripts/side-diff.sh}
side_pane=${DIFF_PANE_SIDE_PANE:-$scripts/side-pane.sh}
state=${DIFF_PANE_STATE:-${XDG_STATE_HOME:-$HOME/.local/state}/agent-diff-pane}
recent=${DIFF_PANE_RECENT_SECS:-1800} # older unpushed work is someone's parked branch, not news

cwd=${DIFF_PANE_CWD:-$(printf '%s' "${input:-}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("cwd",""))' 2>/dev/null)}
cwd=${cwd:-${DEVIN_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$PWD}}}
git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1 || exit 0

show() {
  mkdir -p "$state"
  # Two sessions stopping at once must not both open a pane for the same commit. A run killed
  # mid-way leaves its lock behind, so a lock older than a minute is taken over.
  if ! mkdir "$state/lock" 2>/dev/null; then
    [[ -n $(find "$state/lock" -maxdepth 0 -mmin +1 2>/dev/null) ]] || return 0
    rmdir "$state/lock" 2>/dev/null && mkdir "$state/lock" 2>/dev/null || return 0
  fi
  trap 'rmdir "$state/lock"' RETURN
  local base path branch line key seen head pane now
  base=$(git -C "$cwd" symbolic-ref -q --short refs/remotes/origin/HEAD || echo origin/main)
  now=$(date +%s)
  while IFS= read -r line; do
    case $line in
      "worktree "*) path=${line#worktree } branch='' ;;
      "branch refs/heads/"*) branch=${line#branch refs/heads/} ;;
      '')
        [[ -n $branch && $branch != "${base#origin/}" ]] || continue
        head=$(git -C "$path" rev-parse HEAD 2>/dev/null) || continue
        (( now - $(git -C "$path" log -1 --format=%ct) < recent )) || continue
        if git -C "$path" rev-parse -q --verify '@{u}' >/dev/null; then
          [[ -n $(git -C "$path" rev-list '@{u}..HEAD') ]] || continue
        else
          [[ -n $(git -C "$path" rev-list "$base..HEAD") ]] || continue
        fi
        key=$state/$(printf '%s' "$path" | shasum | cut -c1-16)
        seen=$(cat "$key" 2>/dev/null)
        [[ ${seen%% *} == "$head" ]] && continue
        [[ -n ${seen#* } && $seen == *" "* ]] && "$side_pane" close "${seen#* }" >/dev/null 2>&1
        pane=$(cd "$path" && "$side_diff" "$base...$branch" 2>/dev/null | awk '/^side-pane:/ {print $(NF-1)}')
        [[ -n $pane ]] && echo "$head $pane" >"$key"
        branch='' ;;
    esac
  done < <(git -C "$cwd" worktree list --porcelain; echo)
}

if [[ -n ${DIFF_PANE_SYNC:-} ]]; then show; exit 0; fi
# devin -p exits right after Stop and kills the hook's process group. posix_spawn starts the run
# already in its own session, so no kill can land before it detaches.
DIFF_PANE_SYNC=1 DIFF_PANE_CWD=$cwd python3 -c 'import os, sys; os.posix_spawn(sys.argv[1], sys.argv[1:], os.environ, setsid=True, file_actions=[(os.POSIX_SPAWN_OPEN, fd, os.devnull, os.O_RDWR, 0) for fd in (0, 1, 2)])' "$0"
exit 0

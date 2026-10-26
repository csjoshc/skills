#!/usr/bin/env bash
# Tests for hooks/diff-pane.sh against a throwaway origin, with side-pane calls recorded by a stub.
set -u
here=$(cd "$(dirname "$0")" && pwd)
hook=$here/diff-pane.sh
pass=0
failures=()
check() { if [[ $2 -eq 0 ]]; then pass=$((pass + 1)); else failures+=("$1"); fi; }

tmp=$(cd "$(mktemp -d)" && pwd -P)
trap 'rm -rf "$tmp"' EXIT
printf '[user]\n\tname = t\n\temail = t@t\n[init]\n\tdefaultBranch = main\n' >"$tmp/gitconfig"
export GIT_CONFIG_GLOBAL=$tmp/gitconfig GIT_CONFIG_NOSYSTEM=1
# The stub stands in for side-diff.sh and side-pane.sh close: it logs and hands out pane ids.
cat >"$tmp/stub" <<'STUB'
#!/usr/bin/env bash
n=$(( $(wc -l <"$STUB_LOG") + 1 ))
echo "$(basename "$0") $* @ $PWD" >>"$STUB_LOG"
[[ $1 == close ]] || echo "side-pane: Fake pane $n (run)"
STUB
chmod +x "$tmp/stub"
ln -s "$tmp/stub" "$tmp/side-diff" && ln -s "$tmp/stub" "$tmp/side-pane"
export STUB_LOG=$tmp/log DIFF_PANE_SIDE_DIFF=$tmp/side-diff DIFF_PANE_SIDE_PANE=$tmp/side-pane
export DIFF_PANE_STATE=$tmp/state DIFF_PANE_SYNC=1 WEZTERM_PANE=1
: >"$STUB_LOG"
fire() { echo '{"stop_hook_active": false}' | (cd "$tmp/repo" && "$hook"); }
opens() { grep -c '^side-diff' "$STUB_LOG"; }
commit() { echo "$2" >"$1/$2"; git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q --bare --template= "$tmp/origin.git"
git clone -q --template= "$tmp/origin.git" "$tmp/repo" 2>/dev/null
commit "$tmp/repo" base && git -C "$tmp/repo" push -q -u origin main 2>/dev/null
git -C "$tmp/repo" remote set-head origin main

fire
check "nothing to show, nothing opened" "$([[ $(opens) == 0 ]]; echo $?)"

git -C "$tmp/repo" worktree add -q -b feat "$tmp/wt" && commit "$tmp/wt" a
fire
check "unpushed commit opens one diff" "$([[ $(opens) == 1 ]]; echo $?)"
check "diff covers the branch against origin" "$(grep -q "^side-diff origin/main...feat @ $tmp/wt" "$STUB_LOG"; echo $?)"
fire
check "same commit does not open again" "$([[ $(opens) == 1 ]]; echo $?)"

commit "$tmp/wt" b
fire
check "new commit replaces the old pane" "$([[ $(opens) == 2 ]] && grep -q '^side-pane close 1 ' "$STUB_LOG"; echo $?)"

git -C "$tmp/wt" push -q -u origin feat 2>/dev/null
commit "$tmp/wt" c && git -C "$tmp/wt" push -q 2>/dev/null
fire
check "pushed branch opens nothing" "$([[ $(opens) == 2 ]]; echo $?)"

commit "$tmp/wt" d
AGENT_DIFF_PANE=0 fire
check "off switch opens nothing" "$([[ $(opens) == 2 ]]; echo $?)"

git -C "$tmp/repo" worktree add -q -b old "$tmp/wt-old"
echo o >"$tmp/wt-old/o" && git -C "$tmp/wt-old" add -A
GIT_COMMITTER_DATE="$(( $(date +%s) - 7200 )) +0000" git -C "$tmp/wt-old" commit -qm old && check "stale fixture committed" 0
: >"$STUB_LOG" && rm -rf "$DIFF_PANE_STATE"
fire
check "a stale unpushed branch is left alone" "$(! grep -q 'origin/main...old' "$STUB_LOG"; echo $?)"

: >"$STUB_LOG" && rm -rf "$DIFF_PANE_STATE"
WEZTERM_PANE='' TMUX='' ITERM_SESSION_ID='' fire
check "no supported terminal, nothing opened" "$([[ $(opens) == 0 ]]; echo $?)"

out=$(echo '{}' | (cd "$tmp" && "$hook"); echo "rc=$?")
check "outside a repo it exits 0 quietly" "$([[ $out == rc=0 ]]; echo $?)"

echo "DIFF PANE TEST: $pass passed, ${#failures[@]} failed"
for f in ${failures[@]+"${failures[@]}"}; do echo "  FAIL: $f"; done
[[ ${#failures[@]} -eq 0 ]]

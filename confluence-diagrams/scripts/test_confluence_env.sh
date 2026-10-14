#!/bin/bash
# Run: bash ~/.skills/confluence-diagrams/scripts/test_confluence_env.sh
# Uses fake values and a temp config; no network.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"
printf '{"mcpServers":{"atlassian":{"env":{"CONFLUENCE_URL":"https://cfg.example","CONFLUENCE_USERNAME":"cfg-user","CONFLUENCE_API_TOKEN":"file-token"}}}}' > "$T/cfg.json"
fail=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }
run() { env -i HOME="$T" PATH="$PATH" MCP_CONFIG_PATH="$T/cfg.json" "$@" \
  bash -c ". '$HERE/confluence_env.sh' && echo \"\$CONFLUENCE_URL|\$CONFLUENCE_USERNAME|\$CONFLUENCE_API_TOKEN\""; }

check "env wins over file" \
  "$(run CONFLUENCE_URL=https://env.example CONFLUENCE_USERNAME=env-user CONFLUENCE_API_TOKEN=env-token 2>&1)" \
  "https://env.example|env-user|env-token"
check "url and user fall back to file, token from env" \
  "$(run CONFLUENCE_API_TOKEN=env-token 2>&1)" "https://cfg.example|cfg-user|env-token"
out="$(run 2>&1)"; rc=$?
check "token in file is ignored" "$(echo "$out" | grep -c 'missing: CONFLUENCE_API_TOKEN')" "1"
check "error points at bootstrap" "$(echo "$out" | grep -c './bootstrap.sh --secrets')" "1"
check "error points at work.env" "$(echo "$out" | grep -c 'work.env')" "1"
check "error never prints the file token" "$(echo "$out" | grep -c file-token)" "0"
rm -rf "$T"
exit $fail

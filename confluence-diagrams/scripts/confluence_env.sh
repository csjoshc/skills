# Source me: . confluence_env.sh
# Sets CONFLUENCE_URL, CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN, or prints why not and returns 1.
# The token comes only from the environment (work.env); URL and username may fall back to the
# non-secret entries in the mcp-cli config.

_cd_cfg="${MCP_CONFIG_PATH:-$HOME/.config/mcp/mcp_servers.json}"

_cd_cfg_value() {
  [ -r "$_cd_cfg" ] || return 0
  python3 -I -c '
import json, sys
try:
    print(json.load(open(sys.argv[1]))["mcpServers"]["atlassian"]["env"].get(sys.argv[2], ""))
except Exception:
    pass' "$_cd_cfg" "$1"
}

_cd_missing=""
[ -n "${CONFLUENCE_URL:-}" ] || CONFLUENCE_URL="$(_cd_cfg_value CONFLUENCE_URL)"
[ -n "${CONFLUENCE_USERNAME:-}" ] || CONFLUENCE_USERNAME="$(_cd_cfg_value CONFLUENCE_USERNAME)"
for _cd_v in CONFLUENCE_URL CONFLUENCE_USERNAME CONFLUENCE_API_TOKEN; do
  eval "[ -n \"\${$_cd_v:-}\" ]" || _cd_missing="$_cd_missing $_cd_v"
done

if [ -n "$_cd_missing" ]; then
  echo "confluence-diagrams: missing:$_cd_missing" >&2
  echo "Set them in ~/.config/secrets/work.env (run ./bootstrap.sh --secrets in ~/bootstrap" \
       "to create it) and open a new shell." >&2
  unset _cd_missing _cd_v _cd_cfg
  return 1 2>/dev/null || exit 1
fi
export CONFLUENCE_URL CONFLUENCE_USERNAME CONFLUENCE_API_TOKEN
unset _cd_missing _cd_v _cd_cfg

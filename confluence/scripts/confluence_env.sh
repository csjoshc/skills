# Source me: . confluence_env.sh
# Checks CONFLUENCE_URL (ends in /wiki), CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN, all from the
# environment (work.env), or prints what is missing and returns 1.
# Also defines confluence_curl and confluence_put_storage (REST helpers, token never in argv).

_cd_missing=""
for _cd_v in CONFLUENCE_URL CONFLUENCE_USERNAME CONFLUENCE_API_TOKEN; do
  eval "[ -n \"\${$_cd_v:-}\" ]" || _cd_missing="$_cd_missing $_cd_v"
done

if [ -n "$_cd_missing" ]; then
  echo "confluence: missing:$_cd_missing" >&2
  echo "Set them in ~/.config/secrets/work.env (run ./bootstrap.sh --secrets in ~/bootstrap" \
       "to create it) and open a new shell." >&2
  unset _cd_missing _cd_v
  return 1 2>/dev/null || exit 1
fi
export CONFLUENCE_URL CONFLUENCE_USERNAME CONFLUENCE_API_TOKEN
unset _cd_missing _cd_v

# Basic auth goes through a curl config on a pipe, so the token never shows up in ps.
confluence_curl() {
  curl -sS -K <(printf 'user = "%s:%s"\n' "$CONFLUENCE_USERNAME" "$CONFLUENCE_API_TOKEN") "$@"
}

# Usage: confluence_put_storage <page_id> <storage_body_file>
# Keeps the current title, bumps the version by one, and writes the body as storage format.
confluence_put_storage() {
  local id="$1" body="$2" cur payload
  cur="$(confluence_curl -f "$CONFLUENCE_URL/rest/api/content/$id?expand=version")" || return 1
  payload="$(python3 -I -c '
import json, sys
cur = json.loads(sys.argv[1])
body = open(sys.argv[3], encoding="utf-8").read()
print(json.dumps({"id": sys.argv[2], "type": cur["type"], "title": cur["title"],
  "version": {"number": cur["version"]["number"] + 1},
  "body": {"storage": {"value": body, "representation": "storage"}}}))' \
    "$cur" "$id" "$body")" || return 1
  confluence_curl -f -X PUT -H "Content-Type: application/json" -d "$payload" \
    "$CONFLUENCE_URL/rest/api/content/$id" -o /dev/null -w 'PUT %{http_code}\n'
}

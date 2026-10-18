#!/bin/bash
# Run: bash ~/.skills/confluence/scripts/test_confluence_env.sh
# Uses fake values and a local stub server; no real network.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"
fail=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }
run() { env -i HOME="$T" PATH="$PATH" "$@" \
  bash -c ". '$HERE/confluence_env.sh' && echo \"\$CONFLUENCE_URL|\$CONFLUENCE_USERNAME|\$CONFLUENCE_API_TOKEN\""; }

check "all three from env" \
  "$(run CONFLUENCE_URL=https://env.example CONFLUENCE_USERNAME=env-user CONFLUENCE_API_TOKEN=env-token 2>&1)" \
  "https://env.example|env-user|env-token"
out="$(run CONFLUENCE_URL=https://env.example CONFLUENCE_USERNAME=env-user 2>&1)"
check "missing token is named" "$(echo "$out" | grep -c 'missing: CONFLUENCE_API_TOKEN')" "1"
check "error points at bootstrap" "$(echo "$out" | grep -c './bootstrap.sh --secrets')" "1"
check "error points at work.env" "$(echo "$out" | grep -c 'work.env')" "1"
out="$(run CONFLUENCE_API_TOKEN=env-token 2>&1)"
check "missing url and user are named" "$(echo "$out" | grep -c 'missing: CONFLUENCE_URL CONFLUENCE_USERNAME')" "1"

# Write path against a local stub: checks method, path, version bump, body, and that
# the token is not in the request URL.
cat > "$T/stub.py" <<'PY'
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, obj):
        b = json.dumps(obj).encode(); self.send_response(200)
        self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        self._send({"id": "42", "type": "page", "title": "T", "version": {"number": 7}})
    def do_PUT(self):
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ok = (self.path == "/rest/api/content/42" and d["version"]["number"] == 8
              and d["title"] == "T" and d["body"]["storage"]["representation"] == "storage"
              and d["body"]["storage"]["value"] == "<p>hi</p>" and "Basic" in self.headers["Authorization"])
        open(sys.argv[2], "w").write("ok" if ok else "bad")
        self._send({})
HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
PY
PORT=$((20000 + RANDOM % 20000))
python3 -I "$T/stub.py" "$PORT" "$T/result" & SP=$!
sleep 1
printf '<p>hi</p>' > "$T/body.html"
out="$(env -i HOME="$T" PATH="$PATH" CONFLUENCE_URL="http://127.0.0.1:$PORT" CONFLUENCE_USERNAME=u \
  CONFLUENCE_API_TOKEN=t bash -c ". '$HERE/confluence_env.sh' && confluence_put_storage 42 '$T/body.html'" 2>&1)"
kill $SP 2>/dev/null; wait $SP 2>/dev/null
check "put returns 200" "$out" "PUT 200"
check "stub saw bumped version and storage body" "$(cat "$T/result" 2>/dev/null)" "ok"
rm -rf "$T"
exit $fail

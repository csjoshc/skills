"""Run: python3 -I ~/.skills/agent-sync/test_mcp_pi.py"""
import json, os, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "mcp_pi.py"
MASTER = {"mcpServers": {
    "gh": {"type": "stdio", "command": "gh-mcp", "args": ["x"], "enabled": True, "allowedTools": ["a"],
           "env": {"GITHUB_TOKEN": "${GH_TOKEN}", "PATH": "/bin", "LEAK_TOKEN": "sekrit-literal"}},
    "remote": {"type": "http", "url": "https://x", "headers": {"Authorization": "Bearer ${T}"},
               "args": ["no"], "env": {"A": "b"}},
    "off": {"type": "stdio", "command": "c", "enabled": False},
    "ok": {"type": "http", "url": "https://y", "headers": {"Authorization": "${Y}"}},
}}
TARGET = {"mcpServers": {"claude": {"command": "claude", "args": ["mcp", "serve"], "env": {"K": "v"}},
                         "off": {"command": "old"}}, "other": 1}

class T(unittest.TestCase):
    def run_sync(self, *extra):
        d = tempfile.mkdtemp()
        m, t = Path(d, "master.json"), Path(d, "mcp.json")
        m.write_text(json.dumps(MASTER)); t.write_text(json.dumps(TARGET)); os.chmod(t, 0o644)
        r = subprocess.run([sys.executable, "-I", SCRIPT, "--master", m, "--target", t, *extra],
                           capture_output=True, text=True)
        return d, t, r

    def test_merge(self):
        d, t, r = self.run_sync()
        self.assertEqual(r.returncode, 0, r.stderr)
        doc = json.loads(t.read_text())
        self.assertEqual(doc["other"], 1)
        self.assertEqual(doc["mcpServers"]["claude"], TARGET["mcpServers"]["claude"])
        self.assertNotIn("off", doc["mcpServers"])
        gh = doc["mcpServers"]["gh"]
        self.assertEqual(gh["env"], {"GITHUB_TOKEN": "$ENV:GH_TOKEN", "PATH": "/bin"})
        self.assertNotIn("enabled", gh); self.assertNotIn("allowedTools", gh)
        remote = doc["mcpServers"]["remote"]
        self.assertEqual(set(remote), {"type", "url"})  # partial secret dropped, no args/env on http
        self.assertEqual(doc["mcpServers"]["ok"]["headers"], {"Authorization": "$ENV:Y"})
        self.assertNotIn("sekrit-literal", t.read_text())
        self.assertNotIn("sekrit-literal", r.stdout + r.stderr)
        self.assertEqual(stat.S_IMODE(t.stat().st_mode), 0o600)
        baks = list(Path(d).glob("mcp.json.bak.*"))
        self.assertEqual(len(baks), 1)
        self.assertEqual(stat.S_IMODE(baks[0].stat().st_mode), 0o600)
        self.assertEqual(r.stdout.count("warning:"), 2)

    def test_idempotent_and_dry_run(self):
        d, t, r = self.run_sync("--dry-run")
        self.assertEqual(json.loads(t.read_text()), TARGET)
        self.assertEqual(list(Path(d).glob("*.bak.*")), [])
        subprocess.run([sys.executable, "-I", SCRIPT, "--master", Path(d, "master.json"), "--target", t],
                       capture_output=True)
        before = t.read_text()
        subprocess.run([sys.executable, "-I", SCRIPT, "--master", Path(d, "master.json"), "--target", t],
                       capture_output=True)
        self.assertEqual(t.read_text(), before)
        self.assertEqual(len(list(Path(d).glob("mcp.json.bak.*"))), 1, "no backup when nothing changed")

if __name__ == "__main__":
    unittest.main()

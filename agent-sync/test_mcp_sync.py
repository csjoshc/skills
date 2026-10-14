"""Run: python3 -I ~/.skills/agent-sync/test_mcp_sync.py
Every case uses a temp HOME and fake values; no real config is read or written."""
import json, os, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = Path(os.environ.get("MCP_SYNC_SCRIPT", HERE / "mcp_sync.py"))
NPX = "/opt/node/bin/npx"
FAKE = "fake-value-1234"

MASTER = {"mcpServers": {
    "remote": {"type": "http", "url": "https://mcp.example/mcp", "enabled": True, "allowedTools": ["a"],
           "headers": {"Authorization": "${REMOTE_MCP_AUTH}"}},
    "github": {"type": "stdio", "command": "/usr/local/bin/docker", "enabled": True,
               "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/x/y"],
               "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}",
                       "PATH": "/usr/local/bin:/usr/bin"}},
    "atlassian": {"type": "stdio", "command": "/home/u/.local/bin/uvx", "args": ["mcp-atlassian"],
                  "allowedTools": ["jira_search", "jira_get_issue"], "enabled": True,
                  "env": {"JIRA_URL": "https://j.example/", "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
                          "CONFLUENCE_API_TOKEN": "${JIRA_API_TOKEN}"}},
    "plain": {"type": "stdio", "command": NPX, "args": ["-y", "chrome-devtools-mcp@latest"],
              "env": {"PATH": "/opt/node/bin:/usr/bin"}, "enabled": True},
    "off": {"type": "stdio", "command": "c", "enabled": False},
}}


class Base(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.master = self.home / "master.json"
        self.set_master(MASTER)
        self.paths = {
            "claude": self.home / ".claude.json",
            "opencode": self.home / ".config/opencode/opencode.json",
            "cursor": self.home / ".cursor/mcp.json",
            "desktop": self.home / "Library/Application Support/Claude/claude_desktop_config.json",
            "pi": self.home / ".pi/agent/mcp.json",
            "pi-gateway": self.home / ".gateway-pi/mcp.json",
        }

    def set_master(self, doc):
        self.master.write_text(json.dumps(doc))

    def put(self, target, doc, mode=0o644):
        p = self.paths[target]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, indent=2) + "\n")
        os.chmod(p, mode)

    def get(self, target):
        return json.loads(self.paths[target].read_text())

    def run_sync(self, *extra, path=None):
        env = {"HOME": str(self.home), "PATH": path or "/usr/bin:/bin"}
        return subprocess.run([sys.executable, "-I", str(SCRIPT), "--master", str(self.master),
                               "--npx", NPX, "--ignore-running", *extra],
                              capture_output=True, text=True, env=env)

    def backups(self, target):
        p = self.paths[target]
        return list(p.parent.glob(p.name + ".bak.*"))


class Translation(Base):
    def test_claude_keeps_dollar_brace_and_strips_extensions(self):
        r = self.run_sync("--targets", "claude")
        self.assertEqual(r.returncode, 0, r.stderr)
        s = self.get("claude")["mcpServers"]
        self.assertEqual(s["remote"], {"type": "http", "url": "https://mcp.example/mcp",
                                   "headers": {"Authorization": "${REMOTE_MCP_AUTH}"}})
        self.assertEqual(s["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"],
                         "${GITHUB_PERSONAL_ACCESS_TOKEN}")
        self.assertNotIn("off", s)
        self.assertNotIn("enabled", s["github"])

    def test_claude_atlassian_allowlist_becomes_flag(self):
        self.run_sync("--targets", "claude")
        args = self.get("claude")["mcpServers"]["atlassian"]["args"]
        self.assertEqual(args, ["mcp-atlassian", "--enabled-tools", "jira_search,jira_get_issue"])

    def test_opencode_env_syntax_and_shapes(self):
        self.run_sync("--targets", "opencode")
        s = self.get("opencode")["mcp"]
        self.assertEqual(s["remote"], {"type": "remote", "url": "https://mcp.example/mcp",
                                   "headers": {"Authorization": "{env:REMOTE_MCP_AUTH}"}})
        self.assertEqual(s["github"]["command"][:2], ["/usr/local/bin/docker", "run"])
        self.assertEqual(s["github"]["environment"]["GITHUB_PERSONAL_ACCESS_TOKEN"],
                         "{env:GITHUB_PERSONAL_ACCESS_TOKEN}")
        self.assertNotIn("args", s["github"])

    def test_pi_whole_value_only(self):
        m = json.loads(json.dumps(MASTER))
        m["mcpServers"]["remote"]["headers"]["X-Other"] = "pre ${REMOTE_MCP_AUTH}"
        self.set_master(m)
        r = self.run_sync("--targets", "pi")
        s = self.get("pi")["mcpServers"]
        self.assertEqual(s["remote"]["headers"], {"Authorization": "$ENV:REMOTE_MCP_AUTH"})
        self.assertEqual(s["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"],
                         "$ENV:GITHUB_PERSONAL_ACCESS_TOKEN")
        self.assertIn("X-Other", r.stdout)  # warned about the embedded reference

    def test_cursor_and_desktop_wrap_only_servers_with_references(self):
        self.run_sync("--targets", "cursor,desktop")
        for t in ("cursor", "desktop"):
            s = self.get(t)["mcpServers"]
            self.assertEqual(s["plain"]["command"], NPX)  # no secret, no wrapper
            for n in ("github", "atlassian", "remote"):
                self.assertEqual(s[n]["command"], "/bin/zsh")
                self.assertEqual(s[n]["args"][0], "-c")
                self.assertTrue(s[n]["args"][1].startswith(
                    'set -a; . "$HOME/.config/secrets/work.env"; '))
        self.assertEqual(self.get("cursor")["mcpServers"]["github"]["type"], "stdio")
        self.assertNotIn("type", self.get("desktop")["mcpServers"]["github"])

    def test_inherited_secret_dropped_but_renamed_one_is_exported(self):
        self.run_sync("--targets", "cursor")
        a = self.get("cursor")["mcpServers"]["atlassian"]
        self.assertNotIn("JIRA_API_TOKEN", a.get("env", {}))
        self.assertIn('CONFLUENCE_API_TOKEN="$JIRA_API_TOKEN"; exec ', a["args"][1])
        self.assertEqual(a["env"], {"JIRA_URL": "https://j.example/"})

    def test_disabled_removed_but_soft_off_in_opencode(self):
        self.put("claude", {"mcpServers": {"off": {"command": "old"}}})
        self.put("opencode", {"mcp": {"off": {"type": "local", "command": ["old"]}}})
        self.run_sync("--targets", "claude,opencode")
        self.assertNotIn("off", self.get("claude")["mcpServers"])
        self.assertIs(self.get("opencode")["mcp"]["off"]["enabled"], False)


class Wrappers(Base):
    def make_fake(self, name, body):
        d = self.home / "bin"
        d.mkdir(exist_ok=True)
        f = d / name
        f.write_text("#!/usr/bin/env python3\nimport json,os,sys\n" + body)
        os.chmod(f, 0o755)
        return str(f)

    def write_env(self):
        e = self.home / ".config/secrets/work.env"
        e.parent.mkdir(parents=True)
        e.write_text(f'GH_FAKE={FAKE}\nREMOTE_FAKE=tok\nREMOTE_AUTH="Prefix ${{REMOTE_FAKE}}"\n')

    def exec_entry(self, entry):
        env = {"HOME": str(self.home), "PATH": "/usr/bin:/bin", **entry.get("env", {})}
        r = subprocess.run([entry["command"], *entry["args"]], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_quoting_survives_zsh_round_trip(self):
        self.write_env()
        fake = self.make_fake("tool", "print(json.dumps({'argv': sys.argv[1:], "
                                      "'tok': os.environ.get('GH_FAKE'), 'x': os.environ.get('RENAMED')}))")
        nasty = ["plain", "has space", "it's", 'say "hi"', "dollar $HOME `tick`", "semi; echo pwned",
                 "--flag=a b", "", "back\\slash"]
        m = {"mcpServers": {"t": {"type": "stdio", "command": fake, "args": nasty + ["pre-${GH_FAKE}-post"],
                                  "env": {"GH_FAKE": "${GH_FAKE}", "RENAMED": "${GH_FAKE}"}}}}
        self.set_master(m)
        self.run_sync("--targets", "cursor")
        out = self.exec_entry(self.get("cursor")["mcpServers"]["t"])
        self.assertEqual(out["argv"], nasty + [f"pre-{FAKE}-post"])
        self.assertEqual(out["tok"], FAKE)
        self.assertEqual(out["x"], FAKE)
        self.assertNotIn(FAKE, self.paths["cursor"].read_text())

    def test_mcp_remote_wrapper_builds_header_from_env(self):
        self.write_env()
        npx = self.make_fake("npx", "print(json.dumps({'argv': sys.argv[1:], 'path': os.environ['PATH']}))")
        m = {"mcpServers": {"remote": {"type": "http", "url": "https://u.example/mcp",
                                   "headers": {"Authorization": "${REMOTE_AUTH}", "X-Id": "a b"}}}}
        self.set_master(m)
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--master", str(self.master),
                            "--npx", npx, "--targets", "desktop", "--ignore-running"],
                           capture_output=True, text=True, env={"HOME": str(self.home), "PATH": "/usr/bin"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = self.exec_entry(self.get("desktop")["mcpServers"]["remote"])
        self.assertEqual(out["argv"], ["-y", "mcp-remote", "https://u.example/mcp", "--header",
                                       "Authorization:Prefix tok", "--header", "X-Id:a b"])
        self.assertTrue(out["path"].startswith(str(self.home / "bin") + ":"))
        self.assertNotIn("Prefix tok", self.paths["desktop"].read_text())

    def test_brace_form_when_followed_by_identifier_char(self):
        self.set_master({"mcpServers": {"remote": {"type": "http", "url": "https://u.example",
                         "headers": {"Authorization": "${A}b"}}}})
        self.run_sync("--targets", "cursor")
        self.assertIn('"Authorization:${A}b"', self.get("cursor")["mcpServers"]["remote"]["args"][1])


class LiveEquivalence(Base):
    """The generator must reproduce the hand-migrated Cursor and Claude Desktop wrappers."""
    WORK = 'set -a; . "$HOME/.config/secrets/work.env"; '
    LIVE_REMOTE = {"command": "/bin/zsh", "args": ["-c", WORK + 'PATH="/opt/node/bin:$PATH"; exec '
               '/opt/node/bin/npx -y mcp-remote https://mcp.example/mcp --header "Authorization:$REMOTE_MCP_AUTH"']}
    LIVE_GH = {"command": "/bin/zsh", "args": ["-c", WORK + "exec /usr/local/bin/docker run -i --rm -e "
               "GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/x/y"], "env": {"PATH": "/usr/local/bin:/usr/bin"}}
    LIVE_AT = {"command": "/bin/zsh", "args": ["-c", WORK + 'CONFLUENCE_API_TOKEN="$JIRA_API_TOKEN"; '
               "exec /home/u/.local/bin/uvx mcp-atlassian"], "env": {"JIRA_URL": "https://j.example/"}}

    def key_paths(self, d, p=""):
        if isinstance(d, dict):
            return [x for k, v in d.items() for x in self.key_paths(v, f"{p}.{k}")]
        return [p]

    def test_cursor_and_desktop_match_hand_migrated(self):
        self.run_sync("--targets", "cursor,desktop")
        want = {"remote": self.LIVE_REMOTE, "github": self.LIVE_GH, "atlassian": self.LIVE_AT}
        for t, typed in (("cursor", True), ("desktop", False)):
            got = self.get(t)["mcpServers"]
            for n, w in want.items():
                exp = dict(w, **({"type": "stdio"} if typed else {}))
                self.assertEqual(got[n], exp, f"{t}.{n}")
                self.assertEqual(sorted(self.key_paths(got[n])), sorted(self.key_paths(exp)))


class Safety(Base):
    def literal_master(self):
        m = json.loads(json.dumps(MASTER))
        m["mcpServers"]["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"] = "ghp_literal_" + FAKE
        m["mcpServers"]["remote"]["headers"]["Authorization"] = "Prefix " + FAKE
        self.set_master(m)

    def test_literal_secret_refused_on_every_target(self):
        self.literal_master()
        r = self.run_sync()
        self.assertEqual(r.returncode, 0, "non-strict still exits 0")
        self.assertEqual(r.stdout.count("refused"), 12)  # 2 fields x 6 targets
        for t, p in self.paths.items():
            text = p.read_text()
            self.assertNotIn(FAKE, text, t)
            self.assertNotIn("Authorization", json.dumps(
                {k: v for k, v in json.loads(text).items()}.get("mcpServers", {}).get("remote", {})), t)
        self.assertNotIn(FAKE, r.stdout + r.stderr)

    def test_strict_exits_nonzero_and_writes_nothing(self):
        self.literal_master()
        r = self.run_sync("--strict")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(any(p.exists() for p in self.paths.values()))
        self.assertNotIn(FAKE, r.stdout + r.stderr)

    def test_idempotent_second_run_is_a_noop(self):
        for t in self.paths:
            self.put(t, {"keep": 1}, mode=0o600)
        self.run_sync()
        before = {t: p.read_text() for t, p in self.paths.items()}
        nb = {t: len(self.backups(t)) for t in self.paths}
        inodes = {t: p.stat().st_ino for t, p in self.paths.items()}
        r = self.run_sync()
        # An atomic rewrite swaps the inode, so an unchanged inode proves the file was not touched.
        self.assertEqual(inodes, {t: p.stat().st_ino for t, p in self.paths.items()})
        self.assertEqual(before, {t: p.read_text() for t, p in self.paths.items()})
        self.assertEqual(nb, {t: len(self.backups(t)) for t in self.paths}, "no backup when unchanged")
        self.assertNotIn("\n  +", r.stdout)
        self.assertNotIn("\n  ~", r.stdout)

    def test_tool_only_server_and_unrelated_keys_survive(self):
        self.put("claude", {"theme": "dark", "projects": {"/x": {"mcpServers": {"p": {}}}},
                            "mcpServers": {"mine": {"type": "stdio", "command": "m"}}})
        self.put("opencode", {"model": "z", "mcp": {"mine": {"type": "local", "command": ["m"]}}})
        self.put("desktop", {"preferences": {"a": 1}, "mcpServers": {"mine": {"command": "m"}}})
        self.run_sync()
        self.assertEqual(self.get("claude")["mcpServers"]["mine"], {"type": "stdio", "command": "m"})
        self.assertEqual(self.get("claude")["theme"], "dark")
        self.assertEqual(self.get("claude")["projects"], {"/x": {"mcpServers": {"p": {}}}})
        self.assertEqual(self.get("opencode")["model"], "z")
        self.assertIn("mine", self.get("opencode")["mcp"])
        self.assertEqual(self.get("desktop")["preferences"], {"a": 1})
        self.assertIn("mine", self.get("desktop")["mcpServers"])

    def test_opencode_keeps_its_own_enabled_flag(self):
        self.put("opencode", {"mcp": {"github": {"type": "local", "command": ["x"], "enabled": False}}})
        self.run_sync("--targets", "opencode")
        self.assertIs(self.get("opencode")["mcp"]["github"]["enabled"], False)

    def test_modes_preserved_and_pi_forced_private(self):
        self.put("claude", {}, mode=0o644)
        self.put("cursor", {}, mode=0o600)
        self.put("pi-gateway", {}, mode=0o644)
        self.run_sync()
        mode = lambda t: stat.S_IMODE(self.paths[t].stat().st_mode)
        self.assertEqual(mode("claude"), 0o644)
        self.assertEqual(mode("cursor"), 0o600)
        self.assertEqual(mode("pi-gateway"), 0o600)
        self.assertEqual(mode("pi"), 0o600)  # created fresh
        self.assertEqual(mode("opencode"), 0o600)
        self.assertEqual(stat.S_IMODE(self.backups("claude")[0].stat().st_mode), 0o600)

    def test_dry_run_writes_and_backs_up_nothing_and_lists_key_paths(self):
        self.put("claude", {"mcpServers": {"remote": {"type": "http", "url": "https://old"}}})
        r = self.run_sync("--dry-run")
        self.assertEqual(self.get("claude"), {"mcpServers": {"remote": {"type": "http", "url": "https://old"}}})
        self.assertEqual(self.backups("claude"), [])
        self.assertIn("~mcpServers.remote.url", r.stdout)
        self.assertFalse(self.paths["cursor"].exists())

    def test_running_gui_app_is_not_written(self):
        bin_ = self.home / "fakebin"
        bin_.mkdir()
        (bin_ / "pgrep").write_text("#!/bin/sh\n[ \"$2\" = Cursor ]\n")
        os.chmod(bin_ / "pgrep", 0o755)
        env = {"HOME": str(self.home), "PATH": f"{bin_}:/usr/bin:/bin"}
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--master", str(self.master),
                            "--npx", NPX, "--targets", "cursor,desktop"],
                           capture_output=True, text=True, env=env)
        self.assertFalse(self.paths["cursor"].exists())
        self.assertTrue(self.paths["desktop"].exists())
        self.assertIn("Cursor is running", r.stdout)

    def test_settings_json_mcpservers_pruned(self):
        s = self.home / ".claude/settings.json"
        s.parent.mkdir()
        s.write_text(json.dumps({"model": "m", "mcpServers": {"x": {}}}))
        self.run_sync("--targets", "claude")
        self.assertEqual(json.loads(s.read_text()), {"model": "m"})


if __name__ == "__main__":
    unittest.main()

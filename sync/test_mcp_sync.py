"""Run: python3 -I ~/.skills/sync/test_mcp_sync.py
Every case uses a temp HOME and fake values; no real config is read or written."""
import json, os, re, runpy, stat, subprocess, sys, tempfile, tomllib, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = Path(os.environ.get("MCP_SYNC_SCRIPT", HERE / "mcp_sync.py"))
NPX = "/opt/node/bin/npx"
FAKE = "fake-value-1234"

MASTER = {"mcpServers": {
    "remote": {"type": "http", "url": "https://mcp.example/mcp", "enabled": True, "allowedTools": ["a"],
               "names": {"vscode": "Aliased-Name"},
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
              "env": {"PATH": "/opt/node/bin:/usr/bin"}, "enabled": True, "personal": True},
    "off": {"type": "stdio", "command": "c", "enabled": False},
}}


class Base(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.master = self.home / "master.json"
        self.set_master(MASTER)
        self.codex = self.home / ".codex/config.toml"
        self.paths = {
            "claude": self.home / ".claude.json",
            "opencode": self.home / ".config/opencode/opencode.json",
            "cursor": self.home / ".cursor/mcp.json",
            "vscode": self.home / "Library/Application Support/Code/User/mcp.json",
            "desktop": self.home / "Library/Application Support/Claude/claude_desktop_config.json",
            "omp": self.home / ".omp/agent/mcp.json",
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
        env = {"HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": path or "/usr/bin:/bin"}
        return subprocess.run([sys.executable, "-I", str(SCRIPT), "--master", str(self.master),
                               "--npx", NPX, "--ignore-running", *extra],
                              capture_output=True, text=True, env=env)

    def backups(self, target):
        p = self.paths[target]
        return list(p.parent.glob(p.name + ".bak.*"))


class ScopedReconciliation(Base):
    def test_reader_guard_follows_native_filename_case_rules(self):
        module = runpy.run_path(str(SCRIPT))
        target = module["Target"]("cursor", self.paths["cursor"], "mcpServers", module["to_cursor"])
        master = {"mcpServers": {"github": {"command": "plain-tool"}}}
        for filename in ("credential_exec.py", "CREDENTIAL_EXEC.PY"):
            with self.subTest(filename=filename):
                self.put("cursor", {"mcpServers": {"github": {
                    "command": "python", "args": ["-I", str(self.home / filename)],
                }}})
                before = self.paths["cursor"].read_bytes()
                result = module["sync"](master, [target], False, npx=NPX,
                                        check_apps=False, out=lambda message: None)
                if filename == "credential_exec.py" or os.name == "nt":
                    self.assertEqual(result, 1)
                    self.assertEqual(self.paths["cursor"].read_bytes(), before)
                    self.assertEqual(self.backups("cursor"), [])
                else:
                    self.assertEqual(result, 0)
                    self.assertEqual(self.get("cursor")["mcpServers"]["github"]["command"], "plain-tool")

    def test_shipped_template_requires_reconciliation_on_a_new_machine(self):
        self.set_master(json.loads((HERE / "references/mcp.example.json").read_text()))
        result = self.run_sync("--targets", "claude")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reconciliation", result.stdout)
        self.assertFalse(self.paths["claude"].exists())

    def test_declared_credential_ownership_requires_native_reconciliation(self):
        master = json.loads(json.dumps(MASTER))
        master["mcpServers"]["github"]["credentialSource"] = "work"
        self.set_master(master)
        self.put("claude", {"mcpServers": {"mine": {"command": "keep"}}})
        before = self.paths["claude"].read_bytes()
        for flags in [(), ("--dry-run",)]:
            with self.subTest(flags=flags):
                result = self.run_sync("--targets", "claude", *flags)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("reconciliation", result.stdout)
                self.assertEqual(self.paths["claude"].read_bytes(), before)
                self.assertEqual(self.backups("claude"), [])

    def test_scoped_native_reader_blocks_the_whole_batch_without_writes(self):
        for target, root, entry in [
            ("cursor", "mcpServers", {
                "command": "/usr/bin/python3",
                "args": ["-I", "/private/shared/credential_exec.py", "--descriptor", "opaque"],
            }),
            ("opencode", "mcp", {
                "type": "local",
                "command": ["/usr/bin/python3", "-I", "/private/shared/credential_exec.py",
                            "--file", "/private/work.env", "--var", "TOKEN", "--", "/bin/tool"],
            }),
        ]:
            with self.subTest(target=target):
                self.put("claude", {"mcpServers": {"mine": {"command": "keep"}}})
                self.put(target, {root: {"github": entry}, "unrelated": {"keep": True}})
                paths = [self.paths["claude"], self.paths[target]]
                before = [(path.read_bytes(), path.stat().st_mode) for path in paths]
                result = self.run_sync("--targets", f"claude,{target}")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("reconciliation", result.stdout)
                self.assertEqual([(path.read_bytes(), path.stat().st_mode) for path in paths], before)
                self.assertEqual(self.backups("claude") + self.backups(target), [])


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

    def test_vscode_uses_servers_root_and_typed_entries(self):
        self.put("vscode", {"inputs": [], "servers": {"mine": {"type": "stdio", "command": "x"}}})
        self.run_sync("--targets", "vscode")
        doc = self.get("vscode")
        s = doc["servers"]
        self.assertEqual(doc["inputs"], [])
        self.assertIn("mine", s)
        self.assertEqual(s["plain"], {"command": NPX, "args": ["-y", "chrome-devtools-mcp@latest"],
                                      "env": {"PATH": "/opt/node/bin:/usr/bin"}, "type": "stdio"})
        self.assertEqual(s["github"]["type"], "stdio")
        self.assertEqual(s["Aliased-Name"]["type"], "stdio")  # header needs a variable, so mcp-remote
        self.assertIn("mcp-remote", s["Aliased-Name"]["args"][1])
        self.assertNotIn(FAKE, self.paths["vscode"].read_text())

    def test_vscode_plain_url_server_keeps_http_type(self):
        m = json.loads(json.dumps(MASTER))
        m["mcpServers"]["remote"]["headers"] = {"X-Static": "1"}
        self.set_master(m)
        self.run_sync("--targets", "vscode")
        self.assertEqual(self.get("vscode")["servers"]["Aliased-Name"],
                         {"type": "http", "url": "https://mcp.example/mcp", "headers": {"X-Static": "1"}})

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


class TestOmpProjection(Base):
    def test_native_projection_preserves_references_local_servers_and_omp_fields(self):
        self.put("omp", {"disabledServers": ["do-not-enable"], "mcpServers": {
            "omp-local": {"type": "stdio", "command": "local-tool", "args": ["--keep"]},
            "remote": {"type": "http", "url": "https://old.example/mcp", "timeout": 12000,
                       "enabled": False, "instructions": False, "requestIdFormat": "string",
                       "auth": {"type": "oauth", "credentialId": "profile-local"}},
        }}, mode=0o640)

        r = self.run_sync("--targets", "omp")

        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        doc = self.get("omp")
        servers = doc["mcpServers"]
        self.assertEqual(doc["disabledServers"], ["do-not-enable"])
        self.assertEqual(servers["omp-local"], {"type": "stdio", "command": "local-tool", "args": ["--keep"]})
        self.assertEqual(servers["remote"], {
            "type": "http", "url": "https://mcp.example/mcp",
            "headers": {"Authorization": "${REMOTE_MCP_AUTH}"}, "enabled": False,
            "timeout": 12000, "instructions": False, "requestIdFormat": "string",
            "auth": {"type": "oauth", "credentialId": "profile-local"},
        })
        self.assertEqual(servers["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"],
                         "${GITHUB_PERSONAL_ACCESS_TOKEN}")
        self.assertNotIn("off", servers)
        for server in servers.values():
            self.assertNotIn("allowedTools", server)
            self.assertNotIn("personal", server)
        self.assertEqual(stat.S_IMODE(self.paths["omp"].stat().st_mode), 0o640)
        self.assertNotIn(FAKE, self.paths["omp"].read_text())

    def test_malformed_omp_target_does_not_change_other_targets(self):
        self.put("claude", {"mcpServers": {"untouched": {"type": "stdio", "command": "mine"}}})
        original_claude = self.paths["claude"].read_text()
        self.paths["omp"].parent.mkdir(parents=True)
        original_omp = '{ "mcpServers": '
        self.paths["omp"].write_text(original_omp)

        r = self.run_sync("--targets", "claude,omp")

        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.paths["claude"].read_text(), original_claude)
        self.assertEqual(self.paths["omp"].read_text(), original_omp)
        self.assertEqual(self.backups("claude"), [])
        self.assertEqual(self.backups("omp"), [])

    def test_malformed_master_leaves_omp_and_other_targets_unchanged(self):
        self.put("claude", {"mcpServers": {"untouched": {"type": "stdio", "command": "mine"}}})
        self.put("omp", {"mcpServers": {"omp-local": {"type": "stdio", "command": "local"}}})
        original_claude = self.paths["claude"].read_bytes()
        original_omp = self.paths["omp"].read_bytes()
        self.master.write_text('{ "mcpServers": ')

        r = self.run_sync("--targets", "claude,omp")

        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.paths["claude"].read_bytes(), original_claude)
        self.assertEqual(self.paths["omp"].read_bytes(), original_omp)
        self.assertEqual(self.backups("claude"), [])
        self.assertEqual(self.backups("omp"), [])


class Alias(Base):
    def test_vscode_writes_remote_as_alias_and_not_duplicate(self):
        self.run_sync("--targets", "vscode")
        s = self.get("vscode")["servers"]
        self.assertIn("Aliased-Name", s)
        self.assertNotIn("remote", s)

    def test_existing_alias_entry_is_updated_in_place(self):
        self.put("vscode", {"servers": {"Aliased-Name": {"command": "old", "type": "stdio"},
                                        "Notes": {"url": "https://n.example", "type": "http"}}})
        r = self.run_sync("--targets", "vscode")
        s = self.get("vscode")["servers"]
        self.assertEqual(list(s).count("Aliased-Name"), 1)
        self.assertNotIn("remote", s)
        self.assertIn("Notes", s)
        self.assertIn("remote=updated", r.stdout)
        self.assertNotIn("tool-only servers kept: Aliased-Name", r.stdout)
        self.assertIn("Notes", r.stdout.split("tool-only servers kept:")[1])

    def test_second_run_is_a_noop(self):
        self.put("vscode", {"servers": {"Aliased-Name": {"command": "old", "type": "stdio"}}})
        self.run_sync("--targets", "vscode")
        before = self.paths["vscode"].read_text()
        n = len(self.backups("vscode"))
        r = self.run_sync("--targets", "vscode")
        self.assertEqual(self.paths["vscode"].read_text(), before)
        self.assertEqual(len(self.backups("vscode")), n)
        self.assertIn("remote=unchanged", r.stdout)

    def test_other_targets_keep_the_master_name(self):
        self.run_sync("--targets", "claude,cursor")
        self.assertIn("remote", self.get("claude")["mcpServers"])
        self.assertIn("remote", self.get("cursor")["mcpServers"])
        self.assertNotIn("Aliased-Name", self.get("cursor")["mcpServers"])

    def test_disabled_master_server_removes_the_alias_entry(self):
        doc = json.loads(json.dumps(MASTER))
        doc["mcpServers"]["remote"]["enabled"] = False
        self.set_master(doc)
        self.put("vscode", {"servers": {"Aliased-Name": {"command": "old", "type": "stdio"},
                                        "Mine": {"command": "m", "type": "stdio"}}})
        self.run_sync("--targets", "vscode")
        s = self.get("vscode")["servers"]
        self.assertNotIn("Aliased-Name", s)
        self.assertIn("Mine", s)


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
        self.assertEqual(r.stdout.count("refused"), 12)  # 2 fields x 6 eligible targets; Codex also reports skipped refs
        for t, p in self.paths.items():
            text = p.read_text()
            self.assertNotIn(FAKE, text, t)
            self.assertNotIn("Authorization", json.dumps(
                {k: v for k, v in json.loads(text).items()}.get("mcpServers", {}).get("remote", {})), t)
        self.assertNotIn(FAKE, self.codex.read_text())
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
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
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

    def test_modes_are_preserved_for_managed_targets(self):
        self.put("claude", {}, mode=0o644)
        self.put("cursor", {}, mode=0o600)
        self.run_sync()
        mode = lambda t: stat.S_IMODE(self.paths[t].stat().st_mode)
        self.assertEqual(mode("claude"), 0o644)
        self.assertEqual(mode("cursor"), 0o600)
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

    def test_running_vscode_is_not_written(self):
        bin_ = self.home / "fakebin"
        bin_.mkdir()
        (bin_ / "pgrep").write_text("#!/bin/sh\n[ \"$2\" = Code ]\n")
        os.chmod(bin_ / "pgrep", 0o755)
        env = {"HOME": str(self.home), "PATH": f"{bin_}:/usr/bin:/bin"}
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--master", str(self.master),
                            "--npx", NPX, "--targets", "vscode"], capture_output=True, text=True, env=env)
        self.assertFalse(self.paths["vscode"].exists())
        self.assertIn("Code is running", r.stdout)

    def test_settings_json_mcpservers_pruned(self):
        s = self.home / ".claude/settings.json"
        s.parent.mkdir()
        s.write_text(json.dumps({"model": "m", "mcpServers": {"x": {}}}))
        self.run_sync("--targets", "claude")
        self.assertEqual(json.loads(s.read_text()), {"model": "m"})


class Codex(Base):
    """Codex keeps MCP servers in ~/.codex/config.toml next to model, project trust and its own
    app-managed servers, so sync edits only the tables it owns and leaves every other byte.
    It is personal only: just servers marked "personal": true are written, and never a secret."""

    EXISTING = (
        '# my codex settings\n'
        'model = "m1"\n\n'
        '[mcp_servers.mempalace]\ncommand = "python"\nargs = ["-m", "mempalace"]\n\n'
        '[mcp_servers.plain]\ncommand = "old"\nstartup_timeout_sec = 90\n\n'
        '[mcp_servers.plain.env]\nSTALE = "1"\n\n'
        '[projects."/Users/u/code"]\ntrust_level = "trusted"\n'
    )

    def load(self):
        return tomllib.loads(self.codex.read_text())

    def servers(self):
        return self.load().get("mcp_servers", {}) if self.codex.exists() else {}

    def put_codex(self, text, mode=0o644):
        self.codex.parent.mkdir(parents=True, exist_ok=True)
        self.codex.write_text(text)
        os.chmod(self.codex, mode)

    def personal(self, **servers):
        self.set_master({"mcpServers": {n: {"personal": True, "enabled": True, **e}
                                        for n, e in servers.items()}})

    def test_target_is_listed_and_first_class(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertIn("codex", r.stdout)

    def test_translation_has_no_type_and_no_extensions(self):
        r = self.run_sync("--targets", "codex")
        self.assertEqual(r.returncode, 0, r.stderr)
        s = self.load()["mcp_servers"]
        self.assertEqual(s["plain"], {"command": NPX, "args": ["-y", "chrome-devtools-mcp@latest"],
                                      "env": {"PATH": "/opt/node/bin:/usr/bin"}})
        for entry in s.values():
            for bad in ("type", "enabled", "allowedTools", "headers", "personal"):
                self.assertNotIn(bad, entry)

    def test_only_personal_servers_reach_codex(self):
        r = self.run_sync("--targets", "codex")
        self.assertEqual(set(self.load()["mcp_servers"]), {"plain"})
        text = self.codex.read_text()
        for work in ("github", "atlassian", "work.env", "/bin/zsh", "mcp-remote", "TOKEN"):
            self.assertNotIn(work, text)
        self.assertIn("github=not personal", r.stdout)

    def test_unmarked_server_is_not_written_even_with_no_secret(self):
        self.set_master({"mcpServers": {"x": {"type": "stdio", "command": "x", "enabled": True}}})
        self.run_sync("--targets", "codex")
        self.assertEqual(self.servers(), {})
        self.assertFalse(self.codex.exists(), "nothing to write, so no file is created")

    def test_personal_server_that_needs_a_secret_is_refused(self):
        self.personal(t={"type": "stdio", "command": "t", "env": {"K": "${WORK_TOKEN}"}},
                      u={"type": "http", "url": "https://u.example", "headers": {"Authorization": "${A}"}})
        r = self.run_sync("--targets", "codex")
        self.assertEqual(self.servers(), {})
        self.assertIn("Codex is personal only", r.stdout)
        self.assertFalse(self.codex.exists())

    def test_unmarked_server_already_in_codex_is_flagged_not_deleted(self):
        self.put_codex('[mcp_servers.github]\ncommand = "mine"\n')
        r = self.run_sync("--targets", "codex")
        self.assertEqual(self.load()["mcp_servers"]["github"], {"command": "mine"})
        self.assertIn("not marked personal", r.stdout)

    def test_literal_url_server_keeps_native_http_with_http_headers(self):
        self.personal(docs={"type": "http", "url": "https://d.example/mcp", "headers": {"X-Region": "us"}})
        self.run_sync("--targets", "codex")
        self.assertEqual(self.load()["mcp_servers"]["docs"],
                         {"url": "https://d.example/mcp", "http_headers": {"X-Region": "us"}})

    def test_other_content_is_preserved_byte_for_byte(self):
        self.put_codex(self.EXISTING)
        self.run_sync("--targets", "codex")
        text, got = self.codex.read_text(), self.load()
        self.assertTrue(text.startswith('# my codex settings\nmodel = "m1"\n\n'))
        self.assertIn('[mcp_servers.mempalace]\ncommand = "python"\nargs = ["-m", "mempalace"]\n', text)
        self.assertIn('[projects."/Users/u/code"]\ntrust_level = "trusted"\n', text)
        self.assertEqual(got["mcp_servers"]["mempalace"], {"command": "python", "args": ["-m", "mempalace"]})
        self.assertEqual(got["projects"], {"/Users/u/code": {"trust_level": "trusted"}})
        self.assertEqual(got["model"], "m1")

    def test_unchanged_servers_keep_their_hand_formatting(self):
        # `plain` already equals what sync would write, `mine` is not in the master at all.
        text = ('[mcp_servers.mine]  # my own server\ncommand   = \'tool\'\n\n'
                '[mcp_servers.plain]\n# pinned by hand\ncommand = "%s"  # keep\n'
                'args = [\n  "-y",\n  "chrome-devtools-mcp@latest",\n]\n\n'
                '[mcp_servers.plain.env]\nPATH = "/opt/node/bin:/usr/bin"\n' % NPX)
        self.put_codex(text)
        self.run_sync("--targets", "codex")
        out = self.codex.read_text()
        self.assertIn("[mcp_servers.mine]  # my own server\ncommand   = 'tool'\n", out)
        self.assertIn('# pinned by hand\ncommand = "%s"  # keep\nargs = [\n  "-y",' % NPX, out)
        self.assertEqual(self.load()["mcp_servers"]["plain"]["args"], ["-y", "chrome-devtools-mcp@latest"])

    def test_managed_server_is_replaced_in_place_and_keeps_codex_only_keys(self):
        self.put_codex(self.EXISTING)
        self.run_sync("--targets", "codex")
        p = self.load()["mcp_servers"]["plain"]
        self.assertEqual(p["command"], NPX)
        self.assertEqual(p["startup_timeout_sec"], 90)
        self.assertNotIn("STALE", p.get("env", {}))
        text = self.codex.read_text()
        self.assertLess(text.index("mcp_servers.mempalace"), text.index("mcp_servers.plain"))
        self.assertLess(text.index("mcp_servers.plain"), text.index("[projects."))

    def test_disabled_master_server_is_removed_with_its_subtables(self):
        self.put_codex(self.EXISTING)
        self.personal(plain={"type": "stdio", "command": "x", "enabled": False})
        self.run_sync("--targets", "codex")
        got = self.load()
        self.assertNotIn("plain", got["mcp_servers"])
        self.assertIn("mempalace", got["mcp_servers"])
        self.assertNotIn("STALE", self.codex.read_text())

    def test_idempotent_second_run_does_not_touch_the_file(self):
        self.put_codex(self.EXISTING)
        self.run_sync("--targets", "codex")
        before, ino = self.codex.read_text(), self.codex.stat().st_ino
        nb = len(list(self.codex.parent.glob("config.toml.bak.*")))
        r = self.run_sync("--targets", "codex")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(before, self.codex.read_text())
        self.assertEqual(ino, self.codex.stat().st_ino)
        self.assertEqual(nb, len(list(self.codex.parent.glob("config.toml.bak.*"))))
        self.assertNotIn("\n  +", r.stdout)
        self.assertNotIn("\n  ~", r.stdout)

    def test_backup_made_before_change_and_mode_kept(self):
        self.put_codex(self.EXISTING, mode=0o640)
        self.run_sync("--targets", "codex")
        baks = list(self.codex.parent.glob("config.toml.bak.*"))
        self.assertEqual(len(baks), 1)
        self.assertEqual(baks[0].read_text(), self.EXISTING)
        self.assertEqual(stat.S_IMODE(self.codex.stat().st_mode), 0o640)

    def test_missing_file_is_created_private(self):
        self.run_sync("--targets", "codex")
        self.assertEqual(stat.S_IMODE(self.codex.stat().st_mode), 0o600)
        self.assertIn("plain", self.load()["mcp_servers"])

    def test_dry_run_writes_nothing_and_lists_key_paths(self):
        self.put_codex(self.EXISTING)
        r = self.run_sync("--targets", "codex", "--dry-run")
        self.assertEqual(self.codex.read_text(), self.EXISTING)
        self.assertEqual(list(self.codex.parent.glob("config.toml.bak.*")), [])
        self.assertIn("~mcp_servers.plain.command", r.stdout)

    def test_awkward_values_round_trip(self):
        nasty = ['say "hi"', "back\\slash", "tab\there", "line\nbreak", "unicode \u00e9 \u2713", "'single'", ""]
        self.personal(t={"type": "stdio", "command": "/bin/echo", "args": nasty,
                         "env": {"K E Y": "v.1", "dotted.name": "x"}})
        self.run_sync("--targets", "codex")
        t = self.load()["mcp_servers"]["t"]
        self.assertEqual(t["args"], nasty)
        self.assertEqual(t["env"], {"K E Y": "v.1", "dotted.name": "x"})

    def test_literal_secret_in_a_personal_server_is_refused(self):
        self.personal(t={"type": "stdio", "command": "t", "env": {"MY_TOKEN": "ghp_literal_" + FAKE}})
        r = self.run_sync("--targets", "codex")
        self.assertNotIn(FAKE, self.codex.read_text())
        self.assertNotIn(FAKE, r.stdout + r.stderr)
        self.assertIn("refused", r.stdout)

    def test_unparseable_result_aborts_and_leaves_the_file_alone(self):
        # An inline mcp_servers table cannot be extended by appending a [mcp_servers.x] table.
        text = 'model = "m"\nmcp_servers = { keep = { command = "k" } }\n'
        self.put_codex(text)
        r = self.run_sync("--targets", "codex")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.codex.read_text(), text)
        self.assertEqual(list(self.codex.parent.glob("config.toml.bak.*")), [])
        self.assertIn("codex", r.stdout + r.stderr)


class DropIns(Base):
    """Servers that belong to another repo live in <master dir>/mcp.d/*.json."""

    def drop(self, name, doc):
        d = self.master.parent / "mcp.d"
        d.mkdir(exist_ok=True)
        (d / name).write_text(doc if isinstance(doc, str) else json.dumps(doc))

    def test_drop_in_servers_are_merged_in(self):
        self.drop("extra.json", {"mcpServers": {"extra": {"type": "stdio", "command": "e"}}})
        self.run_sync("--targets", "claude")
        s = self.get("claude")["mcpServers"]
        self.assertEqual(s["extra"], {"type": "stdio", "command": "e"})
        self.assertIn("remote", s)

    def test_drop_in_wins_over_the_master_for_the_same_name(self):
        self.drop("work.json", {"mcpServers": {"remote": {"type": "http", "url": "https://override.example"}}})
        self.run_sync("--targets", "claude")
        self.assertEqual(self.get("claude")["mcpServers"]["remote"]["url"], "https://override.example")

    def test_drop_ins_apply_in_filename_order(self):
        self.drop("20-b.json", {"mcpServers": {"x": {"type": "stdio", "command": "b"}}})
        self.drop("10-a.json", {"mcpServers": {"x": {"type": "stdio", "command": "a"}}})
        self.run_sync("--targets", "claude")
        self.assertEqual(self.get("claude")["mcpServers"]["x"]["command"], "b")

    def test_a_broken_drop_in_stops_the_run_and_names_the_file(self):
        self.drop("bad.json", "{ not json")
        r = self.run_sync("--targets", "claude")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("bad.json", r.stdout + r.stderr)
        self.assertFalse(self.paths["claude"].exists())

    def test_drop_in_literal_secret_is_refused_like_the_master(self):
        self.drop("work.json", {"mcpServers": {"remote": {"type": "http", "url": "https://u.example",
                                                    "headers": {"Authorization": "Prefix " + FAKE}}}})
        r = self.run_sync("--targets", "claude", "--strict")
        self.assertEqual(r.returncode, 1)
        self.assertNotIn(FAKE, r.stdout + r.stderr)


class Template(Base):
    EXAMPLE = HERE / "references" / "mcp.example.json"

    def test_example_master_is_valid_and_strict_clean(self):
        module = runpy.run_path(str(SCRIPT))
        report = module["Report"]()
        for name, entry in json.loads(self.EXAMPLE.read_text())["mcpServers"].items():
            module["clean_server"](name, entry, report)
        self.assertEqual(report.refusals, [])

    def test_example_holds_only_placeholders_and_no_employer_data(self):
        text = self.EXAMPLE.read_text()
        for needle in ("atlassian.net", "ghp_", "Bearer "):
            self.assertNotIn(needle, text)
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text), "an email address")
        self.assertIn("${", text)


if __name__ == "__main__":
    unittest.main()

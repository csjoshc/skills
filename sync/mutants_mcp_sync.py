"""Run: python3 -I ~/.skills/sync/mutants_mcp_sync.py
Breaks one behavior of mcp_sync.py at a time in a temp copy; test_mcp_sync.py must then fail."""
import os, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / "mcp_sync.py").read_text()
MUTANTS = [
    ("opencode keeps ${VAR} instead of {env:VAR}", 'fmt = "{env:%s}"', 'fmt = "${%s}"'),
    ("literal secrets are no longer refused", "and not has_ref(v) and not allow(v)", "and False"),
    ("wrapper does not source work.env", "SOURCE_ENV = 'set -a; . ", "SOURCE_ENV = 'true; . "),
    ("args are not shell-quoted", "return shlex.quote(s)", "return s"),
    ("new files / pi lose their private mode", "mode = t.mode or (", "mode = (0o644 if False else 0o644) or ("),
    ("unchanged files are rewritten every run", "changed = doc != existing", "changed = True"),
    ("tool-only servers are wiped", "servers = doc.setdefault(target.root, {})",
     "servers = doc[target.root] = {}"),
    ("dry run writes", "elif changed and not dry:", "elif changed:"),
    ("strict does not abort", "if strict and refused:", "if False:"),
    ("pi keeps ${VAR} unexpanded", 'kept[k] = f"$ENV:{m.group(1)}"', "kept[k] = v"),
    ("running apps are written anyway", "busy = changed and not dry and check_apps and t.app and app_running(t.app)",
     "busy = False"),
    ("vscode alias is ignored", 'return ((entry or {}).get("names") or {}).get(target.name, name)', "return name"),
    ("alias entry is looked up by the master name", "old = servers.get(key)\n        for k in",
     "old = servers.get(name)\n        for k in"),
    ("codex gets servers that are not marked personal", 'if target.personal_only and entry.get("personal") is not True:', "if False:"),
    ("codex gets servers that need work.env", "    if mentions_ref(s):\n        ctx.report.warn(f\"{name}: skipped, it needs work.env secrets and Codex", "    if False:\n        ctx.report.warn(f\"{name}: skipped, it needs work.env secrets and Codex"),
    ("codex keeps the type field", 'out.pop("type", None)', "pass"),
    ("codex url headers keep the wrong name", 'out["http_headers"] = out.pop("headers")', "pass"),
    ("codex rewrites unchanged servers", "changed = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))",
     "changed = sorted(set(old) | set(new))"),
    ("codex result is not verified", "                    check_toml(new_text, doc)", "                    pass"),
    ("codex tool-only tables are dropped", "if len(path) > 1 and path[0] == root and path[1] in changed:",
     "if len(path) > 1 and path[0] == root:"),
    ("codex own per-server keys are lost", 'keep=("startup_timeout_sec"', 'keep=("zzz"'),
    ("drop-ins are ignored", "master.setdefault(\"mcpServers\", {}).update(servers)", "pass"),
    ("drop-ins apply in reverse order", "for f in sorted(drop.glob(\"*.json\"))", "for f in sorted(drop.glob(\"*.json\"), reverse=True)"),
    ("disabled servers stay in claude", 'if entry.get("enabled") is False:\n            actions[name] = "removed"',
     'if False:\n            actions[name] = "removed"'),
]


def main():
    bad = 0
    for name, old, new in MUTANTS:
        if old not in SRC:
            print(f"BAD MUTANT (pattern missing): {name}")
            bad += 1
            continue
        d = tempfile.mkdtemp()
        f = Path(d, "mcp_sync.py")
        f.write_text(SRC.replace(old, new, 1))
        r = subprocess.run([sys.executable, "-I", str(HERE / "test_mcp_sync.py")], capture_output=True,
                           text=True, env={**os.environ, "MCP_SYNC_SCRIPT": str(f)})
        survived = r.returncode == 0
        bad += survived
        print(("SURVIVED: " if survived else "killed:   ") + name)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

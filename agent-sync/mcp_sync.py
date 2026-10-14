#!/usr/bin/env python3
"""Project the MCP master (~/.secrets/mcp.json) into each tool's native config.

Secrets never travel as literals. A master "${VAR}" becomes the tool's own env reference
(opencode {env:VAR}, Claude Code ${VAR}, pi $ENV:VAR) or, for GUI apps that do not inherit the
shell env, a /bin/zsh wrapper that sources ~/.config/secrets/work.env first. A literal value in a
secret-named env/header field is refused (field dropped, warning, exit 1 with --strict).
Merges are surgical: servers in the master are upserted or, when disabled, removed; tool-only
servers and unrelated keys stay. Writes are temp file + atomic rename with a .bak.<ts> copy first.
Values are never printed.

Usage: mcp_sync.py [--dry-run] [--strict] [--targets a,b] [--master PATH] [--npx PATH]
Targets: claude, opencode, cursor, vscode, desktop, codex, pi, pi-gateway
codex is personal only: it receives just the servers marked "personal": true, never a ${VAR} one.
Servers from other repos can sit in <master dir>/mcp.d/*.json (same schema, applied in name
order after the master, same name wins).
"""
import argparse, copy, json, os, re, shlex, shutil, subprocess, sys, tempfile, time, tomllib
from pathlib import Path

HOME = Path.home()
MASTER = HOME / ".secrets" / "mcp.json"
REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
WHOLE_REF = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")
SECRET_NAME = re.compile(r"token|secret|key|password|passwd|auth|credential|cookie", re.I)
SOURCE_ENV = 'set -a; . "$HOME/.config/secrets/work.env"; '
EXTENSIONS = ("enabled", "allowedTools", "personal")  # agent-sync only, never written to a target


# ---- master parsing -------------------------------------------------------------------------

def server_kind(entry):
    kind = entry.get("type") or ("http" if "url" in entry else "stdio")
    return {"local": "stdio", "remote": "http", "streamable-http": "http"}.get(kind, kind)


def has_ref(value):
    return isinstance(value, str) and REF.search(value) is not None


def clean_server(name, entry, report, allow=lambda v: False):
    """Master entry -> neutral dict. Literal secrets in secret-named fields are refused."""
    kind = server_kind(entry)
    out = {"kind": kind, "allowed": entry.get("allowedTools") or []}
    for f in ("command", "args", "url"):
        if f in entry:
            out[f] = entry[f]
    for f in ("env", "headers"):
        kept = {}
        for k, v in (entry.get(f) or {}).items():
            if isinstance(v, str) and SECRET_NAME.search(k) and not has_ref(v) and not allow(v):
                report.refuse(f"{name}: refused {f}.{k}, it is a literal secret; "
                              "use a ${VAR} placeholder from work.env")
            else:
                kept[k] = v
        if kept:
            out[f] = kept
    return out


def mentions_ref(s):
    flat = [s.get("command"), s.get("url"), *(s.get("args") or []),
            *(s.get("env") or {}).values(), *(s.get("headers") or {}).values()]
    return any(has_ref(v) for v in flat)


class Report:
    def __init__(self):
        self.warnings, self.refusals = [], []

    def warn(self, msg):
        self.warnings.append(msg)

    def refuse(self, msg):
        self.refusals.append(msg)
        self.warnings.append(msg)


# ---- per-target translation of one server ---------------------------------------------------

def sub_refs(value, fmt):
    return REF.sub(lambda m: fmt % m.group(1), value) if isinstance(value, str) else value


def sub_all(obj, fmt):
    if isinstance(obj, dict):
        return {k: sub_all(v, fmt) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sub_all(v, fmt) for v in obj]
    return sub_refs(obj, fmt)


def to_claude(name, s, ctx):
    if s["kind"] == "stdio":
        if "command" not in s:
            ctx.report.warn(f"{name}: skipped, no command")
            return None
        out = {"type": "stdio", "command": s["command"]}
        args = list(s.get("args") or [])
        # mcp-atlassian takes its tool allowlist as a flag; Claude Code is where it is enforced.
        if "mcp-atlassian" in args and s["allowed"] and "--enabled-tools" not in args:
            args += ["--enabled-tools", ",".join(s["allowed"])]
        if args:
            out["args"] = args
        if s.get("env"):
            out["env"] = dict(s["env"])
        return out
    if "url" not in s:
        ctx.report.warn(f"{name}: skipped, no url")
        return None
    out = {"type": s["kind"], "url": s["url"]}
    if s.get("headers"):
        out["headers"] = dict(s["headers"])
    return out


def to_opencode(name, s, ctx):
    fmt = "{env:%s}"
    if s["kind"] == "stdio":
        if "command" not in s:
            ctx.report.warn(f"{name}: skipped, no command")
            return None
        out = {"type": "local", "command": [s["command"], *(s.get("args") or [])]}
        out["command"] = sub_all(out["command"], fmt)
        if s.get("env"):
            out["environment"] = sub_all(s["env"], fmt)
        return out
    if "url" not in s:
        ctx.report.warn(f"{name}: skipped, no url")
        return None
    out = {"type": "remote", "url": sub_refs(s["url"], fmt)}
    if s.get("headers"):
        out["headers"] = sub_all(s["headers"], fmt)
    return out


def dq_escape(s):
    return re.sub(r'([\\"$`])', r"\\\1", s)


def shell_word(s):
    """One shell word for s; a ${VAR} inside becomes a double-quoted $VAR expansion."""
    if not REF.search(s):
        return shlex.quote(s)
    parts, last = [], 0
    for m in REF.finditer(s):
        parts.append(dq_escape(s[last:m.start()]))
        nxt = s[m.end():m.end() + 1]
        parts.append("${%s}" % m.group(1) if nxt[:1].isalnum() or nxt == "_" else "$" + m.group(1))
        last = m.end()
    parts.append(dq_escape(s[last:]))
    return '"' + "".join(parts) + '"'


def zsh_entry(script, env, typed):
    out = {"command": "/bin/zsh", "args": ["-c", script]}
    if env:
        out["env"] = env
    if typed:
        out["type"] = "stdio"
    return out


def gui_stdio(name, s, ctx, typed):
    env, lines = {}, []
    for k, v in (s.get("env") or {}).items():
        m = WHOLE_REF.match(v) if isinstance(v, str) else None
        if m and m.group(1) == k:
            continue  # sourcing work.env already exports it under the same name
        if has_ref(v):
            lines.append(f"{k}={shell_word(v)}; ")
        else:
            env[k] = v
    cmd = " ".join(shell_word(x) for x in [s["command"], *(s.get("args") or [])])
    return zsh_entry(SOURCE_ENV + "".join(lines) + "exec " + cmd, env, typed)


def gui_remote(name, s, ctx, typed):
    npx = ctx.npx
    words = [shell_word(npx), "-y", "mcp-remote", shell_word(s["url"])]
    for k, v in (s.get("headers") or {}).items():
        words += ["--header", shell_word(f"{k}:{v}")]
    # node must be on PATH for npx; the bin dir comes first, the app's own PATH after it.
    prefix = f'PATH="{dq_escape(os.path.dirname(npx))}:$PATH"; '
    return zsh_entry(SOURCE_ENV + prefix + "exec " + " ".join(words), {}, typed)


def to_cursor(name, s, ctx):
    if s["kind"] == "stdio":
        if "command" not in s:
            ctx.report.warn(f"{name}: skipped, no command")
            return None
        if mentions_ref(s):
            return gui_stdio(name, s, ctx, typed=True)
        out = {"command": s["command"]}
        for f in ("args", "env"):
            if s.get(f):
                out[f] = s[f]
        out["type"] = "stdio"
        return out
    if "url" not in s:
        ctx.report.warn(f"{name}: skipped, no url")
        return None
    if mentions_ref(s):
        return gui_remote(name, s, ctx, typed=True)
    out = {"url": s["url"]}
    if s.get("headers"):
        out["headers"] = s["headers"]
    return out


def to_vscode(name, s, ctx):
    # Same wrappers as Cursor; VS Code's own schema wants an explicit type on url servers too.
    out = to_cursor(name, s, ctx)
    if out is not None and "type" not in out:
        out = {"type": s["kind"], **out}
    return out


def to_desktop(name, s, ctx):
    # Claude Desktop only speaks stdio, so every url server goes through mcp-remote.
    if s["kind"] == "stdio":
        if "command" not in s:
            ctx.report.warn(f"{name}: skipped, no command")
            return None
        if mentions_ref(s):
            return gui_stdio(name, s, ctx, typed=False)
        out = {"command": s["command"]}
        for f in ("args", "env"):
            if s.get(f):
                out[f] = s[f]
        return out
    if "url" not in s:
        ctx.report.warn(f"{name}: skipped, no url")
        return None
    return gui_remote(name, s, ctx, typed=False)


def to_pi(name, s, ctx):
    # pi rejects http with args/env and stdio with headers, and expands only a whole $ENV:VAR.
    fields = ("command", "args", "env") if s["kind"] == "stdio" else ("url", "headers")
    out = {"type": s["kind"]}
    for f in fields:
        if f not in s:
            continue
        if f in ("env", "headers"):
            kept = {}
            for k, v in s[f].items():
                m = WHOLE_REF.match(v) if isinstance(v, str) else None
                if m:
                    kept[k] = f"$ENV:{m.group(1)}"
                elif has_ref(v):
                    ctx.report.warn(f"{name}: dropped {f}.{k}, it has a ${{VAR}} inside a longer "
                                    "value, which pi cannot expand; make the master value a "
                                    "bare ${VAR}")
                else:
                    kept[k] = v
            if kept:
                out[f] = kept
        else:
            out[f] = s[f]
    if "command" not in out if s["kind"] == "stdio" else "url" not in out:
        ctx.report.warn(f"{name}: skipped, no {'command' if s['kind'] == 'stdio' else 'url'}")
        return None
    return out


def to_codex(name, s, ctx):
    # Codex is personal only: it never gets work.env, so a server that needs a secret is not
    # written at all. Its tables have no `type`, and url headers are called http_headers.
    if mentions_ref(s):
        ctx.report.warn(f"{name}: skipped, it needs work.env secrets and Codex is personal only")
        return None
    out = to_cursor(name, s, ctx)
    if out is None:
        return None
    out.pop("type", None)
    if "headers" in out:
        out["http_headers"] = out.pop("headers")
    return out


# ---- targets --------------------------------------------------------------------------------

class Target:
    def __init__(self, name, path, root, convert, keep=(), mode=None, app=None, soft_off=False,
                 alias=None, toml=False, personal_only=False):
        self.name, self.path, self.root, self.convert = name, Path(path), root, convert
        self.toml = toml  # config.toml: edited as text, only the tables this script owns
        self.personal_only = personal_only  # only servers marked "personal": true are written
        self.keep, self.mode, self.app, self.soft_off = tuple(keep), mode, app, soft_off
        self.alias = dict(alias or {})  # master name -> the name this tool already uses


def target_name(target, name):
    return target.alias.get(name, name)


# VS Code already has the remote server as "Aliased-Name"; renaming the master would break Claude Code
# permissions and tool prefixes that use "remote", so only this target is mapped.
VSCODE_ALIAS = {"remote": "Aliased-Name"}


def default_targets():
    app = HOME / "Library" / "Application Support"
    return [
        Target("claude", HOME / ".claude.json", "mcpServers", to_claude),
        Target("opencode", HOME / ".config" / "opencode" / "opencode.json", "mcp", to_opencode,
               keep=("enabled", "timeout", "oauth"), soft_off=True),
        Target("cursor", HOME / ".cursor" / "mcp.json", "mcpServers", to_cursor, app="Cursor"),
        Target("vscode", app / "Code" / "User" / "mcp.json", "servers", to_vscode, app="Code",
               alias=VSCODE_ALIAS),
        Target("desktop", app / "Claude" / "claude_desktop_config.json", "mcpServers",
               to_desktop, app="Claude"),
        # The Codex app, CLI and IDE share this file. Its own per-server tuning stays untouched.
        Target("codex", HOME / ".codex" / "config.toml", "mcp_servers", to_codex, toml=True,
               personal_only=True,
               keep=("startup_timeout_sec", "tool_timeout_sec", "enabled", "enabled_tools",
                     "disabled_tools", "default_tools_approval_mode", "required", "tools")),
        Target("pi", HOME / ".pi" / "agent" / "mcp.json", "mcpServers", to_pi, mode=0o600),
        Target("pi-gateway", HOME / ".gateway-pi" / "mcp.json", "mcpServers", to_pi, mode=0o600),
    ]


class Ctx:
    def __init__(self, report, npx):
        self.report, self.npx = report, npx


def find_npx(master):
    for e in master.get("mcpServers", {}).values():
        c = e.get("command")
        if isinstance(c, str) and os.path.basename(c) == "npx":
            return c
    return shutil.which("npx") or "npx"


def project(master, target, existing, npx, report):
    """Returns (new doc, {name: action})."""
    doc = copy.deepcopy(existing)  # not a JSON round trip: TOML can hold dates
    servers = doc.setdefault(target.root, {})
    ctx = Ctx(report, npx)
    allow = (lambda v: v.startswith(("$ENV:", "$CMD:"))) if target.convert is to_pi else None
    actions = {}
    for name, entry in master.get("mcpServers", {}).items():
        key = target_name(target, name)
        if target.personal_only and entry.get("personal") is not True:
            # Opt-in, so a new work server can never reach this tool by default.
            actions[name] = "not personal"
            if key in servers:
                report.warn(f"{name}: is in {target.name} but not marked personal; remove it by hand")
            continue
        if entry.get("enabled") is False and target.soft_off:
            # opencode has its own enabled flag, so an existing entry is switched off, not removed.
            old = servers.get(key)
            if isinstance(old, dict) and old.get("enabled") is not False:
                old["enabled"] = False
                actions[name] = "disabled in place"
            else:
                actions[name] = "disabled"
            continue
        if entry.get("enabled") is False:
            actions[name] = "removed" if servers.pop(key, None) is not None else "disabled"
            continue
        s = clean_server(name, entry, report, allow=allow or (lambda v: False))
        if s["kind"] not in ("stdio", "http", "sse"):
            report.warn(f"{name}: skipped, unsupported type {s['kind']!r}")
            actions[name] = "skipped"
            continue
        new = target.convert(name, s, ctx)
        if new is None:
            actions[name] = "skipped"
            continue
        old = servers.get(key)
        for k in target.keep:
            if isinstance(old, dict) and k in old and k not in new:
                new[k] = old[k]
        if old == new:
            actions[name] = "unchanged"
        else:
            actions[name] = "updated" if old is not None else "added"
            servers[key] = new
    if target.toml and not servers and target.root not in existing:
        del doc[target.root]  # nothing to write, so do not create an empty table or a file
    return doc, actions


def diff_paths(old, new, prefix=""):
    """Key paths that differ between two JSON docs. Values are never returned."""
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for k in sorted(set(old) | set(new)):
            p = f"{prefix}.{k}" if prefix else k
            if k not in old:
                out.append(f"+{p}")
            elif k not in new:
                out.append(f"-{p}")
            else:
                out += diff_paths(old[k], new[k], p)
        return out
    return [] if old == new else [f"~{prefix}"]


# ---- TOML (Codex) ---------------------------------------------------------------------------
# There is no TOML writer in the standard library, and rewriting the whole file would drop the
# comments and the tables Codex manages itself. So only the [mcp_servers.<name>...] blocks of
# servers that changed are cut out and re-emitted, and the result must parse back to exactly the
# projected document or nothing is written.

class TomlError(Exception):
    pass


BARE_KEY = re.compile(r"^[A-Za-z0-9_-]+$")


def toml_key(k):
    return k if BARE_KEY.match(k) else toml_value(k)


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False).replace("\x7f", "\\u007f")
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    raise TomlError(f"cannot write a {type(v).__name__} value")


def toml_tables(path, d):
    scalars = [(k, v) for k, v in d.items() if not isinstance(v, dict)]
    out = ["[" + ".".join(toml_key(p) for p in path) + "]\n"
           + "".join(f"{toml_key(k)} = {toml_value(v)}\n" for k, v in scalars)]
    for k, v in d.items():
        if isinstance(v, dict):
            out += toml_tables(path + [k], v)
    return out


def header_path(line):
    """Key path of a [table] or [[table]] header line, else None."""
    m = re.match(r"^\s*\[\[?\s*(.*?)\s*\]\]?\s*(?:#.*)?$", line.rstrip("\n"))
    if not m or line.lstrip().startswith("#"):
        return None
    parts, i, text = [], 0, m.group(1)
    while i < len(text):
        c = text[i]
        if c in " \t.":
            i += 1
        elif c in "\"'":
            j = i + 1
            while j < len(text) and text[j] != c:
                j += 2 if c == '"' and text[j] == "\\" else 1
            raw = text[i:j + 1]
            parts.append(json.loads(raw) if c == '"' else raw[1:-1])
            i = j + 1
        else:
            j = i
            while j < len(text) and text[j] not in " \t.":
                j += 1
            parts.append(text[i:j])
            i = j
    return parts or None


def toml_blocks(lines):
    """[(path, first line, last content line + 1)]; trailing blanks and comments stay outside."""
    blocks, in_ml = [], None
    for n, line in enumerate(lines):
        if in_ml is None:
            path = header_path(line)
            if path:
                blocks.append([path, n, n + 1])
            elif blocks and line.strip() and not line.lstrip().startswith("#"):
                blocks[-1][2] = n + 1
        elif blocks:
            blocks[-1][2] = n + 1
        for q in ('"""', "'''"):
            if line.count(q) % 2:
                in_ml = None if in_ml == q else (in_ml or q)
    return blocks


def render_toml(orig, existing, doc, root):
    old, new = existing.get(root, {}), doc.get(root, {})
    changed = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    if not changed:
        return orig
    lines = (orig or "").splitlines(keepends=True)
    drop, first = set(), {}
    for path, a, b in toml_blocks(lines):
        if len(path) > 1 and path[0] == root and path[1] in changed:
            drop.update(range(a, b))
            first.setdefault(path[1], a)
    chunks = {k: "\n".join(toml_tables([root, k], new[k])) for k in changed if k in new}
    out = []
    for n, line in enumerate(lines):
        # A rewritten server goes where its first table was, so the file keeps its order.
        for k in [k for k, a in first.items() if a == n and k in chunks]:
            out.append(chunks.pop(k))
        if n not in drop:
            out.append(line)
    text = "".join(out)
    if chunks:
        sep = "" if not text else ("" if text.endswith("\n") else "\n") + "\n"
        text += sep + "\n".join(chunks[k] for k in changed if k in chunks)
    if "\n\n\n" not in (orig or ""):
        text = re.sub(r"\n{3,}", "\n\n", text)  # cut-out blocks leave blank runs behind
    return text


def check_toml(text, doc):
    try:
        got = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise TomlError(f"the result is not valid TOML ({e})")
    if got != doc:
        raise TomlError("the result does not parse back to the planned servers")


# ---- file writing ---------------------------------------------------------------------------

def render(doc, orig_text):
    indent = 2
    m = re.search(r"\n( +)\S", orig_text or "")
    if m:
        indent = len(m.group(1))
    tail = "\n" if orig_text is None or orig_text.endswith("\n") else ""
    return json.dumps(doc, indent=indent, ensure_ascii=False) + tail


def write_atomic(path, text, mode, backup=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        bak = path.with_name(f"{path.name}.bak.{time.strftime('%Y%m%d-%H%M%S')}")
        bak.write_bytes(path.read_bytes())
        os.chmod(bak, 0o600)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def prune_claude_settings(dry):
    """A mcpServers key in ~/.claude/settings.json breaks Claude Code's whole settings file."""
    p = HOME / ".claude" / "settings.json"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    doc = json.loads(text)
    if "mcpServers" not in doc:
        return False
    if not dry:
        del doc["mcpServers"]
        write_atomic(p, render(doc, text), p.stat().st_mode & 0o777)
    return True


def app_running(app):
    r = subprocess.run(["pgrep", "-x", app], capture_output=True)
    return r.returncode == 0


def sync(master, targets, dry, strict=False, npx=None, check_apps=True, out=print):
    """Returns the process exit code."""
    npx = npx or find_npx(master)
    plan = []
    for t in targets:
        report = Report()
        text = t.path.read_text(encoding="utf-8") if t.path.exists() else None
        try:
            existing = (tomllib.loads(text) if t.toml else json.loads(text)) if text else {}
        except (tomllib.TOMLDecodeError, ValueError) as e:
            out(f"{t.name}: cannot read {t.path} ({e}); nothing written")
            return 1
        doc, actions = project(master, t, existing, npx, report)
        new_text = None
        if doc != existing:
            try:
                new_text = render_toml(text, existing, doc, t.root) if t.toml else render(doc, text)
                if t.toml:
                    check_toml(new_text, doc)
            except TomlError as e:
                out(f"{t.name}: refusing to write {t.path}: {e}; nothing written")
                return 1
        plan.append((t, text, existing, doc, actions, report, new_text))
    refused = sum(len(p[5].refusals) for p in plan)
    if strict and refused:
        for t, *_, report, _new in plan:
            for w in report.warnings:
                out(f"{t.name}: warning: {w}")
        out(f"strict: {refused} literal secret field(s) refused; nothing written")
        return 1
    for t, text, existing, doc, actions, report, new_text in plan:
        changed = doc != existing
        busy = changed and not dry and check_apps and t.app and app_running(t.app)
        tag = " (dry run)" if dry else ""
        out(f"{t.name} {t.path}{tag}: " + ", ".join(f"{n}={a}" for n, a in sorted(actions.items())))
        for p in diff_paths(existing, doc):
            out(f"  {p}")
        if busy:
            out(f"  skipped: {t.app} is running, quit it and re-run")
        elif changed and not dry:
            mode = t.mode or (t.path.stat().st_mode & 0o777 if t.path.exists() else 0o600)
            write_atomic(t.path, new_text, mode)
        elif not dry and t.mode and t.path.exists():
            os.chmod(t.path, t.mode)
        owned = {target_name(t, n) for n in master.get("mcpServers", {})}
        kept = sorted(set(doc.get(t.root, {})) - owned)
        out("  tool-only servers kept: " + (", ".join(kept) or "none"))
        for w in report.warnings:
            out("  warning: " + w)
        if t.name == "claude" and prune_claude_settings(dry):
            out("  removed mcpServers from ~/.claude/settings.json" if not dry else
                "  would remove mcpServers from ~/.claude/settings.json")
    if any(t.convert is to_pi for t in targets):
        out("New or changed pi servers start untrusted: run /mcp trust <name> once for each.")
    return 0


def load_master(path, out=print):
    """The master plus <its dir>/mcp.d/*.json, so another repo can ship its own servers."""
    master = json.loads(path.read_text())
    drop = path.parent / "mcp.d"
    for f in sorted(drop.glob("*.json")) if drop.is_dir() else []:
        try:
            extra = json.loads(f.read_text())
        except ValueError as e:
            raise SystemExit(f"{f}: not valid JSON ({e}); nothing written")
        servers = extra.get("mcpServers", {})
        master.setdefault("mcpServers", {}).update(servers)
        out(f"drop-in {f}: {', '.join(servers) or 'no servers'}")
    return master


def main(argv=None):
    names = [t.name for t in default_targets()]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--master", type=Path, default=MASTER)
    ap.add_argument("--targets", default=",".join(names), help="comma list of: " + ", ".join(names))
    ap.add_argument("--npx", help="npx path for mcp-remote wrappers (default: from the master)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 and write nothing on a literal secret")
    ap.add_argument("--ignore-running", action="store_true", help="write GUI app files even if running")
    args = ap.parse_args(argv)
    wanted = [n.strip() for n in args.targets.split(",") if n.strip()]
    bad = [n for n in wanted if n not in names]
    if bad:
        ap.error("unknown target(s): " + ", ".join(bad))
    targets = [t for t in default_targets() if t.name in wanted]
    master = load_master(args.master)
    return sync(master, targets, args.dry_run, args.strict, args.npx, not args.ignore_running)


if __name__ == "__main__":
    sys.exit(main())

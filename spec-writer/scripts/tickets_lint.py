#!/usr/bin/env python3
"""Mechanical checks for .tickets/*.md against shared/TICKET_CONTRACT.md.

Usage: tickets_lint.py <tickets-dir> [--root <repo>] [--runner "<pytest cmd>"] [--dry-red]
Exit 0 when no ERROR lines were printed, 1 otherwise. Stdlib only.
"""

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

STAGES = {"NEW", "SPEC", "SPEC_SPLIT", "PLAN", "BLOCKED", "BUILD", "REVIEW", "COMPLETE", "FAILED"}
ACTIONS = {"CREATE", "MODIFY", "VERIFY", "DELETE"}
REQUIRED_KEYS = ["id", "title", "Stage", "Depends-On", "Files"]
# Section name -> accepted headings; older tickets use the longer names.
SECTIONS = {
    "Scope": ("Scope",),
    "AC": ("Acceptance Criteria → Tests",),
    "Verify": ("Verify",),
    "Notes": ("Notes", "Technical Notes"),
}
GATE_SECTIONS = {
    "Silent Failure Detection": ("Silent Failure Detection",),
    "Proof": ("Proof", "Proof Artifacts"),
}
MAX_PROD_FILES = 5
EM_DASH = "—"
NODE_ID = re.compile(r"^[\w./-]+\.py(::[\w\[\].-]+)+$")
# A -k expression with "or" passes when any one name exists, so a missing test goes unnoticed.
K_OR_CHAIN = re.compile(r"-k\s+[\"'][^\"']*\bor\b")
SAFE_FIRST_WORDS = {"grep", "test", "jq", "diff", "wc", "!"}


class Report:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def error(self, where, msg):
        self.errors += 1
        print(f"ERROR {where}: {msg}")

    def warn(self, where, msg):
        self.warnings += 1
        print(f"WARN  {where}: {msg}")


def parse_scalar(text):
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [parse_scalar(x) for x in inner.split(",")] if inner else []
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def parse_frontmatter(lines):
    """Parse the YAML subset tickets use: scalars, [lists], - scalar lists, - key: value dicts."""
    data, key = {}, None
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0:
            k, _, v = line.partition(":")
            key = k.strip()
            data[key] = parse_scalar(v) if v.strip() else []
        elif key is not None and line.startswith("- "):
            item = line[2:]
            if re.match(r"^[\w-]+:\s", item + " ") and not item.startswith(("\"", "'")):
                k, _, v = item.partition(":")
                data[key].append({k.strip(): parse_scalar(v)})
            else:
                data[key].append(parse_scalar(item))
        elif key is not None and isinstance(data.get(key), list) and data[key] and isinstance(data[key][-1], dict):
            k, _, v = line.partition(":")
            data[key][-1][k.strip()] = parse_scalar(v)
    return data


def split_ticket(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, text
    return parse_frontmatter(lines[1:end]), "\n".join(lines[end + 1:])


def sections(body):
    """Map heading text to section content for every '## ' heading."""
    found, order, current = {}, [], None
    for line in body.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            order.append(current)
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return {k: "\n".join(v) for k, v in found.items()}, order


def find_section(found, names):
    for name in names:
        for heading in found:
            if heading == name or heading.startswith(name + " "):
                return heading
    return None


def bash_blocks(text):
    # Only a fence on its own line closes the block, so ``` inside a command (an awk pattern) is safe.
    return re.findall(r"^```(?:bash|sh)\n(.*?)^```[ \t]*$", text, re.S | re.M)


def table_rows(text):
    rows = [ln for ln in text.split("\n") if ln.strip().startswith("|")]
    out = []
    for ln in rows:
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        out.append(cells)
    return out


def check_cell(cell):
    cell = cell.strip()
    m = re.fullmatch(r"`(.*)`", cell, re.S)
    return m.group(1).strip() if m else cell


def resolve(root, path):
    p = Path(path).expanduser()
    return p if p.is_absolute() else root / p


def ancestors(tid, deps):
    seen, stack = set(), list(deps.get(tid, []))
    while stack:
        d = stack.pop()
        if d not in seen:
            seen.add(d)
            stack.extend(deps.get(d, []))
    return seen


def lint_shell(where, script, rep, label):
    proc = subprocess.run(["bash", "-n"], input=script, text=True, capture_output=True)
    if proc.returncode != 0:
        rep.error(where, f"{label} fails bash -n: {proc.stderr.strip()}")
    for n, line in enumerate(script.split("\n"), 1):
        stripped = line.strip()
        if re.match(r"^!\s", stripped):
            rep.error(where, f"{label} line {n}: bare '! cmd' never fails under set -e; use 'if cmd; then exit 1; fi'")
        if K_OR_CHAIN.search(stripped):
            rep.error(where, f"{label} line {n}: -k or-chain hides missing tests; use one test id per run")


def lint_ticket(path, meta, body, ctx, rep):
    where = path.name
    for k in REQUIRED_KEYS:
        if k not in meta:
            rep.error(where, f"frontmatter missing {k}")
    stage = meta.get("Stage")
    if stage not in STAGES:
        rep.error(where, f"Stage {stage!r} not one of {sorted(STAGES)}")
    if stage == "BLOCKED":
        if not meta.get("Blocked-By"):
            rep.error(where, "BLOCKED ticket needs Blocked-By")
        if not meta.get("Unblock-Check"):
            rep.error(where, "BLOCKED ticket needs Unblock-Check")
        else:
            lint_shell(where, str(meta["Unblock-Check"]), rep, "Unblock-Check")
    tid = meta.get("id")
    for dep in meta.get("Depends-On") or []:
        if dep not in ctx["ids"]:
            rep.error(where, f"Depends-On {dep} is not a ticket id")
    for b in meta.get("Blocks") or []:
        if b not in ctx["ids"]:
            rep.warn(where, f"Blocks {b} is not a ticket id")

    files = meta.get("Files") or []
    if not files:
        rep.error(where, "Files needs at least one entry")
    upstream = set()
    for a in ancestors(tid, ctx["deps"]):
        upstream |= ctx["creates"].get(a, set())
    prod = 0
    for f in files:
        if not isinstance(f, dict) or "path" not in f or "action" not in f:
            rep.error(where, f"Files entry {f!r} needs action and path")
            continue
        if f["action"] not in ACTIONS:
            rep.error(where, f"Files action {f['action']} not one of {sorted(ACTIONS)}")
        if str(f.get("test", "false")).lower() != "true" and f["action"] in {"CREATE", "MODIFY", "DELETE"}:
            prod += 1
        if f["action"] in {"MODIFY", "VERIFY", "DELETE"}:
            check_path(where, f["path"], upstream, ctx, rep, f"Files {f['action']}")
    if prod > MAX_PROD_FILES:
        rep.error(where, f"{prod} non-test files; split above {MAX_PROD_FILES}")
    for p in meta.get("Read-First") or []:
        check_path(where, p, upstream | ctx["creates"].get(tid, set()), ctx, rep, "Read-First")

    found, order = sections(body)
    required = dict(SECTIONS)
    is_gate = meta.get("Type") == "integration-gate"
    if is_gate:
        required.update(GATE_SECTIONS)
    elif str(tid).startswith("IG-"):
        rep.warn(where, "id looks like a gate but Type is not integration-gate")
    heads = {}
    for name, aliases in required.items():
        h = find_section(found, aliases)
        if h is None:
            rep.error(where, f"missing section ## {aliases[0]}")
        heads[name] = h
    positions = [order.index(heads[n]) for n in SECTIONS if heads.get(n)]
    if positions != sorted(positions):
        rep.error(where, "sections out of order; want Scope, Acceptance Criteria → Tests, Verify, Notes")

    if heads.get("AC"):
        lint_ac_table(where, found[heads["AC"]], ctx, rep)
    if heads.get("Verify"):
        blocks = bash_blocks(found[heads["Verify"]])
        if not blocks:
            rep.error(where, "## Verify has no bash block")
        for i, b in enumerate(blocks, 1):
            lint_shell(where, b, rep, f"Verify block {i}")
            if "set -e" not in b and "set -eu" not in b and not re.search(r"set -[a-z]*e", b):
                rep.error(where, f"Verify block {i} lacks set -e, so a failing line won't fail it")

    text = path.read_text()
    if EM_DASH in text:
        rep.error(where, f"{text.count(EM_DASH)} em dash(es); use a plain dash")


def check_path(where, p, upstream, ctx, rep, label):
    if any(ch in p for ch in "*?["):
        return
    if resolve(ctx["root"], p).exists() or p in upstream:
        return
    rep.error(where, f"{label} {p} doesn't exist and no upstream ticket creates it")


def lint_ac_table(where, text, ctx, rep):
    rows = table_rows(text)
    if not rows:
        rep.error(where, "AC table not found")
        return
    header = [h.lower() for h in rows[0]]

    def col(*names):
        for i, h in enumerate(header):
            if any(h == n or h.startswith(n) for n in names):
                return i
        return None

    ac_i, check_i, tier_i = col("ac"), col("check", "test file / command"), col("tier", "risk tier")
    if None in (ac_i, check_i, tier_i):
        rep.error(where, "AC table needs AC, Check and Tier columns")
        return
    body = rows[1:]
    if len(body) < 3:
        rep.error(where, f"AC table has {len(body)} rows; need at least 3")
    if not any("failure path" in r[ac_i].lower() for r in body if len(r) > ac_i):
        rep.error(where, "no AC row marked (failure path)")
    for r in body:
        if len(r) <= max(ac_i, check_i, tier_i):
            rep.error(where, f"AC row has too few cells: {r}")
            continue
        label = r[ac_i].split()[0] if r[ac_i] else "?"
        check = check_cell(r[check_i])
        if not check:
            rep.error(where, f"{label} has no check")
        if r[tier_i] not in {"T1", "T2", "T3"}:
            rep.error(where, f"{label} tier {r[tier_i]!r} not T1/T2/T3")
        if K_OR_CHAIN.search(check):
            rep.error(where, f"{label} check uses a -k or-chain")
        ctx["checks"].append((where, label, check))


def is_safe_shell(cmd):
    """Read-only checks only: every pipeline segment starts with a known read-only word."""
    if re.search(r"[^-]>|\$\(|`", cmd):
        return False
    for seg in re.split(r"\|\||&&|\||;", cmd):
        words = seg.strip().split()
        if not words or words[0] not in SAFE_FIRST_WORDS:
            return False
        if words[0] == "!" and (len(words) < 2 or words[1] not in SAFE_FIRST_WORDS - {"!"}):
            return False
    return True


def dry_red(ctx, runner, rep):
    """Run checks now, before build: expect them to fail for a reason other than a broken environment."""
    root = ctx["root"]
    runner_cmd = shlex.split(runner) if runner else None
    if runner_cmd:
        try:
            probe = subprocess.run(runner_cmd + ["--version"], cwd=root, capture_output=True, text=True)
            why = None if probe.returncode == 0 else (probe.stderr or probe.stdout).strip()[:200]
        except OSError as exc:
            why = str(exc)
        if why is not None:
            rep.error("dry-red", f"runner {runner!r} doesn't start: {why}")
            runner_cmd = None
    ran = skipped = 0
    for where, label, check in ctx["checks"]:
        if NODE_ID.match(check):
            if not runner_cmd:
                skipped += 1
                continue
            proc = subprocess.run(runner_cmd + ["-q", check], cwd=root, capture_output=True, text=True, timeout=300)
        elif is_safe_shell(check):
            proc = subprocess.run(["bash", "-c", check], cwd=root, capture_output=True, text=True, timeout=60)
        else:
            skipped += 1
            continue
        ran += 1
        out = proc.stdout + proc.stderr
        if proc.returncode == 127 or "command not found" in out:
            rep.error(where, f"{label} breaks for an environmental reason: {out.strip()[:200]}")
        elif proc.returncode == 0:
            rep.warn(where, f"{label} passes before build (fine only for a preservation check)")
    print(f"dry-red: {ran} checks run, {skipped} not run (side effects or no runner)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tickets", type=Path)
    ap.add_argument("--root", type=Path, help="repo root (default: parent of the tickets dir)")
    ap.add_argument("--runner", help="pytest command for test-id checks, e.g. 'python3 -m pytest'")
    ap.add_argument("--dry-red", action="store_true", help="run checks now and classify their failures")
    args = ap.parse_args(argv)
    root = (args.root or args.tickets.resolve().parent).resolve()
    rep = Report()
    parsed = []
    for path in sorted(args.tickets.glob("*.md")):
        meta, body = split_ticket(path.read_text())
        if meta is None:
            rep.error(path.name, "no YAML frontmatter")
            continue
        parsed.append((path, meta, body))
    ctx = {"root": root, "ids": set(), "deps": {}, "creates": {}, "checks": []}
    for path, meta, _ in parsed:
        tid = meta.get("id")
        if tid in ctx["ids"]:
            rep.error(path.name, f"duplicate id {tid}")
        ctx["ids"].add(tid)
        ctx["deps"][tid] = list(meta.get("Depends-On") or [])
        ctx["creates"][tid] = {f["path"] for f in meta.get("Files") or [] if isinstance(f, dict) and f.get("action") == "CREATE" and "path" in f}
    for path, meta, body in parsed:
        lint_ticket(path, meta, body, ctx, rep)
    if args.dry_red:
        dry_red(ctx, args.runner, rep)
    print(f"{len(parsed)} tickets: {rep.errors} errors, {rep.warnings} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())

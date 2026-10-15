#!/usr/bin/env python3
"""red_first.py: every test added or changed between base and head must fail without the change.

Runs those tests at head, then against base source plus head tests, with names that head adds
stubbed to return None. A test that still passes there does not pin the change and is flagged.
Read-only on git: both trees are `git archive` exports in a temp dir.

Exit 0 PASS, 1 FAIL, 2 could not run. JSON verdict on stdout.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

EXEMPT = re.compile(r"#\s*red-first:\s*exempt\b\s*(.*)")
STUB_BODY = [ast.Return(value=ast.Constant(value=None))]
# An editable install's finder resolves modules missing from the export to the real working tree.
RUN_PYTEST = ("import sys; sys.meta_path[:] = [f for f in sys.meta_path "
              "if 'editable' not in getattr(f, '__name__', type(f).__name__).lower()]; "
              "import pytest; sys.exit(pytest.main(sys.argv[1:]))")


class GateError(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode:
        raise GateError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def resolve(repo: Path, rev: str) -> str:
    # A rev that starts with '-' would be parsed as an option by later git calls.
    if rev.startswith("-"):
        raise GateError(f"bad revision {rev!r}")
    return git(repo, "rev-parse", "--verify", "--end-of-options", f"{rev}^{{commit}}")


def default_base(repo: Path, head: str) -> str:
    for ref in ("main", "origin/main", "master", "origin/master"):
        try:
            return git(repo, "merge-base", head, resolve(repo, ref))
        except GateError:
            continue
    raise GateError("no main or master to diff against; pass --base")


def export(repo: Path, rev: str, dest: Path) -> None:
    dest.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", rev], capture_output=True)
    if archive.returncode:
        raise GateError(f"git archive {rev}: {archive.stderr.decode().strip()}")
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)


def is_test_path(path: str) -> bool:
    p = Path(path)
    return (p.suffix == ".py" and (
        "tests" in p.parts or "test" in p.parts or p.name.startswith("test_")
        or p.name.endswith("_test.py") or p.name == "conftest.py"))


def changed_files(repo: Path, base: str, head: str) -> list[tuple[str, str]]:
    out = git(repo, "diff", "--name-status", "--no-renames", base, head)
    return [(line[0], line.split("\t", 1)[1]) for line in out.splitlines() if line]


def read(tree: Path, rel: str) -> str | None:
    p = tree / rel
    return p.read_text() if p.is_file() else None


# --- which tests changed -------------------------------------------------------------------

def test_defs(src: str | None) -> dict[str, ast.AST]:
    if not src:
        return {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    out: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            out[node.name] = node
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test"):
                    out[f"{node.name}::{sub.name}"] = sub
    return out


def exemption(src: str, node: ast.AST) -> str | None:
    lines = src.splitlines()
    start = min([d.lineno for d in node.decorator_list] + [node.lineno]) - 2  # one line above too
    for line in lines[max(start, 0):node.end_lineno]:
        m = EXEMPT.search(line)
        if m:
            return m.group(1).strip() or "no reason given"
    return None


def candidate_tests(head_tree: Path, base_tree: Path, test_files: list[str]) -> list[dict]:
    found = []
    for rel in test_files:
        head_src = read(head_tree, rel)
        if head_src is None or Path(rel).name == "conftest.py":
            continue
        base_defs = {k: ast.dump(v) for k, v in test_defs(read(base_tree, rel)).items()}
        for name, node in test_defs(head_src).items():
            if base_defs.get(name) != ast.dump(node):
                found.append({"id": f"{rel}::{name}", "exempt": exemption(head_src, node)})
    return found


# --- base source with head's new names stubbed ---------------------------------------------

def stub_def(node: ast.AST) -> ast.AST:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        node.body = list(STUB_BODY)
    elif isinstance(node, ast.ClassDef):
        for sub in node.body:
            stub_def(sub)
    return node


def defined_names(body: list[ast.stmt]) -> set[str]:
    names = set()
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names |= {t.id for t in targets if isinstance(t, ast.Name)}
    return names


def stubbed_source(base_src: str | None, head_src: str) -> str:
    """Base module plus a None-returning stub for every top-level name or method head adds."""
    head = ast.parse(head_src)
    base = ast.parse(base_src or "")
    have = defined_names(base.body)
    base_imports = {ast.dump(n) for n in base.body if isinstance(n, (ast.Import, ast.ImportFrom))}
    base_classes = {n.name: n for n in base.body if isinstance(n, ast.ClassDef)}

    # New imports go after any __future__ imports so stubbed classes can resolve their bases.
    new_imports = [n for n in head.body if isinstance(n, (ast.Import, ast.ImportFrom))
                   and ast.dump(n) not in base_imports
                   and not (isinstance(n, ast.ImportFrom) and n.module == "__future__")]
    added: list[ast.stmt] = []
    for node in head.body:
        if isinstance(node, ast.ClassDef) and node.name in base_classes:
            bc = base_classes[node.name]
            methods = defined_names(bc.body)
            bc.body += [stub_def(m) for m in node.body
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name not in methods]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name not in have:
            added.append(stub_def(node))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            new = defined_names([node]) - have
            added += [ast.Assign(targets=[ast.Name(id=n, ctx=ast.Store())], value=ast.Constant(None))
                      for n in sorted(new)]
    cut = next((i for i, n in enumerate(base.body)
                if not (isinstance(n, ast.ImportFrom) and n.module == "__future__")
                and not (i == 0 and isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))), len(base.body))
    base.body = base.body[:cut] + new_imports + base.body[cut:] + added
    return ast.unparse(ast.fix_missing_locations(base)) + "\n"


def build_base(base_tree: Path, head_tree: Path, files: list[tuple[str, str]]) -> None:
    """Turn the base export into base source + head tests + stubs for head's new names."""
    for st, rel in files:
        head_src = read(head_tree, rel)
        dest = base_tree / rel
        if is_test_path(rel) or not rel.endswith(".py"):
            if is_test_path(rel):
                if head_src is None:
                    dest.unlink(missing_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(head_src)
            continue
        if head_src is None:
            continue
        try:
            text = stubbed_source(read(base_tree, rel), head_src)
        except SyntaxError:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)


# --- running pytest ------------------------------------------------------------------------

def find_python(repo: Path, override: str | None) -> str:
    if override:
        return override
    for cand in (repo / ".venv/bin/python", repo / "venv/bin/python"):
        if cand.exists():
            return str(cand)
    raise GateError("no .venv/bin/python in the repo; pass --python")


def run_pytest(python: str, tree: Path, ids: list[str], timeout: int) -> tuple[dict[str, str], str]:
    """Return {test_id: passed|failed|error|missing} plus a log tail."""
    xml = tree / ".red_first.xml"
    env = {**os.environ, "PYTHONPATH": str(tree) + os.pathsep + os.environ.get("PYTHONPATH", ""),
           "PYTHONDONTWRITEBYTECODE": "1"}
    cmd = [python, "-c", RUN_PYTEST, "-q", "-p", "no:cacheprovider", f"--junitxml={xml}", *ids]
    try:
        r = subprocess.run(cmd, cwd=tree, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise GateError(f"pytest timed out after {timeout}s in {tree.name}")
    log = (r.stdout + r.stderr)[-3000:]
    results: dict[str, list[str]] = {}
    if xml.exists():
        for case in ET.parse(xml).iter("testcase"):
            # junit classname is dotted path + optional class; rebuild the pytest node id.
            name = re.sub(r"\[.*\]$", "", case.get("name", ""))
            parts = case.get("classname", "").split(".")
            outcome = "passed"
            if case.find("failure") is not None or case.find("error") is not None:
                outcome = "failed"
            elif case.find("skipped") is not None:
                outcome = "skipped"
            for tid in ids:
                rel, _, func = tid.partition("::")
                mod = rel[:-3].replace("/", ".")
                cls, _, meth = func.rpartition("::")
                if name == meth and ".".join(parts) == (f"{mod}.{cls}" if cls else mod):
                    results.setdefault(tid, []).append(outcome)
    out = {}
    for tid in ids:
        got = results.get(tid)
        if not got:
            out[tid] = "error" if r.returncode in (2, 3, 4) or "error" in log.lower() else "missing"
        elif "failed" in got:
            out[tid] = "failed"
        elif all(o == "skipped" for o in got):
            out[tid] = "skipped"
        else:
            out[tid] = "passed"
    return out, log


# --- main ----------------------------------------------------------------------------------

def gate(repo: Path, base_rev: str | None, head_rev: str, python: str | None, timeout: int) -> dict:
    head = resolve(repo, head_rev)
    base = resolve(repo, base_rev) if base_rev else default_base(repo, head)
    if git(repo, "rev-parse", f"{base}^{{tree}}") == git(repo, "rev-parse", f"{head}^{{tree}}"):
        raise GateError("base equals head: nothing to check")
    files = changed_files(repo, base, head)
    test_files = [rel for _, rel in files if is_test_path(rel)]
    source_py = [rel for _, rel in files if rel.endswith(".py") and not is_test_path(rel)]
    verdict = {"base": base, "head": head, "kind": "feature" if source_py else "tests-only", "tests": []}
    if not source_py:
        verdict.update(verdict="PASS", detail="no source change, so no test can be red-first")
        return verdict

    py = find_python(repo, python)
    with tempfile.TemporaryDirectory(prefix="red-first.") as tmp:
        head_tree, base_tree = Path(tmp, "head"), Path(tmp, "base")
        export(repo, head, head_tree)
        export(repo, base, base_tree)
        cands = candidate_tests(head_tree, base_tree, test_files)
        if not cands:
            verdict.update(verdict="PASS", detail="source changed but no tests were added or changed")
            return verdict
        ids = [c["id"] for c in cands]
        at_head, head_log = run_pytest(py, head_tree, ids, timeout)
        build_base(base_tree, head_tree, files)
        green = [i for i in ids if at_head[i] == "passed"]
        at_base, base_log = run_pytest(py, base_tree, green, timeout) if green else ({}, "")

    for c in cands:
        tid, h = c["id"], at_head[c["id"]]
        if h == "skipped":
            row = {"status": "skipped", "detail": "skipped at head (marker or missing dependency); not judged"}
        elif h != "passed":
            row = {"status": "fails_at_head", "detail": f"{h} at head; fix it before red-first can judge it"}
        elif c["exempt"]:
            row = {"status": "exempt", "detail": c["exempt"]}
        elif at_base[tid] == "passed":
            row = {"status": "flagged", "detail": "passes without the change: assert on behavior the change adds"}
        elif at_base[tid] == "error":
            row = {"status": "red", "detail": "errors at base (collection or import), not a clean failure"}
        else:
            row = {"status": "red", "detail": f"{at_base[tid]} at base"}
        verdict["tests"].append({"id": tid, **row})
    bad = [t for t in verdict["tests"] if t["status"] in ("flagged", "fails_at_head")]
    verdict["verdict"] = "FAIL" if bad else "PASS"
    verdict["detail"] = f"{len(bad)} of {len(cands)} changed tests do not pin the change" if bad \
        else f"all {len(cands)} changed tests fail without the change"
    if bad:
        verdict["log_tail"] = {"head": head_log[-1500:], "base": base_log[-1500:]}
    return verdict


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", help="default: merge-base with main")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--python", help="default: <repo>/.venv/bin/python")
    ap.add_argument("--timeout", type=int, default=120, help="seconds per pytest run")
    args = ap.parse_args(argv)
    try:
        repo = Path(git(Path(args.repo), "rev-parse", "--show-toplevel"))
        v = gate(repo, args.base, args.head, args.python, args.timeout)
    except GateError as e:
        print(json.dumps({"verdict": "ERROR", "error": str(e)}, indent=2))
        return 2
    print(json.dumps(v, indent=2))
    for t in v["tests"]:
        if t["status"] in ("flagged", "fails_at_head"):
            print(f"red-first: {t['id']}: {t['detail']}", file=sys.stderr)
    return 0 if v["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

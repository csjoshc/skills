#!/usr/bin/env python3
"""Register the merge gate in installed agent harnesses, idempotently.

Usage:
  register-gate.py [--dry-run] [claude|codex|opencode|omp|all]

`all` touches only harnesses whose config directory exists. A stale registration that still
points at an old checkout (a worktree, a renamed home) is repointed in place. JSON files keep
everything else and are backed up before a change; links are relinked, never copied.
After a Codex change, run `/hooks` once in a real session: Codex skips an untrusted hook.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HOOKS = Path(__file__).resolve().parent
GATE = HOOKS / "merge-gate.py"
ADAPTERS = HOOKS / "adapters"
MARK = "merge-gate"

CLAUDE_MATCHER = "^(Bash|mcp__.*)$"


@dataclass
class Roots:
    claude: Path
    codex: Path
    opencode: Path
    omp: Path

    @classmethod
    def current(cls) -> "Roots":
        home = Path(os.environ.get("HOME") or Path.home())
        xdg = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
        return cls(
            claude=Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude"),
            codex=Path(os.environ.get("CODEX_HOME") or home / ".codex"),
            opencode=xdg / "opencode",
            omp=Path(os.environ.get("PI_CODING_AGENT_DIR") or home / ".omp" / "agent"),
        )


@dataclass
class Result:
    harness: str
    action: str  # ok | changed | would | skip | conflict
    detail: str

    def line(self) -> str:
        return f"{self.action:8} {self.harness}: {self.detail}"


def command_for(hook: dict[str, Any]) -> str:
    return str(hook.get("command", ""))


def is_ours(group: Any) -> bool:
    """A group that already runs this gate, at any path, under any matcher."""
    if not isinstance(group, dict):
        return False
    for hook in group.get("hooks") or []:
        if isinstance(hook, dict) and MARK in command_for(hook):
            return True
    return False


def replace_group(groups: list[Any], desired: dict[str, Any]) -> tuple[list[Any], bool]:
    """Swap the first gate group in place, or append one. Foreign groups are left alone."""
    for i, group in enumerate(groups):
        if is_ours(group):
            if group == desired:
                return groups, False
            merged = list(groups)
            merged[i] = desired
            return merged, True
    return [*groups, desired], True


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON is not an object")
    return data


def write_json(path: Path, data: dict[str, Any], dry: bool) -> None:
    if dry:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    if path.exists():
        backup = path.with_name(f"{path.name}.pre-merge-gate.{stamp}")
        shutil.copy2(path, backup)
        mode = path.stat().st_mode
    else:
        mode = 0o600
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp, mode & 0o777)
    os.replace(tmp, path)


def register_json(name: str, path: Path, desired: dict[str, Any], dry: bool) -> Result:
    try:
        data = load_json(path)
    except (json.JSONDecodeError, ValueError) as exc:
        return Result(name, "conflict", f"{path}: {exc}; left unchanged")
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        return Result(name, "conflict", f"{path}: hooks is not an object; left unchanged")
    groups = hooks.setdefault("PreToolUse", [])
    if not isinstance(groups, list):
        return Result(name, "conflict", f"{path}: hooks.PreToolUse is not a list; left unchanged")
    groups, changed = replace_group(groups, desired)
    hooks["PreToolUse"] = groups
    if not changed:
        return Result(name, "ok", f"already registered in {path}")
    write_json(path, data, dry)
    verb = "would update" if dry else "updated"
    return Result(name, "would" if dry else "changed", f"{verb} {path}")


def check_json(name: str, path: Path, expected: str) -> Result:
    try:
        data = load_json(path)
    except (json.JSONDecodeError, ValueError) as exc:
        return Result(name, "conflict", f"{path}: {exc}")
    groups = (data.get("hooks") or {}).get("PreToolUse") or []
    for group in groups:
        if not is_ours(group):
            continue
        command = command_for(group["hooks"][0])
        if expected not in command:
            return Result(name, "conflict", f"{path}: points at {command!r}, not {expected}")
        return Result(name, "ok", f"registered in {path}")
    return Result(name, "conflict", f"{path}: no merge-gate PreToolUse registration")


def link(name: str, target: Path, dest: Path, dry: bool) -> Result:
    if dest.is_symlink() and dest.exists() and dest.resolve() == target.resolve():
        return Result(name, "ok", f"{dest} -> {target}")
    if dest.is_symlink() or not dest.exists():
        if dry:
            return Result(name, "would", f"link {dest} -> {target}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink():
            dest.unlink()
        dest.symlink_to(target)
        return Result(name, "changed", f"{dest} -> {target}")
    return Result(name, "conflict", f"{dest} is a real file; left unchanged")


def check_link(name: str, target: Path, dest: Path) -> Result:
    if dest.is_symlink() and dest.exists() and dest.resolve() == target.resolve():
        return Result(name, "ok", f"{dest} -> {target}")
    return Result(name, "conflict", f"{dest} does not link to {target}")


def claude_hook() -> dict[str, Any]:
    return {
        "type": "command",
        "command": f"python3 {shlex.quote(str(GATE))}",
        "timeout": 5,
    }


def codex_group() -> dict[str, Any]:
    adapter = ADAPTERS / "codex" / "merge-gate.sh"
    return {
        "matcher": CLAUDE_MATCHER,
        "hooks": [{
            "type": "command",
            "command": f"/bin/sh {shlex.quote(str(adapter))}",
            "timeout": 5,
            "statusMessage": "merge-gate",
        }],
    }


def run(harness: str, roots: Roots, dry: bool, check: bool) -> list[Result]:
    if harness == "claude":
        path = roots.claude / "settings.json"
        if check:
            return [check_json("claude", path, str(GATE))]
        if not roots.claude.is_dir():
            return [Result("claude", "skip", f"{roots.claude} does not exist")]
        return [register_json("claude", path,
                              {"matcher": CLAUDE_MATCHER, "hooks": [claude_hook()]}, dry)]
    if harness == "codex":
        path = roots.codex / "hooks.json"
        if check:
            return [check_json("codex", path, str(ADAPTERS / "codex" / "merge-gate.sh"))]
        if not roots.codex.is_dir():
            return [Result("codex", "skip", f"{roots.codex} does not exist")]
        return [register_json("codex", path, codex_group(), dry)]
    if harness == "opencode":
        target = ADAPTERS / "opencode" / "merge-gate.ts"
        dest = roots.opencode / "plugins" / "merge-gate.ts"
        if check:
            return [check_link("opencode", target, dest)]
        if not roots.opencode.is_dir():
            return [Result("opencode", "skip", f"{roots.opencode} does not exist")]
        return [link("opencode", target, dest, dry)]
    if harness == "omp":
        target = ADAPTERS / "omp" / "merge-gate.ts"
        dest = roots.omp / "extensions" / "merge-gate.ts"
        if check:
            return [check_link("omp", target, dest)]
        if not roots.omp.is_dir():
            return [Result("omp", "skip", f"{roots.omp} does not exist")]
        return [link("omp", target, dest, dry)]
    raise SystemExit(f"unknown harness: {harness}")


HARNESSES = ("claude", "codex", "opencode", "omp")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="report changes without writing")
    mode.add_argument("--check", action="store_true", help="exit 1 unless every registration is live")
    parser.add_argument("harness", nargs="?", default="all", choices=[*HARNESSES, "all"])
    args = parser.parse_args(argv)

    if not GATE.is_file():
        print(f"error: {GATE} is missing", file=sys.stderr)
        return 2
    roots = Roots.current()
    chosen = HARNESSES if args.harness == "all" else (args.harness,)
    results = [r for h in chosen for r in run(h, roots, args.dry_run, args.check)]
    for result in results:
        print(result.line())
    if any(r.action == "conflict" for r in results):
        return 1
    if results and results[0].harness == "codex" and any(r.action in {"changed", "would"} for r in results):
        print("next     run /hooks once in a Codex session; an untrusted hook is skipped silently")
    return 0


if __name__ == "__main__":
    sys.exit(main())

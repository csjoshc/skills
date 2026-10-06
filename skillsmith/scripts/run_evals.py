#!/usr/bin/env python3
"""Run a skill's evals with and without the skill installed.

Usage: run_evals.py <skill> [--model M] [--judge-model M] [--case ID] [--no-baseline]

Format: see skillsmith/reference/evals.md. Costs tokens; run by hand.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]
TOOLS = "Read,Write,Edit,Glob,Grep,Skill,Bash(git:*),Bash(python3:*),Bash(ls:*),Bash(cat:*),Bash(grep:*)"


def claude(prompt: str, cwd: Path, model: str | None, *, stream: bool, tools: str | None) -> subprocess.CompletedProcess:
    # Prompt goes via stdin: --allowedTools is variadic and would swallow a positional prompt.
    cmd = ["claude", "-p", "--setting-sources", "project", "--permission-mode", "dontAsk", "--no-session-persistence"]
    cmd += ["--output-format", "stream-json", "--verbose"] if stream else ["--output-format", "json"]
    if tools:
        cmd += ["--allowedTools", tools]
    if model:
        cmd += ["--model", model]
    return subprocess.run(cmd, input=prompt, cwd=cwd, capture_output=True, text=True, timeout=900)


def stage_fixtures(case: dict, evals_dir: Path, run_dir: Path) -> None:
    for rel in case.get("files", []):
        src = evals_dir / rel
        parts = Path(rel).parts
        dest = run_dir / Path(*parts[1:]) if parts and parts[0] == "files" else run_dir / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def init_git(run_dir: Path) -> None:
    env_args = ["-c", "user.name=eval", "-c", "user.email=eval@example.com"]
    subprocess.run(["git", "init", "-q"], cwd=run_dir, check=True)
    subprocess.run(["git", "add", "-A"], cwd=run_dir, check=True)
    subprocess.run(["git", *env_args, "commit", "-q", "--allow-empty", "-m", "fixtures"], cwd=run_dir, check=True)


def parse_stream(stdout: str) -> tuple[str, list[str]]:
    text, skills = "", []
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            text = ev.get("result") or text
        elif ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                    skills.append(str(block.get("input", {}).get("skill", "")))
    return text, skills


def judge(case: dict, output: str, model: str | None) -> tuple[bool, list[dict]]:
    criteria = case["expected_behavior"]
    prompt = (
        "You are grading an AI assistant's output against a rubric. Judge only the listed criteria.\n\n"
        f"USER PROMPT:\n{case['prompt']}\n\nOUTPUT:\n{output}\n\nCRITERIA:\n"
        + "\n".join(f"{i + 1}. {c}" for i, c in enumerate(criteria))
        + '\n\nReply with only JSON: {"results":[{"n":1,"pass":true,"reason":"short"}]}'
    )
    with tempfile.TemporaryDirectory() as tmp:
        proc = claude(prompt, Path(tmp), model, stream=False, tools=None)
    try:
        body = json.loads(proc.stdout).get("result", "")
        body = body[body.index("{"): body.rindex("}") + 1]
        results = json.loads(body)["results"]
    except (ValueError, KeyError, json.JSONDecodeError):
        return False, [{"n": 0, "pass": False, "reason": "judge returned unparseable output"}]
    return all(r.get("pass") for r in results) and len(results) == len(criteria), results


def run_case(skill: str, case: dict, with_skill: bool, evals_dir: Path, runs_dir: Path, model, judge_model) -> dict:
    variant = "with" if with_skill else "without"
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        stage_fixtures(case, evals_dir, run_dir)
        if with_skill:
            dest = run_dir / ".claude" / "skills" / skill
            shutil.copytree(SKILLS_ROOT / skill, dest, ignore=shutil.ignore_patterns("evals", "__pycache__"))
        init_git(run_dir)
        proc = claude(case["prompt"], run_dir, model, stream=True, tools=TOOLS)
        output, invoked = parse_stream(proc.stdout)
        (run_dir / "output.txt").write_text(output)
        (runs_dir / f"{case['id']}-{variant}.jsonl").write_text(proc.stdout)
        (runs_dir / f"{case['id']}-{variant}.txt").write_text(output)

        if case["type"] == "trigger":
            fired = skill in invoked
            return {"pass": fired == case["should_trigger"], "detail": f"invoked={fired}"}

        check_ok, check_note = True, ""
        if "check" in case:
            res = subprocess.run(case["check"]["cmd"], shell=True, cwd=run_dir, capture_output=True, text=True)
            check_ok = res.returncode == case["check"].get("expect_exit", 0)
            check_note = f"check={'ok' if check_ok else 'FAIL'}"
        judged_ok, results = judge(case, output, judge_model or model)
        failed = [str(r.get("n")) for r in results if not r.get("pass")]
        note = " ".join(x for x in (check_note, f"failed criteria: {','.join(failed)}" if failed else "") if x)
        return {"pass": judged_ok and check_ok, "detail": note or "all criteria met"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("skill")
    ap.add_argument("--model")
    ap.add_argument("--judge-model")
    ap.add_argument("--case")
    ap.add_argument("--no-baseline", action="store_true", help="skip the without-skill runs")
    args = ap.parse_args()

    evals_dir = SKILLS_ROOT / args.skill / "evals"
    spec = json.loads((evals_dir / "evals.json").read_text())
    cases = [c for c in spec["cases"] if not args.case or c["id"] == args.case]
    runs_dir = evals_dir / "runs" / time.strftime("%Y%m%d-%H%M%S")
    runs_dir.mkdir(parents=True)

    rows, failures = [], 0
    for case in cases:
        with_res = run_case(args.skill, case, True, evals_dir, runs_dir, args.model, args.judge_model)
        base = "-"
        if case["type"] == "behavior" and not args.no_baseline:
            base_res = run_case(args.skill, case, False, evals_dir, runs_dir, args.model, args.judge_model)
            base = "pass" if base_res["pass"] else "fail"
        failures += not with_res["pass"]
        rows.append((case["id"], case["type"], "pass" if with_res["pass"] else "FAIL", base, with_res["detail"]))
        print(f"{rows[-1][0]:<42} {rows[-1][1]:<9} with={rows[-1][2]:<5} without={rows[-1][3]:<5} {rows[-1][4]}", flush=True)

    print(f"\n{len(rows) - failures}/{len(rows)} cases pass with the skill. Outputs: {runs_dir}")
    print("A behavior case that also passes without the skill is not testing the skill; rewrite it.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

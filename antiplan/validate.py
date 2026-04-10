#!/usr/bin/env python3
"""Antiplan pre-flight validator.

Mechanically checks antiplan output (PRD + ticket markdown with YAML
frontmatter) against structural rules. Exits non-zero if any check fails.

Usage:
    python validate.py --project-dir /path/to/repo --tickets tickets.md [--prd prd.md]
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

# ── Check registry ───────────────────────────────────────────────────────────

_CHECKS: list[Callable[[PlanData], list[str]]] = []


def check(fn: Callable[[PlanData], list[str]]) -> Callable[[PlanData], list[str]]:
    _CHECKS.append(fn)
    return fn


# ── Data model ───────────────────────────────────────────────────────────────

@dataclass
class TicketFrontmatter:
    id: str
    files: list[dict[str, Any]] = field(default_factory=list)
    assumptions_validated: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanData:
    project_dir: Path
    tickets: list[TicketFrontmatter] = field(default_factory=list)
    assumptions: list[dict[str, str]] = field(default_factory=list)


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_tickets(content: str) -> list[TicketFrontmatter]:
    """Extract YAML frontmatter blocks from a multi-ticket markdown file."""
    results = []
    blocks = re.split(r"^---\s*$", content, flags=re.MULTILINE)
    i = 0
    while i < len(blocks):
        if blocks[i].strip() == "" and i + 1 < len(blocks):
            try:
                fm = yaml.safe_load(blocks[i + 1])
            except yaml.YAMLError:
                i += 1
                continue
            if isinstance(fm, dict) and "id" in fm:
                results.append(TicketFrontmatter(
                    id=str(fm["id"]),
                    files=fm.get("Files") or [],
                    assumptions_validated=[
                        str(a) for a in (fm.get("Assumptions-Validated") or [])
                    ],
                    raw=fm,
                ))
                i += 2
                continue
        i += 1
    return results


def parse_assumptions(prd_content: str) -> list[dict[str, str]]:
    """Extract assumption register rows from PRD markdown table."""
    results = []
    in_table = False
    for line in prd_content.splitlines():
        if "| ID |" in line and "Validation" in line:
            in_table = True
            continue
        if in_table and line.strip().startswith("|---"):
            continue
        if in_table and line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 6:
                results.append({
                    "id": cells[0],
                    "statement": cells[1],
                    "validation": cells[5] if len(cells) > 5 else "",
                })
        elif in_table and not line.strip().startswith("|"):
            in_table = False
    return results


# ── Checks ───────────────────────────────────────────────────────────────────

@check
def paths_resolve(data: PlanData) -> list[str]:
    """Every MODIFY path's parent directory must exist on disk."""
    errors = []
    for ticket in data.tickets:
        for f in ticket.files:
            if f.get("action") == "MODIFY" and not f.get("test", False):
                path_str = f.get("path", "")
                if "..." in path_str:
                    continue
                full = data.project_dir / path_str
                if not full.parent.exists():
                    errors.append(
                        f"{ticket.id}: MODIFY path parent missing: "
                        f"{path_str} (checked {full.parent})"
                    )
    return errors


@check
def ticket_file_count(data: PlanData) -> list[str]:
    """No ticket may modify/create more than 5 production files."""
    errors = []
    for ticket in data.tickets:
        prod_files = [
            f for f in ticket.files
            if not f.get("test", False)
        ]
        if len(prod_files) > 5:
            errors.append(
                f"{ticket.id}: {len(prod_files)} production files (max 5)"
            )
    return errors


@check
def tracer_bullets_scheduled(data: PlanData) -> list[str]:
    """Every assumption with tracer bullet validation must have a matching ticket AC."""
    errors = []
    all_validated = set()
    for ticket in data.tickets:
        all_validated.update(ticket.assumptions_validated)

    for assumption in data.assumptions:
        validation = assumption.get("validation", "").lower()
        if "tracer bullet" in validation or "proof script" in validation:
            a_id = assumption["id"]
            if a_id not in all_validated:
                errors.append(
                    f"Assumption {a_id} has validation '{assumption.get('validation')}' "
                    f"but no ticket has Assumptions-Validated: [{a_id}]"
                )
    return errors


# ── Runner ───────────────────────────────────────────────────────────────────

def run(data: PlanData) -> int:
    total_errors = 0
    for check_fn in _CHECKS:
        name = check_fn.__name__
        errors = check_fn(data)
        if errors:
            print(f"[FAIL] {name}")
            for e in errors:
                print(f"  {e}")
            total_errors += len(errors)
        else:
            count = ""
            if name == "paths_resolve":
                n = sum(
                    1 for t in data.tickets for f in t.files
                    if f.get("action") == "MODIFY" and not f.get("test")
                )
                count = f" ({n} paths checked)"
            elif name == "tracer_bullets_scheduled":
                count = f" ({len(data.assumptions)} assumptions checked)"
            print(f"[PASS] {name}{count}")

    print(f"\n{'=' * 40}")
    if total_errors:
        print(f"{total_errors} error(s). Plan is NOT ready for handoff.")
        return 1
    print("All checks passed. Plan is ready for handoff.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Antiplan pre-flight validator")
    parser.add_argument("--project-dir", required=True, help="Path to the project root")
    parser.add_argument("--tickets", required=True, help="Path to tickets markdown file")
    parser.add_argument("--prd", default=None, help="Path to PRD markdown file")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    tickets_content = Path(args.tickets).read_text(encoding="utf-8")
    tickets = parse_tickets(tickets_content)

    assumptions = []
    if args.prd:
        prd_content = Path(args.prd).read_text(encoding="utf-8")
        assumptions = parse_assumptions(prd_content)

    data = PlanData(
        project_dir=project_dir,
        tickets=tickets,
        assumptions=assumptions,
    )

    print("antiplan pre-flight validation")
    print("=" * 40)
    return run(data)


if __name__ == "__main__":
    sys.exit(main())

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


# ── Transcript checks (optional, --transcript flag) ──────────────────────────

_REQUIRED_YAML_LEDGER_KEYS = {"phase", "resolved", "contested", "unresolved",
                              "cut", "confidence"}
_REQUIRED_PHASE_BLOCKS = {
    "Phase 0": ("BROWNFIELD-CONTEXT", "GREENFIELD-CONTEXT"),
    "Phase 1": ("PROBLEM-STATEMENT",),
    "Phase 2": ("ARCHITECTURE-DECISIONS",),
    "Sign-off": ("SIGNOFF-APPROVALS",),
    "Phase 3": ("TICKET-DAG", "INTEGRATION-GATES"),
}


def check_transcript(transcript_text: str) -> list[str]:
    """Validate an antiplan transcript for required output-shape contracts.

    Returns list of errors. Used when --transcript is passed.
    """
    errors = []

    ledger_match = re.search(
        r"```ya?ml\s*\n(.*?ledger:.*?)\n```",
        transcript_text,
        flags=re.DOTALL,
    )
    if not ledger_match:
        errors.append("No YAML `ledger:` block found in transcript")
    else:
        try:
            parsed = yaml.safe_load(ledger_match.group(1))
            ledger = parsed.get("ledger") if isinstance(parsed, dict) else None
            if not isinstance(ledger, dict):
                errors.append("`ledger:` block is malformed")
            else:
                missing = _REQUIRED_YAML_LEDGER_KEYS - set(ledger.keys())
                if missing:
                    errors.append(f"ledger missing keys: {sorted(missing)}")
        except yaml.YAMLError as e:
            errors.append(f"ledger block is invalid YAML: {e}")

    for phase, block_names in _REQUIRED_PHASE_BLOCKS.items():
        if not any(f"```{name}" in transcript_text for name in block_names):
            errors.append(
                f"{phase}: no output block found "
                f"(expected one of: {', '.join(block_names)})"
            )

    gate_lines = re.findall(r"^PHASE-GATE:.+Proceeding:\s*(\w+)",
                            transcript_text, flags=re.MULTILINE)
    if not gate_lines:
        errors.append("No PHASE-GATE audit lines found")
    elif any(p.lower() == "no" for p in gate_lines):
        errors.append("At least one PHASE-GATE has Proceeding: no — plan incomplete")

    return errors


# ── Rubric / Challenger / Coverage checks ────────────────────────────────────

_RUBRIC_PATH_DEFAULT = Path(__file__).parent / "rubric.yaml"


def load_rubric_ids(rubric_path: Path) -> list[str]:
    """Return ordered list of AP IDs from rubric.yaml. Raises on parse error."""
    raw = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "rules" not in raw:
        raise ValueError(f"{rubric_path}: missing top-level 'rules' key")
    ids = []
    for rule in raw["rules"]:
        if not isinstance(rule, dict) or "id" not in rule:
            raise ValueError(f"{rubric_path}: rule missing 'id'")
        ids.append(str(rule["id"]))
    return ids


def parse_challenger_table(report_text: str) -> list[dict[str, str]]:
    """Extract rows from the Challenger per-AP audit markdown table.

    Expects a 4-column table with headers AP | Verdict | Tickets | Quoted signal.
    Returns one dict per data row. Header / separator rows are skipped.
    """
    rows = []
    in_table = False
    for line in report_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 4:
            continue
        header = [c.lower() for c in cells]
        if "ap" in header[0] and "verdict" in header[1]:
            in_table = True
            continue
        if in_table and set(cells[0]) <= {"-", ":"}:
            continue
        if in_table and cells[0].upper().startswith("AP-"):
            rows.append({
                "ap": cells[0].upper(),
                "verdict": cells[1].upper(),
                "tickets": cells[2],
                "evidence": cells[3].strip('"').strip(),
            })
    return rows


def check_challenger_report(report_text: str, rubric_ids: list[str]) -> list[str]:
    """Validate the Challenger audit table for completeness + evidence."""
    errors = []
    rows = parse_challenger_table(report_text)
    found_ids = {r["ap"] for r in rows}
    expected = set(rubric_ids)

    missing = expected - found_ids
    extra = found_ids - expected
    if missing:
        errors.append(f"audit table missing rows: {sorted(missing)}")
    if extra:
        errors.append(f"audit table has unknown AP IDs: {sorted(extra)}")

    valid_verdicts = {"BLOCK", "WARN", "PASS"}
    for r in rows:
        if r["verdict"] not in valid_verdicts:
            errors.append(f"{r['ap']}: invalid verdict '{r['verdict']}'")
            continue
        ev = r["evidence"]
        if r["verdict"] == "PASS":
            if ev.lower() != "no signal found":
                errors.append(
                    f"{r['ap']}: PASS row must have evidence "
                    f"'no signal found', got: {ev!r}"
                )
        else:
            if len(ev) < 10 or ev.lower() == "no signal found":
                errors.append(
                    f"{r['ap']} ({r['verdict']}): evidence must be a "
                    f"verbatim quote >=10 chars, got: {ev!r}"
                )

    verdict_match = re.search(r"VERDICT:\s*(PASS|FAIL)",
                              report_text, flags=re.IGNORECASE)
    if not verdict_match:
        errors.append("Challenger report missing VERDICT: line")
    elif verdict_match.group(1).upper() == "FAIL":
        errors.append("Challenger VERDICT: FAIL — DAG not ready")

    return errors


def check_coverage_report(report_text: str) -> list[str]:
    """Validate the Coverage Auditor report (option 4 second pass)."""
    errors = []

    if not re.search(r"\|\s*ID\s*\|\s*Set\s*\|", report_text):
        errors.append("Coverage report missing re-derivation table "
                      "(headers: ID | Set | Statement | Transcript quote)")
    if not re.search(r"\|\s*ID\s*\|\s*Verdict\s*\|", report_text):
        errors.append("Coverage report missing coverage table "
                      "(headers: ID | Verdict | Where covered | Notes)")

    missing_quote = re.search(r"<MISSING>", report_text)
    if missing_quote:
        errors.append("Coverage report has <MISSING> quote — auditor failed")

    for field in ("RE_DERIVED", "MATCH", "GAP", "INVERTED", "WEAK"):
        if not re.search(rf"^{field}:\s*\d+", report_text, flags=re.MULTILINE):
            errors.append(f"Coverage summary missing {field}: <count>")

    re_derived_match = re.search(r"^RE_DERIVED:\s*(\d+)",
                                 report_text, flags=re.MULTILINE)
    if re_derived_match and int(re_derived_match.group(1)) < 5:
        errors.append(
            f"Coverage RE_DERIVED count too low ({re_derived_match.group(1)}) "
            "— auditor likely skimmed the transcript"
        )

    verdict_match = re.search(r"VERDICT:\s*(PASS|FAIL)",
                              report_text, flags=re.IGNORECASE)
    if not verdict_match:
        errors.append("Coverage report missing VERDICT: line")
    elif verdict_match.group(1).upper() == "FAIL":
        errors.append("Coverage VERDICT: FAIL — requirements drift detected")

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
    parser.add_argument("--transcript", default=None,
                        help="Optional antiplan session transcript to validate for "
                             "required output-shape contracts (YAML ledger, phase "
                             "blocks, PHASE-GATE lines)")
    parser.add_argument("--challenger-report", default=None,
                        help="Path to Challenger subagent report. Validates the "
                             "per-AP audit table against rubric.yaml — every AP "
                             "must appear with verbatim evidence or 'no signal "
                             "found' for PASS rows.")
    parser.add_argument("--coverage-report", default=None,
                        help="Path to Coverage Auditor report. Validates the "
                             "transcript-vs-PRD second-pass diff (RE_DERIVED >=5, "
                             "no GAP/INVERTED, VERDICT: PASS).")
    parser.add_argument("--rubric", default=str(_RUBRIC_PATH_DEFAULT),
                        help="Path to anti-pattern rubric (default: bundled "
                             "antiplan/rubric.yaml)")
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
    exit_code = run(data)

    if args.transcript:
        print("\ntranscript contract validation")
        print("=" * 40)
        transcript_text = Path(args.transcript).read_text(encoding="utf-8")
        transcript_errors = check_transcript(transcript_text)
        if transcript_errors:
            print("[FAIL] transcript_contracts")
            for e in transcript_errors:
                print(f"  {e}")
            exit_code = 1
        else:
            print("[PASS] transcript_contracts")

    if args.challenger_report:
        print("\nchallenger report validation")
        print("=" * 40)
        rubric_ids = load_rubric_ids(Path(args.rubric))
        report_text = Path(args.challenger_report).read_text(encoding="utf-8")
        ch_errors = check_challenger_report(report_text, rubric_ids)
        if ch_errors:
            print(f"[FAIL] challenger_report ({len(rubric_ids)} APs in rubric)")
            for e in ch_errors:
                print(f"  {e}")
            exit_code = 1
        else:
            print(f"[PASS] challenger_report ({len(rubric_ids)} APs covered)")

    if args.coverage_report:
        print("\ncoverage report validation")
        print("=" * 40)
        cov_text = Path(args.coverage_report).read_text(encoding="utf-8")
        cov_errors = check_coverage_report(cov_text)
        if cov_errors:
            print("[FAIL] coverage_report")
            for e in cov_errors:
                print(f"  {e}")
            exit_code = 1
        else:
            print("[PASS] coverage_report")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

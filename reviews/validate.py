#!/usr/bin/env python3
"""Reviews pre-post validator.

Mechanically checks a review transcript (from `pr-review` or `cleanup`)
against the fenced-block contracts in schemas.md. Exits non-zero if any
check fails. Run this before posting to GitHub or finalizing a cleanup
report.

Usage:
    python3 validate.py --transcript <path>
    python3 validate.py --transcript <path> --skill cleanup
    python3 validate.py --transcript <path> --skill pr-review

Stdlib-only. Uses a minimal YAML subset parser for REVIEW-LEDGER and
REVIEW-FINDINGS blocks (flat dicts, lists of dicts with literal-block
strings). If pyyaml is installed it will be used instead.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    import yaml as _yaml  # type: ignore[import-not-found]
except ImportError:
    _yaml = None

# ── Check registry ───────────────────────────────────────────────────────────

_CHECKS: list[Callable[["Transcript"], list[str]]] = []


def check(fn: Callable[["Transcript"], list[str]]) -> Callable[["Transcript"], list[str]]:
    _CHECKS.append(fn)
    return fn


# ── Constants ────────────────────────────────────────────────────────────────

_ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
_ALLOWED_STATUSES = {"VALIDATED", "DISMISSED", "DEFERRED"}
_ALLOWED_SOURCES = {"tool-flagged", "lens-derived", "rubric-derived", "user-confirmed"}
_ALLOWED_PHASE_0_STATUSES = {"OPEN", "RESOLVED", "OVERRIDDEN"}
_ALLOWED_CONFIDENCES = {"LOW", "MEDIUM", "HIGH"}

_REQUIRED_LEDGER_KEYS = {
    "phase", "findings_total", "validated", "dismissed",
    "deferred", "critical", "confidence", "plan_present",
}


# ── Minimal YAML subset parser ──────────────────────────────────────────────

def _parse_scalar(s: str) -> Any:
    s = s.strip()
    if s == "":
        return ""
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    if s.lower() in ("null", "~"):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def _yaml_subset_load(text: str) -> Any:
    """Parse the YAML subset we emit: flat dicts + lists-of-dicts with
    literal-block (`|`) strings. Not a general YAML parser."""
    if _yaml is not None:
        return _yaml.safe_load(text)

    lines = text.splitlines()
    i = 0

    def skip_blank(idx: int) -> int:
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1
        return idx

    def indent_of(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_block(indent: int, idx: int) -> tuple[Any, int]:
        idx = skip_blank(idx)
        if idx >= len(lines):
            return None, idx

        line = lines[idx]
        cur_indent = indent_of(line)
        if cur_indent < indent:
            return None, idx

        stripped = line.strip()
        if stripped.startswith("- "):
            return parse_list(indent, idx)
        else:
            return parse_dict(indent, idx)

    def parse_list(indent: int, idx: int) -> tuple[list[Any], int]:
        out: list[Any] = []
        while idx < len(lines):
            idx = skip_blank(idx)
            if idx >= len(lines):
                break
            line = lines[idx]
            cur_indent = indent_of(line)
            stripped = line.strip()
            if cur_indent < indent or not stripped.startswith("- "):
                break
            # Treat the rest of the line as the first key of a dict item
            rest = stripped[2:]
            pseudo_line = (" " * (cur_indent + 2)) + rest
            replaced = lines[:idx] + [pseudo_line] + lines[idx + 1:]
            lines[:] = replaced
            item, idx = parse_dict(cur_indent + 2, idx)
            out.append(item)
        return out, idx

    def parse_dict(indent: int, idx: int) -> tuple[dict[str, Any], int]:
        out: dict[str, Any] = {}
        while idx < len(lines):
            idx = skip_blank(idx)
            if idx >= len(lines):
                break
            line = lines[idx]
            cur_indent = indent_of(line)
            if cur_indent < indent:
                break
            if cur_indent > indent:
                break
            stripped = line.strip()
            if stripped.startswith("- "):
                break
            if ":" not in stripped:
                idx += 1
                continue
            key, _, rest = stripped.partition(":")
            key = key.strip()
            rest = rest.rstrip()
            if rest.lstrip().startswith("|"):
                idx += 1
                block_lines: list[str] = []
                block_indent: int | None = None
                while idx < len(lines):
                    l2 = lines[idx]
                    if l2.strip() == "":
                        block_lines.append("")
                        idx += 1
                        continue
                    ind2 = indent_of(l2)
                    if ind2 <= cur_indent:
                        break
                    if block_indent is None:
                        block_indent = ind2
                    block_lines.append(l2[block_indent:])
                    idx += 1
                while block_lines and block_lines[-1] == "":
                    block_lines.pop()
                out[key] = "\n".join(block_lines)
                continue
            value = rest.strip()
            if value == "":
                idx += 1
                child, idx = parse_block(cur_indent + 2, idx)
                out[key] = child if child is not None else {}
            else:
                out[key] = _parse_scalar(value)
                idx += 1
        return out, idx

    result, _ = parse_block(0, i)
    return result


# ── Data model ───────────────────────────────────────────────────────────────

@dataclass
class Finding:
    fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class Transcript:
    text: str
    skill: str  # "pr-review" | "cleanup"
    phase_0_rows: list[dict[str, str]] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    ledger: dict[str, Any] | None = None
    gate_lines: list[str] = field(default_factory=list)
    fragment: bool = False  # True when validating an arch-violations catalog
                            # file or other document containing REVIEW-FINDINGS
                            # few-shots but no full transcript envelope.


# ── Parsing ──────────────────────────────────────────────────────────────────

_PHASE_0_RE = re.compile(r"```REVIEW-PHASE-0\s*\n(.*?)\n```", flags=re.DOTALL)
_FINDINGS_RE = re.compile(r"```REVIEW-FINDINGS\s*\n(.*?)\n```", flags=re.DOTALL)
_LEDGER_RE = re.compile(r"```REVIEW-LEDGER\s*\n(.*?)\n```", flags=re.DOTALL)
_GATE_RE = re.compile(
    r"^REVIEW-GATE:.+Proceeding:\s*(yes|no)\.?\s*$",
    flags=re.MULTILINE | re.IGNORECASE,
)


def parse_phase_0_table(block: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = [l.strip() for l in block.splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        return rows
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    for raw in lines[1:]:
        if set(raw.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def parse_findings_block(block: str) -> list[Finding]:
    parsed = _yaml_subset_load(block)
    if not isinstance(parsed, list):
        return []
    return [Finding(fields=item) for item in parsed if isinstance(item, dict)]


def parse_transcript(text: str, skill: str, fragment: bool = False) -> Transcript:
    t = Transcript(text=text, skill=skill, fragment=fragment)

    for m in _PHASE_0_RE.finditer(text):
        t.phase_0_rows.extend(parse_phase_0_table(m.group(1)))

    for m in _FINDINGS_RE.finditer(text):
        t.findings.extend(parse_findings_block(m.group(1)))

    ledger_m = _LEDGER_RE.search(text)
    if ledger_m:
        parsed = _yaml_subset_load(ledger_m.group(1))
        if isinstance(parsed, dict) and isinstance(parsed.get("ledger"), dict):
            t.ledger = parsed["ledger"]

    for m in _GATE_RE.finditer(text):
        t.gate_lines.append(m.group(0))

    return t


# ── Checks ───────────────────────────────────────────────────────────────────

@check
def required_blocks_present(t: Transcript) -> list[str]:
    if t.fragment:
        # Catalog / few-shot files contain REVIEW-FINDINGS but not ledger
        # or phase-0 blocks by design.
        if not _FINDINGS_RE.search(t.text):
            return ["fragment missing REVIEW-FINDINGS block"]
        return []
    errors = []
    if t.skill == "cleanup" and not _PHASE_0_RE.search(t.text):
        errors.append("cleanup transcript missing REVIEW-PHASE-0 block")
    if not _FINDINGS_RE.search(t.text):
        errors.append("transcript missing REVIEW-FINDINGS block")
    if not _LEDGER_RE.search(t.text):
        errors.append("transcript missing REVIEW-LEDGER block")
    return errors


@check
def gate_lines_present(t: Transcript) -> list[str]:
    if t.fragment:
        return []
    errors = []
    if not t.gate_lines:
        errors.append("no REVIEW-GATE audit lines found")
        return errors

    required_gates = {"phase-1", "report"}
    if t.skill == "cleanup":
        required_gates.add("phase-0")
    if t.skill == "pr-review":
        required_gates.add("post")

    gate_text = "\n".join(t.gate_lines).lower()
    for needle in required_gates:
        if needle not in gate_text:
            errors.append(f"missing REVIEW-GATE referencing '{needle}'")
    return errors


@check
def phase_0_resolved_before_proceeding(t: Transcript) -> list[str]:
    if t.skill != "cleanup":
        return []
    errors = []
    open_rows = [
        r for r in t.phase_0_rows
        if (r.get("status") or "").upper() == "OPEN"
    ]
    if not open_rows:
        return errors
    for gate in t.gate_lines:
        lower = gate.lower()
        if "phase-0" in lower and "proceeding: yes" in lower:
            errors.append(
                f"Phase 0 → Phase 1 gate marked 'Proceeding: yes' with "
                f"{len(open_rows)} OPEN row(s) in REVIEW-PHASE-0"
            )
            break
    return errors


@check
def phase_0_row_shape(t: Transcript) -> list[str]:
    if t.skill != "cleanup" or not t.phase_0_rows:
        return []
    errors = []
    required = {"tool", "rule", "file", "line", "severity", "status"}
    for i, row in enumerate(t.phase_0_rows, 1):
        missing = required - {k.lower() for k in row.keys()}
        if missing:
            errors.append(
                f"REVIEW-PHASE-0 row {i}: missing columns {sorted(missing)}"
            )
            continue
        sev = (row.get("severity") or "").upper()
        if sev not in _ALLOWED_SEVERITIES:
            errors.append(
                f"REVIEW-PHASE-0 row {i}: severity '{sev}' "
                f"not in {sorted(_ALLOWED_SEVERITIES)}"
            )
        st = (row.get("status") or "").upper()
        if st not in _ALLOWED_PHASE_0_STATUSES:
            errors.append(
                f"REVIEW-PHASE-0 row {i}: status '{st}' "
                f"not in {sorted(_ALLOWED_PHASE_0_STATUSES)}"
            )
    return errors


@check
def findings_shape(t: Transcript) -> list[str]:
    errors = []
    required = {
        "id", "category", "file", "line", "severity",
        "source", "status", "evidence", "suggested_fix",
    }
    for f in t.findings:
        fid = f.fields.get("id", "<?>")
        missing = required - set(f.fields.keys())
        if missing:
            errors.append(f"finding {fid}: missing fields {sorted(missing)}")
            continue
        sev = str(f.fields.get("severity", "")).upper()
        if sev not in _ALLOWED_SEVERITIES:
            errors.append(
                f"finding {fid}: severity '{sev}' not in {sorted(_ALLOWED_SEVERITIES)}"
            )
        st = str(f.fields.get("status", "")).upper()
        if st not in _ALLOWED_STATUSES:
            errors.append(
                f"finding {fid}: status '{st}' not in {sorted(_ALLOWED_STATUSES)}"
            )
        src = str(f.fields.get("source", ""))
        if src not in _ALLOWED_SOURCES:
            errors.append(
                f"finding {fid}: source '{src}' not in {sorted(_ALLOWED_SOURCES)}"
            )
    return errors


@check
def structural_findings_have_proof(t: Transcript) -> list[str]:
    """Proof is required for any finding where the architectural claim
    benefits from reproducible evidence:

    - severity == CRITICAL (any category) — original rule
    - category == Architectural Drift (any severity) — enforced elsewhere too
    - category == Layer with severity in {HIGH, CRITICAL} — added because
      ARCH-DEP-UP / ARCH-DEP-CYCLE / ARCH-DEP-LEAK / ARCH-DEP-IO-IN-PURE /
      ARCH-BND-EAGER-INIT findings are exactly the kind that benefit from
      a `madge --circular` / `importlinter` / grep excerpt in `proof:`.

    See schemas.md "Proof requirement (structural findings)"."""
    errors = []
    for f in t.findings:
        sev = str(f.fields.get("severity", "")).upper()
        st = str(f.fields.get("status", "")).upper()
        cat = str(f.fields.get("category", ""))
        if st != "VALIDATED":
            continue
        needs_proof = (
            sev == "CRITICAL"
            or (cat == "Layer" and sev in {"HIGH", "CRITICAL"})
        )
        if not needs_proof:
            continue
        proof = f.fields.get("proof")
        if not proof or not str(proof).strip():
            fid = f.fields.get("id", "<?>")
            if sev == "CRITICAL":
                reason = f"CRITICAL+VALIDATED (severity rule)"
            else:
                reason = f"Layer+{sev}+VALIDATED (Layer-HIGH rule)"
            errors.append(
                f"finding {fid}: {reason} without `proof:` field "
                f"(required by schemas.md 'Proof requirement (structural findings)')"
            )
    return errors


@check
def architectural_drift_has_plan_reference(t: Transcript) -> list[str]:
    """Every VALIDATED `Architectural Drift` finding must either cite the
    linked plan in `proof:` or explicitly say `no-plan-available`. This
    enforces the feedback loop to /antiplan: drift findings must trace
    back to a plan that was (or wasn't) available."""
    errors = []
    for f in t.findings:
        cat = str(f.fields.get("category", ""))
        st = str(f.fields.get("status", "")).upper()
        if cat != "Architectural Drift" or st != "VALIDATED":
            continue
        fid = f.fields.get("id", "<?>")
        proof = str(f.fields.get("proof", "")).strip().lower()
        decidable = str(f.fields.get("decidable_at", "")).strip().lower()
        if decidable not in {"design", "diff", "both"}:
            errors.append(
                f"finding {fid}: Architectural Drift requires "
                f"`decidable_at: design|diff|both` (schemas.md)"
            )
        if not proof:
            errors.append(
                f"finding {fid}: Architectural Drift requires `proof:` "
                f"(plan path/excerpt or 'no-plan-available')"
            )
        elif (
            "no-plan-available" not in proof
            and "plan" not in proof
            and "prd" not in proof
            and "architecture-decisions" not in proof
            and "antiplan" not in proof
        ):
            errors.append(
                f"finding {fid}: Architectural Drift `proof:` must reference "
                f"the linked plan (plan path, PRD excerpt, "
                f"ARCHITECTURE-DECISIONS block) or say `no-plan-available`"
            )
    return errors


@check
def confidence_ceiling_respects_plan_present(t: Transcript) -> list[str]:
    """If `plan_present: false`, ledger confidence may not be HIGH. A
    review without a linked plan cannot fully assess architectural
    drift, so we cap confidence at MEDIUM (schemas.md)."""
    if t.ledger is None:
        return []
    plan_present = t.ledger.get("plan_present")
    conf = str(t.ledger.get("confidence", "")).upper()
    if plan_present is False and conf == "HIGH":
        return [
            "REVIEW-LEDGER: confidence='HIGH' requires plan_present=true "
            "(schemas.md — architectural drift unassessable without a plan)"
        ]
    return []


@check
def ledger_shape(t: Transcript) -> list[str]:
    if t.fragment:
        return []
    errors = []
    if t.ledger is None:
        errors.append("REVIEW-LEDGER: missing or unparseable")
        return errors
    missing = _REQUIRED_LEDGER_KEYS - set(t.ledger.keys())
    if missing:
        errors.append(f"REVIEW-LEDGER: missing keys {sorted(missing)}")
        return errors
    conf = str(t.ledger.get("confidence", "")).upper()
    if conf not in _ALLOWED_CONFIDENCES:
        errors.append(
            f"REVIEW-LEDGER: confidence '{conf}' not in {sorted(_ALLOWED_CONFIDENCES)}"
        )
    return errors


@check
def ledger_counts_match_findings(t: Transcript) -> list[str]:
    if t.ledger is None:
        return []
    errors = []
    total = t.ledger.get("findings_total")
    if isinstance(total, int) and total != len(t.findings):
        errors.append(
            f"REVIEW-LEDGER.findings_total={total} but parsed {len(t.findings)} findings"
        )

    by_status = {"VALIDATED": 0, "DISMISSED": 0, "DEFERRED": 0}
    critical_validated = 0
    for f in t.findings:
        st = str(f.fields.get("status", "")).upper()
        if st in by_status:
            by_status[st] += 1
        if st == "VALIDATED" and str(f.fields.get("severity", "")).upper() == "CRITICAL":
            critical_validated += 1

    for key, expected in (
        ("validated", by_status["VALIDATED"]),
        ("dismissed", by_status["DISMISSED"]),
        ("deferred", by_status["DEFERRED"]),
        ("critical", critical_validated),
    ):
        val = t.ledger.get(key)
        if isinstance(val, int) and val != expected:
            errors.append(
                f"REVIEW-LEDGER.{key}={val} but parsed {expected} from findings"
            )
    return errors


# ── Runner ───────────────────────────────────────────────────────────────────

def run(t: Transcript) -> int:
    total_errors = 0
    for fn in _CHECKS:
        errs = fn(t)
        if errs:
            print(f"[FAIL] {fn.__name__}")
            for e in errs:
                print(f"  {e}")
            total_errors += len(errs)
        else:
            print(f"[PASS] {fn.__name__}")

    print("\n" + "=" * 40)
    if total_errors:
        print(f"{total_errors} error(s). Transcript is NOT safe to post.")
        return 1
    print("All checks passed. Transcript is safe to post.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Reviews pre-post validator")
    parser.add_argument("--transcript", required=True, help="Path to review transcript or catalog file")
    parser.add_argument(
        "--skill", choices=["pr-review", "cleanup"], default=None,
        help="Which skill produced the transcript (auto-detects if omitted)",
    )
    parser.add_argument(
        "--fragment", action="store_true",
        help="Treat input as a catalog/few-shot file with REVIEW-FINDINGS "
             "blocks but no ledger or gates (auto-detected when path is "
             "under arch-violations/).",
    )
    args = parser.parse_args()

    transcript_path = Path(args.transcript)
    text = transcript_path.read_text(encoding="utf-8")
    fragment = args.fragment or "arch-violations" in transcript_path.parts

    skill = args.skill
    if skill is None:
        skill = "cleanup" if "REVIEW-PHASE-0" in text else "pr-review"

    backend = "pyyaml" if _yaml is not None else "stdlib-subset"
    mode = "fragment" if fragment else "transcript"
    print(f"reviews validator (mode: {mode}, skill: {skill}, yaml backend: {backend})")
    print("=" * 40)
    transcript = parse_transcript(text, skill=skill, fragment=fragment)
    return run(transcript)


if __name__ == "__main__":
    sys.exit(main())

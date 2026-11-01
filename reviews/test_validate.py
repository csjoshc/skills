# Tests for validate.py's on-disk proof verification (proof_targets_exist).
# Transcripts are built from a literal template; repo root transcripts untouched.
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import validate

TRANSCRIPT = """```REVIEW-FINDINGS
- id: F-001
  category: Bug
  lens: bug-hunter
  file: x.py
  line: 1
  rule_code: N/A
  severity: {severity}
  source: lens-derived
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    response.json() without checking state
  proof: {proof}
  suggested_fix: |
    guard it
```
"""


def run_check(proof: str, repo: Path | None, severity: str = "CRITICAL"):
    text = TRANSCRIPT.format(severity=severity, proof=proof)
    t = validate.parse_transcript(text, skill="pr-review", repo=repo)
    return validate.proof_targets_exist(t)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "suite_test.py").write_text("def test_login():\n    pass\n")
    return tmp_path


def test_existing_file_proof_passes(repo):
    assert run_check("tests/suite_test.py shows the diff", repo) == []


def test_fabricated_path_fails(repo):
    errors = run_check("curl -s tests/missing_suite_test.py returns 404", repo)
    assert any("does not exist" in e for e in errors)


def test_missing_test_id_fails(repo):
    errors = run_check("pytest tests/suite_test.py::test_missing_case exits 1", repo)
    assert any("does not appear" in e for e in errors)


def test_existing_test_id_passes(repo):
    assert run_check("pytest tests/suite_test.py::test_login exits 0", repo) == []


def test_windows_backslash_path_resolves(repo):
    # Proofs authored on Windows use backslashes; they must resolve to the
    # same file as forward-slash tokens.
    assert run_check("tests\\suite_test.py::test_login exits 0", repo) == []


def test_missing_test_id_fails_with_backslash_path(repo):
    errors = run_check("pytest tests\\suite_test.py::test_missing_case exits 1", repo)
    assert any("does not appear" in e for e in errors)


def test_non_ascii_target_file_reads_as_utf8(tmp_path: Path) -> None:
    # Target files are read byte-identically on all platforms; without an
    # explicit encoding Windows would decode this as cp1252.
    (tmp_path / "readme.md").write_text(
        "check Café-Münzen ✓\n", encoding="utf-8",
    )
    text = TRANSCRIPT.format(
        severity="CRITICAL", proof="readme.md::Café-Münzen",
    )
    t = validate.parse_transcript(text, skill="pr-review", repo=tmp_path)
    assert validate.proof_targets_exist(t) == []


def test_url_only_proof_is_a_note_not_an_error(repo, capsys):
    errors = run_check("https://git.example/ci/job/123 failed with the trace", repo)
    assert errors == []
    assert "not verified offline" in capsys.readouterr().out


def test_medium_finding_needs_no_proof(repo):
    assert run_check("plain narrative proof", repo, severity="MEDIUM") == []


def test_untouched_without_repo_flag(repo):
    # No --repo passed: the presence-only rule stays the contract.
    assert run_check("tests/missing_suite_test.py", None) == []


def test_registrar_still_lists_all_checks():
    names = [fn.__name__ for fn in validate._CHECKS]
    assert "structural_findings_have_proof" in names
    assert "proof_targets_exist" in names

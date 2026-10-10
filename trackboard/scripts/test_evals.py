"""Evals grade the agent, not the script: each scripted check fails on the raw fixture and passes after
the commands SKILL.md prescribes. Fixtures listed in evals.json must exist and be used."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import board_refresh as br

EVALS = Path(__file__).resolve().parent.parent / "evals"
CASES = {c["id"]: c for c in json.loads((EVALS / "evals.json").read_text(encoding="utf-8"))["cases"]}
# The documented path an agent should take for each script-checkable case (project dir, argv list).
PRESCRIBED = {
    "drift-reported-not-resolved": ("drift-shop", [["init"]]),
    "one-history-line-per-change": ("shipped-shop", [["refresh"]]),
    "terminal-html-export": ("terminal-shop", [["init"], ["export", "--target", "html", "--out", "{p}/.plan/board/board.html"]]),
    "brief-reads-not-writes": ("brief-shop", [["init"]]),
}


class TestEvals(unittest.TestCase):
    def test_fixture_list_matches_disk(self) -> None:
        listed = {f for c in CASES.values() for f in c.get("files", [])}
        on_disk = {str(p.relative_to(EVALS)) for p in (EVALS / "files").rglob("*") if p.is_file()}
        self.assertEqual(listed, on_disk)

    def test_checks_fail_on_fixture_and_pass_after_prescribed_path(self) -> None:
        for case_id, (proj, steps) in PRESCRIBED.items():
            with self.subTest(case_id), tempfile.TemporaryDirectory() as tmp:
                shutil.copytree(EVALS / "files", tmp, dirs_exist_ok=True)
                check = CASES[case_id]["check"]

                def run_check() -> int:
                    return subprocess.run(["bash", "-c", check["cmd"]], cwd=tmp, capture_output=True).returncode

                self.assertNotEqual(run_check(), check["expect_exit"], "check passes before the agent acts")
                root = str(Path(tmp) / proj)
                for argv in steps:
                    argv = [a.format(p=root) for a in argv]
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(br.main([*argv, "--root", root, "--today", "2030-01-09"]), 0, argv)
                self.assertEqual(run_check(), check["expect_exit"], "prescribed path fails the check")


if __name__ == "__main__":
    unittest.main()

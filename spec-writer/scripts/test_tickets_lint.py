import io
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tickets_lint  # noqa: E402

GOOD = """\
---
id: T-1
title: "Thing"
Stage: BUILD
Depends-On: []
Files:
  - action: CREATE
    path: pkg/thing.py
    test: false
  - action: MODIFY
    path: existing.txt
    test: false
Read-First:
  - existing.txt
---

## Scope

Create `pkg/thing.py`.

## Acceptance Criteria → Tests

| AC | Check | Tier |
|---|---|---|
| AC-1 Given x, then y | `pkg/test_thing.py::test_y` | T2 |
| AC-2 (failure path) Given bad x, then error | `pkg/test_thing.py::test_bad` | T1 |
| AC-3 Given the doc, then it names thing | `grep -q thing existing.txt` | T3 |

## Verify

```bash
set -euo pipefail
grep -q thing existing.txt
```

## Notes

Plain.
"""


class LintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / ".tickets").mkdir()
        (self.tmp / "existing.txt").write_text("nothing here\n")

    def write(self, name, text):
        (self.tmp / ".tickets" / name).write_text(text)

    def run_lint(self, *extra):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = tickets_lint.main([str(self.tmp / ".tickets"), *extra])
        return rc, buf.getvalue()

    def test_good_ticket_passes(self):
        self.write("001-good.md", GOOD)
        rc, out = self.run_lint()
        self.assertEqual(rc, 0, out)
        self.assertIn("0 errors", out)

    def test_missing_section_fails(self):
        self.write("001-bad.md", GOOD.replace("## Notes\n\nPlain.\n", ""))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("missing section ## Notes", out)

    def test_k_or_chain_fails(self):
        self.write("001-bad.md", GOOD.replace("grep -q thing existing.txt\n```", 'python3 -m pytest -q -k "a or b"\n```'))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("or-chain", out)

    def test_bare_negation_in_verify_fails(self):
        self.write("001-bad.md", GOOD.replace("grep -q thing existing.txt\n```", "! grep -q other existing.txt\n```"))
        rc, out = self.run_lint()
        self.assertIn("bare '! cmd'", out)
        self.assertEqual(rc, 1)

    def test_em_dash_fails(self):
        self.write("001-bad.md", GOOD.replace("Plain.", "Plain — text."))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("em dash", out)

    def test_modify_path_must_exist_or_be_created_upstream(self):
        upstream = GOOD.replace("id: T-1", "id: T-0").replace("pkg/thing.py", "pkg/base.py")
        downstream = GOOD.replace("Depends-On: []", "Depends-On: [T-0]").replace(
            "action: MODIFY\n    path: existing.txt", "action: MODIFY\n    path: pkg/base.py")
        self.write("001-up.md", upstream)
        self.write("002-down.md", downstream)
        rc, out = self.run_lint()
        self.assertEqual(rc, 0, out)
        self.write("002-down.md", downstream.replace("pkg/base.py", "pkg/nowhere.py"))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("pkg/nowhere.py doesn't exist", out)

    def test_ac_table_needs_three_rows_and_a_failure_path(self):
        two = GOOD.replace("| AC-3 Given the doc, then it names thing | `grep -q thing existing.txt` | T3 |\n", "")
        self.write("001-bad.md", two.replace("(failure path) ", ""))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("need at least 3", out)
        self.assertIn("no AC row marked (failure path)", out)

    def test_blocked_needs_unblock_check(self):
        self.write("001-bad.md", GOOD.replace("Stage: BUILD", "Stage: BLOCKED"))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("needs Unblock-Check", out)

    def test_gate_needs_silent_failure_and_proof(self):
        self.write("001-gate.md", GOOD.replace("Stage: BUILD", "Stage: BUILD\nType: integration-gate"))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("## Silent Failure Detection", out)
        self.assertIn("## Proof", out)

    def test_verify_syntax_error_fails(self):
        self.write("001-bad.md", GOOD.replace("grep -q thing existing.txt\n```", "if then fi\n```"))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("bash -n", out)

    def test_fence_inside_command_does_not_end_verify_block(self):
        # Valid bash on both sides of the inner fence; only a parser that reads past it sees the bare '!'.
        inner = "awk '/^```bash$/{f=1}' existing.txt\n! grep -q other existing.txt\n```"
        self.write("001-bad.md", GOOD.replace("grep -q thing existing.txt\n```", inner))
        rc, out = self.run_lint()
        self.assertEqual(rc, 1)
        self.assertIn("bare '! cmd'", out)
        self.assertNotIn("bash -n", out)

    def test_dry_red_broken_runner_is_an_error(self):
        self.write("001-good.md", GOOD)
        rc, out = self.run_lint("--dry-red", "--runner", "no-such-runner-xyz")
        self.assertEqual(rc, 1)
        self.assertIn("doesn't start", out)

    def test_dry_red_missing_test_is_expected_red(self):
        self.write("001-good.md", GOOD)
        runner = f"{sys.executable} -c \"import sys; sys.exit(4)\""
        rc, out = self.run_lint("--dry-red", "--runner", runner)
        # --version also exits 4, so the runner is reported broken; use a runner that accepts --version.
        self.assertIn("doesn't start", out)
        fake = self.tmp / "fakerunner.py"
        fake.write_text("import sys\nsys.exit(0 if sys.argv[1:] == ['--version'] else 4)\n")
        rc, out = self.run_lint("--dry-red", "--runner", f"{sys.executable} {fake}")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("passes before build", out.split("AC-3")[0])

    def test_dry_red_warns_when_a_check_already_passes(self):
        self.write("001-good.md", GOOD.replace("grep -q thing existing.txt` | T3", "grep -q nothing existing.txt` | T3"))
        rc, out = self.run_lint("--dry-red")
        self.assertIn("AC-3 passes before build", out)

    def test_unsafe_shell_check_is_not_run(self):
        self.assertFalse(tickets_lint.is_safe_shell("rm -rf /tmp/x"))
        self.assertFalse(tickets_lint.is_safe_shell("grep -q x f > out"))
        self.assertFalse(tickets_lint.is_safe_shell("test \"$(git rev-parse HEAD)\" = x"))
        self.assertTrue(tickets_lint.is_safe_shell("grep -q x f && ! grep -q y f"))


if __name__ == "__main__":
    unittest.main()

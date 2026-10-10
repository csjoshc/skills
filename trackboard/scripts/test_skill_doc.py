"""SKILL.md must stay runnable: every documented command works as written and every target is real."""

from __future__ import annotations

import contextlib
import io
import os
import re
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import board_refresh as br
from board_export import TARGETS

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"


def documented_commands() -> list[list[str]]:
    lines = re.findall(r"^python3 \$S (.+)$", SKILL.read_text(encoding="utf-8"), re.MULTILINE)
    return [shlex.split(line.split("  #", 1)[0]) for line in lines]


class TestSkillDoc(unittest.TestCase):
    def test_documented_commands_run_in_order_on_a_fresh_project(self) -> None:
        cmds = documented_commands()
        self.assertGreaterEqual(len(cmds), 5)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".tickets").mkdir()
            (root / ".tickets" / "t-002.md").write_text("---\nid: T-002\nStage: BUILD\n---\n", encoding="utf-8")
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                for argv in cmds:
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        code = br.main([*argv, "--root", tmp, "--today", "2030-01-02"])
                    self.assertEqual(code, 0, " ".join(argv))
            finally:
                os.chdir(cwd)
            self.assertTrue((root / ".plan" / "board" / "board.html").exists())

    def test_targets_named_in_doc_are_registered(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        table = text.split("## Choosing a harness", 1)[1].split("\n## ", 1)[0]
        named = {t for row in re.findall(r"\| `(\w+)`(?: and `(\w+)`)? \|", table) for t in row if t}
        self.assertEqual(named, set(TARGETS))


if __name__ == "__main__":
    unittest.main()

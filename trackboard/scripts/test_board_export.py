"""Tests for board_export.py: each target carries the board intact and renders it without the network."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import board_export as be

T1 = {"id": "T-001", "title": "Card form", "stage": "BUILD", "deps": [], "gate": "GATE-1", "is_gate": False,
      "owner": "dana", "note": "closes </script> & <b>", "evidence": []}
GATE = {**T1, "id": "GATE-1", "title": "Ship gate", "stage": "NEW", "gate": None, "is_gate": True,
        "owner": None, "note": None, "evidence": [{"label": "PR 12", "url": "https://example.test/pr/12"}]}
BOARD = {"title": "Shop | board", "generated_at": "2030-01-02", "tickets": [T1, GATE], "cycles": [],
         "drift": [{"ticket": "T-001", "kind": "stage-mismatch", "values": {"tickets": "BUILD", "stages": "REVIEW"}}],
         "burn": [], "events": [{"ts": "2030-01-02", "cycle": None, "ticket": "T-001", "from": "NEW", "to": "BUILD"}]}


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.board = self.root / "board.json"
        self.board.write_text(json.dumps(BOARD), encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def export(self, target: str) -> str:
        out = self.root / f"out.{target}"
        self.assertEqual(be.export(self.board, target, out), 0, target)
        return out.read_text(encoding="utf-8")


class TestMarkdown(Base):
    def test_shows_active_work_drift_gates_and_moves(self) -> None:
        md = self.export("md")
        self.assertIn("# Shop | board\n", md)
        for heading in ("## Now", "## Drift", "## Gates", "## Recent stage changes", "## All tickets"):
            self.assertIn(heading, md)
        self.assertIn("[PR 12](https://example.test/pr/12)", md)
        self.assertIn("| GATE-1 | NEW | T-001 |", md)

    def test_table_cells_cannot_break_columns(self) -> None:
        self.assertEqual(be.md_cell("a|b\nc"), "a\\|b c")

    def test_unknown_stage_ticket_keeps_its_spec(self) -> None:
        odd = {**T1, "id": "T-9", "stage": "SPEC_DRAFT", "intent": "Does x", "acceptance": [{"text": "AC one"}]}
        md = be.render_md({**BOARD, "tickets": [odd]})
        self.assertIn("**T-9 Card form** (SPEC_DRAFT): Does x\n- AC one", md)


class TestHtml(Base):
    def test_data_survives_script_close_and_parses_back(self) -> None:
        html = self.export("html")
        block = html.split('id="board-data">', 1)[1].split("</script>", 1)[0]
        self.assertNotIn("<", block)
        self.assertEqual(json.loads(block), BOARD)

    def test_offline_and_no_markup_injection(self) -> None:
        html = self.export("html")
        self.assertIsNone(re.search(r"<script[^>]+src=|<link[^>]+href=|innerHTML|fetch\(", html))


class TestTemplates(Base):
    def test_every_template_has_one_slot_and_bad_input_fails(self) -> None:
        for name in be.TARGETS.values():
            self.assertEqual((be.TEMPLATES / name).read_text(encoding="utf-8").count(be.PLACEHOLDER), 1, name)
        self.assertEqual(be.export(self.root / "missing.json", "md", self.root / "x.md"), 1)


TSX = {"cursor": {"cursor/canvas"}, "artifact": {"react"}}


class TestReactTemplates(Base):
    def test_board_inlined_as_literal_with_sandbox_safe_imports(self) -> None:
        for target, allowed in TSX.items():
            text = self.export(target)
            data, _ = json.JSONDecoder().raw_decode(text.split("const BOARD: Board = ", 1)[1])
            self.assertEqual(data, BOARD, target)
            self.assertEqual(set(re.findall(r'from "([^"]+)"', text)), allowed, target)
            self.assertIn("export default function", text, target)

    def test_types_declare_every_field_refresh_writes(self) -> None:
        import board_refresh as br

        (self.root / ".tickets").mkdir()
        (self.root / ".tickets" / "t.md").write_text("---\nid: T\nStage: NEW\n---\n", encoding="utf-8")
        for cmd in ("init", "refresh"):
            self.assertEqual(br.main([cmd, "--root", str(self.root), "--today", "2030-01-02"]), 0)
        board = json.loads((self.root / ".plan" / "board" / "board.json").read_text(encoding="utf-8"))
        for target in TSX:
            src = (be.TEMPLATES / be.TARGETS[target]).read_text(encoding="utf-8")
            for type_name, keys in (("Board", board), ("Ticket", board["tickets"][0])):
                decl = src.split(f"type {type_name} = {{", 1)[1].split("\n};", 1)[0]
                for key in keys:
                    self.assertRegex(decl, rf"\b{key}\??:", f"{target} {type_name}.{key}")


if __name__ == "__main__":
    unittest.main()

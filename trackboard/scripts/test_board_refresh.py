"""Tests for board_refresh.py. Run: python3 -m unittest discover -s scripts -p 'test_*.py'."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import board_refresh as br

CYCLES = [
    {"id": "C1", "name": "Cycle 1", "start": "2030-01-01", "end": "2030-01-07"},
    {"id": "C2", "name": "Cycle 2", "start": "2030-01-08", "end": "2030-01-14"},
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ticket(root: Path, tid: str, stage: str, deps: str = "[]", extra: str = "") -> None:
    write(
        root / ".tickets" / f"{tid.lower()}.md",
        f"---\nid: {tid}\ntitle: Work item {tid}\nStage: {stage}\nDepends-On: {deps}\n{extra}---\n\n# Body\n",
    )


def lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.board_dir = self.root / ".plan" / "board"
        self.history = self.board_dir / "history.jsonl"
        self.board = self.board_dir / "board.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_cli(self, *args: str) -> int:
        return br.main([*args, "--root", str(self.root)])

    def init(self, today: str = "2030-01-02") -> None:
        self.assertEqual(self.run_cli("init", "--today", today), 0)
        cfg = self.board_dir / "config.json"
        data = json.loads(cfg.read_text(encoding="utf-8"))
        data["cycles"] = CYCLES
        cfg.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.assertEqual(self.run_cli("refresh", "--today", today), 0)


class TestFrontmatter(Base):
    def test_inline_list_and_gate_id(self) -> None:
        ticket(self.root, "T-002", "build", "[T-001, T-000]", "Gate: GATE-1\nowner: dana\nnote: waits on API\n")
        t = br.parse_ticket_file(self.root / ".tickets" / "t-002.md")
        self.assertEqual(t["id"], "T-002")
        self.assertEqual(t["stage"], "BUILD")
        self.assertEqual(t["deps"], ["T-001", "T-000"])
        self.assertEqual(t["gate"], "GATE-1")
        self.assertFalse(t["is_gate"])
        self.assertEqual(t["owner"], "dana")
        self.assertEqual(t["note"], "waits on API")

    def test_block_list_gate_true_and_evidence(self) -> None:
        write(
            self.root / ".tickets" / "gate-1.md",
            "---\nid: GATE-1\ntitle: \"Gate one\"\nStage: NEW\ngate: true\ndeps:\n  - T-001\n  - T-002\n"
            "evidence:\n  - PR 12 | https://example.test/pr/12\n---\n",
        )
        t = br.parse_ticket_file(self.root / ".tickets" / "gate-1.md")
        self.assertEqual(t["title"], "Gate one")
        self.assertTrue(t["is_gate"])
        self.assertEqual(t["deps"], ["T-001", "T-002"])
        self.assertEqual(t["evidence"], [{"label": "PR 12", "url": "https://example.test/pr/12"}])

    def test_stage_aliases_normalize(self) -> None:
        self.assertEqual(br.normalize_stage("Done"), "COMPLETE")
        self.assertEqual(br.normalize_stage("spec_split"), "NEW")
        self.assertEqual(br.normalize_stage("FAILED"), "BLOCKED")
        self.assertEqual(br.normalize_stage("in review"), "REVIEW")


class TestTaskSequenceFallback(Base):
    def test_table_with_alias_headers(self) -> None:
        write(
            self.root / ".plan" / "task-sequence.md",
            "# Plan\n\n| Ticket | Title | Depends on | Status | Gate |\n|---|---|---|---|---|\n"
            "| T-001 | Schema | — | Done | GATE-1 |\n| T-002 | API | T-001 | in progress | GATE-1 |\n"
            "| GATE-1 | Gate one | T-001, T-002 | New | — |\n",
        )
        self.init()
        board = json.loads(self.board.read_text(encoding="utf-8"))
        by_id = {t["id"]: t for t in board["tickets"]}
        self.assertEqual(set(by_id), {"T-001", "T-002", "GATE-1"})
        self.assertEqual(by_id["T-001"]["stage"], "COMPLETE")
        self.assertEqual(by_id["T-002"]["deps"], ["T-001"])
        self.assertEqual(by_id["T-002"]["stage"], "BUILD")
        self.assertTrue(by_id["GATE-1"]["is_gate"])
        self.assertEqual([s["kind"] for s in board["sources"]], ["task-sequence"])

    def test_tickets_win_metadata_task_sequence_adds_rows(self) -> None:
        ticket(self.root, "T-001", "BUILD")
        write(
            self.root / ".plan" / "task-sequence.md",
            "| ID | Title | Deps |\n|---|---|---|\n| T-001 | Old title | |\n| T-002 | Planned | T-001 |\n",
        )
        self.init()
        by_id = {t["id"]: t for t in json.loads(self.board.read_text())["tickets"]}
        self.assertEqual(by_id["T-001"]["title"], "Work item T-001")
        self.assertEqual(by_id["T-002"]["stage"], "NEW")


class TestDrift(Base):
    def test_disagreement_records_drift_and_no_event(self) -> None:
        ticket(self.root, "T-001", "BUILD")
        self.init()
        before = lines(self.history)
        write(self.board_dir / "stages.yaml", "# manual\nT-001: COMPLETE\n")
        self.assertEqual(self.run_cli("refresh", "--today", "2030-01-03"), 0)
        board = json.loads(self.board.read_text())
        self.assertEqual(len(board["drift"]), 1)
        d = board["drift"][0]
        self.assertEqual(d["ticket"], "T-001")
        self.assertEqual(d["kind"], "stage-mismatch")
        self.assertEqual(d["values"], {"tickets": "BUILD", "stages": "COMPLETE"})
        self.assertEqual(board["tickets"][0]["stage"], "BUILD")
        self.assertEqual(lines(self.history), before)

    def test_check_fails_on_drift(self) -> None:
        ticket(self.root, "T-001", "BUILD")
        write(self.board_dir / "stages.yaml", "T-001: REVIEW\n")
        self.init()
        self.assertNotEqual(self.run_cli("refresh", "--check", "--today", "2030-01-03"), 0)


class TestHistory(Base):
    def test_append_only_and_baseline(self) -> None:
        ticket(self.root, "T-001", "NEW")
        ticket(self.root, "T-002", "NEW")
        self.init()
        first = self.history.read_text(encoding="utf-8")
        self.assertEqual(len(first.splitlines()), 2)
        self.assertIsNone(json.loads(first.splitlines()[0])["from"])
        ticket(self.root, "T-001", "BUILD")
        self.run_cli("refresh", "--today", "2030-01-03")
        second = self.history.read_text(encoding="utf-8")
        self.assertTrue(second.startswith(first))
        new = second[len(first):].splitlines()
        self.assertEqual(len(new), 1)
        ev = json.loads(new[0])
        self.assertEqual((ev["ticket"], ev["from"], ev["to"], ev["ts"]), ("T-001", "NEW", "BUILD", "2030-01-03"))

    def test_idempotent_refresh(self) -> None:
        ticket(self.root, "T-001", "BUILD")
        self.init()
        b1, h1 = self.board.read_bytes(), self.history.read_bytes()
        self.run_cli("refresh", "--today", "2030-01-05")
        self.run_cli("refresh", "--today", "2030-01-06")
        self.assertEqual(self.board.read_bytes(), b1)
        self.assertEqual(self.history.read_bytes(), h1)
        self.assertEqual(self.run_cli("refresh", "--check", "--today", "2030-01-06"), 0)

    def test_check_detects_stale_board(self) -> None:
        ticket(self.root, "T-001", "BUILD")
        self.init()
        ticket(self.root, "T-001", "REVIEW")
        h = self.history.read_bytes()
        self.assertNotEqual(self.run_cli("refresh", "--check", "--today", "2030-01-03"), 0)
        self.assertEqual(self.history.read_bytes(), h)


class TestCycles(Base):
    def test_event_gets_cycle_containing_today(self) -> None:
        ticket(self.root, "T-001", "NEW")
        self.init()
        ticket(self.root, "T-001", "BUILD")
        self.run_cli("refresh", "--today", "2030-01-09")
        ticket(self.root, "T-001", "COMPLETE")
        self.run_cli("refresh", "--today", "2030-02-01")
        evs = [json.loads(x) for x in lines(self.history)]
        self.assertEqual([e["cycle"] for e in evs], [None, "C2", None])
        board = json.loads(self.board.read_text())
        burn = {b["cycle"]: b for b in board["burn"]}
        self.assertEqual(burn["C2"]["started"], 1)
        self.assertEqual(burn["C2"]["completed"], 0)

    def test_cycle_for_date(self) -> None:
        self.assertEqual(br.cycle_for("2030-01-07", CYCLES), "C1")
        self.assertEqual(br.cycle_for("2030-01-08", CYCLES), "C2")
        self.assertIsNone(br.cycle_for("2029-12-31", CYCLES))


class TestExport(Base):
    def test_each_target_inlines_data(self) -> None:
        ticket(self.root, "T-001", "BUILD", extra="note: closes </script> tag risk\n")
        self.init()
        for target in ("cursor", "artifact", "html", "md"):
            out = self.root / "out" / f"board.{target}"
            self.assertEqual(self.run_cli("export", "--target", target, "--out", str(out)), 0)
            text = out.read_text(encoding="utf-8")
            self.assertNotIn(br.PLACEHOLDER, text, target)
            self.assertIn("Work item T-001", text, target)
        html = (self.root / "out" / "board.html").read_text(encoding="utf-8")
        self.assertIn('<script type="application/json" id="board-data">', html)
        data_block = html.split('id="board-data">', 1)[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(data_block)["tickets"][0]["note"], "closes </script> tag risk")
        tsx = (self.root / "out" / "board.cursor").read_text(encoding="utf-8")
        self.assertIn('from "cursor/canvas"', tsx)


if __name__ == "__main__":
    unittest.main()

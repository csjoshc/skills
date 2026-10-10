"""Tests for board_sources.py: every ticket dialect reads into one schema, and reading never writes."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import board_sources as bs


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class TestTicketFile(Base):
    def test_inline_list_and_gate_id(self) -> None:
        p = self.write(".tickets/t-002.md", "---\nid: T-002\ntitle: Work item\nStage: build\n"
                       "Depends-On: [T-001, T-000]\nGate: GATE-1\nowner: dana\nnote: waits on API\n---\n")
        t = bs.parse_ticket_file(p)
        self.assertEqual((t["id"], t["stage"], t["deps"]), ("T-002", "BUILD", ["T-001", "T-000"]))
        self.assertEqual((t["gate"], t["is_gate"], t["owner"], t["note"]), ("GATE-1", False, "dana", "waits on API"))

    def test_block_list_gate_true_and_evidence(self) -> None:
        p = self.write(".tickets/gate-1.md", "---\nid: GATE-1\ntitle: \"Gate one\"\nStage: NEW\ngate: true\n"
                       "deps:\n  - T-001\n  - T-002\nevidence:\n  - PR 12 | https://example.test/pr/12\n---\n")
        t = bs.parse_ticket_file(p)
        self.assertEqual(t["title"], "Gate one")
        self.assertTrue(t["is_gate"])
        self.assertEqual(t["deps"], ["T-001", "T-002"])
        self.assertEqual(t["evidence"], [{"label": "PR 12", "url": "https://example.test/pr/12"}])

    def test_other_skill_vocab_maps_to_board_stages(self) -> None:
        cases = {"Done": "COMPLETE", "spec_split": "NEW", "FAILED": "BLOCKED", "in review": "REVIEW", "wip": "BUILD"}
        for raw, stage in cases.items():
            self.assertEqual(bs.normalize_stage(raw), stage, raw)
        self.assertEqual(set(bs.STAGE_ALIASES), set(bs.STAGES))

    def test_body_gives_intent_and_checked_acceptance(self) -> None:
        p = self.write(".tickets/t-1.md", "---\nid: T-1\n---\n\n# Card form\n\nPay by [card](x) in one screen.\n\n"
                       "## Acceptance criteria\n\n- [x] Validates number\n- [ ] Shows decline reason\n- Emails receipt\n")
        t = bs.parse_ticket_file(p)
        self.assertEqual((t["title"], t["intent"]), ("Card form", "Pay by card in one screen."))
        self.assertEqual(t["acceptance"], [{"text": "Validates number", "checked": True},
                                           {"text": "Shows decline reason", "checked": False},
                                           {"text": "Emails receipt"}])

    def test_missing_stage_stays_unknown_not_guessed(self) -> None:
        t = bs.parse_ticket_file(self.write(".tickets/x.md", "# Only a heading\n"))
        self.assertEqual((t["id"], t["stage"]), ("x", None))


class TestTaskSequence(Base):
    def test_first_table_with_id_column_wins(self) -> None:
        p = self.write(".plan/task-sequence.md",
                       "| Phase | Weeks |\n|---|---|\n| 1 | 2 |\n\n| Ticket | Title | Depends on | Status | Gate |\n"
                       "|---|---|---|---|---|\n| `T-001` | Schema | — | Done | GATE-1 |\n"
                       "| T-002 | API | T-001 | | GATE-1 |\n| GATE-1 | Gate | T-001, T-002 | New | yes |\n")
        by_id = {t["id"]: t for t in bs.parse_task_sequence(p)}
        self.assertEqual(list(by_id), ["T-001", "T-002", "GATE-1"])
        self.assertEqual((by_id["T-001"]["stage"], by_id["T-001"]["deps"]), ("COMPLETE", []))
        self.assertIsNone(by_id["T-002"]["stage"])
        self.assertTrue(by_id["GATE-1"]["is_gate"])

    def test_acceptance_lines_attach_to_heading_ids(self) -> None:
        p = self.write(".plan/task-sequence.md", "## T-001 and T-010\n\n- AC: Schema migrates\n"
                       "- [x] AC: Rolls back\n\n## T-002\n\n- AC: API answers\n")
        acs = bs.parse_sequence_acs(p, ["T-001", "T-002", "T-01"])
        self.assertEqual(acs["T-001"], [{"text": "Schema migrates"}, {"text": "Rolls back", "checked": True}])
        self.assertEqual(acs["T-002"], [{"text": "API answers"}])
        self.assertNotIn("T-01", acs)


class TestStagesOverride(Base):
    def test_yaml_ignores_comments_and_blank_values(self) -> None:
        self.write("board/stages.yaml", "# manual\nT-001: done  # shipped\nT-002:\n'T-003': in review\n")
        self.assertEqual(bs.parse_stages_override(self.root / "board"), {"T-001": "COMPLETE", "T-003": "REVIEW"})

    def test_absent_is_empty(self) -> None:
        self.assertEqual(bs.parse_stages_override(self.root / "board"), {})


class TestBriefSources(Base):
    def test_prd_claims_are_tagged_and_absent_prd_is_none(self) -> None:
        self.assertIsNone(bs.parse_prd(self.root / "PRD.md", "PRD.md"))
        p = self.write("PRD.md", "# Checkout\n\n## Problem\n\nBuyers drop off.\n\n## Non-goals\n\n- Gift cards\n")
        prd = bs.parse_prd(p, "PRD.md")
        assert prd is not None
        self.assertEqual(prd["title"], "Checkout")
        self.assertEqual(prd["goal"], [{"text": "Buyers drop off.", "tags": ["PRD"]}])
        self.assertEqual(prd["non_goals"], [{"text": "Gift cards", "tags": ["PRD"]}])

    def test_brief_flags_untagged_claims(self) -> None:
        p = self.write("brief.md", "---\nwritten_by: agent\n---\n## Building\n\nCard pay. [chat]\nNo source here.\n"
                       "## Spec\n\n- T-1: Form validates.\n## Proof\n\n- BUILD: Tests fail first. [D3]\n")
        b = bs.parse_brief(p)
        self.assertEqual(b["building"][0], {"text": "Card pay.", "tags": ["chat"]})
        self.assertEqual(b["untagged"], ["No source here."])
        self.assertEqual(b["spec"]["T-1"]["text"], "Form validates.")
        self.assertEqual(b["proof"]["BUILD"], {"text": "Tests fail first.", "tags": ["D3"]})

    def test_spec_keys_accept_real_ticket_id_styles(self) -> None:
        p = self.write("brief.md", "## Spec\n\n- T-4a: Split helper. [PRD]\n- `T-001`: Form validates.\n"
                       "- 001-auth: Login works.\n")
        self.assertEqual(sorted(bs.parse_brief(p)["spec"]), ["001-auth", "T-001", "T-4a"])

    def test_authored_sections_win_prd_fills_rest(self) -> None:
        prd = {"title": "T", "goal": [{"text": "g"}], "non_goals": [{"text": "n"}], "constraints": [], "source": "P"}
        merged = bs.merge_overview(prd, {"building": [{"text": "b"}], "not_building": []})
        assert merged is not None
        self.assertEqual((merged["goal"], merged["non_goals"]), ([{"text": "b"}], [{"text": "n"}]))
        self.assertIsNone(bs.merge_overview(None, None))


class TestCoversHash(Base):
    def test_order_free_but_sensitive_to_stage_and_acs(self) -> None:
        a, b = bs.blank_ticket("A"), bs.blank_ticket("B")
        h = bs.covers_hash([a, b])
        self.assertEqual(h, bs.covers_hash([b, a]))
        self.assertNotEqual(h, bs.covers_hash([{**a, "stage": "BUILD"}, b]))
        self.assertNotEqual(h, bs.covers_hash([{**a, "acceptance": [{"text": "x"}]}, b]))


class TestReadOnly(Base):
    def test_readers_leave_sources_untouched(self) -> None:
        files = [self.write(".tickets/t.md", "---\nid: T\nStage: NEW\n---\n"),
                 self.write("board/stages.yaml", "T: BUILD\n"), self.write("brief.md", "## Building\n\nx [y]\n")]
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
        bs.parse_ticket_file(files[0])
        bs.parse_stages_override(self.root / "board")
        bs.parse_brief(files[2])
        self.assertEqual({p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}, before)
        self.assertEqual(sorted(self.root.rglob("*")), sorted({*files, *(p.parent for p in files)} - {self.root}))


if __name__ == "__main__":
    unittest.main()

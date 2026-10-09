"""Tests for the brief pages: overview, spec, proof. Run with the other test_*.py files."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import board_refresh as br
from test_board_refresh import Base, ticket, write


def texts(claims: list[dict[str, object]]) -> list[object]:
    return [c["text"] for c in claims]

PRD = """# Shop checkout

Draft owned by the planning skill.

## Problem

Buyers drop off at payment. Card entry takes four screens. Support gets twenty tickets a week.
Returning buyers retype their address. This sentence is the fourth.

## Non-goals

- Gift cards
- Subscriptions
- **Crypto** payments
- Marketplace sellers
- Tax engine rewrite
- Loyalty points

## Constraints

- Card data never touches our servers
- Ship behind a [flag](https://example.test/flags)
"""

CARD_BODY = """
# Card payment

Let buyers pay by card in one screen.

## Acceptance criteria

- [x] Card form validates the number
- [ ] Declines show the bank reason
- Receipt emailed within a minute

## Notes

- Not an acceptance item
"""


class TestOverview(Base):
    def test_extracts_title_goal_and_lists(self) -> None:
        write(self.root / ".plan" / "PRD.md", PRD)
        ticket(self.root, "T-001", "NEW")
        self.init()
        ov = json.loads(self.board.read_text())["brief"]["overview"]
        self.assertEqual(ov["title"], "Shop checkout")
        self.assertEqual(
            texts(ov["goal"]),
            ["Buyers drop off at payment. Card entry takes four screens. Support gets twenty tickets a week."],
        )
        self.assertEqual(texts(ov["non_goals"]), ["Gift cards", "Subscriptions", "Crypto payments",
                                           "Marketplace sellers", "Tax engine rewrite"])
        self.assertEqual(texts(ov["constraints"]), ["Card data never touches our servers", "Ship behind a flag"])
        self.assertEqual(ov["source"], ".plan/PRD.md")

    def test_goal_falls_back_to_first_paragraph(self) -> None:
        write(self.root / ".plan" / "PRD.md", "# Search\n\nFind orders by email.\n\n## Non-goals\n\n- Fuzzy match\n")
        ticket(self.root, "T-001", "NEW")
        self.init()
        ov = json.loads(self.board.read_text())["brief"]["overview"]
        self.assertEqual(texts(ov["goal"]), ["Find orders by email."])
        self.assertEqual(texts(ov["non_goals"]), ["Fuzzy match"])
        self.assertEqual(ov["constraints"], [])

    def test_long_goal_truncates(self) -> None:
        write(self.root / ".plan" / "PRD.md", "# X\n\n## Goal\n\n" + "word " * 200 + "\n")
        ticket(self.root, "T-001", "NEW")
        self.init()
        goal = json.loads(self.board.read_text())["brief"]["overview"]["goal"][0]["text"]
        self.assertLessEqual(len(goal), 300)
        self.assertTrue(goal.endswith("..."))

    def test_missing_prd_hides_overview(self) -> None:
        ticket(self.root, "T-001", "NEW")
        self.init()
        self.assertIsNone(json.loads(self.board.read_text())["brief"]["overview"])


class TestSpec(Base):
    def test_acceptance_from_ticket_body_keeps_checked_state(self) -> None:
        write(self.root / ".tickets" / "t-001-card.md",
              "---\nid: T-001\ntitle: Card payment\nStage: BUILD\n---\n" + CARD_BODY)
        t = br.parse_ticket_file(self.root / ".tickets" / "t-001-card.md")
        self.assertEqual(t["intent"], "Let buyers pay by card in one screen.")
        self.assertEqual(t["acceptance"], [
            {"text": "Card form validates the number", "checked": True},
            {"text": "Declines show the bank reason", "checked": False},
            {"text": "Receipt emailed within a minute"},
        ])

    def test_ticket_without_body_has_no_intent(self) -> None:
        ticket(self.root, "T-001", "NEW")
        t = br.parse_ticket_file(self.root / ".tickets" / "t-001.md")
        self.assertIsNone(t["intent"])
        self.assertEqual(t["acceptance"], [])

    def test_acceptance_falls_back_to_task_sequence(self) -> None:
        ticket(self.root, "T-002", "NEW")
        write(self.root / ".plan" / "task-sequence.md",
              "| ID | Title |\n|---|---|\n| T-002 | API |\n| T-020 | Other |\n\n"
              "### T-002\n\n- AC: Returns 201 on create\n- AC: Rejects an unknown id\n\n"
              "### T-020\n\n- AC: Belongs to another ticket\n")
        self.init()
        by_id = {t["id"]: t for t in json.loads(self.board.read_text())["tickets"]}
        self.assertEqual([a["text"] for a in by_id["T-002"]["acceptance"]],
                         ["Returns 201 on create", "Rejects an unknown id"])
        self.assertEqual([a["text"] for a in by_id["T-020"]["acceptance"]], ["Belongs to another ticket"])


class TestProof(Base):
    def test_default_rules_from_init(self) -> None:
        ticket(self.root, "T-001", "NEW")
        self.init()
        cfg = json.loads((self.board_dir / "config.json").read_text())
        self.assertEqual(cfg["stage_rules"], br.DEFAULT_STAGE_RULES)
        brief = json.loads(self.board.read_text())["brief"]
        self.assertEqual(brief["stage_rules"], br.DEFAULT_STAGE_RULES)
        self.assertEqual(brief["stage_rules_source"], "default")
        self.assertEqual(set(br.DEFAULT_STAGE_RULES), set(br.STAGES))

    def test_config_rules_override_defaults(self) -> None:
        ticket(self.root, "T-001", "NEW")
        self.init()
        cfg_path = self.board_dir / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["stage_rules"]["BUILD"] = "Spike merged and test plan agreed"
        cfg_path.write_text(json.dumps(cfg))
        self.run_cli("refresh", "--today", "2030-01-03")
        brief = json.loads(self.board.read_text())["brief"]
        self.assertEqual(brief["stage_rules_source"], "config")
        self.assertEqual(brief["stage_rules"]["BUILD"], "Spike merged and test plan agreed")

    def test_gate_met_needs_complete_and_evidence(self) -> None:
        ev = "evidence:\n  - Run 3 | https://example.test/runs/3\n"
        ticket(self.root, "GATE-1", "COMPLETE", extra="gate: true\n" + ev)
        ticket(self.root, "GATE-2", "COMPLETE", extra="gate: true\n")
        ticket(self.root, "GATE-3", "REVIEW", extra="gate: true\n" + ev)
        self.init()
        gates = {g["id"]: g for g in json.loads(self.board.read_text())["brief"]["gates"]}
        self.assertEqual({k: g["met"] for k, g in gates.items()},
                         {"GATE-1": True, "GATE-2": False, "GATE-3": False})
        self.assertEqual(gates["GATE-1"]["question"], "Work item GATE-1")
        self.assertEqual(gates["GATE-1"]["evidence"][0]["url"], "https://example.test/runs/3")


class TestBriefBoard(Base):
    def setUp(self) -> None:
        super().setUp()
        write(self.root / ".plan" / "PRD.md", PRD)
        write(self.root / ".tickets" / "t-001.md", "---\nid: T-001\ntitle: Card payment\nStage: BUILD\n---\n" + CARD_BODY)
        self.init()

    def test_default_view_order(self) -> None:
        self.assertEqual(json.loads(self.board.read_text())["views"]["order"],
                         ["overview", "spec", "proof", "now", "timeline", "dag", "gates", "burn"])

    def test_old_five_view_config_gains_brief_views(self) -> None:
        cfg_path = self.root / ".plan" / "board" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["views"] = {"order": ["now", "timeline", "dag", "gates", "burn"]}
        cfg_path.write_text(json.dumps(cfg))
        self.run_cli("refresh", "--today", "2030-01-09")
        self.assertEqual(json.loads(self.board.read_text())["views"]["order"][:3], ["overview", "spec", "proof"])

    def test_custom_view_order_kept(self) -> None:
        cfg_path = self.root / ".plan" / "board" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["views"] = {"order": ["dag", "now"]}
        cfg_path.write_text(json.dumps(cfg))
        self.run_cli("refresh", "--today", "2030-01-09")
        self.assertEqual(json.loads(self.board.read_text())["views"]["order"], ["dag", "now"])

    def test_idempotent_with_brief(self) -> None:
        b1, h1 = self.board.read_bytes(), self.history.read_bytes()
        self.run_cli("refresh", "--today", "2030-01-09")
        self.assertEqual(self.board.read_bytes(), b1)
        self.assertEqual(self.history.read_bytes(), h1)

    def test_exports_carry_brief(self) -> None:
        for target in ("cursor", "artifact", "html", "md"):
            out = self.root / "out" / f"b.{target}"
            self.assertEqual(self.run_cli("export", "--target", target, "--out", str(out)), 0)
            text = out.read_text(encoding="utf-8")
            for needle in ("Buyers drop off at payment", "Declines show the bank reason", "Tests written and failing"):
                self.assertIn(needle, text, f"{target}: {needle}")

    def test_refresh_module_stays_small(self) -> None:
        n = len((Path(br.__file__)).read_text(encoding="utf-8").splitlines())
        self.assertLess(n, 350)


if __name__ == "__main__":
    unittest.main()

"""Tests for the agent-authored brief: .plan/board/brief.md."""

from __future__ import annotations

import contextlib
import io
import json
import unittest

import board_refresh as br
from board_export import TARGETS
from test_board_brief import PRD, texts
from test_board_refresh import Base, ticket, write

BRIEF = """---
written_at: 2030-01-02
written_by: test agent
covers: {covers}
---

## Building

Buyers pay by card on one screen. [chat 2030-01-01]
Saved cards come later. [D2] [T-002]

## Not building

- Gift cards [PRD]
- Wallet payments

## Spec

- T-001: Card form that validates as the buyer types. [chat 2030-01-01]
- T-002: Receipt email after payment.

## Proof

- BUILD: Card form tests fail before the form exists. [D3]
- GATE-1: A recorded checkout run is the proof. [PR #12]
Sandbox only until launch.
"""


class AuthoredBase(Base):
    def setUp(self) -> None:
        super().setUp()
        write(self.root / ".tickets" / "t-001.md",
              "---\nid: T-001\ntitle: Card form\nStage: BUILD\nGate: GATE-1\n---\n\nBody intent.\n\n"
              "## Acceptance\n\n- [ ] Rejects a short number\n")
        ticket(self.root, "T-002", "NEW", extra="Gate: GATE-1\n")
        ticket(self.root, "GATE-1", "NEW", extra="gate: true\n")
        self.init()
        self.brief_path = self.board_dir / "brief.md"

    def cli_out(self, *args: str) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = self.run_cli(*args)
        return code, buf.getvalue()

    def write_brief(self, body: str = BRIEF) -> None:
        code, out = self.cli_out("brief-hash", "--today", "2030-01-02")
        self.assertEqual(code, 0)
        write(self.brief_path, body.format(covers=out.strip()))
        self.run_cli("refresh", "--today", "2030-01-02")

    def brief(self) -> dict[str, object]:
        data: dict[str, object] = json.loads(self.board.read_text())["brief"]
        return data


class TestParse(AuthoredBase):
    def test_sections_and_frontmatter(self) -> None:
        write(self.brief_path, BRIEF.format(covers="sha256:abc"))
        b = br.parse_brief(self.brief_path)
        self.assertEqual((b["written_at"], b["written_by"], b["covers"]), ("2030-01-02", "test agent", "sha256:abc"))
        self.assertEqual(b["building"][1], {"text": "Saved cards come later.", "tags": ["D2", "T-002"]})
        self.assertEqual(texts(b["not_building"]), ["Gift cards", "Wallet payments"])
        self.assertEqual(b["spec"]["T-001"], {"text": "Card form that validates as the buyer types.",
                                              "tags": ["chat 2030-01-01"]})
        self.assertEqual(b["spec"]["T-002"]["tags"], [])
        self.assertEqual(b["proof"]["BUILD"]["tags"], ["D3"])
        self.assertEqual(b["proof"]["GATE-1"]["text"], "A recorded checkout run is the proof.")
        self.assertEqual(texts(b["proof_notes"]), ["Sandbox only until launch."])

    def test_untagged_claims_counted_not_drift(self) -> None:
        self.write_brief()
        brief = self.brief()
        self.assertEqual(brief["untagged"], ["Wallet payments", "Sandbox only until launch."])
        self.assertEqual(json.loads(self.board.read_text())["drift"], [])
        self.brief_path.write_text(self.brief_path.read_text() + "\nOne more untagged line.\n")
        _, out = self.cli_out("refresh", "--today", "2030-01-03")
        self.assertIn("brief_untagged: 3", out)


class TestCovers(AuthoredBase):
    def hash(self) -> str:
        return self.cli_out("brief-hash", "--today", "2030-01-02")[1].strip()

    def test_hash_stable_and_sensitive(self) -> None:
        h1 = self.hash()
        self.assertEqual(h1, self.hash())
        self.assertTrue(h1.startswith("sha256:"))
        self.assertEqual(len(h1), len("sha256:") + 64)
        t1 = self.root / ".tickets" / "t-001.md"
        t1.write_text(t1.read_text().replace("Body intent.", "Other intent."))
        self.assertEqual(self.hash(), h1, "intent is not covered")
        t1.write_text(t1.read_text().replace("Rejects a short number", "Rejects a long number"))
        h2 = self.hash()
        self.assertNotEqual(h2, h1, "AC text is covered")
        t1.write_text(t1.read_text().replace("Stage: BUILD", "Stage: REVIEW"))
        self.assertNotEqual(self.hash(), h2, "stage is covered")

    def test_stale_lists_changed_tickets(self) -> None:
        self.write_brief()
        self.assertEqual((self.brief()["stale"], self.brief()["changed"]), (False, []))
        t2 = self.root / ".tickets" / "t-002.md"
        t2.write_text(t2.read_text().replace("Stage: NEW", "Stage: BUILD"))
        self.run_cli("refresh", "--today", "2030-01-04")
        self.assertEqual((self.brief()["stale"], self.brief()["changed"]), (True, ["T-002"]))
        out = self.root / "b.md"
        self.run_cli("export", "--target", "md", "--out", str(out))
        self.assertIn("Brief written 2030-01-02; 1 ticket changed since (T-002)", out.read_text())

    def test_strict_brief_check(self) -> None:
        self.write_brief()
        self.assertEqual(self.run_cli("refresh", "--check", "--strict-brief", "--today", "2030-01-02"), 0)
        t2 = self.root / ".tickets" / "t-002.md"
        t2.write_text(t2.read_text().replace("Stage: NEW", "Stage: BUILD"))
        self.run_cli("refresh", "--today", "2030-01-04")
        self.assertEqual(self.run_cli("refresh", "--check", "--today", "2030-01-04"), 0)
        self.assertEqual(self.run_cli("refresh", "--check", "--strict-brief", "--today", "2030-01-04"), 3)

    def test_no_brief_is_not_stale(self) -> None:
        brief = self.brief()
        self.assertEqual((brief["authored"], brief["stale"], brief["untagged"]), (None, False, []))


class TestPrecedence(AuthoredBase):
    def test_brief_sections_override_prd_per_section(self) -> None:
        write(self.root / ".plan" / "PRD.md", PRD)
        self.write_brief()
        ov = self.brief()["overview"]
        assert isinstance(ov, dict)
        self.assertEqual(texts(ov["goal"]), ["Buyers pay by card on one screen.", "Saved cards come later."])
        self.assertEqual(ov["goal"][0]["tags"], ["chat 2030-01-01"])
        self.assertEqual(texts(ov["non_goals"]), ["Gift cards", "Wallet payments"])
        self.assertEqual(texts(ov["constraints"]), ["Card data never touches our servers", "Ship behind a flag"])
        self.assertEqual(ov["title"], "Shop checkout")
        self.assertEqual(ov["source"], ".plan/board/brief.md, .plan/PRD.md")

    def test_missing_section_falls_back_to_prd(self) -> None:
        write(self.root / ".plan" / "PRD.md", PRD)
        self.write_brief(BRIEF.replace("## Not building\n\n- Gift cards [PRD]\n- Wallet payments\n", ""))
        ov = self.brief()["overview"]
        assert isinstance(ov, dict)
        self.assertEqual(texts(ov["non_goals"])[0], "Gift cards")
        self.assertEqual(len(ov["non_goals"]), 5)

    def test_brief_without_prd_shows_overview(self) -> None:
        self.write_brief()
        ov = self.brief()["overview"]
        assert isinstance(ov, dict)
        self.assertEqual(ov["title"], "")
        self.assertEqual(ov["source"], ".plan/board/brief.md")

    def test_spec_and_proof_override(self) -> None:
        self.write_brief()
        board = json.loads(self.board.read_text())
        t1 = next(t for t in board["tickets"] if t["id"] == "T-001")
        self.assertEqual((t1["intent"], t1["intent_tags"]),
                         ("Card form that validates as the buyer types.", ["chat 2030-01-01"]))
        self.assertEqual([a["text"] for a in t1["acceptance"]], ["Rejects a short number"])
        brief = board["brief"]
        self.assertEqual(brief["stage_rules"]["BUILD"], "Card form tests fail before the form exists.")
        self.assertEqual(brief["stage_rules"]["REVIEW"], br.DEFAULT_STAGE_RULES["REVIEW"])
        self.assertEqual(brief["stage_rule_tags"], {"BUILD": ["D3"]})
        self.assertEqual(brief["stage_rules_source"], "brief")
        self.assertEqual(brief["gates"][0]["note"], {"text": "A recorded checkout run is the proof.", "tags": ["PR #12"]})
        self.assertEqual(texts(brief["proof_notes"]), ["Sandbox only until launch."])
        self.assertEqual(brief["authored"], {"path": ".plan/board/brief.md", "written_at": "2030-01-02",
                                             "written_by": "test agent", "covers": brief["authored"]["covers"]})

    def test_idempotent_with_authored_brief(self) -> None:
        self.write_brief()
        b1 = self.board.read_bytes()
        self.run_cli("refresh", "--today", "2030-01-05")
        self.assertEqual(self.board.read_bytes(), b1)

    def test_exports_carry_text_and_tags(self) -> None:
        self.write_brief()
        for target in TARGETS:
            out = self.root / "out" / f"b.{target}"
            self.assertEqual(self.run_cli("export", "--target", target, "--out", str(out)), 0)
            text = out.read_text(encoding="utf-8")
            for needle in ("Buyers pay by card on one screen", "chat 2030-01-01", "PR #12", "test agent"):
                self.assertIn(needle, text, f"{target}: {needle}")


if __name__ == "__main__":
    unittest.main()

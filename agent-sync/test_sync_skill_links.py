"""Tests for per-skill link platforms (codex, pi, pi-gateway). Run: python3 -I test_sync_skill_links.py"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("sync", Path(__file__).with_name("sync.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class Quiet:
    def __getattr__(self, _):
        return lambda *a, **k: None


class PiSkillLinkTests(unittest.TestCase):
    def setUp(self):
        root = Path(tempfile.mkdtemp())
        self.master = root / "skills"
        (self.master / "tdd").mkdir(parents=True)
        (self.master / "tdd" / "SKILL.md").write_text("---\nname: tdd\n---\n")
        (self.master / "shared").mkdir()  # not a skill: no SKILL.md
        (self.master / "AGENTS.md").write_text("notes")  # root doc pi must not see
        self.pi = root / "pi" / "skills"
        self.pi.parent.mkdir()
        os.symlink(self.master, self.pi)
        sync.SKILLS_DIR = self.master
        self.cfg = sync.PlatformConfig(
            name="pi", skills_symlink=self.pi, permission_type="trust", platform_key="pi")

    def test_full_symlink_is_flagged(self):
        r = sync.audit_symlink("pi", self.cfg, Quiet())
        self.assertEqual(r.symlink_status, sync.Status.WRONG_TARGET)

    def test_repair_makes_real_dir_of_skill_links_only(self):
        self.assertTrue(sync.repair_symlink(self.cfg, Quiet()))
        self.assertFalse(self.pi.is_symlink())
        self.assertEqual(sorted(p.name for p in self.pi.iterdir()), ["tdd"])
        self.assertEqual(self.pi.joinpath("tdd").resolve(), (self.master / "tdd").resolve())
        self.assertEqual(sync.audit_symlink("pi", self.cfg, Quiet()).symlink_status, sync.Status.SYNCED)

    def test_repair_is_idempotent_and_picks_up_new_skills(self):
        sync.repair_symlink(self.cfg, Quiet())
        (self.master / "caveman").mkdir()
        (self.master / "caveman" / "SKILL.md").write_text("x")
        self.assertEqual(sync.audit_symlink("pi", self.cfg, Quiet()).symlink_status, sync.Status.BROKEN)
        sync.repair_symlink(self.cfg, Quiet())
        self.assertEqual(sorted(p.name for p in self.pi.iterdir()), ["caveman", "tdd"])
        self.assertEqual(sync.audit_symlink("pi", self.cfg, Quiet()).symlink_status, sync.Status.SYNCED)


if __name__ == "__main__":
    unittest.main()

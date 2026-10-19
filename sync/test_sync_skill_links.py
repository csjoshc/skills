"""Tests for per-skill link platforms (Codex and OMP). Run: python3 -I test_sync_skill_links.py"""
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


class TestOmpSkillLink(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.master = self.root / "skills"
        (self.master / "tdd").mkdir(parents=True)
        (self.master / "tdd" / "SKILL.md").write_text("shared skill\n")
        (self.master / "caveman").mkdir()
        (self.master / "caveman" / "SKILL.md").write_text("another shared skill\n")
        self.omp = self.root / ".omp" / "agent" / "skills"
        (self.omp / "local-only").mkdir(parents=True)
        (self.omp / "local-only" / "SKILL.md").write_text("local skill\n")
        (self.omp / "tdd").mkdir()
        (self.omp / "tdd" / "SKILL.md").write_text("OMP override\n")
        sync.SKILLS_DIR = self.master
        self.cfg = sync.PlatformConfig(
            name="OMP", skills_symlink=self.omp, permission_type="trust", platform_key="omp")

    def test_omp_uses_native_agent_skills_path(self):
        self.assertEqual(
            sync.PLATFORMS["omp"].skills_symlink,
            sync.HOME / ".omp" / "agent" / "skills",
        )

    def test_shared_skill_links_leave_omp_local_skills_unchanged(self):
        before = (self.omp / "tdd" / "SKILL.md").read_bytes()
        local = self.omp / "local-only" / "SKILL.md"
        local_before = local.read_bytes()

        self.assertTrue(sync.repair_symlink(self.cfg, Quiet()))

        self.assertFalse(self.omp.is_symlink())
        self.assertTrue((self.omp / "tdd").is_dir())
        self.assertFalse((self.omp / "tdd").is_symlink())
        self.assertEqual((self.omp / "tdd" / "SKILL.md").read_bytes(), before)
        self.assertEqual(local.read_bytes(), local_before)
        self.assertTrue((self.omp / "caveman").is_symlink())
        self.assertEqual((self.omp / "caveman").resolve(), (self.master / "caveman").resolve())
        self.assertEqual(sync.audit_symlink("omp", self.cfg, Quiet()).symlink_status,
                         sync.Status.SYNCED)

if __name__ == "__main__":
    unittest.main()

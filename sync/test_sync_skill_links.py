"""Tests for per-skill link platforms (Codex and OMP). Run: python3 -I test_sync_skill_links.py"""
import importlib.util
import os
import subprocess
import sys
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

    def test_copilot_uses_native_personal_skills_path(self):
        self.assertEqual(sync.PLATFORMS["copilot"].skills_symlink, sync.HOME / ".copilot/skills")

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


class TestPrivateSkillBoundary(unittest.TestCase):
    def test_repairs_only_shared_links_and_preserves_native_private_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            master = home / ".skills"
            native = home / ".claude/skills"
            native.mkdir(parents=True)
            for name in ("shared", "new-public", "wrong"):
                skill = master / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("public definition\n")
            private = home / "private-pack/shared"
            private.mkdir(parents=True)
            (private / "SKILL.md").write_text("private override\n")
            offline = home / "private-pack/offline"
            (native / "shared").symlink_to(private)
            (native / "offline").symlink_to(offline)
            (native / "stale").symlink_to(master / "removed")
            (native / "wrong").symlink_to(master / "shared")
            for _ in range(2):
                result = subprocess.run(
                    [sys.executable, "-B", str(Path(__file__).with_name("sync.py"))],
                    env={"HOME": str(home), "PATH": os.environ["PATH"]},
                    capture_output=True, text=True, timeout=10, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for name, target in (("shared", private), ("offline", offline)):
                    with self.subTest(name=name):
                        self.assertTrue((native / name).is_symlink())
                        self.assertEqual((native / name).readlink(), target)
                self.assertEqual((native / "new-public").resolve(), master / "new-public")
                self.assertEqual((native / "wrong").resolve(), master / "wrong")
                self.assertFalse((native / "stale").is_symlink())

    def test_foreign_native_root_is_preserved_and_reported_as_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            (home / ".skills").mkdir()
            private = home / "private-pack/skills"
            private.mkdir(parents=True)
            native = home / ".config/devin/skills"
            native.parent.mkdir(parents=True)
            native.symlink_to(private)
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).with_name("sync.py"))],
                env={"HOME": str(home), "PATH": os.environ["PATH"]},
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(native.readlink(), private)
            self.assertIn("foreign skills root", result.stdout)

    def test_missing_link_audit_preserves_success_status_without_repair(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            skill = home / ".skills/public"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("public definition\n")
            (home / ".claude").mkdir()
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).with_name("sync.py")), "--audit"],
                env={"HOME": str(home), "PATH": os.environ["PATH"]},
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((home / ".claude/skills").exists())

    def test_shared_vendor_links_sync_without_touching_native_private_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            master = home / ".skills"
            vendor = master / ".vendor/public/package"
            vendor.mkdir(parents=True)
            (vendor / "SKILL.md").write_text("public definition\n")
            (master / "public").symlink_to(vendor)
            private = home / "private-pack/work-only"
            private.mkdir(parents=True)
            (private / "SKILL.md").write_text("private definition\n")
            natives = [home / path for path in (
                ".omp/agent/skills", ".claude/skills", ".cursor/skills",
                ".config/opencode/skills", ".copilot/skills", ".config/devin/skills",
            )]
            for native in natives:
                native.mkdir(parents=True)
                (native / "work-only").symlink_to(private)
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).with_name("sync.py"))],
                env={"HOME": str(home), "PATH": os.environ["PATH"]},
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for native in natives:
                self.assertFalse(native.is_symlink())
                self.assertEqual((native / "public").resolve(), vendor.resolve())
                self.assertEqual((native / "work-only").resolve(), private.resolve())
            self.assertFalse((master / "work-only").exists())

    def test_cli_does_not_recreate_retired_antigravity_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            public = home / ".skills/public"
            public.mkdir(parents=True)
            (public / "SKILL.md").write_text("public definition\n")
            retired = home / ".gemini/antigravity"
            retired.mkdir(parents=True)
            (home / ".copilot").mkdir()
            for _ in range(2):
                result = subprocess.run(
                    [sys.executable, "-B", str(Path(__file__).with_name("sync.py"))],
                    env={"HOME": str(home), "PATH": os.environ["PATH"]},
                    capture_output=True, text=True, timeout=10, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual((home / ".copilot/skills/public").resolve(), public.resolve())
                self.assertFalse((retired / "skills").exists())
                self.assertNotIn("Antigravity", result.stdout)

    def test_cli_refuses_external_definitions_before_linking_any_consumer(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            master = home / ".skills"
            master.mkdir()
            private = home / "private-pack/skills/work-only"
            private.mkdir(parents=True)
            (private / "SKILL.md").write_text("private definition\n")
            (master / "work-only").symlink_to(private)
            (home / ".codex/skills/.system").mkdir(parents=True)
            project = home / "project"
            project.mkdir()
            for args in ([], ["--audit"], ["--project", str(project)]):
                with self.subTest(args=args):
                    result = subprocess.run(
                        [sys.executable, "-B", str(Path(__file__).with_name("sync.py")), *args],
                        env={"HOME": str(home), "PATH": os.environ["PATH"]},
                        capture_output=True, text=True, timeout=10, check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("native", result.stdout)
                    self.assertFalse((home / ".codex/skills/work-only").is_symlink())
                    self.assertFalse((project / ".skills").is_symlink())
                    self.assertTrue((master / "work-only").is_symlink())
                    self.assertTrue((home / ".codex/skills/.system").is_dir())


if __name__ == "__main__":
    unittest.main()

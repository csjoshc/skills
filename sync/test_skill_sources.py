"""Exercise pinned installs against real local Git repositories, without network access."""
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("skill_sources", Path(__file__).with_name("skill_sources.py"))
sources = importlib.util.module_from_spec(spec)
if spec.loader and Path(spec.origin).exists():
    spec.loader.exec_module(sources)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "upstream"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "bundle").mkdir()
        (self.repo / "bundle/SKILL.md").write_text("version one\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "first")
        self.pin = git(self.repo, "rev-parse", "HEAD")
        self.master = self.root / "skills"
        (self.master / "sync").mkdir(parents=True)
        self.manifest = self.master / "sync/skill-sources.json"
        self.write_manifest()

    def write_manifest(self, **changes):
        entry = dict(name="sample", repository=str(self.repo), commit=self.pin, path="bundle")
        entry.update(changes)
        self.manifest.write_text(json.dumps([entry]))

    def test_install_pin_and_expose_skill_idempotently(self):
        sources.sync_sources(self.master)
        clone = self.master / ".vendor/sample"
        self.assertEqual(git(clone, "rev-parse", "HEAD"), self.pin)
        self.assertEqual((self.master / "sample/SKILL.md").read_text(), "version one\n")
        self.assertTrue((self.master / "sample").is_symlink())
        sources.sync_sources(self.master)
        sources.sync_sources(self.master, audit=True)
        self.assertEqual(git(clone, "status", "--porcelain"), "")

    def test_audit_missing_is_read_only(self):
        with self.assertRaisesRegex(RuntimeError, "missing"):
            sources.sync_sources(self.master, audit=True)
        self.assertFalse((self.master / ".vendor").exists())

    def test_changed_pin_audit_and_install(self):
        sources.sync_sources(self.master)
        (self.repo / "bundle/SKILL.md").write_text("version two\n")
        git(self.repo, "commit", "-qam", "second")
        new_pin = git(self.repo, "rev-parse", "HEAD")
        self.write_manifest(commit=new_pin)
        with self.assertRaisesRegex(RuntimeError, "revision"):
            sources.sync_sources(self.master, audit=True)
        self.assertEqual((self.master / "sample/SKILL.md").read_text(), "version one\n")
        sources.sync_sources(self.master)
        self.assertEqual((self.master / "sample/SKILL.md").read_text(), "version two\n")

    def test_upstream_advance_does_not_change_pin(self):
        sources.sync_sources(self.master)
        (self.repo / "bundle/SKILL.md").write_text("new upstream\n")
        git(self.repo, "commit", "-qam", "advance")
        sources.sync_sources(self.master)
        self.assertEqual((self.master / "sample/SKILL.md").read_text(), "version one\n")

    def test_audit_missing_link_does_not_repair(self):
        sources.sync_sources(self.master)
        (self.master / "sample").unlink()
        with self.assertRaisesRegex(RuntimeError, "link missing"):
            sources.sync_sources(self.master, audit=True)
        self.assertFalse((self.master / "sample").is_symlink())

    def test_pin_change_preserves_attached_branch(self):
        sources.sync_sources(self.master)
        clone = self.master / ".vendor/sample"
        git(clone, "checkout", "-qb", "local-work")
        (self.repo / "bundle/SKILL.md").write_text("new upstream\n")
        git(self.repo, "commit", "-qam", "advance")
        self.write_manifest(commit=git(self.repo, "rev-parse", "HEAD"))
        with self.assertRaisesRegex(RuntimeError, "attached branch"):
            sources.sync_sources(self.master)
        self.assertEqual(git(clone, "symbolic-ref", "--short", "HEAD"), "local-work")

    def test_cli_failure_has_nonzero_exit(self):
        result = subprocess.run(
            [sys.executable, "-I", str(Path(__file__).with_name("skill_sources.py")), "--master", str(self.master), "--audit"],
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("source checkout missing", result.stderr)

    def test_sync_stops_before_platform_repair_on_source_failure(self):
        for name in ("sync.py", "skill_sources.py", "directory_links.py"):
            shutil.copyfile(Path(__file__).with_name(name), self.master / "sync" / name)
        (self.root / ".skills").symlink_to(self.master, target_is_directory=True)
        result = subprocess.run(
            [sys.executable, "-I", str(self.master / "sync/sync.py"), "--audit"],
            env={**os.environ, "HOME": str(self.root), "USERPROFILE": str(self.root)}, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("source checkout missing", result.stderr)
        self.assertNotIn("--- Codex ---", result.stdout)
        self.assertFalse((self.root / ".codex").exists())

    def test_dirty_clone_refused_and_preserved(self):
        sources.sync_sources(self.master)
        skill = self.master / "sample/SKILL.md"
        skill.write_text("local work\n")
        with self.assertRaisesRegex(RuntimeError, "local changes"):
            sources.sync_sources(self.master)
        self.assertEqual(skill.read_text(), "local work\n")

    def test_untracked_file_refused(self):
        sources.sync_sources(self.master)
        (self.master / ".vendor/sample/local.txt").write_text("keep")
        with self.assertRaisesRegex(RuntimeError, "local changes"):
            sources.sync_sources(self.master)

    def test_existing_source_directory_refused(self):
        (self.master / "sample").mkdir()
        with self.assertRaisesRegex(RuntimeError, "existing"):
            sources.sync_sources(self.master)
        self.assertFalse((self.master / ".vendor").exists())

    def test_wrong_origin_refused(self):
        sources.sync_sources(self.master)
        git(self.master / ".vendor/sample", "remote", "set-url", "origin", "wrong")
        with self.assertRaisesRegex(RuntimeError, "origin"):
            sources.sync_sources(self.master)

    def test_bad_pin_and_path_rejected_without_writes(self):
        for changes in [dict(commit="main"), dict(path="../escape"), dict(name="../escape")]:
            with self.subTest(changes=changes):
                self.write_manifest(**changes)
                with self.assertRaises(ValueError):
                    sources.sync_sources(self.master)
                self.assertFalse((self.master / ".vendor").exists())

    def test_missing_skill_does_not_publish_checkout(self):
        self.write_manifest(path="absent")
        with self.assertRaises(RuntimeError):
            sources.sync_sources(self.master)
        self.assertFalse((self.master / ".vendor/sample").exists())
        self.assertFalse((self.master / "sample").exists())


if __name__ == "__main__":
    unittest.main()

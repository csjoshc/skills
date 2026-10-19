"""Pi retirement removes only old links into the shared skill store."""
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


class RetiredPiTargets(unittest.TestCase):
    def test_pi_is_not_a_skill_sync_platform(self):
        self.assertNotIn("pi", sync.PLATFORMS)
        self.assertNotIn("pi-gateway", sync.PLATFORMS)

    def test_only_shared_store_links_are_removed(self):
        root = Path(tempfile.mkdtemp())
        home = root / "home"
        master = root / "skills"
        (master / "tdd").mkdir(parents=True)
        (master / "tdd/SKILL.md").write_text("shared\n")
        foreign = root / "foreign"
        foreign.mkdir()
        (foreign / "local").write_text("keep\n")
        sync.SKILLS_DIR = master
        paths = [home / ".pi/agent/skills", home / ".gateway-pi/skills"]
        for path in paths:
            path.mkdir(parents=True)
            os.symlink(master / "tdd", path / "tdd")
            os.symlink(master / "tdd", path / "my-personal-alias")
            os.symlink(foreign / "local", path / "local-link")
            (path / "local-only").write_text("keep\n")

        removed = sync.retire_pi_skill_links(home, Quiet())

        self.assertEqual(removed, 2)
        for path in paths:
            self.assertFalse((path / "tdd").exists())
            self.assertTrue((path / "my-personal-alias").is_symlink())
            self.assertEqual((path / "my-personal-alias").resolve(), (master / "tdd").resolve())
            self.assertTrue((path / "local-link").is_symlink())
            self.assertEqual((path / "local-only").read_text(), "keep\n")


if __name__ == "__main__":
    unittest.main()

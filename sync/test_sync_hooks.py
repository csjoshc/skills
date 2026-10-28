"""sync.py must never write git hooks. Run: python3 -I test_sync_hooks.py"""
import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location("sync", Path(__file__).with_name("sync.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

STUB = b'#!/bin/sh\nexec "$HOME/.config/git/warn-leave-main" "$@"\n'


class TestSyncLeavesGitHooksAlone(unittest.TestCase):
    def setUp(self):
        root = Path(tempfile.mkdtemp())
        sync.SKILLS_DIR = root / "skills"
        sync.LOG_FILE = root / "sync.log"
        (sync.SKILLS_DIR / "hooks").mkdir(parents=True)
        (sync.SKILLS_DIR / "hooks" / "post-checkout").write_text("#!/bin/sh\necho old sync hook\n")
        self.repo = root / "repo"
        subprocess.run(["git", "init", "-q", "--template=", str(self.repo)], check=True)
        self.stub = self.repo / ".git" / "hooks" / "post-checkout"
        self.stub.parent.mkdir(exist_ok=True)
        self.stub.write_bytes(STUB)

    def test_hook_dir_flag_is_rejected_and_stub_survives(self):
        argv = ["sync.py", "--hook-dir", str(self.repo)]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stderr(io.StringIO()), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as exit_:
                sync.main()
        self.assertEqual(exit_.exception.code, 2)
        self.assertEqual(self.stub.read_bytes(), STUB)


if __name__ == "__main__":
    unittest.main()

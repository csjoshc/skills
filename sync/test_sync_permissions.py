"""Tests for the permission audit and repair in sync.py. Run: python3 -I test_sync_permissions.py"""
import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("sync", Path(__file__).with_name("sync.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class Quiet:
    def __getattr__(self, _):
        return lambda *a, **k: None


def opencode(path):
    return sync.PlatformConfig(
        name="OpenCode", skills_symlink=Path("/nonexistent"),
        permission_type="external_directory", config_path=path,
    )


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.cfg = self.dir / "opencode.json"

    def audit(self):
        return sync.audit_permissions(opencode(self.cfg), Quiet()).permission_status

    def test_missing_file_is_missing(self):
        self.assertEqual(self.audit(), sync.Status.PERMISSION_MISSING)

    def test_unrelated_config_is_missing(self):
        self.cfg.write_text(json.dumps({"mcp": {}, "permission": {"webfetch": "deny"}}))
        self.assertEqual(self.audit(), sync.Status.PERMISSION_MISSING)

    def test_v2_rule_array_is_ok(self):
        self.cfg.write_text(json.dumps({"permissions": sync.OPENCODE_SKILLS_RULES}))
        self.assertEqual(self.audit(), sync.Status.PERMISSION_OK)

    def test_v1_object_is_ok(self):
        self.cfg.write_text(json.dumps({"permission": {"external_directory": {"~/.skills/**": "allow"}}}))
        self.assertEqual(self.audit(), sync.Status.PERMISSION_OK)

    def test_deny_rule_is_not_ok(self):
        rule = {"action": "external_directory", "resource": "~/.skills/*", "effect": "deny"}
        self.cfg.write_text(json.dumps({"permissions": [rule]}))
        self.assertEqual(self.audit(), sync.Status.PERMISSION_MISSING)

    def test_broken_json_is_broken_and_untouched(self):
        self.cfg.write_text("{not json")
        self.assertEqual(self.audit(), sync.Status.PERMISSION_BROKEN)
        self.assertFalse(sync.repair_permissions(opencode(self.cfg), Quiet()))
        self.assertEqual(self.cfg.read_text(), "{not json")

    def test_repair_adds_rules_keeps_other_keys_and_mode(self):
        self.cfg.write_text(json.dumps({"mcp": {"a": 1}, "permissions": [{"action": "bash", "resource": "*", "effect": "ask"}]}))
        os.chmod(self.cfg, 0o600)
        expected_mode = stat.S_IMODE(self.cfg.stat().st_mode)
        self.assertTrue(sync.repair_permissions(opencode(self.cfg), Quiet()))
        data = json.loads(self.cfg.read_text())
        self.assertEqual(data["mcp"], {"a": 1})
        self.assertIn({"action": "bash", "resource": "*", "effect": "ask"}, data["permissions"])
        self.assertEqual(self.audit(), sync.Status.PERMISSION_OK)
        self.assertEqual(stat.S_IMODE(self.cfg.stat().st_mode), expected_mode)

    def test_repair_is_idempotent(self):
        self.cfg.write_text("{}")
        sync.repair_permissions(opencode(self.cfg), Quiet())
        first = self.cfg.read_text()
        sync.repair_permissions(opencode(self.cfg), Quiet())
        self.assertEqual(self.cfg.read_text(), first)
        self.assertEqual(len(json.loads(first)["permissions"]), len(sync.OPENCODE_SKILLS_RULES))

    def test_unmanaged_platform_is_reported_not_failed(self):
        cfg = sync.PlatformConfig(name="X", skills_symlink=Path("/x"), permission_type="unmanaged",
                                  permission_note="note")
        r = sync.audit_permissions(cfg, Quiet())
        self.assertEqual(r.permission_status, sync.Status.PERMISSION_UNMANAGED)
        self.assertEqual(r.permission_details, "note")


if __name__ == "__main__":
    unittest.main()

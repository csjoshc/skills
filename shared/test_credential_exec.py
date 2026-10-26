"""Real child-process checks with synthetic homes and private credential files."""
import base64
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HELPER = Path(__file__).with_name("credential_exec.py")


class CredentialExec(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.file = self.home / "work.env"
        self.file.write_text("SHARED=work-value\nOTHER=file-only\n")
        self.file.chmod(0o600)
        self.env = {"HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C",
                    "TMPDIR": str(self.home), "HTTPS_PROXY": "http://proxy.example:80",
                    "SSL_CERT_FILE": "/synthetic/ca.pem", "UNUSUAL_NAME": "inherited-secret",
                    "SHARED": "inherited-wrong", "BASH_ENV": str(self.home / "startup")}
        (self.home / "startup").write_text("echo startup-ran\n")
        self.command = [sys.executable, "-I", "-c",
                        ("import json,os,sys; print(json.dumps({'env':dict(os.environ),"
                         "'argv':sys.argv[1:]}))")]

    def run_helper(self, options, args=()):
        return subprocess.run([sys.executable, "-I", str(HELPER), *options,
                               "--", *self.command, *args], check=False, env=self.env,
                              capture_output=True, text=True)

    def test_required_only_clean_environment_and_literal_arguments(self):
        r = self.run_helper(["--file", str(self.file), "--var", "SHARED", "--set", "REGION=local"],
                            ["${SHARED}", "a b; $HOME"])
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertEqual(got["argv"], ["${SHARED}", "a b; $HOME"])
        env = got["env"]
        self.assertEqual(env["SHARED"], "work-value")
        self.assertEqual(env["REGION"], "local")
        for key in ("UNUSUAL_NAME", "OTHER", "BASH_ENV"):
            self.assertNotIn(key, env)
        for key in ("HOME", "PATH", "LANG", "TMPDIR", "HTTPS_PROXY", "SSL_CERT_FILE"):
            self.assertEqual(env[key], self.env[key])

    def test_source_isolation_and_rotation(self):
        personal = self.home / "personal.env"
        personal.write_text("SHARED=personal-value\n")
        personal.chmod(0o600)
        for file, value in ((self.file, "work-value"), (personal, "personal-value"),
                            (self.file, "rotated-value")):
            if value == "rotated-value":
                file.write_text("SHARED=rotated-value\n")
            r = self.run_helper(["--file", str(file), "--var", "SHARED"])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)["env"]["SHARED"], value)

    def test_failure_is_closed_and_source_output_is_suppressed(self):
        for content in ("SHARED=''\n", "OTHER=unused\n",
                        "echo secret-value; echo secret-value >&2; false\n",
                        "SHARED='unterminated-secret-value\n"):
            with self.subTest(content=content):
                self.file.write_text(content)
                r = self.run_helper(["--file", str(self.file), "--var", "SHARED"])
                self.assertEqual(r.returncode, 1)
                self.assertEqual(r.stdout, "")
                self.assertNotIn("secret-value", r.stderr)
                self.assertIn(str(self.file), r.stderr)
        self.file.write_text("SHARED=valid-synthetic-value\n")
        for mode in (0o644, 0o000):
            self.file.chmod(mode)
            r = self.run_helper(["--file", str(self.file), "--var", "SHARED"])
            self.assertEqual(r.returncode, 1)
            self.assertEqual(r.stdout, "")
            self.assertEqual(self.file.stat().st_mode & 0o777, mode)
        self.file.unlink()
        r = self.run_helper(["--file", str(self.file), "--var", "SHARED"])
        self.assertEqual(r.returncode, 1)
        self.assertIn(str(self.file), r.stderr)

    def test_file_without_required_vars_is_not_sourced(self):
        self.file.write_text("exit 1\n")
        r = self.run_helper(["--file", str(self.file)])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("SHARED", json.loads(r.stdout)["env"])

    def descriptor(self, **overrides):
        data = {"version": 1, "file": str(self.file), "vars": ["SHARED"],
                "env": {"RENAMED": "pre-${SHARED}-post"}, "argv": self.command,
                **overrides}
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        return subprocess.run([sys.executable, "-I", str(HELPER), "--descriptor", encoded],
                              check=False, env=self.env, capture_output=True, text=True)

    def test_descriptor_templates_and_headers_never_expand_argv(self):
        r = self.descriptor(headers={"Authorization": "Bearer ${SHARED}"},
                            path_prepend="/synthetic/node/bin")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertEqual(got["env"]["RENAMED"], "pre-work-value-post")
        self.assertEqual(got["argv"], ["--header", "Authorization:Bearer ${SHARED}"])
        self.assertEqual(got["env"]["PATH"], "/synthetic/node/bin:/usr/bin:/bin")
        self.assertNotIn("work-value", json.dumps(got["argv"]))
        self.assertNotIn("OTHER", got["env"])

    def test_descriptor_rejects_unsafe_or_incomplete_contract(self):
        for change in ({"argv": self.command + ["${SHARED}"]},
                       {"vars": []}, {"version": 2}, {"file": None},
                       {"env": {"RENAMED": "${UNDECLARED}"}},
                       {"headers": {"X-Test": "${UNDECLARED}"}},
                       {"env": {"not=valid": "${SHARED}"}},
                       {"unknown": "secret-value"}):
            r = self.descriptor(**change)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertEqual(r.stdout, "")
            self.assertNotIn("secret-value", r.stderr)

    def test_shell_compatible_values_and_source_noise_stay_private(self):
        value = "synthetic 'quoted' \"double\" ; $HOME `literal`\nsecond line"
        self.file.write_text("set -x\nSHARED=" + shlex.quote(value)
                             + "\necho \"$SHARED\"\necho \"$SHARED\" >&2\n"
                             + "DERIVED=\"prefix ${SHARED} suffix\"\n")
        r = self.run_helper(["--file", str(self.file), "--var", "DERIVED"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, "")
        got = json.loads(r.stdout)["env"]
        self.assertEqual(got["DERIVED"], "prefix " + value + " suffix")
        self.assertNotIn("SHARED", got)

    def test_required_names_do_not_collide_with_shell_collection_variables(self):
        self.file.write_text("name=synthetic-name-value\nSHARED=required-value\nset -- changed\n")
        r = self.run_helper(["--file", str(self.file), "--var", "name", "--var", "SHARED"])
        self.assertEqual(r.returncode, 0, r.stderr)
        env = json.loads(r.stdout)["env"]
        self.assertEqual(env["name"], "synthetic-name-value")
        self.assertEqual(env["SHARED"], "required-value")

    def test_missing_file_variables_cannot_fall_back_to_shell_defaults(self):
        for name in ("PATH", "PWD", "SHLVL"):
            r = self.run_helper(["--file", str(self.file), "--var", name])
            self.assertEqual(r.returncode, 1, name)
            self.assertEqual(r.stdout, "")
            self.assertIn(name, r.stderr)

    def test_wrong_owner_and_nonregular_file_are_refused(self):
        code = (
            "import os,runpy,sys; from unittest.mock import patch; "
            "module=runpy.run_path(sys.argv[1]); "
            "patcher=patch('os.getuid',return_value=os.getuid()+1); patcher.start(); "
            "sys.exit(module['main'](['--file',sys.argv[2],'--var','SHARED','--','/bin/echo','ran']))"
        )
        r = subprocess.run([sys.executable, "-I", "-c", code, str(HELPER), str(self.file)],
                           check=False, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn(str(self.file), r.stderr)
        self.file.unlink()
        os.mkfifo(self.file, 0o600)
        r = self.run_helper(["--file", str(self.file), "--var", "SHARED"])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")

if __name__ == "__main__":
    unittest.main()

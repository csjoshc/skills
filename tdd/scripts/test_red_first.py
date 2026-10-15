import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import red_first  # noqa: E402

GIT = ["git", "-c", "commit.gpgsign=false", "-c", "user.name=rf-test", "-c", "user.email=test@invalid"]

CALC = "def add(a, b):\n    return a + b\n"
TEST_ADD = "from pkg.calc import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
SUB = CALC + "\n\ndef sub(a, b):\n    return a - b\n"


def git(repo, *args):
    return subprocess.run([*GIT, "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def commit(repo, msg):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """main has pkg.calc.add and a passing test; HEAD is a branch off main."""
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    write(r, "pkg/__init__.py", "")
    write(r, "pkg/calc.py", CALC)
    write(r, "tests/test_calc.py", TEST_ADD)
    # The runner's own venv has pytest; red_first looks for <repo>/.venv.
    (r / ".venv").symlink_to(sys.prefix)
    write(r, ".git/info/exclude", ".venv\n")
    commit(r, "base")
    git(r, "checkout", "-q", "-b", "slice")
    monkeypatch.chdir(r)
    return r


def run(capsys, *args):
    rc = red_first.main(list(args))
    return rc, json.loads(capsys.readouterr().out)


def status(v, test_id):
    return next(t for t in v["tests"] if t["id"] == test_id)


def test_load_bearing_test_on_new_function_passes(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == 2\n")
    commit(repo, "add sub")
    rc, v = run(capsys)
    assert (rc, v["verdict"], v["kind"]) == (0, "PASS", "feature")
    assert status(v, "tests/test_sub.py::test_sub")["status"] == "red"


def test_tautological_test_is_flagged(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub_exists():\n    assert callable(sub)\n")
    commit(repo, "add sub with a tautological test")
    rc, v = run(capsys)
    assert (rc, v["verdict"]) == (1, "FAIL")
    t = status(v, "tests/test_sub.py::test_sub_exists")
    assert t["status"] == "flagged"
    assert "passes without the change" in t["detail"]


def test_self_referential_test_is_flagged(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == sub(5, 3)\n")
    commit(repo, "self-referential test")
    rc, v = run(capsys)
    # Fails against the raising stub, passes against the None one: weak, not a hard fail.
    assert (rc, v["verdict"]) == (0, "WEAK")
    assert status(v, "tests/test_sub.py::test_sub")["status"] == "weak"


def test_strict_makes_weak_exit_1(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == sub(5, 3)\n")
    commit(repo, "self-referential test")
    rc, v = run(capsys, "--strict")
    assert (rc, v["verdict"]) == (1, "WEAK")


def test_new_function_that_returns_none_is_weak_not_flagged(repo, capsys):
    write(repo, "pkg/calc.py", CALC + "\n\ndef safe_div(a, b):\n    return None if b == 0 else a / b\n")
    write(repo, "tests/test_div.py", "from pkg.calc import safe_div\n\n\n"
          "def test_div_by_zero_is_none():\n    assert safe_div(1, 0) is None\n\n\n"
          "def test_div():\n    assert safe_div(6, 3) == 2\n")
    commit(repo, "safe_div")
    rc, v = run(capsys)
    assert (rc, v["verdict"]) == (0, "WEAK")
    assert status(v, "tests/test_div.py::test_div_by_zero_is_none")["status"] == "weak"
    assert status(v, "tests/test_div.py::test_div")["status"] == "red"

def test_changed_function_needs_a_test_that_tells_old_from_new(repo, capsys):
    write(repo, "pkg/calc.py", "def add(a, b):\n    return max(a + b, 0)\n")
    write(repo, "tests/test_calc.py", TEST_ADD
          + "\n\ndef test_add_floor():\n    assert add(-5, 2) == 0\n"
          + "\n\ndef test_add_again():\n    assert add(1, 1) == 2\n")
    commit(repo, "floor add at zero")
    rc, v = run(capsys)
    assert rc == 1
    assert status(v, "tests/test_calc.py::test_add_floor")["status"] == "red"
    assert status(v, "tests/test_calc.py::test_add_again")["status"] == "flagged"
    # Unchanged tests are not candidates.
    assert all(t["id"] != "tests/test_calc.py::test_add" for t in v["tests"])


def test_new_module_and_new_method_get_stubbed(repo, capsys):
    write(repo, "pkg/calc.py", CALC + "\n\nclass Acc:\n    def __init__(self):\n        self.n = 0\n")
    commit(repo, "acc on main")
    git(repo, "branch", "-f", "main", "HEAD")
    write(repo, "pkg/calc.py", CALC + "\n\nclass Acc:\n    def __init__(self):\n        self.n = 0\n\n"
          "    def bump(self):\n        self.n += 1\n        return self.n\n")
    write(repo, "pkg/fresh.py", "import math\n\n\ndef root(x):\n    return math.sqrt(x)\n")
    write(repo, "tests/test_new.py", "from pkg.calc import Acc\nfrom pkg.fresh import root\n\n\n"
          "def test_bump():\n    assert Acc().bump() == 1\n\n\n"
          "def test_root():\n    assert root(9) == 3\n\n\n"
          "def test_root_exists():\n    assert root is not None\n")
    commit(repo, "bump and root")
    rc, v = run(capsys)
    assert rc == 1
    assert status(v, "tests/test_new.py::test_bump")["status"] == "red"
    assert status(v, "tests/test_new.py::test_root")["status"] == "red"
    assert status(v, "tests/test_new.py::test_root_exists")["status"] == "flagged"


def test_exempt_comment_lets_a_characterization_test_through(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_calc.py", TEST_ADD
          + "\n\ndef test_add_neg():\n    # red-first: exempt pins existing add before the refactor\n"
          + "    assert add(-1, -1) == -2\n")
    commit(repo, "pin add")
    rc, v = run(capsys)
    assert (rc, v["verdict"]) == (0, "PASS")
    t = status(v, "tests/test_calc.py::test_add_neg")
    assert t["status"] == "exempt"
    assert "pins existing add" in t["detail"]


def test_tests_only_change_is_skipped(repo, capsys):
    write(repo, "tests/test_more.py", TEST_ADD.replace("test_add", "test_add_zero").replace("(2, 3) == 5", "(0, 0) == 0"))
    commit(repo, "more tests")
    rc, v = run(capsys)
    assert (rc, v["verdict"], v["kind"]) == (0, "PASS", "tests-only")


def test_failing_at_head_fails(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == 3\n")
    commit(repo, "wrong expectation")
    rc, v = run(capsys)
    assert rc == 1
    assert status(v, "tests/test_sub.py::test_sub")["status"] == "fails_at_head"


def test_skipped_at_head_is_not_a_failure(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "import pytest\nfrom pkg.calc import sub\n\n\n"
          "@pytest.mark.skip(reason='needs a live runtime')\ndef test_sub_live():\n    assert sub(5, 3) == 2\n\n\n"
          "def test_sub():\n    assert sub(5, 3) == 2\n")
    commit(repo, "live test")
    rc, v = run(capsys)
    assert (rc, v["verdict"]) == (0, "PASS")
    assert status(v, "tests/test_sub.py::test_sub_live")["status"] == "skipped"


CHECK_JS = ("const assert = require('node:assert');\nconst {{ sub }} = require('../lib/calc.js');\n"
            "assert.strictEqual({expr}, 2);\n")


@pytest.fixture
def jsrepo(repo):
    """A non-Python shape: plain node scripts as the check, run through --cmd."""
    write(repo, "lib/calc.js", "exports.add = (a, b) => a + b;\n")
    commit(repo, "js lib")
    git(repo, "branch", "-f", "main", "HEAD")
    return repo


def test_cmd_mode_passes_when_check_fails_at_base(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", "const assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\nassert.strictEqual(add(-5, 2), 0);\n")
    commit(jsrepo, "floor add")
    rc, v = run(capsys, "--cmd", "node {checks}")
    assert (rc, v["verdict"], v["mode"]) == (0, "PASS", "cmd")
    assert v["checks"] == ["test/add.test.js"]


def test_cmd_mode_sees_nested_toolchain_dirs(jsrepo, capsys):
    write(jsrepo, "apps/web/package.json", "{}\n")
    write(jsrepo, "apps/web/node_modules/dep.js", "exports.ok = 1;\n")
    write(jsrepo, ".git/info/exclude", ".venv\nnode_modules\n")
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", "const assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\nassert.strictEqual(add(-5, 2), 0);\n")
    commit(jsrepo, "floor add")
    rc, v = run(capsys, "--cmd", "test -f apps/web/node_modules/dep.js && node {checks}")
    assert (rc, v["verdict"]) == (0, "PASS")


def test_cmd_mode_workspace_links_resolve_to_the_export(jsrepo, capsys):
    write(jsrepo, ".git/info/exclude", ".venv\nnode_modules\n")
    write(jsrepo, "packages/lib/index.js", "exports.add = (a, b) => a + b;\n")
    write(jsrepo, "apps/web/package.json", "{}\n")
    commit(jsrepo, "workspace")
    git(jsrepo, "branch", "-f", "main", "HEAD")
    (jsrepo / "apps/web/node_modules").mkdir()
    (jsrepo / "apps/web/node_modules/lib").symlink_to("../../../packages/lib")
    write(jsrepo, "packages/lib/index.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "apps/web/test/add.test.js", "const assert = require('node:assert');\n"
          "assert.strictEqual(require('lib').add(-5, 2), 0);\n")
    commit(jsrepo, "floor add in the workspace package")
    # A whole-dir link would resolve 'lib' to the repo checkout (head) and pass at base.
    rc, v = run(capsys, "--cmd", "node {checks}")
    assert (rc, v["verdict"]) == (0, "PASS")


def test_cmd_mode_only_scopes_checks_in_a_mixed_commit(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", "const assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\nassert.strictEqual(add(-5, 2), 0);\n")
    write(jsrepo, "tests/test_more.py", "def test_x():\n    assert True\n")
    commit(jsrepo, "mixed")
    rc, v = run(capsys, "--cmd", "node {checks}", "--only", "test/*.js")
    assert (rc, v["verdict"], v["checks"]) == (0, "PASS", ["test/add.test.js"])


NODE_JUNIT = "node --test --test-reporter=junit --test-reporter-destination={junit} {checks}"


def test_junit_flags_a_new_case_that_passes_at_base(jsrepo, capsys):
    write(jsrepo, "test/add.test.js", "const test = require('node:test');\nconst assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\ntest('adds', () => assert.strictEqual(add(1, 1), 2));\n")
    commit(jsrepo, "existing case")
    git(jsrepo, "branch", "-f", "main", "HEAD")
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", "const test = require('node:test');\nconst assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\ntest('adds', () => assert.strictEqual(add(1, 1), 2));\n"
          "test('floors at zero', () => assert.strictEqual(add(-5, 2), 0));\n"
          "test('still adds positives', () => assert.strictEqual(add(2, 2), 4));\n")
    commit(jsrepo, "floor add")
    rc, v = run(capsys, "--cmd", NODE_JUNIT)
    # The file fails at base thanks to one case; the per-case view still catches the other.
    assert (rc, v["verdict"]) == (1, "FAIL")
    assert [t["id"] for t in v["tests"] if t["status"] == "flagged"] == ["test::still adds positives"]
    assert all("floors" not in t["id"] for t in v["tests"] if t["status"] == "flagged")


def test_junit_parametrized_existing_cases_are_not_judged(jsrepo, capsys):
    each = ("const test = require('node:test');\nconst assert = require('node:assert');\n"
            "const { add } = require('../lib/calc.js');\n"
            "for (const n of [1, 2, 3]) test(`adds ${n}`, () => assert.strictEqual(add(n, n), 2 * n));\n")
    write(jsrepo, "test/add.test.js", each)
    commit(jsrepo, "parametrized cases")
    git(jsrepo, "branch", "-f", "main", "HEAD")
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", each + "test('floors at zero', () => assert.strictEqual(add(-5, 2), 0));\n")
    commit(jsrepo, "floor add")
    rc, v = run(capsys, "--cmd", NODE_JUNIT)
    assert (rc, v["verdict"]) == (0, "PASS")
    assert [t["id"] for t in v["tests"]] == ["test::floors at zero"]


def test_junit_exempt_comment_in_js(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", "const test = require('node:test');\nconst assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\n"
          "test('floors at zero', () => assert.strictEqual(add(-5, 2), 0));\n"
          "test('still adds positives', () => {\n  // red-first: exempt pins existing addition\n"
          "  assert.strictEqual(add(2, 2), 4);\n});\n")
    commit(jsrepo, "floor add")
    rc, v = run(capsys, "--cmd", NODE_JUNIT)
    assert (rc, v["verdict"]) == (0, "PASS")
    assert status(v, "test::still adds positives") == {
        "id": "test::still adds positives", "status": "exempt", "detail": "pins existing addition"}


def test_junit_passes_when_every_new_case_is_red(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => Math.max(a + b, 0);\n")
    write(jsrepo, "test/add.test.js", "const test = require('node:test');\nconst assert = require('node:assert');\n"
          "const { add } = require('../lib/calc.js');\n"
          "test('floors at zero', () => assert.strictEqual(add(-5, 2), 0));\n")
    commit(jsrepo, "floor add")
    rc, v = run(capsys, "--cmd", NODE_JUNIT)
    assert (rc, v["verdict"]) == (0, "PASS")
    assert [t["status"] for t in v["tests"]] == ["red"]


def test_junit_case_that_never_ran_at_base_is_weak(jsrepo, capsys):
    write(jsrepo, "lib/sub.js", "exports.sub = (a, b) => a - b;\n")
    write(jsrepo, "test/sub.test.js", "const test = require('node:test');\nconst assert = require('node:assert');\n"
          "const { sub } = require('../lib/sub.js');\ntest('subtracts', () => assert.strictEqual(sub(5, 3), 2));\n")
    commit(jsrepo, "new module")
    rc, v = run(capsys, "--cmd", NODE_JUNIT)
    assert (rc, v["verdict"]) == (0, "WEAK")
    assert v["tests"][0]["status"] == "weak"


def test_cmd_mode_new_export_is_weak(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => a + b;\nexports.sub = (a, b) => a - b;\n")
    write(jsrepo, "test/sub.test.js", CHECK_JS.format(expr="sub(5, 3)"))
    commit(jsrepo, "sub")
    rc, v = run(capsys, "--cmd", "node {checks}")
    assert (rc, v["verdict"]) == (0, "WEAK")


def test_cmd_mode_fails_when_check_passes_at_base(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => a + b;\nexports.sub = (a, b) => a - b;\n")
    write(jsrepo, "test/sub.test.js", "const assert = require('node:assert');\nassert.ok(true);\n")
    commit(jsrepo, "sub with a tautological check")
    rc, v = run(capsys, "--cmd", "node {checks}")
    assert (rc, v["verdict"]) == (1, "FAIL")
    assert "passes without the change" in v["detail"]


def test_cmd_mode_fails_when_head_fails(jsrepo, capsys):
    write(jsrepo, "lib/calc.js", "exports.add = (a, b) => a + b;\nexports.sub = (a, b) => a + b;\n")
    write(jsrepo, "test/sub.test.js", CHECK_JS.format(expr="sub(5, 3)"))
    commit(jsrepo, "buggy sub")
    rc, v = run(capsys, "--cmd", "node {checks}")
    assert (rc, v["verdict"]) == (1, "FAIL")
    assert "fails at head" in v["detail"]


def test_cmd_mode_marks_missing_symbol_failures_weak(jsrepo, capsys):
    write(jsrepo, "lib/sub.js", "exports.sub = (a, b) => a - b;\n")
    write(jsrepo, "test/sub.test.js", "const assert = require('node:assert');\n"
          "const { sub } = require('../lib/sub.js');\nassert.strictEqual(sub(5, 3), 2);\n")
    commit(jsrepo, "new module")
    rc, v = run(capsys, "--cmd", "node {checks}")
    # Base fails only because the module is missing, which proves nothing about the assertion.
    assert (rc, v["verdict"]) == (0, "WEAK")
    assert "Cannot find module" in v["base_log_tail"]


def test_worktree_judges_uncommitted_work_without_touching_git(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == 2\n")
    before = [git(repo, "status", "--porcelain"), git(repo, "for-each-ref"), git(repo, "rev-parse", "HEAD")]
    rc, v = run(capsys, "--worktree")
    assert (rc, v["verdict"]) == (0, "PASS")
    assert status(v, "tests/test_sub.py::test_sub")["status"] == "red"
    assert [git(repo, "status", "--porcelain"), git(repo, "for-each-ref"), git(repo, "rev-parse", "HEAD")] == before


def test_explicit_base_and_head(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == 2\n")
    commit(repo, "add sub")
    git(repo, "checkout", "-q", "main")
    rc, v = run(capsys, "--base", "main", "--head", "slice")
    assert (rc, v["verdict"]) == (0, "PASS")


def test_base_equals_head_exits_2(repo, capsys):
    rc, v = run(capsys)
    assert (rc, v["verdict"]) == (2, "ERROR")
    assert "base equals head" in v["error"]


def test_option_injection_rejected(repo, tmp_path, capsys):
    target = tmp_path / "x"
    rc, v = run(capsys, f"--head=--output={target}")
    assert rc == 2
    assert not target.exists()


def test_git_state_is_untouched(repo, capsys):
    write(repo, "pkg/calc.py", SUB)
    write(repo, "tests/test_sub.py", "from pkg.calc import sub\n\n\ndef test_sub():\n    assert sub(5, 3) == 2\n")
    commit(repo, "add sub")

    def state():
        return [git(repo, "status", "--porcelain", "--ignored"), git(repo, "stash", "list"),
                git(repo, "worktree", "list", "--porcelain"), git(repo, "for-each-ref")]

    before = state()
    run(capsys)
    assert state() == before

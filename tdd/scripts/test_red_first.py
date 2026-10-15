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
    assert rc == 1
    assert status(v, "tests/test_sub.py::test_sub")["status"] == "flagged"


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

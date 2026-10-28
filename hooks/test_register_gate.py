"""register-gate.py adds, preserves and repoints the gate without duplicating it."""

import json
import os
import subprocess
import sys
from pathlib import Path

REGISTER = Path(__file__).with_name("register-gate.py")
GATE = Path(__file__).with_name("merge-gate.py")
ROOTS = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "XDG_CONFIG_HOME", "PI_CODING_AGENT_DIR")


def env_for(home: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in ROOTS}
    env["HOME"] = str(home)
    env.pop("DEVIN_PROJECT_DIR", None)
    env.pop("CLAUDE_PROJECT_DIR", None)
    return env


def call(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(REGISTER), *args],
                          capture_output=True, text=True, check=False, env=env_for(home))


def blocking(command: str) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "gh pr merge 1"}})
    return subprocess.run(["/bin/sh", "-c", command], input=payload, capture_output=True,
                          text=True, check=False, cwd="/")


def allowed(command: str) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "gh pr view 1"}})
    return subprocess.run(["/bin/sh", "-c", command], input=payload, capture_output=True,
                          text=True, check=False, cwd="/")


def settings(home: Path) -> dict:
    return json.loads((home / ".claude" / "settings.json").read_text())


def test_claude_fresh_registration_blocks(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    result = call(tmp_path, "claude")
    assert result.returncode == 0, result.stderr
    data = settings(tmp_path)
    group = data["hooks"]["PreToolUse"][0]
    assert group["matcher"] == "^(Bash|mcp__.*)$"
    assert group["hooks"][0]["timeout"] == 5
    assert str(GATE) in group["hooks"][0]["command"]
    assert blocking(group["hooks"][0]["command"]).returncode == 2
    assert allowed(group["hooks"][0]["command"]).returncode == 0


def test_claude_preserves_unrelated_settings_and_hooks(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    foreign = {"matcher": "Bash", "hooks": [{"type": "command", "command": "/bin/true"}]}
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({
        "model": "x",
        "permissions": {"allow": ["Bash(ls)"]},
        "hooks": {"Notification": [{"hooks": [{"type": "command", "command": "/opt/n"}]}],
                  "PreToolUse": [foreign]},
    }))
    assert call(tmp_path, "claude").returncode == 0
    data = settings(tmp_path)
    assert data["model"] == "x"
    assert data["permissions"] == {"allow": ["Bash(ls)"]}
    assert data["hooks"]["Notification"][0]["hooks"][0]["command"] == "/opt/n"
    assert data["hooks"]["PreToolUse"][0] == foreign
    assert len(data["hooks"]["PreToolUse"]) == 2


def test_claude_second_run_is_a_noop(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    assert call(tmp_path, "claude").returncode == 0
    before = (tmp_path / ".claude" / "settings.json").read_bytes()
    again = call(tmp_path, "claude")
    assert again.returncode == 0
    assert "ok" in again.stdout
    assert (tmp_path / ".claude" / "settings.json").read_bytes() == before
    assert not list((tmp_path / ".claude").glob("settings.json.pre-merge-gate.*"))


def test_existing_file_is_backed_up_before_a_change(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    original = tmp_path / ".claude" / "settings.json"
    original.write_text('{"model": "x"}\n')
    assert call(tmp_path, "claude").returncode == 0
    backups = list((tmp_path / ".claude").glob("settings.json.pre-merge-gate.*"))
    assert len(backups) == 1
    assert backups[0].read_text() == '{"model": "x"}\n'


def test_claude_repoints_a_stale_worktree_without_duplicating(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    stale = {"matcher": "^(Bash|mcp__.*)$", "hooks": [{
        "type": "command", "command": "python3 /old/worktree/hooks/merge-gate.py", "timeout": 5}]}
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [stale]}}))
    assert call(tmp_path, "claude").returncode == 0
    groups = settings(tmp_path)["hooks"]["PreToolUse"]
    assert len(groups) == 1
    assert str(GATE) in groups[0]["hooks"][0]["command"]


def test_codex_registration_answers_deny_and_allow(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    result = call(tmp_path, "codex")
    assert result.returncode == 0, result.stderr
    assert "/hooks" in result.stdout
    group = json.loads((tmp_path / ".codex" / "hooks.json").read_text())["hooks"]["PreToolUse"][0]
    command = group["hooks"][0]["command"]
    denied = blocking(command)
    assert denied.returncode == 0
    assert json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert allowed(command).stdout.strip() == ""


def test_codex_preserves_other_groups_and_is_idempotent(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    foreign = {"matcher": "Bash", "hooks": [{"type": "command", "command": "/bin/true"}]}
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps({
        "description": "mine", "hooks": {"PreToolUse": [foreign], "Stop": []}}))
    assert call(tmp_path, "codex").returncode == 0
    data = json.loads((tmp_path / ".codex" / "hooks.json").read_text())
    assert data["description"] == "mine"
    assert data["hooks"]["PreToolUse"][0] == foreign
    assert data["hooks"]["Stop"] == []
    before = (tmp_path / ".codex" / "hooks.json").read_bytes()
    assert call(tmp_path, "codex").returncode == 0
    assert (tmp_path / ".codex" / "hooks.json").read_bytes() == before


def test_check_fails_before_and_passes_after(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    assert call(tmp_path, "--check", "claude").returncode == 1
    assert call(tmp_path, "claude").returncode == 0
    assert call(tmp_path, "--check", "claude").returncode == 0


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    result = call(tmp_path, "--dry-run", "claude")
    assert result.returncode == 0
    assert "would" in result.stdout
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_invalid_json_is_left_alone(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    broken = tmp_path / ".claude" / "settings.json"
    broken.write_text("{")
    result = call(tmp_path, "claude")
    assert result.returncode == 1
    assert "conflict" in result.stdout
    assert broken.read_text() == "{"


def test_all_skips_harnesses_that_are_not_installed(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    result = call(tmp_path, "all")
    assert result.returncode == 0
    assert "skip" in result.stdout
    assert not (tmp_path / ".codex").exists()
    assert not (tmp_path / ".omp").exists()


def test_opencode_link_replaces_a_wrong_target(tmp_path: Path) -> None:
    plugins = tmp_path / ".config" / "opencode" / "plugins"
    plugins.mkdir(parents=True)
    (plugins / "merge-gate.ts").symlink_to("/tmp/not-the-adapter.ts")
    assert call(tmp_path, "opencode").returncode == 0
    target = (plugins / "merge-gate.ts").resolve()
    assert target == (Path(__file__).parent / "adapters" / "opencode" / "merge-gate.ts").resolve()


def test_real_file_is_not_overwritten(tmp_path: Path) -> None:
    plugins = tmp_path / ".config" / "opencode" / "plugins"
    plugins.mkdir(parents=True)
    (plugins / "merge-gate.ts").write_text("// mine\n")
    result = call(tmp_path, "opencode")
    assert result.returncode == 1
    assert (plugins / "merge-gate.ts").read_text() == "// mine\n"


def test_omp_extension_link(tmp_path: Path) -> None:
    (tmp_path / ".omp" / "agent").mkdir(parents=True)
    assert call(tmp_path, "omp").returncode == 0
    link = tmp_path / ".omp" / "agent" / "extensions" / "merge-gate.ts"
    assert link.resolve() == (Path(__file__).parent / "adapters" / "omp" / "merge-gate.ts").resolve()
    assert call(tmp_path, "--check", "omp").returncode == 0

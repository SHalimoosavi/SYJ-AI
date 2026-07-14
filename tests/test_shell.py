import pytest

from syj_ai.tools.shell import ShellPermissionDenied, run_command


def test_dangerous_command_blocked(tmp_path):
    with pytest.raises(ShellPermissionDenied):
        run_command("rm -rf /", cwd=tmp_path)


def test_unconfirmed_command_blocked(tmp_path):
    with pytest.raises(ShellPermissionDenied):
        run_command("echo hi", cwd=tmp_path, require_confirmation=True, confirmed=False)


def test_confirmed_command_runs(tmp_path):
    result = run_command("echo hello", cwd=tmp_path, require_confirmation=True, confirmed=True)
    assert result.ok
    assert "hello" in result.stdout


def test_no_confirmation_required_when_disabled(tmp_path):
    result = run_command("echo hi", cwd=tmp_path, require_confirmation=False)
    assert result.ok

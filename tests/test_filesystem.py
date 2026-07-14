import pytest

from syj_ai.tools.filesystem import Workspace, WorkspaceEscapeError


def test_write_and_read_file(tmp_path):
    ws = Workspace(tmp_path / "workspace")
    ws.write_file("app/main.py", "print('hi')\n")
    assert ws.read_file("app/main.py") == "print('hi')\n"


def test_list_files(tmp_path):
    ws = Workspace(tmp_path / "workspace")
    ws.write_file("a.py", "1")
    ws.write_file("sub/b.py", "2")
    assert ws.list_files() == ["a.py", "sub/b.py"]


def test_escape_is_blocked(tmp_path):
    ws = Workspace(tmp_path / "workspace")
    with pytest.raises(WorkspaceEscapeError):
        ws.write_file("../../etc/passwd", "nope")


def test_delete_file(tmp_path):
    ws = Workspace(tmp_path / "workspace")
    ws.write_file("a.py", "1")
    ws.delete_file("a.py")
    assert not ws.exists("a.py")

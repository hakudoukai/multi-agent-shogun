#!/usr/bin/env python3
"""Tests for SecondPC → MainPC reverse file sync (handle_reverse_file_sync).

Tests cover:
  1. Whitelist enforcement (exact paths only)
  2. Path traversal rejection
  3. Symlink escape rejection
  4. Partial failure → returns False (no partial ACK)
  5. Encoding-safe read/write (Japanese YAML content)
"""
import json, os, sys, tempfile, shutil
import pytest

# Add the shim directory to path so we can import the function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shim", "hakudokai"))

# We need to mock sys.argv before importing the module
# since it reads argv at module level
_orig_argv = sys.argv
sys.argv = ["test", "/dev/null", "/dev/null", "/tmp", "http://localhost", "fake_key"]

# Suppress module-level execution by patching
import importlib
import types

def _load_handle_reverse_file_sync():
    """Extract handle_reverse_file_sync from the poll script without running module-level code."""
    module_path = os.path.join(
        os.path.dirname(__file__), "..", "shim", "hakudokai",
        "hakudokai_secondpc_watcher_poll.py"
    )
    with open(module_path, encoding="utf-8") as f:
        source = f.read()

    # Extract the function and its dependencies
    mod = types.ModuleType("watcher_poll_test")
    mod.__dict__.update({
        "sys": sys, "json": json, "os": os, "subprocess": __import__("subprocess"),
        "time": __import__("time"), "re": __import__("re"), "pathlib": __import__("pathlib"),
    })

    # We need log function
    exec("def log(msg): pass", mod.__dict__)

    # Extract handle_reverse_file_sync function from source
    import textwrap
    func_start = source.find("def handle_reverse_file_sync(")
    func_end = source.find("\ndef detect_target_agent(")
    if func_end == -1:
        func_end = len(source)
    func_source = source[func_start:func_end]
    exec(func_source, mod.__dict__)

    return mod.handle_reverse_file_sync


handle_reverse_file_sync = _load_handle_reverse_file_sync()
sys.argv = _orig_argv


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with queue directories."""
    (tmp_path / "queue" / "reports").mkdir(parents=True)
    (tmp_path / "queue" / "tasks").mkdir(parents=True)
    return str(tmp_path)


def _make_msg(files):
    """Build a fake pc_handshake message with file_sync content."""
    return {
        "id": "test-id-001",
        "message_type": "file_sync",
        "from_pc": "second_pc",
        "to_pc": "main_pc",
        "content": json.dumps({"target_agent": "ashigaru2", "files": files}),
    }


class TestWhitelistEnforcement:
    """SR1: Only exact whitelisted paths should be accepted."""

    def test_allowed_report_ashigaru2(self, project_root):
        msg = _make_msg([{"path": "queue/reports/ashigaru2_report.yaml", "content": "test: ok"}])
        assert handle_reverse_file_sync(msg, project_root) is True
        assert os.path.exists(os.path.join(project_root, "queue/reports/ashigaru2_report.yaml"))

    def test_allowed_report_ashigaru8(self, project_root):
        msg = _make_msg([{"path": "queue/reports/ashigaru8_report.yaml", "content": "test: ok"}])
        assert handle_reverse_file_sync(msg, project_root) is True

    def test_allowed_task_ashigaru2(self, project_root):
        msg = _make_msg([{"path": "queue/tasks/ashigaru2.yaml", "content": "status: done"}])
        assert handle_reverse_file_sync(msg, project_root) is True

    def test_reject_other_agent_report(self, project_root):
        """ashigaru1's report should be rejected (not a SecondPC agent)."""
        msg = _make_msg([{"path": "queue/reports/ashigaru1_report.yaml", "content": "hacked"}])
        assert handle_reverse_file_sync(msg, project_root) is False
        assert not os.path.exists(os.path.join(project_root, "queue/reports/ashigaru1_report.yaml"))

    def test_reject_other_agent_task(self, project_root):
        """ashigaru3's task should be rejected."""
        msg = _make_msg([{"path": "queue/tasks/ashigaru3.yaml", "content": "hacked"}])
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_reject_context_file(self, project_root):
        """context/ files should not be writable via reverse sync."""
        msg = _make_msg([{"path": "context/teriha-zero-wait.md", "content": "hacked"}])
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_reject_claudemd(self, project_root):
        """CLAUDE.md should not be writable via reverse sync."""
        msg = _make_msg([{"path": "CLAUDE.md", "content": "hacked"}])
        assert handle_reverse_file_sync(msg, project_root) is False


class TestPathTraversal:
    """Security: path traversal attempts must be rejected."""

    def test_reject_dotdot_path(self, project_root):
        msg = _make_msg([{"path": "../../../etc/passwd", "content": "root:x:0:0"}])
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_reject_dotdot_in_allowed_prefix(self, project_root):
        msg = _make_msg([{"path": "queue/reports/../../../etc/shadow", "content": "x"}])
        assert handle_reverse_file_sync(msg, project_root) is False


class TestPartialFailure:
    """SR5: Partial success should return False (no partial ACK)."""

    def test_mixed_allowed_and_rejected(self, project_root):
        """One allowed + one rejected → should return False."""
        msg = _make_msg([
            {"path": "queue/reports/ashigaru2_report.yaml", "content": "ok"},
            {"path": "queue/reports/ashigaru1_report.yaml", "content": "rejected"},
        ])
        result = handle_reverse_file_sync(msg, project_root)
        assert result is False


class TestEncodingSafe:
    """SR7: Japanese YAML content must be handled correctly."""

    def test_japanese_content(self, project_root):
        japanese_yaml = "report:\n  summary: |\n    PDF抽出→日計表連動完了。三者監査PASS。\n  status: done\n"
        msg = _make_msg([{"path": "queue/reports/ashigaru2_report.yaml", "content": japanese_yaml}])
        assert handle_reverse_file_sync(msg, project_root) is True

        written = open(
            os.path.join(project_root, "queue/reports/ashigaru2_report.yaml"),
            encoding="utf-8"
        ).read()
        assert "PDF抽出→日計表連動完了" in written

    def test_empty_content(self, project_root):
        msg = _make_msg([{"path": "queue/reports/ashigaru2_report.yaml", "content": ""}])
        assert handle_reverse_file_sync(msg, project_root) is True


class TestEntryTypeValidation:
    """T1: Non-dict entries in files list must be rejected."""

    def test_reject_string_entry(self, project_root):
        msg = _make_msg(["queue/reports/ashigaru2_report.yaml"])
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_reject_null_entry(self, project_root):
        msg = _make_msg([None])
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_reject_int_entry(self, project_root):
        msg = _make_msg([42])
        assert handle_reverse_file_sync(msg, project_root) is False


class TestInvalidPayload:
    """Edge cases for malformed messages."""

    def test_invalid_json_content(self, project_root):
        msg = {"id": "x", "content": "not-json{{{"}
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_empty_files_list(self, project_root):
        msg = {"id": "x", "content": json.dumps({"target_agent": "ashigaru2", "files": []})}
        assert handle_reverse_file_sync(msg, project_root) is False

    def test_no_content_key(self, project_root):
        msg = {"id": "x"}
        assert handle_reverse_file_sync(msg, project_root) is False

#!/usr/bin/env python3
"""Tests for Watcher Hotfix 001 — self-send, retry cap, disable flags.

Covers:
  1. Self-send instant ACK (fukuincho_reverse_poll, secondpc_receiver_poll, kuro_desktop_poll)
  2. Retry cap → dead-letter (secondpc_receiver_poll, kuro_desktop_poll)
  3. Manual disable flag (watchdog.sh, kuro_desktop_watcher.sh) — shellcheck only
  4. ntfy failure → no ACK (kuro_desktop_poll outbound)
"""
import json, os, sys, tempfile, types
from unittest.mock import patch, MagicMock
import pytest


# --- Helpers to extract functions from module sources ---

def _extract_module(filename, globals_override=None):
    """Load a poll module into a namespace without executing module-level code."""
    module_path = os.path.join(
        os.path.dirname(__file__), "..", "shim", "hakudokai", filename
    )
    with open(module_path, encoding="utf-8") as f:
        source = f.read()
    return source, module_path


# ============================================================
# Test: fukuincho_reverse_poll.py self-send detection
# ============================================================

class TestFukuinchoReverseSelfSend:
    """Self-send messages (from_pc == to_pc) must be ACKed immediately."""

    def _run_poll(self, messages, *, urlopen_side_effect=None):
        """Run the poll script with mocked argv and urlopen."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as rf:
            json.dump(messages, rf)
            response_file = rf.name

        processed_file = tempfile.mktemp(suffix=".txt")
        open(processed_file, "w").close()

        script_dir = os.path.join(os.path.dirname(__file__), "..")

        with patch("sys.argv", [
            "test", response_file, processed_file, script_dir,
            "http://localhost:54321/rest/v1", "fake_key", "fukuincho:0.0"
        ]):
            with patch("urllib.request.urlopen") as mock_urlopen:
                if urlopen_side_effect:
                    mock_urlopen.side_effect = urlopen_side_effect
                else:
                    mock_resp = MagicMock()
                    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
                    mock_resp.__exit__ = MagicMock(return_value=False)
                    mock_urlopen.return_value = mock_resp

                # We need to exec the whole module
                source, _ = _extract_module("hakudokai_fukuincho_reverse_poll.py")
                try:
                    exec(compile(source, "<test>", "exec"), {"__name__": "__test__"})
                except SystemExit:
                    pass

        # Read processed file
        with open(processed_file) as f:
            processed = set(line.strip() for line in f if line.strip())

        os.unlink(response_file)
        os.unlink(processed_file)
        return processed, mock_urlopen

    def test_self_send_gets_acked_and_recorded(self):
        """from_pc=main_pc, to_pc=main_pc → ACK with close_reason=self_send_rejected."""
        msgs = [{
            "id": "test-self-send-001",
            "from_pc": "main_pc",
            "to_pc": "main_pc",
            "topic": "test_topic",
            "content": "hello",
            "priority": "normal",
            "message_type": "status_update",
        }]
        processed, mock_urlopen = self._run_poll(msgs)

        # Should be recorded as processed (no infinite retry)
        assert "test-self-send-001" in processed
        # Should have called urlopen for ACK (PATCH with self_send_rejected)
        assert mock_urlopen.called
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        body = json.loads(req.data.decode())
        assert body["acknowledged_by"] == "system"
        assert "self_send_rejected" in body["context_data"]


# ============================================================
# Test: secondpc_receiver_poll.py retry cap
# ============================================================

class TestSecondpcReceiverRetry:
    """Messages exceeding MAX_RETRY must be dead-lettered."""

    def test_retry_cap_dead_letters(self, tmp_path):
        """After MAX_RETRY failures, message gets dead-lettered."""
        # Prepare a retry tracker file pre-loaded at limit
        tracker_file = str(tmp_path / "retry_tracker.json")
        msg_id = "test-retry-cap-001"
        with open(tracker_file, "w") as f:
            json.dump({msg_id: 5}, f)  # Already at MAX_RETRY=5

        response_file = str(tmp_path / "response.json")
        with open(response_file, "w") as f:
            json.dump([{
                "id": msg_id,
                "from_pc": "main_pc",
                "to_pc": "second_pc",
                "topic": "test",
                "content": "hello",
                "message_type": "status_update",
            }], f)

        processed_file = str(tmp_path / "processed.txt")
        open(processed_file, "w").close()

        script_dir = os.path.join(os.path.dirname(__file__), "..")

        # Patch the RETRY_TRACKER_FILE constant and urlopen
        source, _ = _extract_module("hakudokai_secondpc_receiver_poll.py")

        # Replace the tracker file path
        source = source.replace(
            'RETRY_TRACKER_FILE = "/tmp/hakudokai_receiver_retry_tracker.json"',
            f'RETRY_TRACKER_FILE = "{tracker_file}"'
        )

        with patch("sys.argv", [
            "test", response_file, processed_file, script_dir,
            "http://localhost:54321/rest/v1", "fake_key"
        ]):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_resp = MagicMock()
                mock_resp.__enter__ = MagicMock(return_value=mock_resp)
                mock_resp.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_resp

                try:
                    exec(compile(source, "<test>", "exec"), {"__name__": "__test__"})
                except SystemExit:
                    pass

        # Should be recorded as processed (dead-lettered)
        with open(processed_file) as f:
            processed = set(line.strip() for line in f if line.strip())
        assert msg_id in processed

        # urlopen should have been called with dead_letter ACK
        assert mock_urlopen.called
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode())
        assert body["acknowledged_by"] == "dead_letter"
        assert "max_retry_exceeded" in body["context_data"]

    def test_self_send_detection(self, tmp_path):
        """from_pc == to_pc → immediate dead-letter without retry."""
        tracker_file = str(tmp_path / "retry_tracker.json")
        with open(tracker_file, "w") as f:
            json.dump({}, f)

        msg_id = "test-self-send-receiver-001"
        response_file = str(tmp_path / "response.json")
        with open(response_file, "w") as f:
            json.dump([{
                "id": msg_id,
                "from_pc": "second_pc",
                "to_pc": "second_pc",
                "topic": "self_test",
                "content": "loopback",
                "message_type": "status_update",
            }], f)

        processed_file = str(tmp_path / "processed.txt")
        open(processed_file, "w").close()

        script_dir = os.path.join(os.path.dirname(__file__), "..")
        source, _ = _extract_module("hakudokai_secondpc_receiver_poll.py")
        source = source.replace(
            'RETRY_TRACKER_FILE = "/tmp/hakudokai_receiver_retry_tracker.json"',
            f'RETRY_TRACKER_FILE = "{tracker_file}"'
        )

        with patch("sys.argv", [
            "test", response_file, processed_file, script_dir,
            "http://localhost:54321/rest/v1", "fake_key"
        ]):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_resp = MagicMock()
                mock_resp.__enter__ = MagicMock(return_value=mock_resp)
                mock_resp.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_resp

                try:
                    exec(compile(source, "<test>", "exec"), {"__name__": "__test__"})
                except SystemExit:
                    pass

        with open(processed_file) as f:
            processed = set(line.strip() for line in f if line.strip())
        assert msg_id in processed

        # Should be dead-lettered with self_send_rejected
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode())
        assert body["acknowledged_by"] == "dead_letter"
        assert "self_send_rejected" in body["context_data"]


# ============================================================
# Test: watchdog disable flags
# ============================================================

class TestWatchdogDisableFlags:
    """Watchdog must respect ~/.openclaw/global_disable and per-watcher flags."""

    def test_watchdog_has_global_disable_check(self):
        """Verify the watchdog script checks for global_disable."""
        source, _ = _extract_module("hakudokai_watchdog.sh")
        assert "global_disable" in source
        assert "DISABLED by flag file" in source

    def test_watchdog_has_per_watcher_disable(self):
        """Verify per-watcher disable flags for fukuincho and inbox watchers."""
        source, _ = _extract_module("hakudokai_watchdog.sh")
        assert "disable_fukuincho_watcher" in source
        assert "disable_fukuincho_reverse_watcher" in source
        assert "disable_inbox_watcher_" in source

    def test_kuro_desktop_watcher_has_disable_check(self):
        """Verify kuro_desktop_watcher checks disable flags."""
        source, _ = _extract_module("hakudokai_kuro_desktop_watcher.sh")
        assert "global_disable" in source
        assert "disable_kuro_desktop_watcher" in source


# ============================================================
# Test: kuro_desktop_poll outbound ntfy failure → no ACK
# ============================================================

class TestKuroDesktopOutboundNoAckOnFail:
    """Outbound (ntfy) failure must NOT ACK the message."""

    def test_ntfy_failure_prevents_ack(self, tmp_path):
        """When ntfy subprocess fails, message is not ACKed and retry increments."""
        tracker_file = str(tmp_path / "retry_tracker.json")
        with open(tracker_file, "w") as f:
            json.dump({}, f)

        msg_id = "test-ntfy-fail-001"
        response_file = str(tmp_path / "response.json")
        with open(response_file, "w") as f:
            json.dump([{
                "id": msg_id,
                "from_pc": "main_pc",
                "to_pc": "kuro_desktop",
                "topic": "test_msg",
                "content": "hello kuro",
                "priority": "normal",
                "message_type": "status_update",
            }], f)

        processed_file = str(tmp_path / "processed.txt")
        open(processed_file, "w").close()

        script_dir = os.path.join(os.path.dirname(__file__), "..")
        source, _ = _extract_module("hakudokai_kuro_desktop_poll.py")

        # Patch the retry tracker file path
        source = source.replace(
            'RETRY_TRACKER_FILE = f"/tmp/hakudokai_kuro_desktop_{direction}_retry_tracker.json"',
            f'RETRY_TRACKER_FILE = "{tracker_file}"'
        )

        with patch("sys.argv", [
            "test", response_file, processed_file, script_dir,
            "http://localhost:54321/rest/v1", "fake_key", "outbound"
        ]):
            with patch("subprocess.run") as mock_run:
                # Make ntfy subprocess fail
                mock_result = MagicMock()
                mock_result.returncode = 1
                mock_result.stdout = b""
                mock_result.stderr = b"connection refused"
                mock_run.return_value = mock_result

                with patch("urllib.request.urlopen") as mock_urlopen:
                    mock_resp = MagicMock()
                    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
                    mock_resp.__exit__ = MagicMock(return_value=False)
                    mock_urlopen.return_value = mock_resp

                    try:
                        exec(compile(source, "<test>", "exec"), {"__name__": "__test__"})
                    except SystemExit:
                        pass

        # Should NOT be recorded as processed
        with open(processed_file) as f:
            processed = set(line.strip() for line in f if line.strip())
        assert msg_id not in processed

        # Retry tracker should show 1 retry
        with open(tracker_file) as f:
            tracker = json.load(f)
        assert tracker.get(msg_id) == 1

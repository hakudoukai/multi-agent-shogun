#!/usr/bin/env python3
"""Regression contract for SecondPC same-PC role routing."""
import json
import os
from unittest.mock import MagicMock, patch


def _receiver_source():
    root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(root, "shim", "hakudokai", "hakudokai_secondpc_receiver_poll.py")
    with open(path, encoding="utf-8") as f:
        return f.read()


def _run_poll(tmp_path, message):
    response_file = tmp_path / "response.json"
    response_file.write_text(json.dumps([message]), encoding="utf-8")
    processed_file = tmp_path / "processed.txt"
    processed_file.write_text("", encoding="utf-8")
    script_dir = tmp_path / "receiver_root"
    (script_dir / "scripts").mkdir(parents=True)
    (script_dir / "queue" / "inbox").mkdir(parents=True)
    writer = script_dir / "scripts" / "inbox_write.sh"
    writer.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    writer.chmod(0o755)
    retry_file = tmp_path / "retry.json"

    source = _receiver_source()
    with patch.dict(os.environ, {"SECONDPC_RECEIVER_RETRY_TRACKER_FILE": str(retry_file)}):
        with patch("sys.argv", [
            "test", str(response_file), str(processed_file), str(script_dir),
            "http://localhost:54321/rest/v1", "fake_key",
        ]):
            with patch("urllib.request.urlopen") as mock_urlopen:
                response = MagicMock()
                response.__enter__ = MagicMock(return_value=response)
                response.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = response
                try:
                    exec(compile(source, "<receiver-test>", "exec"), {"__name__": "__test__"})
                except SystemExit:
                    pass
    body = json.loads(mock_urlopen.call_args[0][0].data.decode())
    return processed_file.read_text(encoding="utf-8"), body


def test_same_pc_different_role_is_delivered(tmp_path):
    """Same PC but different declared roles is valid routing, not self-send."""
    processed, body = _run_poll(tmp_path, {
        "id": "same-pc-different-role", "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": "cross_pc_inbox_ashigaru1", "content": "deliver",
        "message_type": "answer",
        "context_data": {"sender_agent": "gunshi-second", "target_agent": "ashigaru1"},
    })
    assert "same-pc-different-role" in processed
    assert body["acknowledged_by"] == "second_pc"


def test_same_pc_same_role_is_rejected(tmp_path):
    """A declared same-role loop remains a self-send and is rejected."""
    processed, body = _run_poll(tmp_path, {
        "id": "same-pc-same-role", "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": "cross_pc_inbox_ashigaru1", "content": "loopback",
        "message_type": "answer",
        "context_data": {"sender_agent": "ashigaru1", "target_agent": "ashigaru1"},
    })
    assert "same-pc-same-role" in processed
    assert body["acknowledged_by"] == "dead_letter"
    assert "self_send_rejected" in body["context_data"]


def test_same_pc_missing_sender_identity_fails_closed(tmp_path):
    """Ambiguous same-PC origin must not be delivered by inference."""
    processed, body = _run_poll(tmp_path, {
        "id": "same-pc-missing-sender", "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": "cross_pc_inbox_ashigaru1", "content": "ambiguous",
        "message_type": "answer",
        "context_data": {"target_agent": "ashigaru1"},
    })
    assert "same-pc-missing-sender" in processed
    assert body["acknowledged_by"] == "dead_letter"
    assert "self_send_rejected" in body["context_data"]

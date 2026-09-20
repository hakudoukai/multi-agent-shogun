#!/usr/bin/env python3
"""Regression contract: dead-lettering must not destroy the handshake envelope.

Replacing context_data wholesale dropped target_agent/sender_agent, and a row
with no sender can never pass is_same_agent_send() again, so a single close made
the row permanently self-rejecting.  (board 12674e7c)
"""
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
    with patch.dict(os.environ, {
        "SECONDPC_RECEIVER_RETRY_TRACKER_FILE": str(retry_file),
        "SUPABASE_SERVICE_ROLE_KEY": "fake_key",
    }):
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
    return processed_file.read_text(encoding="utf-8"), json.loads(body["context_data"])


def test_dead_letter_preserves_routing_identity(tmp_path):
    """A close must add its reason on top of the envelope, never replace it."""
    processed, ctx = _run_poll(tmp_path, {
        "id": "envelope-dict", "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": "cross_pc_inbox_ashigaru1", "content": "same role",
        "message_type": "answer",
        "context_data": {"target_agent": "ashigaru1", "sender_agent": "ashigaru1"},
    })
    assert "envelope-dict" in processed
    assert ctx["target_agent"] == "ashigaru1"
    assert ctx["sender_agent"] == "ashigaru1"
    assert ctx["close_reason"] == "max_retry_exceeded"
    assert ctx["last_error"] == "self_send_rejected"


def test_dead_letter_preserves_envelope_supplied_as_json_string(tmp_path):
    """context_data arrives as a JSON string from PostgREST as often as a dict."""
    _, ctx = _run_poll(tmp_path, {
        "id": "envelope-str", "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": "cross_pc_inbox_ashigaru1", "content": "same role",
        "message_type": "answer",
        "context_data": json.dumps({"target_agent": "ashigaru1", "sender_agent": "ashigaru1"}),
    })
    assert ctx["target_agent"] == "ashigaru1"
    assert ctx["sender_agent"] == "ashigaru1"
    assert ctx["close_reason"] == "max_retry_exceeded"


def test_dead_letter_without_envelope_is_unchanged(tmp_path):
    """Negative control: no envelope must still close exactly as it used to."""
    _, ctx = _run_poll(tmp_path, {
        "id": "envelope-absent", "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": "cross_pc_inbox_ashigaru1", "content": "no context",
        "message_type": "answer",
    })
    assert ctx == {"close_reason": "max_retry_exceeded", "last_error": "self_send_rejected"}

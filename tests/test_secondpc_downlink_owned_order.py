#!/usr/bin/env python3
"""Regression contract: downlink ownership must be adjudicated BEFORE self-send.

The skip for DOWNLINK_OWNED_TARGETS already existed, but it sat inside the
standard-message branch, after the self-send test.  That test fails closed when
a row carries no sender identity, so an envelope-less row bound for honbucho /
gunshi-second / dr-s was dead-lettered by the generic receiver and never reached
the skip written to protect it.  Order, not presence, was the defect.
(board 12674e7c)
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
    """Run one poll and report every observable that distinguishes the outcomes."""
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
    delivery_state = tmp_path / "delivery_state.yaml"

    source = _receiver_source()
    with patch.dict(os.environ, {
        "SECONDPC_RECEIVER_RETRY_TRACKER_FILE": str(tmp_path / "retry.json"),
        "SECONDPC_RECEIVER_DELIVERY_STATE_FILE": str(delivery_state),
        "SECONDPC_RECEIVER_DELIVERY_STATE_NOTIFIED_FILE": str(tmp_path / "notified.txt"),
        "SECONDPC_RECEIVER_UNROUTABLE_NOTIFIED_FILE": str(tmp_path / "unroutable.txt"),
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
                methods = [c[0][0].get_method() for c in mock_urlopen.call_args_list]
    return {
        "processed": processed_file.read_text(encoding="utf-8"),
        "methods": methods,
        "state": delivery_state.read_text(encoding="utf-8") if delivery_state.exists() else "",
        "script_dir": script_dir,
    }


def _row(msg_id, topic, context_data=None, message_type="answer", content="body"):
    msg = {
        "id": msg_id, "from_pc": "second_pc", "to_pc": "second_pc",
        "topic": topic, "content": content, "message_type": message_type,
    }
    if context_data is not None:
        msg["context_data"] = context_data
    return msg


def test_envelopeless_downlink_row_is_not_dead_lettered(tmp_path):
    """The case that used to break: no sender identity, target owned by a downlink."""
    out = _run_poll(tmp_path, _row("own-no-sender", "cross_pc_inbox_honbucho"))
    assert "PATCH" not in out["methods"], "the source row must not be mutated at all"
    assert "own-no-sender" not in out["processed"], "an untouched row must stay unprocessed"
    assert "target_owned_by_dedicated_downlink" in out["state"]
    assert "acknowledged_mutation: false" in out["state"]


def test_downlink_row_with_sender_is_also_left_alone(tmp_path):
    """Same skip for a well-formed envelope — ownership does not depend on identity."""
    out = _run_poll(tmp_path, _row(
        "own-with-sender", "cross_pc_inbox_gunshi-second",
        {"target_agent": "gunshi-second", "sender_agent": "karo-second"},
    ))
    assert "PATCH" not in out["methods"]
    assert "target_owned_by_dedicated_downlink" in out["state"]


def test_negative_control_ordinary_target_still_dead_letters(tmp_path):
    """Negative control: the guard must be narrow.  A non-owned target is unchanged."""
    out = _run_poll(tmp_path, _row("ordinary-no-sender", "cross_pc_inbox_ashigaru1"))
    assert "PATCH" in out["methods"], "self-send closing must survive for ordinary targets"
    assert "ordinary-no-sender" in out["processed"]
    assert "target_owned_by_dedicated_downlink" not in out["state"]


def test_negative_control_file_sync_is_not_captured_by_the_guard(tmp_path):
    """Negative control: the guard covers inbox routing only, not file_sync writes."""
    payload = json.dumps({
        "target_agent": "honbucho",
        "files": [{"path": "context/probe.md", "content": "x\n"}],
    })
    out = _run_poll(tmp_path, _row(
        "sync-owned", "file_sync_probe",
        {"target_agent": "honbucho", "sender_agent": "karo-second"},
        message_type="file_sync", content=payload,
    ))
    assert "target_owned_by_dedicated_downlink" not in out["state"]
    assert (out["script_dir"] / "context" / "probe.md").exists(), "file_sync must still write"

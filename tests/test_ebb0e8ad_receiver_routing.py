#!/usr/bin/env python3
"""Non-live acceptance tests for ebb0e8ad receiver routing repair."""
import json
import os
import pathlib
import sys
from unittest.mock import MagicMock, patch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
MODULE = REPO / "shim/hakudokai/hakudokai_secondpc_receiver_poll.py"


def _run(tmp_path, rows, tracker=None):
    response = tmp_path / "response.json"
    processed = tmp_path / "processed.txt"
    tracker_path = tmp_path / "retry.json"
    state = tmp_path / "delivery.yaml"
    notified = tmp_path / "delivery-notified.txt"
    response.write_text(json.dumps(rows), encoding="utf-8")
    processed.write_text("", encoding="utf-8")
    tracker_path.write_text(json.dumps(tracker or {}), encoding="utf-8")
    posts = []

    def fake_urlopen(req, *args, **kwargs):
        posts.append(req)
        response = MagicMock()
        response.__enter__ = MagicMock(return_value=response)
        response.__exit__ = MagicMock(return_value=False)
        return response

    env = {
        "SUPABASE_SERVICE_ROLE_KEY": "fake-key",
        "SECONDPC_RECEIVER_RETRY_TRACKER_FILE": str(tracker_path),
        "SECONDPC_RECEIVER_DELIVERY_STATE_FILE": str(state),
        "SECONDPC_RECEIVER_DELIVERY_STATE_NOTIFIED_FILE": str(notified),
        "SECONDPC_RECEIVER_UNROUTABLE_NOTIFIED_FILE": str(tmp_path / "unroutable.txt"),
    }
    argv = ["test", str(response), str(processed), str(REPO), "http://mock/rest/v1"]
    source = MODULE.read_text(encoding="utf-8")
    with patch.dict(os.environ, env, clear=False), patch("sys.argv", argv), patch("urllib.request.urlopen", side_effect=fake_urlopen):
        try:
            exec(compile(source, str(MODULE), "exec"), {"__name__": "__test__"})
        except SystemExit:
            pass
    return processed.read_text(encoding="utf-8"), state.read_text(encoding="utf-8") if state.exists() else "", posts


def test_worker_panes_are_identity_not_fixed_indexes():
    source = MODULE.read_text(encoding="utf-8")
    assert '"karo-second": "@karo-second"' in source
    assert '"gunshi-second": "multiagent-second:0.8"' not in source


def test_identity_resolver_rejects_a_wrong_old_pane_and_finds_live_identity(tmp_path):
    # The old karo target 0.0 is ashigaru-second-1.  Only the live agent identity
    # may resolve karo-second; this is entirely fixture-based (no tmux call).
    namespace = {"__name__": "receiver_test"}
    source = MODULE.read_text(encoding="utf-8")
    source = source.replace("if not new_msgs:\n    sys.exit(0)", "if False:\n    sys.exit(0)", 1)
    source = source.replace("for msg in new_msgs:", "for msg in []:", 1)
    argv = ["test", str(tmp_path / "response.json"), str(tmp_path / "processed.txt"), str(REPO), "http://mock/rest/v1"]
    # Avoid the module's early empty-response exit while keeping its loop empty.
    (tmp_path / "response.json").write_text('[{"id":"already-processed"}]', encoding="utf-8")
    (tmp_path / "processed.txt").write_text("already-processed\n", encoding="utf-8")
    with patch.dict(os.environ, {"SUPABASE_SERVICE_ROLE_KEY":"fake", "SECONDPC_RECEIVER_RETRY_TRACKER_FILE":str(tmp_path / "retry.json")}, clear=False), patch("sys.argv", argv):
        try:
            exec(compile(source, str(MODULE), "exec"), namespace)
        except SystemExit:
            pass
    resolver = namespace["resolve_agent_pane"]
    assert resolver("karo-second", ["multiagent-second:0.0|ashigaru-second-1"]) is None
    assert resolver("karo-second", ["karo-second:0.0|karo-second"]) == "karo-second:0.0"
    assert resolver("gunshi-second", ["hermes-gunshi-second:0.0|gunshi-second"]) is None


def test_downlink_owned_target_is_not_written_or_acked(tmp_path):
    msg = {"id":"owned-1","from_pc":"dr-s","to_pc":"second_pc","topic":"cross_pc_inbox_gunshi-second","content":"F1","message_type":"answer"}
    processed, state, posts = _run(tmp_path, [msg])
    assert processed == ""
    assert "target_owned_by_dedicated_downlink" in state
    assert "acknowledged_mutation: false" in state
    assert all(b'acknowledged_by' not in request.data for request in posts)


def test_retry_cap_preserves_original_ack_and_returns_failure(tmp_path):
    msg = {"id":"retry-1","from_pc":"third_pc","to_pc":"second_pc","topic":"cross_pc_inbox_karo-second","content":"x","message_type":"answer"}
    processed, state, posts = _run(tmp_path, [msg], {"retry-1": 5})
    assert processed == ""
    assert "delivery_failed" in state and "acknowledged_mutation: false" in state
    assert len(posts) == 1
    payload = json.loads(posts[0].data.decode())
    assert payload["to_pc"] == "third_pc" and payload["topic"] == "receiver_delivery_failed"


def test_invalid_target_escalates_once_without_original_ack(tmp_path):
    msg = {"id":"bad-1","from_pc":"third_pc","to_pc":"second_pc","topic":"cross_pc_inbox_missing","content":"x","message_type":"answer"}
    processed, state, posts = _run(tmp_path, [msg])
    assert "bad-1" in processed  # local dead-letter is durable; no recipient ACK
    assert len(posts) == 1
    payload = json.loads(posts[0].data.decode())
    assert payload["topic"] == "wrong_recipient_or_unroutable"
    assert all(b'acknowledged_by' not in request.data for request in posts)

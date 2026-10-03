import importlib.util
import json
import pathlib
import sys

SCRIPT = pathlib.Path(__file__).parents[1] / "shim/hakudokai/senmu_desktop_route_watcher.py"
spec = importlib.util.spec_from_file_location("senmu_watcher", SCRIPT)
assert spec is not None and spec.loader is not None
watcher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = watcher
spec.loader.exec_module(watcher)


def test_eligibility_and_minimum_sequence_filter(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(watcher, "fetch", lambda params: calls.append(params) or [])
    watcher.inbound_once({})
    assert calls[0]["seq"] == f"gt.{watcher.MIN_SEQ}"
    assert calls[0]["order"] == "seq.asc"
    assert watcher.eligible({"id": "x", "message_type": "ack", "topic": "x"}) is False
    assert watcher.eligible({"id": "x", "message_type": "status_update", "topic": "enter_restart"}) is False
    assert watcher.eligible({"id": "x", "message_type": "answer", "topic": "normal"}) is True
    assert capsys.readouterr().out == ""


def run_inbound(monkeypatch, row, actuator_status, state=None):
    monkeypatch.setattr(watcher, "fetch", lambda params: [row])
    monkeypatch.setattr(watcher, "trigger", lambda row, state: {"rc": 0, "result": {"status": actuator_status}})
    state = state if state is not None else {}
    watcher.inbound_once(state)
    return state


def test_delivery_unverified_records_no_retry_and_emits_hold(monkeypatch, capsys):
    row = {"id": "id-1", "seq": 137987, "message_type": "answer", "topic": "normal"}
    state = run_inbound(monkeypatch, row, "delivery_unverified")
    saved = state["rows"]["id-1"]
    output = json.loads(capsys.readouterr().out)
    assert saved["status"] == "delivery_unknown_no_retry"
    assert saved["attempts"] == 1
    assert saved["delivery_status"] == "unknown_no_retry"
    assert saved["box_held"] is True and saved["return_to_sender_required"] is True
    assert saved["return_event_key"] == "id-1:attempt:1"
    assert output["status"] == "delivery_unknown_no_retry"
    assert output["delivery_status"] == "unknown_no_retry"
    assert output["database_ack_written"] is False
    run_inbound(monkeypatch, row, "success", state)
    assert state["rows"]["id-1"]["attempts"] == 1


def test_retry_exhaustion_is_held_and_visible(monkeypatch, capsys):
    row = {"id": "id-2", "seq": 137988, "message_type": "answer", "topic": "normal"}
    state = run_inbound(monkeypatch, row, "failed")
    state["rows"]["id-2"]["attempts"] = watcher.MAX_ATTEMPTS - 1
    state["rows"]["id-2"]["status"] = "pending_delivery"
    state = run_inbound(monkeypatch, row, "failed", state)
    saved = state["rows"]["id-2"]
    output = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert saved["status"] == "retry_exhausted"
    assert saved["terminal_reason"] == "attempt_limit_reached"
    assert output["return_to_sender_required"] is True
    assert output["terminal_reason"] == "attempt_limit_reached"


def test_atomic_state_replace_preserves_valid_json(tmp_path):
    path = tmp_path / "state.json"
    watcher.atomic_json(path, {"rows": {"x": {"status": "queued_unrung"}}})
    assert json.loads(path.read_text()) == {"rows": {"x": {"status": "queued_unrung"}}}
    assert not path.with_suffix(".json.tmp").exists()


def test_existing_persisted_rows_are_not_retriggered(monkeypatch, capsys):
    row = {"id": "id-3", "seq": 137989, "message_type": "answer", "topic": "normal"}
    called = []
    monkeypatch.setattr(watcher, "fetch", lambda params: [row])
    monkeypatch.setattr(watcher, "trigger", lambda *args: called.append(True))
    state = {"rows": {"id-3": {"status": "delivery_unknown_no_retry", "attempts": 1}}}
    watcher.inbound_once(state)
    assert not called
    assert capsys.readouterr().out == ""

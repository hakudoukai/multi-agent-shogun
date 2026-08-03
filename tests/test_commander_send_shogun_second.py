import json
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "commander_send_shogun_second.sh"


def dry_run(topic: str, content: str = "test body") -> dict:
    completed = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", topic, content],
        check=True,
        capture_output=True,
        text=True,
        env={},
    )
    return json.loads(completed.stdout)


def test_dry_run_forces_commander_secondpc_envelope_without_credentials() -> None:
    payload = dry_run("gunshi-second /clear result")

    assert payload["from_pc"] == "commander"
    assert payload["to_pc"] == "second_pc"
    assert payload["topic"] == "cross_pc_inbox_shogun-second: gunshi-second /clear result"
    assert payload["context_data"] == {
        "target_agent": "shogun-second",
        "sender_helper": "commander_send_shogun_second.sh",
    }


def test_dry_run_preserves_existing_canonical_topic_once() -> None:
    topic = "cross_pc_inbox_shogun-second: existing canonical notice"
    payload = dry_run(topic)

    assert payload["topic"] == topic
    assert payload["topic"].count("cross_pc_inbox_shogun-second") == 1


def test_dry_run_preserves_message_options() -> None:
    completed = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "decision",
            "body",
            "status_update",
            "high",
            "true",
        ],
        check=True,
        capture_output=True,
        text=True,
        env={},
    )
    payload = json.loads(completed.stdout)

    assert payload["message_type"] == "status_update"
    assert payload["priority"] == "high"
    assert payload["requires_response"] is True

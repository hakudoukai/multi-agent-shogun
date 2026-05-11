#!/usr/bin/env python3
"""
test_migrate_legacy_verification_log.py — pytest tests for migrate_legacy_verification_log.py

Tests:
  - migration conversion logic (field mapping, event_id computation)
  - dedupe behavior (existing event_ids are skipped)
  - archive creation (legacy entries preserved)
"""

import hashlib
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from migrate_legacy_verification_log import (
    SOURCE_PC,
    compute_existing_event_ids,
    load_yaml_verifications,
    migrate_entry,
    payload_hash,
    stable_event_id,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_LEGACY_ENTRY = {
    "audit_entry_excerpt": {
        "audit_id": "kuroda_006",
        "audited_at": "2026-05-10T15:40:00+09:00",
        "commit_hash": "abc123",
        "target_id": "subtask_test_001",
        "verdict": "pass",
    },
    "auditor_who": "kuroda",
    "checks": {
        "codex_log_exists": True,
        "commit_hash_valid": True,
        "findings_specific": True,
        "gemini_log_exists": False,
        "related_files_exist": True,
        "timestamp_consistent": True,
    },
    "checks_passed": "5/6",
    "flags": [],
    "shogun_verified": True,
    "target": "kuroda_006",
    "verified_at": "2026-05-10T06:42:22+00:00",
}


# ---------------------------------------------------------------------------
# stable_event_id
# ---------------------------------------------------------------------------


def test_stable_event_id_deterministic():
    eid1 = stable_event_id("mainpc", "kuroda", "kuroda_006", "2026-05-10T06:42:22+00:00")
    eid2 = stable_event_id("mainpc", "kuroda", "kuroda_006", "2026-05-10T06:42:22+00:00")
    assert eid1 == eid2
    assert len(eid1) == 12


def test_stable_event_id_different_inputs_differ():
    eid_a = stable_event_id("mainpc", "kuroda", "kuroda_006", "2026-05-10T06:42:22+00:00")
    eid_b = stable_event_id("mainpc", "kuroda", "kuroda_007", "2026-05-10T06:42:22+00:00")
    assert eid_a != eid_b


def test_stable_event_id_known_value():
    # Verify naomasa_new_001 matches known stored value
    eid = stable_event_id("mainpc", "naomasa_secondpc", "naomasa_new_001", "2026-05-10T23:02:40+00:00")
    assert eid == "e33c5a04202f"


# ---------------------------------------------------------------------------
# migrate_entry: conversion logic
# ---------------------------------------------------------------------------


def test_migrate_entry_adds_source_pc():
    result, reason = migrate_entry(SAMPLE_LEGACY_ENTRY)
    assert reason is None
    assert result["source_pc"] == SOURCE_PC


def test_migrate_entry_adds_event_id():
    result, reason = migrate_entry(SAMPLE_LEGACY_ENTRY)
    assert reason is None
    expected = stable_event_id(
        SOURCE_PC,
        SAMPLE_LEGACY_ENTRY["auditor_who"],
        SAMPLE_LEGACY_ENTRY["target"],
        SAMPLE_LEGACY_ENTRY["verified_at"],
    )
    assert result["event_id"] == expected


def test_migrate_entry_adds_payload_hash():
    result, reason = migrate_entry(SAMPLE_LEGACY_ENTRY)
    assert reason is None
    expected = payload_hash(SAMPLE_LEGACY_ENTRY)
    assert result["payload_hash"] == expected


def test_migrate_entry_preserves_original_fields():
    result, reason = migrate_entry(SAMPLE_LEGACY_ENTRY)
    assert reason is None
    assert result["auditor_who"] == "kuroda"
    assert result["target"] == "kuroda_006"
    assert result["shogun_verified"] is True
    assert result["checks_passed"] == "5/6"


def test_migrate_entry_missing_target_returns_none():
    bad = {k: v for k, v in SAMPLE_LEGACY_ENTRY.items() if k != "target"}
    result, reason = migrate_entry(bad)
    assert result is None
    assert reason is not None


def test_migrate_entry_missing_verified_at_returns_none():
    bad = {k: v for k, v in SAMPLE_LEGACY_ENTRY.items() if k != "verified_at"}
    result, reason = migrate_entry(bad)
    assert result is None
    assert reason is not None


def test_migrate_entry_target_audit_ids_list_takes_first():
    entry = dict(SAMPLE_LEGACY_ENTRY)
    del entry["target"]
    entry["target_audit_ids"] = ["first_audit_id", "second_audit_id"]
    result, reason = migrate_entry(entry)
    assert reason is None
    assert result["target"] == "first_audit_id"


def test_migrate_entry_target_audit_ids_empty_returns_none():
    entry = dict(SAMPLE_LEGACY_ENTRY)
    del entry["target"]
    entry["target_audit_ids"] = []
    result, reason = migrate_entry(entry)
    assert result is None


# ---------------------------------------------------------------------------
# compute_existing_event_ids: dedupe
# ---------------------------------------------------------------------------


def test_compute_existing_event_ids_returns_correct_set():
    existing = [
        {
            "target": "naomasa_new_001",
            "auditor_who": "naomasa_secondpc",
            "verified_at": "2026-05-10T23:02:40+00:00",
        }
    ]
    eids = compute_existing_event_ids(existing)
    expected = stable_event_id("mainpc", "naomasa_secondpc", "naomasa_new_001", "2026-05-10T23:02:40+00:00")
    assert expected in eids


def test_compute_existing_event_ids_skips_malformed():
    existing = [{"target": None, "auditor_who": "x", "verified_at": "2026-01-01T00:00:00+00:00"}]
    eids = compute_existing_event_ids(existing)
    assert len(eids) == 0


# ---------------------------------------------------------------------------
# archive creation
# ---------------------------------------------------------------------------


def test_archive_created_and_contains_all_legacy():
    """Integration test: run migration on temp files and verify archive."""
    import subprocess

    legacy_entries = [dict(SAMPLE_LEGACY_ENTRY)]
    legacy_data = {"verifications": legacy_entries}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        legacy_path = tmpdir / "legacy.yaml"
        mainpc_path = tmpdir / "mainpc.yaml"
        archive_path = tmpdir / "archive.yaml"

        legacy_path.write_text(
            yaml.safe_dump(legacy_data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
        mainpc_path.write_text(
            yaml.safe_dump({"verifications": []}, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "migrate_legacy_verification_log.py"),
                "--legacy-log", str(legacy_path),
                "--mainpc-log", str(mainpc_path),
                "--archive-log", str(archive_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Archive should exist and contain original legacy entries
        assert archive_path.exists()
        archive_data = yaml.safe_load(archive_path.read_text(encoding="utf-8"))
        assert len(archive_data["verifications"]) == 1
        assert archive_data["verifications"][0]["target"] == "kuroda_006"

        # mainpc_log should have the migrated entry
        mainpc_data = yaml.safe_load(mainpc_path.read_text(encoding="utf-8"))
        assert len(mainpc_data["verifications"]) == 1


def test_dedupe_skips_already_existing_entry():
    """Integration test: entry already in mainpc_log should not be duplicated."""
    import subprocess

    entry = dict(SAMPLE_LEGACY_ENTRY)
    legacy_data = {"verifications": [entry]}

    existing_entry = dict(entry)
    existing_entry["source_pc"] = SOURCE_PC
    mainpc_data = {"verifications": [existing_entry]}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        legacy_path = tmpdir / "legacy.yaml"
        mainpc_path = tmpdir / "mainpc.yaml"
        archive_path = tmpdir / "archive.yaml"

        legacy_path.write_text(
            yaml.safe_dump(legacy_data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
        mainpc_path.write_text(
            yaml.safe_dump(mainpc_data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "migrate_legacy_verification_log.py"),
                "--legacy-log", str(legacy_path),
                "--mainpc-log", str(mainpc_path),
                "--archive-log", str(archive_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

        mainpc_after = yaml.safe_load(mainpc_path.read_text(encoding="utf-8"))
        assert len(mainpc_after["verifications"]) == 1, "Dedup failed: duplicate entry was added"

"""Tests for shogun_active_verify_queue.py — cycle 1 dry-run scanner.

privacy-validator: fixtures-allowed
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from shogun_active_verify_queue import (  # noqa: E402
    LockHeld,
    acquire_lock,
    compute_candidates,
    run_scan,
    scan_audit_pass_entries,
    scan_unread_inbox,
    scan_verified_ids,
)


# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------

def _write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")


def _inbox(read_flags: list[bool]) -> dict:
    return {
        "messages": [
            {"id": f"msg_{i}", "read": flag, "content": "x", "type": "task_assigned"}
            for i, flag in enumerate(read_flags)
        ]
    }


def _audit_entry(audit_id: str, target_id: str, verdict: str, commit: str = "deadbeef") -> dict:
    return {
        "audit_id": audit_id,
        "target_id": target_id,
        "verdict": verdict,
        "commit_hash": commit,
        "audited_at": "2026-05-12T10:00:00+09:00",
    }


# ---------------------------------------------------------------------------
# scan_unread_inbox
# ---------------------------------------------------------------------------

class TestScanUnreadInbox:
    def test_counts_unread(self, tmp_path: Path) -> None:
        inbox_dir = tmp_path / "inbox"
        _write_yaml(inbox_dir / "karo.yaml", _inbox([True, False, False]))
        _write_yaml(inbox_dir / "gunshi.yaml", _inbox([True, True]))

        counts = scan_unread_inbox(inbox_dir, ["karo", "gunshi", "ashigaru1"])
        assert counts == {"karo": 2, "gunshi": 0, "ashigaru1": 0}

    def test_missing_file_is_zero(self, tmp_path: Path) -> None:
        counts = scan_unread_inbox(tmp_path / "inbox", ["karo"])
        assert counts == {"karo": 0}

    def test_malformed_messages_is_zero(self, tmp_path: Path) -> None:
        inbox_dir = tmp_path / "inbox"
        _write_yaml(inbox_dir / "karo.yaml", {"messages": "not_a_list"})
        counts = scan_unread_inbox(inbox_dir, ["karo"])
        assert counts == {"karo": 0}


# ---------------------------------------------------------------------------
# scan_audit_pass_entries
# ---------------------------------------------------------------------------

class TestScanAuditPassEntries:
    def test_extracts_pass_variants(self, tmp_path: Path) -> None:
        reports = tmp_path / "reports"
        _write_yaml(reports / "kuroda_mainpc_report.yaml", {
            "reports": [
                _audit_entry("k_001", "task_a", "pass"),
                _audit_entry("k_002", "task_b", "pass_with_concerns"),
                _audit_entry("k_003", "task_c", "fail"),
                _audit_entry("k_004", "task_d", "pass_with_conditions"),
            ],
        })
        entries = scan_audit_pass_entries(reports, [("kuroda", "kuroda_mainpc_report.yaml")])
        ids = sorted(e["audit_id"] for e in entries)
        assert ids == ["k_001", "k_002", "k_004"]
        assert all(e["auditor"] == "kuroda" for e in entries)
        assert all("queue/reports/" in e["source_file"] or e["source_file"].endswith(".yaml") for e in entries)

    def test_missing_report_skipped(self, tmp_path: Path) -> None:
        reports = tmp_path / "reports"
        reports.mkdir()
        entries = scan_audit_pass_entries(reports, [("kuroda", "kuroda_mainpc_report.yaml")])
        assert entries == []

    def test_non_dict_entry_ignored(self, tmp_path: Path) -> None:
        reports = tmp_path / "reports"
        _write_yaml(reports / "kuroda_mainpc_report.yaml", {"reports": ["scalar", None]})
        entries = scan_audit_pass_entries(reports, [("kuroda", "kuroda_mainpc_report.yaml")])
        assert entries == []


# ---------------------------------------------------------------------------
# scan_verified_ids
# ---------------------------------------------------------------------------

class TestScanVerifiedIds:
    def test_collects_target_and_excerpt_ids(self, tmp_path: Path) -> None:
        log_path = tmp_path / "verify.yaml"
        _write_yaml(log_path, {
            "verifications": [
                {"target": "k_001", "audit_entry_excerpt": {"audit_id": "k_001", "target_id": "task_a"}},
                {"target": "k_002"},
                {"audit_entry_excerpt": {"audit_id": "k_005", "target_id": "task_e"}},
            ],
        })
        ids = scan_verified_ids(log_path)
        assert ids == {"k_001", "task_a", "k_002", "k_005", "task_e"}

    def test_missing_log_empty(self, tmp_path: Path) -> None:
        assert scan_verified_ids(tmp_path / "absent.yaml") == set()


# ---------------------------------------------------------------------------
# compute_candidates
# ---------------------------------------------------------------------------

class TestComputeCandidates:
    def test_pass_minus_verified(self) -> None:
        entries = [
            {"auditor": "kuroda", "audit_id": "k_001", "target_id": "task_a", "verdict": "pass",
             "commit_hash": "h1", "audited_at": "", "source_file": "x"},
            {"auditor": "kuroda", "audit_id": "k_002", "target_id": "task_b", "verdict": "pass",
             "commit_hash": "h2", "audited_at": "", "source_file": "x"},
        ]
        verified = {"k_001"}
        cands = compute_candidates(entries, verified)
        assert [c["audit_id"] for c in cands] == ["k_002"]

    def test_target_id_match_also_excludes(self) -> None:
        entries = [
            {"auditor": "kuroda", "audit_id": "k_010", "target_id": "task_x", "verdict": "pass",
             "commit_hash": "", "audited_at": "", "source_file": "x"},
        ]
        verified = {"task_x"}
        assert compute_candidates(entries, verified) == []

    def test_empty_id_does_not_collide(self) -> None:
        entries = [
            {"auditor": "kuroda", "audit_id": "", "target_id": "", "verdict": "pass",
             "commit_hash": "", "audited_at": "", "source_file": "x"},
        ]
        # Empty ids must not match the empty-string in verified set.
        assert compute_candidates(entries, {""}) == entries


# ---------------------------------------------------------------------------
# run_scan integration
# ---------------------------------------------------------------------------

class TestRunScan:
    def test_dry_run_writes_candidate_log(self, tmp_path: Path) -> None:
        repo = tmp_path
        inbox = repo / "queue" / "inbox"
        reports = repo / "queue" / "reports"
        _write_yaml(inbox / "karo.yaml", _inbox([False, False]))
        _write_yaml(inbox / "shogun.yaml", _inbox([True]))
        _write_yaml(reports / "kuroda_mainpc_report.yaml", {
            "reports": [
                _audit_entry("k_001", "task_a", "pass"),
                _audit_entry("k_002", "task_b", "pass_with_concerns"),
            ],
        })
        _write_yaml(reports / "shogun_verification_mainpc_log.yaml", {
            "verifications": [{"target": "k_001"}],
        })
        candidate_log = reports / "active_verify_queue_candidate_log.yaml"

        payload = run_scan(
            repo_root=repo,
            inbox_dir=inbox,
            reports_dir=reports,
            verification_log=reports / "shogun_verification_mainpc_log.yaml",
            candidate_log=candidate_log,
            inbox_agents=["karo", "shogun"],
            auditor_reports=[("kuroda", "kuroda_mainpc_report.yaml")],
        )

        assert payload["mode"] == "dry_run"
        assert payload["unread_inbox_counts"]["karo"] == 2
        assert payload["unread_inbox_counts"]["shogun"] == 0
        assert payload["audit_pass_total"] == 2
        assert payload["already_verified_total"] == 1
        assert payload["candidates_total"] == 1
        assert payload["candidates"][0]["audit_id"] == "k_002"

        loaded = yaml.safe_load(candidate_log.read_text(encoding="utf-8"))
        assert loaded["candidates_total"] == 1
        assert loaded["candidates"][0]["audit_id"] == "k_002"

    def test_no_candidates_when_all_verified(self, tmp_path: Path) -> None:
        repo = tmp_path
        inbox = repo / "queue" / "inbox"
        reports = repo / "queue" / "reports"
        _write_yaml(inbox / "karo.yaml", _inbox([True]))
        _write_yaml(reports / "kuroda_mainpc_report.yaml", {
            "reports": [_audit_entry("k_001", "task_a", "pass")],
        })
        _write_yaml(reports / "shogun_verification_mainpc_log.yaml", {
            "verifications": [{"target": "k_001"}],
        })

        payload = run_scan(
            repo_root=repo,
            inbox_dir=inbox,
            reports_dir=reports,
            verification_log=reports / "shogun_verification_mainpc_log.yaml",
            candidate_log=reports / "active_verify_queue_candidate_log.yaml",
            inbox_agents=["karo"],
            auditor_reports=[("kuroda", "kuroda_mainpc_report.yaml")],
        )
        assert payload["candidates_total"] == 0


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------

class TestLock:
    def test_lock_blocks_second_acquire(self, tmp_path: Path) -> None:
        lock_path = tmp_path / ".lock"
        first = acquire_lock(lock_path)
        try:
            with pytest.raises(LockHeld):
                acquire_lock(lock_path)
        finally:
            first.close()

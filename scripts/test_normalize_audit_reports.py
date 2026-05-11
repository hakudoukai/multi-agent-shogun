"""Tests for normalize_audit_reports.py"""

import sys
import io
import textwrap
import tempfile
from pathlib import Path

import yaml
import pytest

sys.path.insert(0, str(Path(__file__).parent))
from normalize_audit_reports import (
    _detect_partial_reason,
    _normalize_verdict,
    _normalize_entry,
    load_report_file,
    normalize,
)


# ---------------------------------------------------------------------------
# _detect_partial_reason
# ---------------------------------------------------------------------------

class TestDetectPartialReason:
    def test_env_from_verification_pytest_fail(self):
        entry = {
            "audit_id": "x",
            "verification": {
                "pytest_attempt_1": "FAIL: /usr/bin/python3 has no pytest module",
            },
        }
        assert _detect_partial_reason(entry) == "blocked_env"

    def test_env_from_wsl_in_recommendations(self):
        entry = {
            "audit_id": "x",
            "recommendations": ["WSL 上では pytest 実行不能"],
        }
        assert _detect_partial_reason(entry) == "blocked_env"

    def test_env_from_environment_keyword_in_findings(self):
        entry = {
            "audit_id": "x",
            "findings": ["テスト実行不能のため skip"],
        }
        assert _detect_partial_reason(entry) == "blocked_env"

    def test_missing_from_lack_of_evidence(self):
        entry = {
            "audit_id": "x",
            "findings": ["証跡が残存"],
        }
        assert _detect_partial_reason(entry) == "missing"

    def test_missing_default(self):
        entry = {"audit_id": "x"}
        assert _detect_partial_reason(entry) == "missing"

    def test_missing_from_test_perspective_fail(self):
        entry = {
            "audit_id": "x",
            "perspective_verdicts": {"6_test": "fail"},
        }
        assert _detect_partial_reason(entry) == "missing"


# ---------------------------------------------------------------------------
# _normalize_verdict
# ---------------------------------------------------------------------------

class TestNormalizeVerdict:
    def test_pass(self):
        v, es, cg, _ = _normalize_verdict("pass", {})
        assert v == "pass"
        assert es == "complete"
        assert cg == "open"

    def test_pass_with_concerns(self):
        v, es, cg, _ = _normalize_verdict("pass_with_concerns", {})
        assert v == "pass_with_concerns"
        assert es == "complete"
        assert cg == "open"

    def test_concerns_alias(self):
        v, es, cg, _ = _normalize_verdict("concerns", {})
        assert v == "pass_with_concerns"
        assert es == "complete"
        assert cg == "open"

    def test_fail(self):
        v, es, cg, _ = _normalize_verdict("fail", {})
        assert v == "fail"
        assert es == "missing"
        assert cg == "blocked"

    def test_partial_env(self, capsys):
        entry = {
            "audit_id": "t1",
            "verification": {"pytest": "FAIL: WSL issue"},
        }
        v, es, cg, reason = _normalize_verdict("partial", entry)
        assert v == "fail"
        assert es == "blocked_env"
        assert cg == "blocked"
        assert "partial→fail" in reason
        captured = capsys.readouterr()
        assert "partial verdict detected" in captured.err

    def test_partial_missing(self, capsys):
        entry = {"audit_id": "t2"}
        v, es, cg, reason = _normalize_verdict("partial", entry)
        assert v == "fail"
        assert es == "missing"
        assert cg == "blocked"
        assert "partial→fail" in reason

    def test_partial_failed_test(self, capsys):
        entry = {
            "audit_id": "t3",
            "perspective_verdicts": {"6_test": "fail"},
        }
        v, es, cg, reason = _normalize_verdict("partial", entry)
        assert v == "fail"
        assert es == "missing"
        assert cg == "blocked"

    def test_unknown_verdict(self, capsys):
        v, es, cg, reason = _normalize_verdict("weird_verdict", {"audit_id": "x"})
        assert v == "fail"
        assert es == "schema_unsupported"
        assert cg == "blocked"
        captured = capsys.readouterr()
        assert "unknown verdict" in captured.err


# ---------------------------------------------------------------------------
# _normalize_entry
# ---------------------------------------------------------------------------

class TestNormalizeEntry:
    def test_fields_populated(self):
        raw = {
            "audit_id": "kuroda_001",
            "target_id": "some_task",
            "verdict": "pass",
            "audited_at": "2026-05-10T09:00:00+09:00",
            "related_files": ["backend/a.py"],
            "commit_hash": "abc123",
            "log_path": "logs/foo.log",
        }
        out = _normalize_entry(raw, "queue/reports/kuroda.yaml", "reports", "reports")
        assert out["audit_id"] == "kuroda_001"
        assert out["verdict"] == "pass"
        assert out["evidence_state"] == "complete"
        assert out["completion_gate"] == "open"
        assert out["source_verdict"] == "pass"
        assert out["shogun_verified"] is False
        assert out["source_file"] == "queue/reports/kuroda.yaml"
        assert out["source_section"] == "reports"
        assert out["original_schema_type"] == "reports"

    def test_related_files_string_converted_to_list(self):
        raw = {
            "audit_id": "x",
            "verdict": "pass",
            "related_files": "single_file.py",
        }
        out = _normalize_entry(raw, "src.yaml", "reports", "reports")
        assert out["related_files"] == ["single_file.py"]

    def test_partial_env_pattern(self, capsys):
        raw = {
            "audit_id": "naomasa_new_001",
            "verdict": "partial",
            "verification": {"pytest_attempt_1": "FAIL: WSL UtilAcceptVsock accept4 failed 110"},
        }
        out = _normalize_entry(raw, "src.yaml", "new_project_audits", "new_project_audits")
        assert out["verdict"] == "fail"
        assert out["evidence_state"] == "blocked_env"
        assert out["completion_gate"] == "blocked"


# ---------------------------------------------------------------------------
# load_report_file — schema type tests
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path: Path, name: str, content: dict) -> Path:
    p = tmp_path / name
    p.write_text(yaml.dump(content, allow_unicode=True), encoding="utf-8")
    return p


class TestLoadReportFile:
    def test_reports_schema(self, tmp_path, capsys):
        data = {
            "reports": [
                {"audit_id": "r001", "target_id": "cmd_001", "verdict": "pass"},
            ]
        }
        path = _write_yaml(tmp_path, "test_report.yaml", data)
        entries = load_report_file(path)
        assert len(entries) == 1
        assert entries[0]["audit_id"] == "r001"
        assert entries[0]["original_schema_type"] == "reports"
        assert entries[0]["source_section"] == "reports"

    def test_new_project_audits_schema(self, tmp_path, capsys):
        data = {
            "new_project_audits": [
                {
                    "audit_id": "naomasa_new_001",
                    "target_id": "proj_a",
                    "verdict": "partial",
                    "verification": {"pytest_attempt_1": "FAIL: WSL error"},
                }
            ]
        }
        path = _write_yaml(tmp_path, "naomasa.yaml", data)
        entries = load_report_file(path)
        assert len(entries) == 1
        assert entries[0]["original_schema_type"] == "new_project_audits"
        assert entries[0]["verdict"] == "fail"
        assert entries[0]["evidence_state"] == "blocked_env"

    def test_phase_b_reaudits_schema(self, tmp_path, capsys):
        data = {
            "phase_b_reaudits": [
                {
                    "audit_id": "naomasa_reaudit_001",
                    "target_audit_id": "naomasa_008",
                    "target_id": "cmd_001",
                    "verdict": "pass",
                    "audit_passed": True,
                    "findings": [],
                    "recommendations": [],
                }
            ]
        }
        path = _write_yaml(tmp_path, "reaudit.yaml", data)
        entries = load_report_file(path)
        assert len(entries) == 1
        assert entries[0]["original_schema_type"] == "phase_b_reaudits"
        assert entries[0]["source_section"] == "phase_b_reaudits"
        assert entries[0]["verdict"] == "pass"

    def test_legacy_schema_warns(self, tmp_path, capsys):
        data = {
            "old_audits": [
                {"audit_id": "legacy_001", "target_id": "x", "verdict": "pass"}
            ]
        }
        path = _write_yaml(tmp_path, "legacy.yaml", data)
        entries = load_report_file(path)
        assert len(entries) == 1
        assert entries[0]["original_schema_type"] == "legacy"
        captured = capsys.readouterr()
        assert "legacy schema section" in captured.err

    def test_missing_file_warns(self, tmp_path, capsys):
        path = tmp_path / "nonexistent.yaml"
        entries = load_report_file(path)
        assert entries == []
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_all_sections_combined(self, tmp_path, capsys):
        data = {
            "reports": [
                {"audit_id": "r001", "target_id": "x", "verdict": "pass"},
            ],
            "new_project_audits": [
                {"audit_id": "np001", "target_id": "y", "verdict": "fail"},
            ],
            "phase_b_reaudits": [
                {"audit_id": "pb001", "target_id": "z", "verdict": "pass_with_concerns"},
            ],
        }
        path = _write_yaml(tmp_path, "multi.yaml", data)
        entries = load_report_file(path)
        assert len(entries) == 3
        ids = {e["audit_id"] for e in entries}
        assert ids == {"r001", "np001", "pb001"}


# ---------------------------------------------------------------------------
# partial mapping — 3 patterns
# ---------------------------------------------------------------------------

class TestPartialMapping:
    def test_pattern_environment_reason(self, tmp_path, capsys):
        """partial + environment reason → fail, blocked_env, blocked"""
        data = {
            "reports": [
                {
                    "audit_id": "env_partial",
                    "target_id": "task",
                    "verdict": "partial",
                    "verification": {
                        "pytest_attempt_1": "FAIL: no module named pytest",
                        "skip_count": "unknown (tests did not start)",
                    },
                }
            ]
        }
        path = _write_yaml(tmp_path, "r.yaml", data)
        entries = load_report_file(path)
        assert entries[0]["verdict"] == "fail"
        assert entries[0]["evidence_state"] == "blocked_env"
        assert entries[0]["completion_gate"] == "blocked"

    def test_pattern_failed_test(self, tmp_path, capsys):
        """partial + failed test → fail, missing, blocked"""
        data = {
            "reports": [
                {
                    "audit_id": "test_partial",
                    "target_id": "task",
                    "verdict": "partial",
                    "perspective_verdicts": {"6_test": "fail"},
                }
            ]
        }
        path = _write_yaml(tmp_path, "r.yaml", data)
        entries = load_report_file(path)
        assert entries[0]["verdict"] == "fail"
        assert entries[0]["evidence_state"] == "missing"
        assert entries[0]["completion_gate"] == "blocked"

    def test_pattern_missing_evidence(self, tmp_path, capsys):
        """partial + missing evidence → fail, missing, blocked"""
        data = {
            "reports": [
                {
                    "audit_id": "missing_partial",
                    "target_id": "task",
                    "verdict": "partial",
                    "findings": ["証跡が不足している"],
                }
            ]
        }
        path = _write_yaml(tmp_path, "r.yaml", data)
        entries = load_report_file(path)
        assert entries[0]["verdict"] == "fail"
        assert entries[0]["evidence_state"] == "missing"
        assert entries[0]["completion_gate"] == "blocked"


# ---------------------------------------------------------------------------
# normalize (integration)
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_multiple_files(self, tmp_path, capsys):
        data1 = {
            "reports": [{"audit_id": "a1", "target_id": "t1", "verdict": "pass"}]
        }
        data2 = {
            "reports": [{"audit_id": "a2", "target_id": "t2", "verdict": "fail"}]
        }
        p1 = _write_yaml(tmp_path, "r1.yaml", data1)
        p2 = _write_yaml(tmp_path, "r2.yaml", data2)
        entries = normalize([p1, p2])
        assert len(entries) == 2

    def test_missing_file_skipped(self, tmp_path, capsys):
        data1 = {
            "reports": [{"audit_id": "a1", "target_id": "t1", "verdict": "pass"}]
        }
        p1 = _write_yaml(tmp_path, "r1.yaml", data1)
        p2 = tmp_path / "nonexistent.yaml"
        entries = normalize([p1, p2])
        assert len(entries) == 1

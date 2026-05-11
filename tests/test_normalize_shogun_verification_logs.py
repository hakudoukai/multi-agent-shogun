"""Tests for normalize_shogun_verification_logs.py"""

import subprocess
import sys
from pathlib import Path

import yaml
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from normalize_shogun_verification_logs import (  # noqa: E402
    normalize,
    normalize_entry,
    payload_hash,
    redact_string,
    redact_value,
    stable_event_id,
)

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "normalize_shogun_verification_logs.py"


def _sample_entry(target="kuroda_001", verified_at="2026-05-10T06:42:22+00:00"):
    return {
        "target": target,
        "auditor_who": "kuroda",
        "verified_at": verified_at,
        "shogun_verified": True,
        "checks_passed": "4/6",
        "checks": {
            "codex_log_exists": True,
            "gemini_log_exists": False,
            "commit_hash_valid": True,
            "findings_specific": True,
            "timestamp_consistent": True,
            "related_files_exist": True,
        },
        "flags": [],
        "audit_entry_excerpt": {
            "audit_id": target,
            "target_id": "subtask_x",
            "verdict": "pass",
            "audited_at": "2026-05-10T15:40:00+09:00",
            "commit_hash": "abc1234",
        },
    }


def _write_log(path: Path, entries):
    path.write_text(
        yaml.safe_dump({"verifications": entries}, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# redact_string
# ---------------------------------------------------------------------------

class TestRedactString:
    def test_aws_key_redacted(self):
        out, matched = redact_string("AKIAABCDEFGHIJKLMNOP token")
        assert "AKIA" not in out
        assert "aws_key" in matched

    def test_openai_key_redacted(self):
        out, matched = redact_string("sk-abcdefghijklmnopqrstuvwxyz0123")
        assert "<REDACTED:openai_key>" in out
        assert "openai_key" in matched

    def test_absolute_home_redacted(self):
        out, matched = redact_string("see /home/user/projects/foo.py for detail")
        assert "/home/user" not in out
        assert "absolute_home" in matched

    def test_absolute_wsl_redacted(self):
        out, matched = redact_string("opens /mnt/c/Users/Me/dir")
        assert "/mnt/c/Users" not in out
        assert "absolute_wsl_c" in matched

    def test_clean_string_no_match(self):
        out, matched = redact_string("ordinary message with id=42")
        assert matched == []
        assert out == "ordinary message with id=42"


# ---------------------------------------------------------------------------
# stable_event_id / payload_hash
# ---------------------------------------------------------------------------

class TestEventId:
    def test_stable_for_same_inputs(self):
        a = stable_event_id("mainpc", "kuroda", "kuroda_001", "2026-05-10T06:42:22+00:00")
        b = stable_event_id("mainpc", "kuroda", "kuroda_001", "2026-05-10T06:42:22+00:00")
        assert a == b
        assert len(a) == 12

    def test_changes_with_source_pc(self):
        a = stable_event_id("mainpc", "kuroda", "kuroda_001", "ts")
        b = stable_event_id("secondpc", "kuroda", "kuroda_001", "ts")
        assert a != b


class TestPayloadHash:
    def test_stable_for_equal_payloads(self):
        a = payload_hash(_sample_entry())
        b = payload_hash(_sample_entry())
        assert a == b

    def test_changes_when_flags_differ(self):
        e1 = _sample_entry()
        e2 = _sample_entry()
        e2["flags"] = ["something"]
        assert payload_hash(e1) != payload_hash(e2)


# ---------------------------------------------------------------------------
# normalize_entry
# ---------------------------------------------------------------------------

class TestNormalizeEntry:
    def test_basic_canonical_fields(self):
        canonical = normalize_entry(_sample_entry(), "mainpc")
        assert canonical is not None
        for k in (
            "event_id",
            "source_pc",
            "target_id",
            "shogun_verified",
            "checks_passed",
            "verified_at",
            "payload_hash",
        ):
            assert k in canonical
        assert canonical["source_pc"] == "mainpc"
        assert canonical["shogun_verified"] is True
        assert canonical["checks_passed"] == "4/6"

    def test_redacts_absolute_path_in_flags(self):
        entry = _sample_entry()
        entry["flags"] = ["some related_files do not exist: ['/home/user/projects/x.ts']"]
        canonical = normalize_entry(entry, "mainpc")
        # /home/user/projects/... not present in serialized form
        assert "/home/user/projects" not in yaml.safe_dump(canonical, allow_unicode=True)
        assert "redaction_note" in canonical

    def test_skips_invalid_entry_shape(self):
        assert normalize_entry({}, "mainpc") is None
        assert normalize_entry("not a dict", "mainpc") is None  # type: ignore[arg-type]
        assert normalize_entry({"target": "x"}, "mainpc") is None  # missing verified_at


# ---------------------------------------------------------------------------
# normalize: merge + dedup + missing
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_merge_two_pcs(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        sc = tmp_path / "sc.yaml"
        _write_log(mc, [_sample_entry("kuroda_001"), _sample_entry("kuroda_002", "2026-05-10T07:00:00+00:00")])
        _write_log(sc, [_sample_entry("naomasa_001", "2026-05-10T08:00:00+00:00")])
        entries, missing, parse_err = normalize([("mainpc", mc), ("secondpc", sc)])
        assert len(entries) == 3
        assert missing == []
        assert parse_err is False

    def test_duplicate_event_id_skipped(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        sc = tmp_path / "sc.yaml"
        e = _sample_entry("kuroda_001", "2026-05-10T07:00:00+00:00")
        # exact same entry submitted twice from same writer = duplicate event_id
        _write_log(mc, [e, dict(e)])
        _write_log(sc, [])
        entries, missing, parse_err = normalize([("mainpc", mc), ("secondpc", sc)])
        assert len(entries) == 1
        assert parse_err is False

    def test_missing_one_pc_log_partial(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        sc = tmp_path / "sc_does_not_exist.yaml"
        _write_log(mc, [_sample_entry()])
        entries, missing, parse_err = normalize([("mainpc", mc), ("secondpc", sc)])
        assert len(entries) == 1
        assert "secondpc" in missing
        assert parse_err is False

    def test_parse_error_flagged(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        sc = tmp_path / "sc.yaml"
        mc.write_text("verifications: [\n  - not valid yaml: :")
        sc.write_text("verifications: []")
        entries, missing, parse_err = normalize([("mainpc", mc), ("secondpc", sc)])
        assert parse_err is True
        assert entries == []


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

class TestCli:
    def test_dry_run_partial_exit_zero(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        _write_log(mc, [_sample_entry()])
        out_path = tmp_path / "out.yaml"
        res = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--mainpc-log",
                str(mc),
                "--secondpc-log",
                str(tmp_path / "missing.yaml"),
                "--output",
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, res.stderr
        data = yaml.safe_load(out_path.read_text())
        assert data["total_events"] == 1
        assert data["missing_pc_logs"] == ["secondpc"]

    def test_strict_missing_returns_one(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        _write_log(mc, [_sample_entry()])
        out_path = tmp_path / "out.yaml"
        res = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--strict",
                "--mainpc-log",
                str(mc),
                "--secondpc-log",
                str(tmp_path / "missing.yaml"),
                "--output",
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 1, res.stderr

    def test_parse_error_returns_two(self, tmp_path: Path):
        mc = tmp_path / "mc.yaml"
        sc = tmp_path / "sc.yaml"
        mc.write_text("verifications: [oops: ::")
        _write_log(sc, [])
        res = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--dry-run",
                "--mainpc-log",
                str(mc),
                "--secondpc-log",
                str(sc),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 2, res.stderr

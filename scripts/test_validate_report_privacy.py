"""Tests for validate_report_privacy.py"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from validate_report_privacy import scan_text, scan_file  # noqa: E402

SCRIPT_PATH = Path(__file__).parent / "validate_report_privacy.py"


# ---------------------------------------------------------------------------
# scan_text — pattern detection
# ---------------------------------------------------------------------------

class TestScanText:
    def test_aws_key_detected(self):
        high, _warn = scan_text("AKIA0123456789ABCDEF embedded")
        assert any(v["pattern"] == "aws_key" for v in high)

    def test_openai_key_detected(self):
        high, _warn = scan_text("token=sk-AbCdEfGhIjKlMnOpQrStUv0123")
        assert any(v["pattern"] == "openai_key" for v in high)

    def test_anthropic_key_detected(self):
        high, _warn = scan_text("ANTHROPIC=sk-ant-AbCdEfGhIjKlMnOpQrStUv0123_xyz")
        assert any(v["pattern"] == "anthropic_key" for v in high)

    def test_github_token_detected(self):
        high, _warn = scan_text("export TOK=ghp_ABCDEFGHIJ0123456789klmn")
        assert any(v["pattern"] == "github_token" for v in high)

    def test_absolute_home_detected(self):
        high, _warn = scan_text("see /home/user/projects/foo.py for detail")
        assert any(v["pattern"] == "absolute_home" for v in high)

    def test_absolute_wsl_detected(self):
        high, _warn = scan_text("opens /mnt/c/Users/Me/file.txt")
        assert any(v["pattern"] == "absolute_wsl_c" for v in high)

    def test_clean_text_no_high(self):
        high, warn = scan_text("ordinary text without secrets")
        assert high == []
        # benign string may still produce no warns
        assert all(v["pattern"] != "absolute_home" for v in warn)

    def test_digit_id_warns_only(self):
        high, warn = scan_text("patient_no=1234567 in record")
        assert high == []
        assert any(v["pattern"] == "digit_id_candidate" for v in warn)

    def test_env_assignment_warns_only(self):
        high, warn = scan_text("MY_VAR=value\nOTHER=foo")
        assert high == []
        assert any(v["pattern"] == "env_assignment" for v in warn)


# ---------------------------------------------------------------------------
# scan_file
# ---------------------------------------------------------------------------

class TestScanFile:
    def test_clean_file(self, tmp_path: Path):
        p = tmp_path / "clean.yaml"
        p.write_text("a: 1\nb: hello\n")
        result = scan_file(p)
        assert result["status"] == "clean"
        assert result["high"] == []

    def test_violations_file(self, tmp_path: Path):
        p = tmp_path / "leaky.yaml"
        p.write_text("aws: AKIA0123456789ABCDEF\npath: /home/user/foo\n")
        result = scan_file(p)
        assert result["status"] == "violations"
        kinds = {v["pattern"] for v in result["high"]}
        assert "aws_key" in kinds
        assert "absolute_home" in kinds

    def test_missing_file(self, tmp_path: Path):
        p = tmp_path / "absent.yaml"
        result = scan_file(p)
        assert result["status"] == "missing"

    def test_log_path_wsl_detected(self, tmp_path: Path):
        p = tmp_path / "report.yaml"
        p.write_text("log_path: /mnt/c/Users/User/secret.log\n")
        result = scan_file(p)
        assert result["status"] == "violations"
        assert any(v["pattern"] == "absolute_wsl_c" for v in result["high"])


# ---------------------------------------------------------------------------
# CLI: exit codes
# ---------------------------------------------------------------------------

class TestCli:
    def _run(self, *args, capture_json=False):
        cmd = [sys.executable, str(SCRIPT_PATH), *args]
        if capture_json:
            cmd.insert(2, "--format")
            cmd.insert(3, "json")
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_clean_returns_zero(self, tmp_path: Path):
        p = tmp_path / "ok.yaml"
        p.write_text("hello: world\n")
        res = self._run(str(p))
        assert res.returncode == 0, res.stdout + res.stderr

    def test_high_violation_returns_one(self, tmp_path: Path):
        p = tmp_path / "bad.yaml"
        p.write_text("aws_key: AKIA0123456789ABCDEF\n")
        res = self._run(str(p))
        assert res.returncode == 1
        assert "aws_key" in res.stdout

    def test_warn_only_clean_without_strict(self, tmp_path: Path):
        p = tmp_path / "warn.yaml"
        p.write_text("patient_id: 1234567\n")
        res = self._run(str(p))
        assert res.returncode == 0

    def test_warn_only_fails_with_strict(self, tmp_path: Path):
        p = tmp_path / "warn.yaml"
        p.write_text("patient_id: 1234567\n")
        res = self._run("--strict", str(p))
        assert res.returncode == 1

    def test_json_output_format(self, tmp_path: Path):
        p = tmp_path / "ok.yaml"
        p.write_text("hello: world\n")
        res = self._run(str(p), capture_json=True)
        assert res.returncode == 0
        parsed = json.loads(res.stdout)
        assert isinstance(parsed, list)
        assert parsed[0]["status"] == "clean"

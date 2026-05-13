"""cmd_014 Phase 6 false-positive 根本治癒 regression test (Option C 二重防御).

設計書 ID:
  - docs/cmd004_cicd_pipeline_design.md §2-1 (= multi-agent repo lint workflow)
  - docs/cmd004_security_hardening_design.md §2-3 (= validate_report_privacy.py / HIGH_PATTERNS)

副医院長 handshake b4fac131 / 親 cmd_014 acceptance_criteria 整合。

検証対象 (= 二重防御):
  (A) validate_report_privacy.py scan_text — 空値 sample / YAML null 解釈 → HIGH 抑制
  (B) scripts/lint/check_secrets.sh — queue/reports/* path 全体 skip
  (C) workflow Phase 6 path passing — newline / NUL-safe + queue/reports filter (awk RS=\\0)

acceptance_criteria 整合:
  - queue/reports 空値抑制側 regression evidence (= HIGH 検出ゼロ)
  - queue/reports 外 本物機密検知温存側 regression evidence (= HIGH 検出 1 件以上)
  - workflow Phase 6 word-splitting 解消 (= null-terminated / awk RS=\\0)
  - queue/reports YAML 自体改変無 (= application code 改変禁)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_SECRETS = REPO_ROOT / "scripts" / "lint" / "check_secrets.sh"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cmd004-lint.yml"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_report_privacy import scan_text  # noqa: E402


# ---------------------------------------------------------------------------
# (A) scan_text — 空値 / YAML null sample suppression
# ---------------------------------------------------------------------------

class TestScanTextEmptyValueSuppression:
    """空値 sample (= None / "" / null / ~ / 空白) で HIGH 検出ゼロ verify."""

    @pytest.mark.parametrize(
        "empty",
        ["", "null", "NULL", "Null", "~", "None", "none", "   ", '""', "''"],
    )
    def test_empty_yaml_value_produces_no_high(self, empty):
        high, warn = scan_text(empty)
        assert high == [], f"empty value {empty!r} unexpectedly produced HIGH: {high}"
        assert warn == [], f"empty value {empty!r} unexpectedly produced WARN: {warn}"


# ---------------------------------------------------------------------------
# (A') scan_text — 本物機密検知温存 (= HIGH_PATTERNS 改変無 evidence)
# ---------------------------------------------------------------------------

class TestScanTextRealSecretRetention:
    """空値 filter 投入で本物機密検知が損なわれていない事を verify."""

    @pytest.mark.parametrize(
        "text,pattern",
        [
            ("AKIA0123456789ABCDEF", "aws_key"),
            ("token=sk-AbCdEfGhIjKlMnOpQrStUv0123", "openai_key"),
            ("sk-ant-AbCdEfGhIjKlMnOpQrStUv0123_xyz", "anthropic_key"),
            ("export TOK=ghp_ABCDEFGHIJ0123456789klmn", "github_token"),
            ("Authorization: Bearer abcdefghijklmnopqrstuv1234", "bearer_token"),
            ("xai-AbCdEfGhIjKlMnOpQrStUv0123_xyz", "xai_key"),
            ("glpat-AbCdEfGhIjKlMnOpQrStUv0123_xyz", "gitlab_pat"),
            ("see /home/secret_user/key.pem", "absolute_home"),
            ("path: /mnt/c/Users/Me/secret.txt", "absolute_wsl_c"),
        ],
    )
    def test_real_secret_still_detected(self, text, pattern):
        high, _ = scan_text(text)
        kinds = {h["pattern"] for h in high}
        assert pattern in kinds, f"expected {pattern} in {kinds} for {text!r}"


# ---------------------------------------------------------------------------
# (B) check_secrets.sh — queue/reports/* path skip
# ---------------------------------------------------------------------------

class TestCheckSecretsPathExclusion:
    """check_secrets.sh の case 文 skip pattern 適用 verify."""

    def _run(self, cwd: Path, *files: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(CHECK_SECRETS), *files],
            cwd=cwd,
            capture_output=True,
            text=True,
        )

    def test_queue_reports_yaml_with_infra_paths_is_skipped(self, tmp_path: Path):
        """queue/reports/ 配下の YAML が infra path (/home/*) を含んでも HIGH ゼロ."""
        qr = tmp_path / "queue" / "reports"
        qr.mkdir(parents=True)
        report = qr / "sample_report.yaml"
        report.write_text(
            textwrap.dedent(
                """\
                task_id: subtask_demo
                log_path: /home/hakudokai/projects/foo.log
                empty_value:
                null_value: null
                tilde_value: ~
                wsl_path: /mnt/c/Users/Me/data.txt
                """
            )
        )

        res = self._run(tmp_path, "queue/reports/sample_report.yaml")
        assert res.returncode == 0, f"stdout={res.stdout} stderr={res.stderr}"
        assert "[HIGH]" not in res.stdout, res.stdout
        assert "FAIL" not in res.stdout

    def test_nested_queue_reports_also_skipped(self, tmp_path: Path):
        """サブディレクトリに埋まった queue/reports/* も skip 対象 (= */queue/reports/*)."""
        nested = tmp_path / "wt" / "queue" / "reports"
        nested.mkdir(parents=True)
        (nested / "nested.yaml").write_text("path: /home/foo/bar\n")

        res = self._run(tmp_path, "wt/queue/reports/nested.yaml")
        assert res.returncode == 0
        assert "[HIGH]" not in res.stdout

    def test_real_secret_outside_queue_reports_still_caught(self, tmp_path: Path):
        """queue/reports/ 外の path で本物 API key が HIGH 検出される事を verify."""
        src = tmp_path / "src"
        src.mkdir()
        leak = src / "leaky.py"
        leak.write_text('AWS_KEY = "AKIA0123456789ABCDEF"\n')

        res = self._run(tmp_path, "src/leaky.py")
        assert res.returncode == 1, f"stdout={res.stdout} stderr={res.stderr}"
        assert "[HIGH]" in res.stdout
        assert "aws_key" in res.stdout

    def test_mixed_input_skips_reports_catches_real_secret(self, tmp_path: Path):
        """queue/reports/ と本物機密 file を混在 → 後者のみ HIGH (= dual side evidence)."""
        qr = tmp_path / "queue" / "reports"
        qr.mkdir(parents=True)
        (qr / "ok.yaml").write_text("note: /home/hakudokai/x\nval:\n")

        src = tmp_path / "src"
        src.mkdir()
        (src / "creds.py").write_text('TOKEN = "ghp_ABCDEFGHIJ0123456789klmn"\n')

        res = self._run(
            tmp_path, "queue/reports/ok.yaml", "src/creds.py"
        )
        assert res.returncode == 1
        assert "[HIGH] github_token" in res.stdout
        assert "queue/reports/ok.yaml" not in res.stdout  # 出力に登場しない (= skip)


# ---------------------------------------------------------------------------
# (C) workflow Phase 6 — null-terminated path passing + queue/reports filter
# ---------------------------------------------------------------------------

class TestWorkflowPathPassing:
    """AC: workflow Phase 6 path passing は word-splitting 解消必須."""

    def test_workflow_uses_null_terminated_path_list(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        assert "git diff -z" in content, "workflow must use git diff -z (NUL-terminated)"
        assert "xargs -0" in content, "workflow must use xargs -0 (NUL-terminated input)"

    def test_workflow_excludes_queue_reports_path(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        # awk RS=\0 ORS=\0 で queue/reports/ を filter
        assert "queue\\/reports\\/" in content or "queue/reports/" in content
        assert 'RS="\\0"' in content and 'ORS="\\0"' in content, (
            "workflow must use awk RS/ORS = \\0 for NUL-safe filtering"
        )

    def test_workflow_no_unquoted_word_split(self):
        """旧 `bash check_secrets.sh $files` (word-splitting hazard) を残さない."""
        content = WORKFLOW.read_text(encoding="utf-8")
        assert "check_secrets.sh $files" not in content, (
            "old word-splitting form `check_secrets.sh $files` must be removed"
        )

    def test_awk_filter_behavior_locally(self, tmp_path: Path):
        """workflow と同等 awk command が null-terminated input を正しく filter する事を verify."""
        if shutil.which("awk") is None:
            pytest.skip("awk not available")

        nul_input = tmp_path / "in.z"
        nul_input.write_bytes(
            b"queue/reports/foo.yaml\0"
            b"scripts/bar with space.sh\0"
            b"sub/queue/reports/baz.yaml\0"
            b"docs/qux.md\0"
        )
        nul_output = tmp_path / "out.z"

        # workflow 内 awk と同等 command
        with open(nul_input, "rb") as fi, open(nul_output, "wb") as fo:
            subprocess.run(
                [
                    "awk",
                    'BEGIN { RS="\\0"; ORS="\\0" } '
                    "!/^queue\\/reports\\// && !/\\/queue\\/reports\\//",
                ],
                stdin=fi,
                stdout=fo,
                check=True,
            )

        records = [r for r in nul_output.read_bytes().split(b"\x00") if r]
        decoded = [r.decode("utf-8") for r in records]
        assert decoded == ["scripts/bar with space.sh", "docs/qux.md"], decoded

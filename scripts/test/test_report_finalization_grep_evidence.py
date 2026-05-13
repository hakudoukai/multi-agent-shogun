"""Tests for scripts/lint/check_report_finalization.sh — scoped grep + allowlist + self verify.

Scope (= task YAML AC5):
- scoped grep: only the four completion-claim sections are walked
  (commit_history, push_plan, acceptance_criteria, next_actions).
- allowlist: status taxonomy enum + lifecycle meta field + 履歴 cross-reference are exempt.
- self-verify: this task's final report yaml is itself scanned and must pass.

Refs:
- scripts/lint/check_report_finalization.sh
- scripts/lint/report_finalization_allowlist.txt
- docs/report_finalization_norm.md §6 自身実証
- queue/tasks/subtask_cmd020_scope_contamination_prevention_v2.yaml AC5
"""
from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "lint" / "check_report_finalization.sh"
ALLOWLIST = REPO_ROOT / "scripts" / "lint" / "report_finalization_allowlist.txt"
NORM_DOC = REPO_ROOT / "docs" / "report_finalization_norm.md"
SELF_REPORT = (
    REPO_ROOT
    / "queue"
    / "reports"
    / "ashigaru2_subtask_cmd020_scope_contamination_v2_report.yaml"
)


def _run(file: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["bash", str(SCRIPT), str(file)], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_script_and_allowlist_and_norm_doc_present() -> None:
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    assert ALLOWLIST.is_file(), f"missing {ALLOWLIST}"
    assert NORM_DOC.is_file(), f"missing {NORM_DOC}"
    mode = SCRIPT.stat().st_mode
    assert mode & 0o111, f"script not executable (mode={oct(mode)})"


def test_clean_completion_claim_passes(tmp_path: Path) -> None:
    f = tmp_path / "clean.yaml"
    f.write_text(
        textwrap.dedent(
            """\
            report_id: x
            verdict: pass_with_concerns
            commit_history:
              - sha: e681820
              - sha: 2d97598
            push_plan:
              status: completed
              pushed_sha: [e681820, 2d97598]
            acceptance_criteria:
              AC0: pass
              AC1: pass
            next_actions:
              - karo inbox 完遂報告
            """
        ),
        encoding="utf-8",
    )
    rc, _out, err = _run(f)
    assert rc == 0, f"clean report should pass; stderr={err}"


def test_forbidden_tokens_in_completion_claim_fail(tmp_path: Path) -> None:
    f = tmp_path / "dirty.yaml"
    f.write_text(
        textwrap.dedent(
            """\
            report_id: x
            commit_history:
              - sha: TBD_SHA_3
                message: pending
            push_plan:
              status: pending_user_sashihai
            acceptance_criteria:
              AC5: pending
            next_actions:
              - push 予定
            """
        ),
        encoding="utf-8",
    )
    rc, _out, err = _run(f)
    assert rc == 1, "dirty report should fail"
    # Each of the 5 forbidden tokens should produce a FAIL line
    for token in ("TBD_SHA_3", "message: pending", "pending_user_sashihai", "AC5: pending", "予定"):
        assert token in err, f"expected {token!r} in stderr; got: {err}"


def test_historical_section_with_forbidden_tokens_is_ignored(tmp_path: Path) -> None:
    """Tokens appearing outside the four scoped sections must NOT fail the report."""
    f = tmp_path / "history.yaml"
    f.write_text(
        textwrap.dedent(
            """\
            report_id: x
            commit_history:
              - sha: e681820
            push_plan:
              status: completed
            acceptance_criteria:
              AC0: pass
            next_actions:
              - karo inbox 完遂報告
            revise_history:
              - cycle1: pending
              - cycle2: TBD
              - cycle3: planned 予定 in_progress
            fail_evidence:
              - prior_state: pending_user_sashihai
            """
        ),
        encoding="utf-8",
    )
    rc, _out, err = _run(f)
    assert rc == 0, f"historical section tokens must be ignored; stderr={err}"


def test_allowlist_status_taxonomy_exempts_enum_value(tmp_path: Path) -> None:
    """status taxonomy enums embedded inside completion-claim sections are exempt."""
    f = tmp_path / "enums.yaml"
    f.write_text(
        textwrap.dedent(
            """\
            report_id: x
            commit_history:
              - sha: e681820
                verdict: pass_with_conditions
                completion_gate: open_with_concerns
            push_plan:
              status: completed
            acceptance_criteria:
              AC0: pass
              AC1:
                verdict: pass_with_concerns
                audit_gate_status: awaiting_naomasa_codex_review
            next_actions:
              - karo inbox 完遂報告
            """
        ),
        encoding="utf-8",
    )
    rc, _out, err = _run(f)
    assert rc == 0, f"allowlist should exempt status enums; stderr={err}"


def test_self_verify_v2_final_report_passes_when_present() -> None:
    """Self-verify: this task's final report yaml must itself pass the scoped grep.

    When commit_5 (= the final report yaml + pytest log) has not yet been
    written this test is skipped — the AC5 self-verify is enforced at the
    final commit step.
    """
    if not SELF_REPORT.exists():
        pytest.skip(
            "ashigaru2 v2 final report not yet present (= commit_5 pending in same task);"
            " self-verify will be exercised when the final report yaml is committed"
        )
    rc, _out, err = _run(SELF_REPORT)
    assert rc == 0, (
        f"self-verify failed: ashigaru2 v2 final report contains unfinalized tokens"
        f" in completion-claim sections.\nstderr={err}"
    )


def test_norm_doc_documents_scoped_sections_and_forbidden_tokens() -> None:
    doc = NORM_DOC.read_text(encoding="utf-8")
    for section in ("commit_history", "push_plan", "acceptance_criteria", "next_actions"):
        assert section in doc, f"norm doc must enumerate completion-claim section {section}"
    for token in ("TBD", "pending", "予定", "planned", "in_progress"):
        assert token in doc, f"norm doc must document forbidden token {token}"
    # Allowlist categories are documented
    assert "allowlist" in doc.lower() or "allow-list" in doc.lower()
    assert "status taxonomy" in doc or "taxonomy enum" in doc

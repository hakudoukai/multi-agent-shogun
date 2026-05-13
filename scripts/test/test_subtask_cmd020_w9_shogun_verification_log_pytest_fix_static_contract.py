"""Static source-contract tests for cmd_020 W9 shogun_verification_log pytest fix.

Target source files:
  - scripts/regenerate_dashboard.py     (= compute_child_machine_state w9_batch / w9_stage blocked field)
  - tests/test_regenerate_dashboard.py  (= status-classification 反転 test 2 件)
  - queue/reports/ashigaru1_w9_pytest_fix_evidence.yaml (= AC7/AC8 evidence yaml)

Test nature: file regex grep + structural anchor check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。

Test purpose: cmd_020 W9 pytest fix の status-classification 変更 path 採択を
contract 化し、後続 cycle で synthetic shogun verification entry 投入 / false-green
化 / 並行 rendering path への drift を機械検出する。

Test names:
  1. test_compute_child_machine_state_w9_batch_blocked_field_present
  2. test_compute_child_machine_state_w9_stage_blocked_field_present
  3. test_test_regenerate_dashboard_w9_assertions_inverted_to_truth
  4. test_evidence_yaml_synthetic_zero_marker_present
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REGENERATE_DASHBOARD_PY = REPO_ROOT / "scripts" / "regenerate_dashboard.py"
TEST_REGENERATE_DASHBOARD_PY = REPO_ROOT / "tests" / "test_regenerate_dashboard.py"
EVIDENCE_YAML = (
    REPO_ROOT / "queue" / "reports" / "ashigaru1_w9_pytest_fix_evidence.yaml"
)


@pytest.fixture(scope="module")
def regenerate_dashboard_text() -> str:
    assert REGENERATE_DASHBOARD_PY.is_file(), (
        f"regenerate_dashboard.py missing: {REGENERATE_DASHBOARD_PY}"
    )
    return REGENERATE_DASHBOARD_PY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def test_regenerate_dashboard_text() -> str:
    assert TEST_REGENERATE_DASHBOARD_PY.is_file(), (
        f"test_regenerate_dashboard.py missing: {TEST_REGENERATE_DASHBOARD_PY}"
    )
    return TEST_REGENERATE_DASHBOARD_PY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def evidence_yaml_text() -> str:
    assert EVIDENCE_YAML.is_file(), f"evidence yaml missing: {EVIDENCE_YAML}"
    return EVIDENCE_YAML.read_text(encoding="utf-8")


def test_compute_child_machine_state_w9_batch_blocked_field_present(
    regenerate_dashboard_text: str,
) -> None:
    """w9_batch 分岐に blocked / blocked_reason field を返す return dict があり、
    sv is None かつ base_pct == 0.0 で blocked=True を立てる logic anchor が存在する。
    """
    # w9_batch 分岐 anchor
    assert re.search(
        r'if\s+kind\s*==\s*[\'"]w9_batch[\'"]\s*:', regenerate_dashboard_text
    ), "compute_child_machine_state w9_batch 分岐が消失"
    # blocked field 名 anchor
    assert re.search(
        r'"blocked"\s*:\s*blocked', regenerate_dashboard_text
    ), 'w9_batch return dict に "blocked": blocked field が無い'
    # blocked_reason 文字列 anchor
    assert "shogun_verify_pending_no_w9_task_or_ledger_entry" in regenerate_dashboard_text, (
        "blocked_reason 文字列 'shogun_verify_pending_no_w9_task_or_ledger_entry' が無い"
    )
    # blocked 判定式 anchor (= sv is None and base_pct == 0.0)
    assert re.search(
        r"blocked\s*=\s*\(sv\s+is\s+None\)\s*and\s*\(base_pct\s*==\s*0\.0\)",
        regenerate_dashboard_text,
    ), "w9_batch blocked 判定式 (sv is None) and (base_pct == 0.0) が無い"
    # missing 分岐側にも blocked field anchor (= w9_batch_missing も blocked=True)
    assert re.search(
        r'"kind"\s*:\s*"w9_batch_missing"', regenerate_dashboard_text
    ), "w9_batch_missing 分岐 anchor が消失"


def test_compute_child_machine_state_w9_stage_blocked_field_present(
    regenerate_dashboard_text: str,
) -> None:
    """w9_stage 分岐にも同等の blocked field 装備 anchor が存在する。"""
    assert re.search(
        r'if\s+kind\s*==\s*[\'"]w9_stage[\'"]\s*:', regenerate_dashboard_text
    ), "compute_child_machine_state w9_stage 分岐が消失"
    # w9_stage_missing 分岐に blocked anchor
    assert re.search(
        r'"kind"\s*:\s*"w9_stage_missing"', regenerate_dashboard_text
    ), "w9_stage_missing 分岐 anchor が消失"
    # w9_stage_missing 直後に blocked: True を立てる
    pattern = re.compile(
        r'"kind"\s*:\s*"w9_stage_missing"[^}]*"blocked"\s*:\s*True', re.DOTALL
    )
    assert pattern.search(regenerate_dashboard_text), (
        "w9_stage_missing return dict に blocked: True が無い"
    )


def test_test_regenerate_dashboard_w9_assertions_inverted_to_truth(
    test_regenerate_dashboard_text: str,
) -> None:
    """W9 batch 系 test の assertion が真値固定 (= matched_ids == [] / blocked) に
    反転されている事を contract lock。逆方向 drift (= 旧 cycle13 期待 復活) を機械検出。
    """
    # test_real_shogun_log_w9_batch1_to_batch6_all_matched: matched_ids == []
    test1_pattern = re.compile(
        r"def\s+test_real_shogun_log_w9_batch1_to_batch6_all_matched.*?"
        r"assert\s+matched_ids\s*==\s*\[\]",
        re.DOTALL,
    )
    assert test1_pattern.search(test_regenerate_dashboard_text), (
        "test_real_shogun_log_w9_batch1_to_batch6_all_matched が真値 (= matched_ids == []) を assert していない"
    )
    # 旧期待 [C-15-B1..C-15-B6] が assertion 側に残存していない事 (= comment は許容)
    legacy_assert = re.search(
        r"assert\s+matched_ids\s*==\s*\[\s*[\"\']C-15-B1[\"\']",
        test_regenerate_dashboard_text,
    )
    assert legacy_assert is None, (
        "旧 cycle13 期待 (= matched_ids == [C-15-B1..]) が test assertion に残存している (= drift)"
    )

    # test_w9_stage_a_b1_b6_all_green_in_real_state: blocked_ids == ids
    test2_pattern = re.compile(
        r"def\s+test_w9_stage_a_b1_b6_all_green_in_real_state.*?"
        r"assert\s+blocked_ids\s*==\s*ids",
        re.DOTALL,
    )
    assert test2_pattern.search(test_regenerate_dashboard_text), (
        "test_w9_stage_a_b1_b6_all_green_in_real_state が真値 (= blocked_ids == ids) を assert していない"
    )


def test_evidence_yaml_synthetic_zero_marker_present(
    evidence_yaml_text: str,
) -> None:
    """ashigaru1_w9_pytest_fix_evidence.yaml に synthetic 投入 0 件 evidence
    (before/after sha256 同値 + diff_byte_count: 0) が記録されている。
    """
    # synthetic_injection_zero_evidence section anchor
    assert "synthetic_injection_zero_evidence:" in evidence_yaml_text, (
        "evidence yaml に synthetic_injection_zero_evidence section が無い"
    )
    # AC8 policy 文字列
    assert (
        "AC8 synthetic shogun verification entries 投入 0 件" in evidence_yaml_text
    ), "evidence yaml に AC8 policy 文字列が無い"
    # 主 source (= shogun_verification_mainpc_log) の before/after sha256 同値 anchor
    main_log_section = re.search(
        r"shogun_verification_mainpc_log_diff:(.+?)active_verify_queue_candidate_log_diff:",
        evidence_yaml_text,
        re.DOTALL,
    )
    assert main_log_section is not None, (
        "evidence yaml に shogun_verification_mainpc_log_diff section が無い"
    )
    section_text = main_log_section.group(1)
    sha256_values = re.findall(r"sha256:\s*\"([0-9a-f]{64})\"", section_text)
    assert len(sha256_values) == 2, (
        f"shogun_verification_mainpc_log_diff section に sha256 (before/after) が "
        f"2 件揃っていない (検出 {len(sha256_values)} 件)"
    )
    assert sha256_values[0] == sha256_values[1], (
        f"shogun_verification_mainpc_log の before/after sha256 が不一致 "
        f"(= synthetic 投入疑義): before={sha256_values[0]} after={sha256_values[1]}"
    )
    # diff_byte_count: 0 anchor
    assert re.search(
        r"shogun_verification_mainpc_log_diff:.*?diff_byte_count:\s*0",
        evidence_yaml_text,
        re.DOTALL,
    ), "shogun_verification_mainpc_log_diff に diff_byte_count: 0 が無い"

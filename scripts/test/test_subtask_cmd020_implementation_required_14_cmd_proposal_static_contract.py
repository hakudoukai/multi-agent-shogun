"""Static source-contract tests for cmd_020 implementation_required 14 件 cmd 上申準備提案.

Target: docs/cmd020_implementation_required_14_cmd_proposal.md
       queue/reports/ashigaru6_subtask_cmd020_implementation_required_14_cmd_proposal_inventory.yaml

Test nature: markdown/yaml grep + structural check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。

Pre-audit findings (= naomasa msg_20260513_134905、pass_with_concerns):
 - finding medium 1: deliverable は docs/report only、queue task assignment NG、Supabase status edit NG
 - finding medium 2: C-15-B7 / C-V29 / C-V30 を 14 件と collapse しない
本 test suite は両 finding に対する machine guard 役割を兼ねる。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSAL_DOC = REPO_ROOT / "docs" / "cmd020_implementation_required_14_cmd_proposal.md"
INVENTORY_YAML = (
    REPO_ROOT
    / "queue"
    / "reports"
    / "ashigaru6_subtask_cmd020_implementation_required_14_cmd_proposal_inventory.yaml"
)

FOURTEEN_CANDIDATES = [
    "C-V21-W9TENSU",
    "C-V22-W9SPIDCHK",
    "C-V31-W11CHOREI",
    "C-V33-W12CLNUI",
    "C-V34-W13VISIT",
    "C-V35-W13RTE",
    "C-V36-W14PAY",
    "C-V37-W14CTI",
    "C-V38-W14LINE",
    "C-V39-W14YOSHI3",
    "C-V41-W15DEP",
    "C-V42-W15MAN",
    "C-V43-W16MAT",
    "C-V44-W17JINJI",
]

OUT_OF_SCOPE_IDS = ["C-15-B7", "C-V29-W11DDA", "C-V30-W11DDB"]


@pytest.fixture(scope="module")
def proposal_text() -> str:
    assert PROPOSAL_DOC.is_file(), f"Proposal doc missing: {PROPOSAL_DOC}"
    return PROPOSAL_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def inventory_text() -> str:
    assert INVENTORY_YAML.is_file(), f"Inventory yaml missing: {INVENTORY_YAML}"
    return INVENTORY_YAML.read_text(encoding="utf-8")


def test_14_candidates_full_coverage(proposal_text: str, inventory_text: str) -> None:
    """14 candidate 全 ID が proposal doc + inventory yaml 双方に anchor として存在する。"""
    missing_proposal = [c for c in FOURTEEN_CANDIDATES if c not in proposal_text]
    assert not missing_proposal, (
        f"proposal doc に 14 candidate のうち欠落: {missing_proposal}"
    )

    missing_inventory = [c for c in FOURTEEN_CANDIDATES if c not in inventory_text]
    assert not missing_inventory, (
        f"inventory yaml に 14 candidate のうち欠落: {missing_inventory}"
    )

    assert "14" in proposal_text, "proposal doc に '14' anchor (= 件数明示) が無い"


def test_out_of_scope_boundary_explicit(
    proposal_text: str, inventory_text: str
) -> None:
    """直政 pre_audit finding medium 2 整合: C-15-B7 / C-V29 / C-V30 を 14 件と
    collapse しない境界明示が proposal doc + inventory yaml 双方に存在する。
    """
    for oos in OUT_OF_SCOPE_IDS:
        assert oos in proposal_text, (
            f"proposal doc に out-of-scope 境界 anchor '{oos}' が無い "
            f"(= 直政 pre_audit finding medium 2 違反 risk)"
        )
        assert oos in inventory_text, (
            f"inventory yaml に out-of-scope 境界 anchor '{oos}' が無い "
            f"(= 直政 pre_audit finding medium 2 違反 risk)"
        )

    boundary_keywords = ["out-of-scope", "out_of_scope_boundary"]
    boundary_hit = any(kw in proposal_text or kw in inventory_text for kw in boundary_keywords)
    assert boundary_hit, (
        "proposal doc / inventory yaml に 'out-of-scope' / 'out_of_scope_boundary' "
        "section anchor が無い (= 境界明示の構造 anchor 必要)"
    )


def test_docs_only_deliverable_nature(
    proposal_text: str, inventory_text: str
) -> None:
    """直政 pre_audit finding medium 1 整合: deliverable は docs/report only、
    queue task assignment NG、Supabase status edit NG の明示が両ファイルに存在する。
    """
    forbidden_anchors = [
        "queue/tasks/",
        "Supabase",
    ]
    proposal_forbidden_section = re.search(
        r"forbidden_side_effects|厳禁|範囲外", proposal_text
    )
    assert proposal_forbidden_section, (
        "proposal doc に forbidden_side_effects / 厳禁 / 範囲外 anchor が無い"
    )

    inventory_forbidden_section = re.search(
        r"forbidden_side_effects", inventory_text
    )
    assert inventory_forbidden_section, (
        "inventory yaml に forbidden_side_effects section が無い "
        "(= 直政 pre_audit finding medium 1 違反 risk)"
    )

    for anchor in forbidden_anchors:
        assert anchor in inventory_text, (
            f"inventory yaml に '{anchor}' 言及 anchor が無い "
            f"(= queue/Supabase 不変宣言の証跡欠落)"
        )

    docs_only_pattern = re.compile(r"docs/report\s*ONLY|docs/report\s*only")
    assert docs_only_pattern.search(proposal_text), (
        "proposal doc に 'docs/report ONLY' 明示が無い"
    )
    assert docs_only_pattern.search(inventory_text), (
        "inventory yaml に 'docs/report ONLY' 明示が無い"
    )


def test_per_cmd_acceptance_criteria_structure(proposal_text: str) -> None:
    """各 cmd 提案に (a) acceptance_criteria (b) target_file (c) test plan
    (d) ashigaru 配分案 (e) bloom level の 5 要素が含まれる構造を持つ。
    """
    required_sections = [
        "(a) acceptance_criteria",
        "(b) target_file",
        "(c) test plan",
        "(d) ashigaru 配分案",
        "(e) bloom level",
    ]
    for section in required_sections:
        count = proposal_text.count(section)
        assert count >= 9, (
            f"proposal doc 内 '{section}' anchor が {count} 件、"
            "9 cmd 各々で記載要 (= 9 件以上必要)"
        )

    cmd_anchors = ["cmd_021", "cmd_022", "cmd_023", "cmd_024", "cmd_025",
                   "cmd_026", "cmd_027", "cmd_028", "cmd_029"]
    missing_cmd = [c for c in cmd_anchors if c not in proposal_text]
    assert not missing_cmd, f"提案 cmd 番号 anchor 欠落: {missing_cmd}"

    bloom_levels = re.findall(r"\*\*L[3-5]\*\*", proposal_text)
    assert len(bloom_levels) >= 9, (
        f"bloom level (= **L3** / **L4** / **L5**) anchor が {len(bloom_levels)} 件、"
        "9 cmd 各々 bloom level 記載要 (= 9 件以上必要)"
    )


def test_design_doc_charter_reference(proposal_text: str) -> None:
    """design doc 正本 + Charter v0.1 §15 reference anchor が proposal doc に存在する。"""
    required_refs = [
        "naomasa_sc_audit_phase2_status_green_path_20260512.yaml",
        "shogun_orchestration_charter_v0.1.md",
        "1 Issue = 1 Branch = 1 PR",
        "unverified_inventory_20260512.yaml",
    ]
    missing = [r for r in required_refs if r not in proposal_text]
    assert not missing, f"design doc / Charter reference anchor 欠落: {missing}"

    pre_audit_pattern = re.compile(r"pre[_-]audit|pre_audit")
    assert pre_audit_pattern.search(proposal_text), (
        "proposal doc に pre_audit reference anchor が無い"
    )

    assert "msg_20260513_134905" in proposal_text, (
        "proposal doc に 直政 pre_audit msg id (= msg_20260513_134905) anchor が無い"
    )


def test_no_tbd_in_inventory_grep_evidence(inventory_text: str) -> None:
    """直政 post_audit finding severity high 9_doc + medium 6_test 整合 machine guard:
    inventory yaml の existing_artifacts_grep field 内に TBD / need verify placeholder が
    残存しない (= AC0 evidence completeness、結果 hits 全件確定値で記述)。

    本 test は revision_v2 (= 2026-05-13T17:00) で追加。直政 finding 6_test の指摘
    『静的 test は構造的 anchor を見るのみで TBD 残存を検出しない』へ machine guard で応答。

    検査範囲: 'hits:' 行に対する TBD / 'need verify' 文字列の検出のみ。
    inventory metadata 内の改修記録 (= revision_v2 / impact_assessment 等)
    は対象外 (= 改修履歴は事象記述に必要、guard 対象外)。
    """
    tbd_pattern = re.compile(
        r'^\s*hits:\s*.*(?:TBD|need\s+verify)', re.MULTILINE | re.IGNORECASE
    )
    matches = tbd_pattern.findall(inventory_text)
    assert not matches, (
        f"inventory yaml の existing_artifacts_grep hits field に "
        f"TBD / need verify placeholder が {len(matches)} 件残存 "
        f"(= 直政 post_audit finding 9_doc 違反 risk)。"
        f"残存例: {matches[:3]}"
    )

    grep_field_pattern = re.compile(r"existing_artifacts_grep:", re.MULTILINE)
    assert grep_field_pattern.search(inventory_text), (
        "inventory yaml に existing_artifacts_grep field 構造 anchor が無い "
        "(= 本 test の検査 scope 前提崩壊)"
    )

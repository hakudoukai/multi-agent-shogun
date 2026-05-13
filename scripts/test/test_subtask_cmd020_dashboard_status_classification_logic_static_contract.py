"""Static source-contract tests for dashboard status classification logic.

Target: docs/dashboard_status_classification_logic.md
        docs/dashboard_layer_c_function.md (= cross-layer reference anchor)
        docs/dashboard_layer_d_zunou.md (= cross-layer reference anchor)
        scripts/regenerate_dashboard.py (= existing constants reference)

Test nature: markdown grep + Python constant existence + structural anchor check
(= 静的 source-contract、network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。

naomasa pre_audit msg_20260513_134905 concerns 整合:
  - "Layer C/D render edits could conflict with existing LAYER_CHILDREN ..."
  - "Require focused static tests against existing constants/functions rather than
     a new parallel rendering path."
  → 本 test は既存 constants (= PROGRESS_COLOR_TIERS / STATUS_STAGE_PCT) の文字列が
    canonical doc 内に参照 anchor として存在する事を assert し、parallel rendering
    path 起案を機械検出 (= 並行 PROGRESS_COLOR_TIERS table 重複起案を禁ずる).

Test names:
  1. test_classification_doc_2_axis_section_present
  2. test_classification_doc_pass_with_concerns_yellow_rule
  3. test_classification_doc_audited_blocked_12_items_listed
  4. test_classification_doc_references_existing_constants_no_duplicate_table
  5. test_layer_c_d_cross_layer_reference_anchor_present
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLASSIFICATION_DOC = REPO_ROOT / "docs" / "dashboard_status_classification_logic.md"
LAYER_C_DOC = REPO_ROOT / "docs" / "dashboard_layer_c_function.md"
LAYER_D_DOC = REPO_ROOT / "docs" / "dashboard_layer_d_zunou.md"
REGENERATE_DASHBOARD_PY = REPO_ROOT / "scripts" / "regenerate_dashboard.py"

AUDITED_BLOCKED_12_IDS = [
    "C-15-A",
    "C-15-B2",
    "C-15-B4",
    "C-15-B6",
    "C-V21-W9TENSU",
    "C-V29-W11DDA",
    "C-V31-W11CHOREI",
    "C-V34-W13VISIT",
    "C-V36-W14PAY",
    "C-V38-W14LINE",
    "C-V41-W15DEP",
    "C-V43-W16MAT",
]

THREE_CLASSIFICATIONS = ["implementation_required", "monitor", "manifest_pending"]


@pytest.fixture(scope="module")
def classification_doc_text() -> str:
    assert CLASSIFICATION_DOC.is_file(), (
        f"classification logic doc missing: {CLASSIFICATION_DOC}"
    )
    return CLASSIFICATION_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def layer_c_text() -> str:
    assert LAYER_C_DOC.is_file(), f"Layer C doc missing: {LAYER_C_DOC}"
    return LAYER_C_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def layer_d_text() -> str:
    assert LAYER_D_DOC.is_file(), f"Layer D doc missing: {LAYER_D_DOC}"
    return LAYER_D_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def regenerate_dashboard_text() -> str:
    assert REGENERATE_DASHBOARD_PY.is_file(), (
        f"regenerate_dashboard.py missing: {REGENERATE_DASHBOARD_PY}"
    )
    return REGENERATE_DASHBOARD_PY.read_text(encoding="utf-8")


def test_classification_doc_2_axis_section_present(classification_doc_text: str) -> None:
    """§2 2 軸 直交モデル (= Axis A progress-percent + Axis B task-state) section が存在。"""
    assert re.search(r"^##\s+2\.[^\n]*2\s*軸", classification_doc_text, re.MULTILINE), (
        "classification doc に '## 2. ... 2 軸 ...' section anchor が無い"
    )
    assert re.search(r"Axis\s*A", classification_doc_text), (
        "classification doc に 'Axis A' anchor が無い (= progress-percent axis 不在)"
    )
    assert re.search(r"Axis\s*B", classification_doc_text), (
        "classification doc に 'Axis B' anchor が無い (= task-state axis 不在)"
    )
    assert re.search(r"直交", classification_doc_text), (
        "classification doc に '直交' anchor が無い (= 2 軸独立 規範欠落)"
    )
    for classification in THREE_CLASSIFICATIONS:
        assert classification in classification_doc_text, (
            f"classification doc に 3 分類 '{classification}' anchor が無い"
        )
    for color in ("red", "yellow", "orange", "green"):
        assert color in classification_doc_text, (
            f"classification doc に 4 段階 color '{color}' anchor が無い"
        )


def test_classification_doc_pass_with_concerns_yellow_rule(
    classification_doc_text: str,
) -> None:
    """§3 pass_with_concerns visual rule (= green ではなく yellow conditional) が存在。"""
    assert re.search(r"^##\s+3\.[^\n]*pass_with_concerns", classification_doc_text, re.MULTILINE), (
        "classification doc に '## 3. ... pass_with_concerns ...' section anchor が無い"
    )
    assert "pass_with_concerns" in classification_doc_text, (
        "classification doc に 'pass_with_concerns' 文字列が無い"
    )
    assert re.search(r"yellow\s*conditional", classification_doc_text, re.IGNORECASE), (
        "classification doc に 'yellow conditional' anchor が無い (= visual rule 名称欠落)"
    )
    assert re.search(r"green\s*ではなく|≠\s*green|not\s+green", classification_doc_text), (
        "classification doc に 'green ではなく' / '≠ green' 規範 anchor が無い"
    )
    # 75 score reference (verdict_based_score_mapping 既装備整合)
    assert re.search(r"\b75\b", classification_doc_text), (
        "classification doc に '75' score anchor が無い (= 既装備 verdict_based_score_mapping 整合 reference 欠落)"
    )


def test_classification_doc_audited_blocked_12_items_listed(
    classification_doc_text: str,
) -> None:
    """§4 audited-blocked 12 件 status 整合 table に 12 件全件 id が存在 + 件数整合 (4+7+1=12)。"""
    assert re.search(r"^##\s+4\.[^\n]*audited[- ]?blocked", classification_doc_text, re.MULTILINE), (
        "classification doc に '## 4. ... audited-blocked ...' section anchor が無い"
    )
    missing_ids = [cid for cid in AUDITED_BLOCKED_12_IDS if cid not in classification_doc_text]
    assert not missing_ids, (
        f"classification doc に audited-blocked 12 件 id が欠落: {missing_ids}"
    )
    # 件数 anchor 整合: 4 (manifest_pending) + 7 (implementation_required) + 1 (monitor) = 12
    assert re.search(r"4\s*\+\s*7\s*\+\s*1\s*=\s*\*?\*?12", classification_doc_text), (
        "classification doc §4.2 に '4 + 7 + 1 = 12' 件数整合式 anchor が無い"
    )
    # source-of-truth audit report reference
    assert re.search(
        r"naomasa_unverified_audit_batch1_20260512",
        classification_doc_text,
    ), (
        "classification doc に '12 件 audit verdict 原本' (naomasa_unverified_audit_batch1_20260512) reference が無い"
    )


def test_classification_doc_references_existing_constants_no_duplicate_table(
    classification_doc_text: str,
    regenerate_dashboard_text: str,
) -> None:
    """既存 constants 参照 anchor 存在 + 並行 PROGRESS_COLOR_TIERS table 重複起案禁。"""
    # 既存 constants/function を doc 内で名指し anchor
    for constant in (
        "PROGRESS_COLOR_TIERS",
        "STATUS_STAGE_PCT",
        "progress_color_tier",
    ):
        assert constant in classification_doc_text, (
            f"classification doc に既装備 '{constant}' anchor が無い (= 参照 anchor only 規範違反)"
        )
        assert constant in regenerate_dashboard_text, (
            f"regenerate_dashboard.py から '{constant}' が消えている (= 既装備 source 喪失検出)"
        )
    # 並行 rendering path 起案禁 anchor (= naomasa concerns 整合)
    assert re.search(r"参照\s*anchor\s*only|改変\s*しない|改変せず", classification_doc_text), (
        "classification doc に '参照 anchor only' / '改変しない' 規範 anchor が無い (= 並行 rendering path 起案禁 違反)"
    )
    # 並行 PROGRESS_COLOR_TIERS table 重複起案禁: doc 内に Python list literal pattern が重複していない
    # PROGRESS_COLOR_TIERS の dict literal は regenerate_dashboard.py 内に存在、doc 内では引用 markdown table のみ。
    python_list_assigns = re.findall(
        r"^PROGRESS_COLOR_TIERS\s*[:=]\s*\[", classification_doc_text, re.MULTILINE
    )
    assert len(python_list_assigns) == 0, (
        f"classification doc 内に PROGRESS_COLOR_TIERS = [...] Python list 再定義 "
        f"{len(python_list_assigns)} 件検出 (= 並行 rendering path 重複起案、naomasa concerns 違反)"
    )


def test_layer_c_d_cross_layer_reference_anchor_present(
    layer_c_text: str, layer_d_text: str
) -> None:
    """Layer C/D markdown に classification doc への cross-layer reference anchor が追加されている。"""
    expected_reference = "dashboard_status_classification_logic.md"
    assert expected_reference in layer_c_text, (
        f"Layer C markdown に '{expected_reference}' cross-layer reference anchor が無い"
    )
    assert expected_reference in layer_d_text, (
        f"Layer D markdown に '{expected_reference}' cross-layer reference anchor が無い"
    )
    # cross-layer reference は §6 配置先 (= 各 layer 既 anchor 構造維持)
    layer_c_section6_present = re.search(
        r"^##\s+6\.[^\n]*cross[- ]layer\s+reference", layer_c_text, re.MULTILINE
    )
    layer_d_section6_present = re.search(
        r"^##\s+6\.[^\n]*cross[- ]layer\s+reference", layer_d_text, re.MULTILINE
    )
    assert layer_c_section6_present, "Layer C markdown に '## 6. ... cross-layer reference ...' section anchor が無い (= 既 anchor 構造破壊検出)"
    assert layer_d_section6_present, "Layer D markdown に '## 6. ... cross-layer reference ...' section anchor が無い (= 既 anchor 構造破壊検出)"

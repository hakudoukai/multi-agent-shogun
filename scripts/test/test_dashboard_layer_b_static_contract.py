"""Static source-contract tests for dashboard Layer B Phase 層 render component.

Target: docs/dashboard_layer_b_phase.md

Test nature: markdown grep + field/anchor presence check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_b_phase.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer B render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_b_phase_records_present(doc_text: str) -> None:
    """phase A / B / C / D / E の 5 群 anchor が全件 markdown 内に存在する。"""
    required_phases = [
        "phase A",
        "phase B",
        "phase C",
        "phase D",
        "phase E",
    ]
    missing = [name for name in required_phases if name not in doc_text]
    assert not missing, f"phase 群 anchor から欠落: {missing}"

    section_pattern = re.compile(
        r"^###\s+2\.2[^\n]*phase\s*A\s*/\s*B\s*/\s*C\s*/\s*D\s*/\s*E",
        re.MULTILINE,
    )
    assert section_pattern.search(doc_text), (
        "phase A-E 命名対応 anchor section (= '### 2.2 ... phase A / B / C / D / E ...') が無い"
    )


def test_layer_b_progress_pct_field_present(doc_text: str) -> None:
    """progress_pct field name + 算出式 syntax が markdown 内に存在する。"""
    pct_count = len(re.findall(r"progress_pct", doc_text))
    assert pct_count >= 3, (
        f"progress_pct field が {pct_count} 件、最低 3 件要 (= 算出式 + leaf 定義 + field schema)"
    )

    formula_pattern = re.compile(r"progress_pct\s*\(\s*node\s*\)\s*=", re.MULTILINE)
    assert formula_pattern.search(doc_text), (
        "progress_pct(node) = ... 算出式 syntax が markdown 内に無い"
    )

    leaf_pattern = re.compile(r"progress_pct\s*\(\s*leaf\s*\)\s*=", re.MULTILINE)
    assert leaf_pattern.search(doc_text), (
        "progress_pct(leaf) = ... 算出式 syntax が markdown 内に無い"
    )


def test_layer_b_supabase_table_reference_anchor(doc_text: str) -> None:
    """Supabase development_progress table reference anchor が存在する。"""
    table_name_count = doc_text.count("development_progress")
    assert table_name_count >= 3, (
        f"development_progress table 名が {table_name_count} 件、最低 3 件要 "
        "(= anchor table + schema 説明 + cross-reference)"
    )

    assert "Supabase" in doc_text, (
        "Supabase keyword が doc 内に無い (= access 経路 anchor 欠落)"
    )

    anchor_pattern = re.compile(
        r"^##\s+5\.[^\n]*development_progress",
        re.MULTILINE,
    )
    assert anchor_pattern.search(doc_text), (
        "development_progress reference anchor section (= '## 5. ... development_progress ...') が無い"
    )


def test_layer_b_color_coding_4_levels(doc_text: str) -> None:
    """色分け 4 段階 (green / yellow / orange / red) 全件 reference が存在する。"""
    required_colors = ["green", "yellow", "orange", "red"]
    missing = [c for c in required_colors if c not in doc_text]
    assert not missing, f"色分け 4 段階 anchor から欠落: {missing}"

    section_pattern = re.compile(
        r"^##\s+4\.[^\n]*色分け\s*4\s*段階",
        re.MULTILINE,
    )
    assert section_pattern.search(doc_text), (
        "色分け 4 段階 section (= '## 4. 色分け 4 段階 ...') が無い"
    )


def test_layer_b_w_phase_anchor(doc_text: str) -> None:
    """W4 〜 W17 phase window anchor が markdown 内に存在する。"""
    w_pattern = re.compile(r"\bW(\d{1,2})\b")
    w_numbers = sorted({int(m) for m in w_pattern.findall(doc_text)})
    required_min = 4
    required_max = 17
    assert required_min in w_numbers, f"W{required_min} anchor が doc 内に無い: 検出 W={w_numbers}"
    assert required_max in w_numbers, f"W{required_max} anchor が doc 内に無い: 検出 W={w_numbers}"

    window_text_pattern = re.compile(r"W4[^\n]*W17|W4\s*〜\s*W17|W4[^\n]*-\s*W17")
    assert window_text_pattern.search(doc_text), (
        "W4-W17 phase window anchor 文字列 (= 'W4 ... W17' or 'W4〜W17' or 'W4-W17') が無い"
    )

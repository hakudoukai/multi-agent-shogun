"""Static source-contract tests for dashboard Layer D 頭脳層 蜘蛛の糸 render component.

Target: docs/dashboard_layer_d_zunou.md

Test nature: markdown grep + mermaid syntax check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_d_zunou.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer D render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_d_legal_sources_count_field(doc_text: str) -> None:
    """legal_sources 1,600 件 count field が anchor として存在する。"""
    pattern = re.compile(r"`?legal_sources`?[^\n]*?1[,，]?600", re.DOTALL)
    assert pattern.search(doc_text), (
        "Layer D render に legal_sources 1,600 records count field anchor が無い"
    )
    occurrences = re.findall(r"legal_sources", doc_text)
    assert len(occurrences) >= 3, (
        f"legal_sources anchor が {len(occurrences)} 件、最低 3 件要 (= table + mermaid + cross-layer)"
    )


def test_layer_d_legal_linkages_section(doc_text: str) -> None:
    """legal_source_linkages 3,235 件 section が anchor として存在する。"""
    pattern = re.compile(r"`?legal_source_linkages`?[^\n]*?3[,，]?235", re.DOTALL)
    assert pattern.search(doc_text), (
        "Layer D render に legal_source_linkages 3,235 records section anchor が無い"
    )
    occurrences = re.findall(r"legal_source_linkages", doc_text)
    assert len(occurrences) >= 3, (
        f"legal_source_linkages anchor が {len(occurrences)} 件、"
        "最低 3 件要 (= table + mermaid + cross-layer reference)"
    )


def test_layer_d_design_decisions_anchor(doc_text: str) -> None:
    """design_decisions anchor (= DD-* business decision 200+ records) が文中に存在する。"""
    occurrences = re.findall(r"design_decisions", doc_text)
    assert len(occurrences) >= 2, (
        f"design_decisions anchor が {len(occurrences)} 件、"
        "最低 2 件要 (= section 内 + mermaid or cross-layer reference)"
    )
    assert re.search(r"DD-020", doc_text), (
        "design_decisions 主要 anchor DD-020 (= 蜘蛛の糸原典) が文中に無い"
    )
    assert re.search(r"DD-054", doc_text), (
        "design_decisions 主要 anchor DD-054 (= Layer A 原典) が文中に無い"
    )


def test_layer_d_kumonoito_cross_layer_diff(doc_text: str) -> None:
    """蜘蛛の糸 cross-layer mermaid (= Layer A/B/C → Layer D 接続) が存在する。"""
    fence_pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    blocks = fence_pattern.findall(doc_text)
    assert blocks, "Layer D render に ```mermaid ... ``` code fence が無い"

    graph_td_blocks = [b for b in blocks if re.search(r"^\s*graph\s+TD\b", b, re.MULTILINE)]
    assert graph_td_blocks, "mermaid block 内に 'graph TD' declaration が無い"

    target_block = graph_td_blocks[0]

    dotted_edges = re.findall(r"-\.[^\n]*\.->", target_block)
    assert len(dotted_edges) >= 3, (
        f"mermaid 内蜘蛛の糸 cross-layer 破線接続 (= '-. ... .->') が {len(dotted_edges)} 件、"
        "最低 3 件要 (= Layer A/B/C → Layer D の 3 本入射)"
    )

    for layer_anchor in ("LA", "LB", "LC"):
        assert re.search(rf"\b{layer_anchor}\b", target_block), (
            f"mermaid 内 cross-layer 接続元 anchor '{layer_anchor}' (= Layer A/B/C node) が無い"
        )

    assert re.search(r"\bLD\b", target_block), (
        "mermaid 内 Layer D 中心 node anchor 'LD' が無い"
    )

    edge_lines = [
        ln for ln in target_block.splitlines()
        if "-->" in ln or "---" in ln or "-.->" in ln or "-." in ln
    ]
    for ln in edge_lines:
        stripped = ln.strip()
        if not stripped:
            continue
        assert re.match(r"^[A-Za-z0-9_]+", stripped), (
            f"mermaid edge line が node id で始まらない (= 構文 invalid): {stripped!r}"
        )


def test_layer_d_query_budget_compliance(doc_text: str) -> None:
    """diff fetch ETag strategy reference (= v0.2 §3.2 query budget) が anchor として存在する。"""
    assert re.search(r"diff\s*fetch", doc_text), (
        "Layer D render に 'diff fetch' strategy anchor が無い (= v0.2 §3.2 query budget reference 欠落)"
    )
    assert re.search(r"ETag", doc_text), (
        "Layer D render に 'ETag' anchor が無い (= diff fetch strategy 規範根拠 欠落)"
    )

    assert re.search(r"§\s*3\.2", doc_text) or re.search(r"3\.2\s*query\s*budget", doc_text), (
        "Layer D render に v0.2 §3.2 query budget reference anchor が無い"
    )

    diff_fetch_count = len(re.findall(r"diff\s*fetch", doc_text))
    assert diff_fetch_count >= 3, (
        f"'diff fetch' anchor が {diff_fetch_count} 件、"
        "最低 3 件要 (= legal_sources + legal_source_linkages + inspection_checklists 3 table 適用)"
    )

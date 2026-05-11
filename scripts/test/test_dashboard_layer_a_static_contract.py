"""Static source-contract tests for dashboard Layer A 構想層 render component.

Target: docs/dashboard_layer_a_kousou.md

Test nature: markdown grep + mermaid syntax check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_a_kousou.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer A render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_a_5_kaisou_section_present(doc_text: str) -> None:
    """## 2 ... 5 階層 section が単独 anchor として存在する。"""
    pattern = re.compile(r"^##\s+2\.[^\n]*5\s*階層", re.MULTILINE)
    assert pattern.search(doc_text), (
        "Layer A render に「5 階層」section anchor (= '## 2. ... 5 階層 ...') が無い"
    )
    table_pattern = re.compile(r"第\s*0\s*層.*第\s*5\s*層", re.DOTALL)
    assert table_pattern.search(doc_text), (
        "「5 階層」section に第 0 層 〜 第 5 層 の table 列挙が無い"
    )


def test_layer_a_10_pillar_section_present(doc_text: str) -> None:
    """## 3 ... 10 柱 section が単独 anchor として存在する。"""
    pattern = re.compile(r"^##\s+3\.[^\n]*10\s*柱", re.MULTILINE)
    assert pattern.search(doc_text), (
        "Layer A render に「10 柱」section anchor (= '## 3. ... 10 柱 ...') が無い"
    )
    required_pillars = [
        "画像 AI",
        "歯の状態 DB",
        "治療計画ナビ",
        "患者アプリ",
        "AI 副院長",
        "処置セット",
        "リアルタイム会計",
        "蜘蛛の糸",
        "AI 副社長",
    ]
    missing = [name for name in required_pillars if name not in doc_text]
    assert not missing, f"10 柱 section から欠落: {missing}"


def test_layer_a_mermaid_graph_td_syntax(doc_text: str) -> None:
    """```mermaid block が存在し graph TD declaration を含む + 最低限の有効構文。"""
    fence_pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    blocks = fence_pattern.findall(doc_text)
    assert blocks, "Layer A render に ```mermaid ... ``` code fence が無い"

    graph_td_blocks = [b for b in blocks if re.search(r"^\s*graph\s+TD\b", b, re.MULTILINE)]
    assert graph_td_blocks, "mermaid block 内に 'graph TD' declaration が無い"

    target_block = graph_td_blocks[0]
    arrow_count = len(re.findall(r"-->", target_block))
    assert arrow_count >= 5, (
        f"mermaid graph TD の '-->' 矢印が {arrow_count} 件、最低 5 件要 (= 階層連結 evidence)"
    )

    edge_lines = [ln for ln in target_block.splitlines() if "-->" in ln or "---" in ln or "-.->" in ln or "-." in ln]
    for ln in edge_lines:
        stripped = ln.strip()
        if not stripped:
            continue
        assert re.match(r"^[A-Za-z0-9_]+", stripped), (
            f"mermaid edge line が node id で始まらない (= 構文 invalid): {stripped!r}"
        )


def test_layer_a_dd054_reference_anchor(doc_text: str) -> None:
    """DD-054 anchor (= 5 階層 + 10 柱 原典) が文中に存在する。"""
    matches = re.findall(r"DD-054", doc_text)
    assert len(matches) >= 2, (
        f"DD-054 anchor が {len(matches)} 件、最低 2 件要 (= 原典 anchor + mermaid 内 node 等)"
    )


def test_layer_a_kumonoito_reference_anchor(doc_text: str) -> None:
    """蜘蛛の糸 layer 接続 anchor (= Layer D へ cross-layer) が文中に存在する。"""
    kumo_count = doc_text.count("蜘蛛の糸")
    assert kumo_count >= 3, (
        f"蜘蛛の糸 anchor が {kumo_count} 件、最低 3 件要 (= 10 柱 + Layer D 接続 + mermaid 内)"
    )
    assert re.search(r"Layer\s*D", doc_text), (
        "蜘蛛の糸接続先 Layer D anchor が文中に無い (= cross-layer reference 欠落)"
    )

"""Static source-contract tests for dashboard Layer C 機能層 render component.

Target: docs/dashboard_layer_c_function.md

Test nature: markdown grep + mermaid syntax check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_c_function.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer C render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_c_cmd_004_two_battlefields_present(doc_text: str) -> None:
    """## 2 ... cmd_004 二大戦線 section に 会計待ちゼロ + 小児恐竜王国 両 anchor が存在する。"""
    section_pattern = re.compile(r"^##\s+2\.[^\n]*二大戦線", re.MULTILINE)
    assert section_pattern.search(doc_text), (
        "Layer C render に 「## 2. ... 二大戦線」 section anchor が無い"
    )
    assert "会計待ちゼロ" in doc_text, (
        "二大戦線 section に「会計待ちゼロ」 anchor が無い"
    )
    assert "小児恐竜王国" in doc_text, (
        "二大戦線 section に「小児恐竜王国」 anchor が無い"
    )


def test_layer_c_function_1_to_7_anchors(doc_text: str) -> None:
    """機能①-⑦ 7 件の anchor (= 機能 1〜機能 7 / ①〜⑦ 表記) が全件存在する。"""
    required_functions = [
        ("機能 ①", "QR"),
        ("機能 ②", "領収書"),
        ("機能 ③", "パスポート"),
        ("機能 ④", "DB 連動"),
        ("機能 ⑤", "AI チャット"),
        ("機能 ⑥", "specialty_mode"),
        ("機能 ⑦", "同意"),
    ]
    missing: list[str] = []
    for marker, keyword in required_functions:
        if marker not in doc_text or keyword not in doc_text:
            missing.append(f"{marker} ({keyword})")
    assert not missing, f"機能①-⑦ anchor 欠落: {missing}"


def test_layer_c_moushi_engine_section_present(doc_text: str) -> None:
    """申し送りエンジン section anchor が存在し、Stage 1/2/3 が記載されている。"""
    assert "申し送りエンジン" in doc_text, (
        "Layer C render に 「申し送りエンジン」 section anchor が無い"
    )
    stage_count = sum(1 for s in ("Stage 1", "Stage 2", "Stage 3") if s in doc_text)
    assert stage_count >= 3, (
        f"申し送りエンジン Stage 1/2/3 anchor が {stage_count} 件、3 件全件要"
    )


def test_layer_c_kumonoito_layer_d_reference(doc_text: str) -> None:
    """蜘蛛の糸 layer 接続 anchor + Layer D reference が文中に存在する。"""
    kumo_count = doc_text.count("蜘蛛の糸")
    assert kumo_count >= 3, (
        f"蜘蛛の糸 anchor が {kumo_count} 件、最低 3 件要 (= 二大戦線 + 機能①-⑦ + mermaid 内)"
    )
    assert re.search(r"Layer\s*D", doc_text), (
        "蜘蛛の糸接続先 Layer D anchor が文中に無い (= cross-layer reference 欠落)"
    )

    fence_pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    blocks = fence_pattern.findall(doc_text)
    assert blocks, "Layer C render に ```mermaid ... ``` code fence が無い"
    graph_td_blocks = [b for b in blocks if re.search(r"^\s*graph\s+TD\b", b, re.MULTILINE)]
    assert graph_td_blocks, "mermaid block 内に 'graph TD' declaration が無い"
    target_block = graph_td_blocks[0]
    dashed_edges = re.findall(r"-\.[^>]*\.->", target_block)
    assert len(dashed_edges) >= 5, (
        f"mermaid 内 蜘蛛の糸 破線 '-.*.->' が {len(dashed_edges)} 件、最低 5 件要 "
        "(= 機能①-⑦ + 小児恐竜王国 push 等の Layer D 接続 evidence)"
    )


def test_layer_c_completion_rate_field(doc_text: str) -> None:
    """完遂率 field anchor が文中に存在する (= MC generator 算出参照)。"""
    completion_count = doc_text.count("完遂率")
    assert completion_count >= 3, (
        f"完遂率 field anchor が {completion_count} 件、最低 3 件要 "
        "(= 二大戦線 + 機能①-⑦ + 算出 source 参照)"
    )
    assert re.search(r"§\s*3\.6|算出式|progress\s*算出", doc_text), (
        "完遂率 算出 source 参照 anchor (= v0.2 §3.6 progress 算出式) が文中に無い"
    )

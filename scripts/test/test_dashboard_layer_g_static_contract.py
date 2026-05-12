"""Static source-contract tests for dashboard Layer G 統合層 render component.

Target: docs/dashboard_layer_g_integration_drill_down.md

Test nature: markdown grep + HTML/systemd syntax anchor check (= 静的
source-contract、network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。

Test names (= task YAML exact_test_names):
  1. test_layer_g_html_details_accordion_design
  2. test_layer_g_progress_bar_section
  3. test_layer_g_color_coding_4_levels
  4. test_layer_g_systemd_timer_15min
  5. test_layer_g_stage_5_verify_plan
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_g_integration_drill_down.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer G render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_g_html_details_accordion_design(doc_text: str) -> None:
    """<details> native accordion design が spec 内に存在し、HTML5 native である事の anchor + 実 HTML 例を含む。"""
    assert re.search(r"<details", doc_text), (
        "Layer G spec に '<details' anchor が無い (= HTML5 native accordion 不在)"
    )
    assert re.search(r"<summary", doc_text), (
        "Layer G spec に '<summary' anchor が無い (= accordion header 不在)"
    )
    assert re.search(r"native\s*accordion|native\s*`?<details`?", doc_text), (
        "Layer G spec に 'native accordion' 表明 anchor が無い"
    )
    code_blocks = re.findall(r"```html\s*\n(.*?)```", doc_text, re.DOTALL)
    nested_blocks = [b for b in code_blocks if b.count("<details") >= 2]
    assert nested_blocks, (
        "Layer G spec に ```html code fence + ネスト <details> 例 が無い (= 階層 click 展開 evidence 欠落)"
    )


def test_layer_g_progress_bar_section(doc_text: str) -> None:
    """<progress> HTML element reference が spec 内に存在する (= native progress bar)。"""
    progress_tags = re.findall(r"<progress[^>]*>", doc_text)
    assert len(progress_tags) >= 1, (
        f"Layer G spec に '<progress ...>' tag が {len(progress_tags)} 件、最低 1 件要"
    )
    assert re.search(r"value\s*=", doc_text), (
        "Layer G spec に 'value=' attribute reference が無い (= progress value 機械算出 anchor 欠落)"
    )
    assert re.search(r"max\s*=\s*[\"']?100", doc_text), (
        "Layer G spec に 'max=100' anchor が無い (= progress 0-100 範囲 anchor 欠落)"
    )


def test_layer_g_color_coding_4_levels(doc_text: str) -> None:
    """色分け 4 段階 (= green/yellow/orange/red) design が spec 内に存在する。"""
    required_colors = ["green", "yellow", "orange", "red"]
    missing = [c for c in required_colors if c not in doc_text]
    assert not missing, f"色分け 4 段階 anchor 欠落: {missing}"
    assert re.search(r"4\s*段階|four\s+levels?", doc_text, re.IGNORECASE), (
        "Layer G spec に '4 段階' 明示 anchor が無い"
    )
    table_pattern = re.compile(
        r"\|\s*green.*\|.*\n\|.*\n\|\s*yellow.*\|", re.DOTALL
    )
    if not table_pattern.search(doc_text):
        green_idx = doc_text.find("green")
        red_idx = doc_text.find("red")
        assert 0 <= green_idx < red_idx, (
            "Layer G spec に green→yellow→orange→red の table 化 or 序列が無い"
        )


def test_layer_g_systemd_timer_15min(doc_text: str) -> None:
    """dashboard-update.timer 15min interval reference が spec 内に存在する。"""
    assert re.search(r"dashboard-update\.timer", doc_text), (
        "Layer G spec に 'dashboard-update.timer' anchor が無い"
    )
    assert re.search(r"dashboard-update\.service", doc_text), (
        "Layer G spec に 'dashboard-update.service' anchor が無い"
    )
    assert re.search(r"OnUnitActiveSec\s*=\s*15min", doc_text), (
        "Layer G spec に 'OnUnitActiveSec=15min' anchor が無い (= 15min interval 機械 evidence 欠落)"
    )
    assert re.search(r"Persistent\s*=\s*true", doc_text), (
        "Layer G spec に 'Persistent=true' anchor が無い (= WSL 再起動跨ぎ resilience 欠落)"
    )
    ini_blocks = re.findall(r"```ini\s*\n(.*?)```", doc_text, re.DOTALL)
    assert ini_blocks, "Layer G spec に ```ini systemd unit template fence が無い"


def test_layer_g_stage_5_verify_plan(doc_text: str) -> None:
    """Stage 5 検証 plan (= 24h 運用 + AC 17+1 件 verify plan section) が spec 内に存在する。"""
    assert re.search(r"^##\s+4\.[^\n]*Stage\s*5", doc_text, re.MULTILINE), (
        "Layer G spec に '## 4. ... Stage 5 ...' section anchor が無い"
    )
    assert re.search(r"24h\s*運用|24\s*hours?\s*運用|24h\s+verify", doc_text), (
        "Layer G spec に '24h 運用' anchor が無い"
    )
    ac_matches = re.findall(r"AC\s*1[0-8]\b", doc_text)
    assert len(ac_matches) >= 5, (
        f"Layer G spec の Stage 5 verify section に AC10-18 anchor が {len(ac_matches)} 件、最低 5 件要"
    )
    assert "AC18" in doc_text, (
        "Layer G spec に 'AC18' alert anchor が無い (= 17+1 件の +1 alert AC 欠落)"
    )
    assert re.search(r"rollback|disable.*timer", doc_text, re.IGNORECASE), (
        "Layer G spec に rollback path anchor が無い (= 失敗時 retreat 規範欠落)"
    )

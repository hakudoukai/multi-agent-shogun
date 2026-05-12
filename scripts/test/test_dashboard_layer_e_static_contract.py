"""Static source-contract tests for dashboard Layer E 運用層 render component.

Target: docs/dashboard_layer_e_unyou.md

Test nature: markdown grep + mermaid syntax check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
Pattern: ashigaru1 Layer A 規範整合 (= scripts/test/test_dashboard_layer_a_static_contract.py)。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_e_unyou.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer E render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_e_tmux_session_9_panes(doc_text: str) -> None:
    """## 3 tmux session 9 panes section が単独 anchor として存在し、multiagent:agents.0-0.8 panes を mention する。"""
    pattern = re.compile(r"^##\s+3\.[^\n]*9\s*panes", re.MULTILINE)
    assert pattern.search(doc_text), (
        "Layer E render に「tmux session 9 panes」section anchor (= '## 3. ... 9 panes ...') が無い"
    )
    pane_indices_present = [
        idx for idx in range(9)
        if re.search(rf"multiagent:agents\.{idx}\b", doc_text)
    ]
    assert len(pane_indices_present) == 9, (
        f"multiagent:agents.0-agents.8 全 9 panes mention 必須、実 mention: {pane_indices_present}"
    )


def test_layer_e_auto_git_sync_timer(doc_text: str) -> None:
    """auto-git-sync.timer / systemd FF pull anchor が mention されている。"""
    assert "auto-git-sync.timer" in doc_text, (
        "Layer E render に 'auto-git-sync.timer' anchor が無い"
    )
    auto_git_count = len(re.findall(r"auto-git-sync", doc_text))
    assert auto_git_count >= 3, (
        f"'auto-git-sync' anchor が {auto_git_count} 件、最低 3 件要 (= unit + script + log の anchor)"
    )
    assert re.search(r"FF\s*pull|fast-forward\s*pull|pull-only", doc_text, re.IGNORECASE), (
        "auto-git-sync の 'FF pull / pull-only' 仕様 anchor が無い"
    )


def test_layer_e_inbox_watcher_section(doc_text: str) -> None:
    """inbox_watcher.sh + mailbox + nudge anchor が mention されている。"""
    assert "inbox_watcher.sh" in doc_text, (
        "Layer E render に 'inbox_watcher.sh' anchor が無い"
    )
    assert re.search(r"queue/inbox", doc_text), (
        "queue/inbox mailbox anchor が無い (= inbox_watcher の対象 anchor)"
    )
    inbox_watcher_count = len(re.findall(r"inbox_watcher", doc_text))
    assert inbox_watcher_count >= 3, (
        f"'inbox_watcher' anchor が {inbox_watcher_count} 件、最低 3 件要 (= process + supervisor + section header)"
    )


def test_layer_e_ntfy_ttyd_reference(doc_text: str) -> None:
    """ntfy.sh + ttyd-shogun 通知 + web 配信 anchor が mention されている。"""
    assert "ntfy.sh" in doc_text or "ntfy_listener" in doc_text, (
        "Layer E render に 'ntfy.sh' / 'ntfy_listener' anchor が無い"
    )
    assert re.search(r"ttyd", doc_text), (
        "Layer E render に 'ttyd' anchor が無い (= web 配信 layer)"
    )
    assert re.search(r"shogun-tunnel", doc_text), (
        "Layer E render に 'shogun-tunnel' anchor が無い (= ttyd 統合 path)"
    )


def test_layer_e_systemd_services_anchor(doc_text: str) -> None:
    """systemd user unit anchor (= timer / service) + mermaid graph TD が存在する。"""
    assert re.search(r"systemctl\s+--user", doc_text), (
        "Layer E render に 'systemctl --user' 取得 command anchor が無い"
    )
    assert re.search(r"\.timer\b", doc_text) and re.search(r"\.service\b", doc_text), (
        "Layer E render に systemd '.timer' + '.service' 両 unit anchor が無い"
    )
    fence_pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    blocks = fence_pattern.findall(doc_text)
    assert blocks, "Layer E render に ```mermaid ... ``` code fence が無い"
    graph_td_blocks = [b for b in blocks if re.search(r"^\s*graph\s+TD\b", b, re.MULTILINE)]
    assert graph_td_blocks, "mermaid block 内に 'graph TD' declaration が無い"
    target_block = graph_td_blocks[0]
    arrow_count = len(re.findall(r"-->", target_block))
    assert arrow_count >= 5, (
        f"mermaid graph TD の '-->' 矢印が {arrow_count} 件、最低 5 件要 (= Layer E component 連結 evidence)"
    )

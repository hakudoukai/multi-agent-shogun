"""Static source-contract tests for dashboard Layer F 規範層 render component.

Target: docs/dashboard_layer_f_kihan.md

Test nature: markdown grep + mermaid syntax check (= 静的 source-contract、
network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "docs" / "dashboard_layer_f_kihan.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert TARGET.is_file(), f"Layer F render component missing: {TARGET}"
    return TARGET.read_text(encoding="utf-8")


def test_layer_f_memory_mcp_18_entities_sc_export_base(doc_text: str) -> None:
    """## 2 ... memory MCP 18 entities section + SC export 8:43 source reference が存在する。"""
    section_pattern = re.compile(
        r"^##\s+2\.[^\n]*memory\s*MCP\s*18\s*entities", re.MULTILINE
    )
    assert section_pattern.search(doc_text), (
        "Layer F render に 「## 2. ... memory MCP 18 entities ...」 section anchor が無い"
    )

    sc_export_pattern = re.compile(
        r"sc_memory_entities_export_20260512\.yaml|SC\s*export\s*8:43|2026-05-12T08:43"
    )
    assert sc_export_pattern.search(doc_text), (
        "SC export source (= queue/reports/sc_memory_entities_export_20260512.yaml / "
        "SC export 8:43 / 2026-05-12T08:43) anchor が文中に無い"
    )

    required_entities = [
        "mistake_prevention_principle",
        "radical_solution_during_development",
        "F007_git_push_approval_rule",
        "audit_exclusive_to_gunshi_codex",
        "ashigaru_model_selection_strategy",
        "task_directive_pre_audit_rule",
        "shogun_15min_self_check_rule",
        "council_autonomous_decision_rule",
        "auto_git_sync_mechanism",
        "SC_shogun_tunnel_service",
        "supabase_directive_distribution_rule",
        "SC_restart_procedure",
        "SC_linger_enabled",
        "Session_0_isolation_limit",
        "SC_vsock_healthy",
        "ieyasu_persona_2026",
        "nobunaga_ieyasu_alias_mirror",
        "SC_ttyd_absent",
    ]
    missing = [name for name in required_entities if name not in doc_text]
    assert not missing, (
        f"SC export 18 entities のうち欠落: {missing}"
    )

    assert "18" in doc_text, "件数 18 anchor が文中に無い"


def test_layer_f_claude_md_reference(doc_text: str) -> None:
    """CLAUDE.md + instructions/karo.md + instructions/ashigaru.md + instructions/gunshi.md
    reference anchor が文中に存在する。"""
    required_refs = [
        "CLAUDE.md",
        "instructions/karo.md",
        "instructions/ashigaru.md",
        "instructions/gunshi.md",
    ]
    missing = [ref for ref in required_refs if ref not in doc_text]
    assert not missing, f"reference anchor 欠落: {missing}"

    forbidden_actions_pattern = re.compile(
        r"instructions/common/forbidden_actions\.md"
    )
    assert forbidden_actions_pattern.search(doc_text), (
        "instructions/common/forbidden_actions.md reference anchor が文中に無い"
    )


def test_layer_f_forbidden_actions_f001_f007(doc_text: str) -> None:
    """F001-F007 全 7 件の anchor が文中に存在し、forbidden table section が独立 anchor として
    存在する。"""
    section_pattern = re.compile(
        r"^##\s+3\.[^\n]*F001-F007", re.MULTILINE
    )
    assert section_pattern.search(doc_text), (
        "Layer F render に 「## 3. ... F001-F007 ...」 section anchor が無い"
    )

    required_ids = ["F001", "F002", "F003", "F004", "F005", "F006", "F007"]
    missing = [fid for fid in required_ids if fid not in doc_text]
    assert not missing, f"F001-F007 anchor 欠落: {missing}"

    role_keywords = ["karo", "ashigaru", "gunshi"]
    missing_roles = [r for r in role_keywords if r not in doc_text]
    assert not missing_roles, (
        f"役職別 forbidden table の役職 anchor 欠落: {missing_roles}"
    )


def test_layer_f_destructive_d001_d008(doc_text: str) -> None:
    """D001-D008 全 8 件の anchor が文中に存在し、Destructive Operation Safety section が
    独立 anchor として存在する。"""
    section_pattern = re.compile(
        r"^##\s+4\.[^\n]*D001-D008", re.MULTILINE
    )
    assert section_pattern.search(doc_text), (
        "Layer F render に 「## 4. ... D001-D008 ...」 section anchor が無い"
    )

    required_ids = ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"]
    missing = [did for did in required_ids if did not in doc_text]
    assert not missing, f"D001-D008 anchor 欠落: {missing}"

    tier_keywords = ["Tier 1", "Tier 2", "Tier 3"]
    missing_tiers = [t for t in tier_keywords if t not in doc_text]
    assert not missing_tiers, (
        f"Destructive Operation Safety Tier anchor 欠落: {missing_tiers}"
    )


def test_layer_f_radical_solution_rule(doc_text: str) -> None:
    """根本治療原則 (= radical_solution_during_development_rule) reference + mermaid graph TD
    + Layer E 規範適用 cross-layer anchor が文中に存在する。"""
    section_pattern = re.compile(
        r"^##\s+5\.[^\n]*根本治療原則", re.MULTILINE
    )
    assert section_pattern.search(doc_text), (
        "Layer F render に 「## 5. ... 根本治療原則 ...」 section anchor が無い"
    )

    radical_anchor_count = (
        doc_text.count("根本治療")
        + doc_text.count("radical_solution_during_development")
    )
    assert radical_anchor_count >= 3, (
        f"根本治療原則 anchor が {radical_anchor_count} 件、最低 3 件要 "
        "(= rule_supreme entity + section heading + 適用例 / 現在期間意義 等)"
    )

    fence_pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    blocks = fence_pattern.findall(doc_text)
    assert blocks, "Layer F render に ```mermaid ... ``` code fence が無い"
    graph_td_blocks = [
        b for b in blocks if re.search(r"^\s*graph\s+TD\b", b, re.MULTILINE)
    ]
    assert graph_td_blocks, "mermaid block 内に 'graph TD' declaration が無い"

    target_block = graph_td_blocks[0]
    arrow_count = len(re.findall(r"-->", target_block))
    assert arrow_count >= 5, (
        f"mermaid graph TD の '-->' 矢印が {arrow_count} 件、最低 5 件要 "
        "(= principle → rule / mechanism / procedure 階層連結 evidence)"
    )

    dashed_edges = re.findall(r"-\.[^>]*\.->", target_block)
    assert len(dashed_edges) >= 3, (
        f"mermaid 内 Layer E 規範適用 破線 '-.*.->' が {len(dashed_edges)} 件、"
        "最低 3 件要 (= rule / mechanism / procedure / agent / recovery_path から "
        "Layer E への規範適用 evidence)"
    )

    assert re.search(r"Layer\s*E", doc_text), (
        "規範適用先 Layer E anchor が文中に無い (= cross-layer reference 欠落)"
    )

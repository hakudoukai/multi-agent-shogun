"""Static source-contract tests for subtask_cmd020_sc_specialty_inventory deliverables.

Targets:
    - queue/reports/ashigaru3_subtask_cmd020_sc_specialty_inventory_inventory.yaml
    - docs/sc_specialty_inventory.md

Test nature: yaml schema + markdown grep + no-runtime-config-change static invariants
(= network / Supabase / agent unrelated)。pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。

直政 pre_audit AC condition 反映:
    1. docs/inventory only (= no runtime config / instructions / queue tasks edit)
    2. source list with timestamp evidence
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
YAML_TARGET = (
    REPO_ROOT
    / "queue"
    / "reports"
    / "ashigaru3_subtask_cmd020_sc_specialty_inventory_inventory.yaml"
)
MD_TARGET = REPO_ROOT / "docs" / "sc_specialty_inventory.md"

EXPECTED_AGENT_IDS = {
    "ashigaru1",
    "ashigaru2",
    "ashigaru3",
    "ashigaru4",
    "ashigaru5",
    "ashigaru6",
    "ashigaru7",
    "karo",
    "gunshi",
}

EXPECTED_DEPARTMENTS = {
    "統括AI",
    "仕様AI",
    "アーキテクトAI",
    "実装AI",
    "テストAI",
    "レビューAI",
    "セキュリティAI",
    "ドキュメントAI",
    "リリースAI",
}


@pytest.fixture(scope="module")
def inventory() -> dict:
    assert YAML_TARGET.is_file(), f"inventory yaml missing: {YAML_TARGET}"
    with YAML_TARGET.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "inventory yaml は root mapping である必要"
    return data


@pytest.fixture(scope="module")
def md_text() -> str:
    assert MD_TARGET.is_file(), f"sc_specialty_inventory.md missing: {MD_TARGET}"
    return MD_TARGET.read_text(encoding="utf-8")


def test_inventory_yaml_nine_agents_present(inventory: dict) -> None:
    """sc_9_agent_inventory list が 9 件、agent_id set が 期待 9 件と一致。"""
    agents = inventory.get("sc_9_agent_inventory")
    assert isinstance(agents, list), "sc_9_agent_inventory は list である必要"
    assert len(agents) == 9, (
        f"sc_9_agent_inventory list 長 {len(agents)}、期待 9 (= ashigaru1-7 + karo + gunshi)"
    )
    observed_ids = {a.get("agent_id") for a in agents}
    assert observed_ids == EXPECTED_AGENT_IDS, (
        f"agent_id set 不整合: 観測 {observed_ids - EXPECTED_AGENT_IDS} 余剰 / "
        f"{EXPECTED_AGENT_IDS - observed_ids} 不足"
    )


def test_inventory_yaml_nine_department_mapping(inventory: dict) -> None:
    """nine_department_mapping が 9 件、Charter v0.1 §8 9 部署と完全一致。"""
    section = inventory.get("nine_department_mapping")
    assert isinstance(section, dict), "nine_department_mapping は mapping である必要"
    mappings = section.get("mappings")
    assert isinstance(mappings, list), "nine_department_mapping.mappings は list 要"
    assert len(mappings) == 9, (
        f"nine_department_mapping.mappings 長 {len(mappings)}、期待 9 (= Charter v0.1 §8)"
    )
    observed = {m.get("department") for m in mappings}
    assert observed == EXPECTED_DEPARTMENTS, (
        f"department set 不整合: 余剰 {observed - EXPECTED_DEPARTMENTS} / "
        f"不足 {EXPECTED_DEPARTMENTS - observed}"
    )


def test_inventory_yaml_ac0_anti_dup_present(inventory: dict) -> None:
    """ac0_anti_dup_inventory に 関連 deliverable 列 + 新規 deliverable 4 件 が明示。"""
    section = inventory.get("ac0_anti_dup_inventory")
    assert isinstance(section, dict), "ac0_anti_dup_inventory は mapping 要"
    related = section.get("related_deliverables_found")
    assert isinstance(related, list) and len(related) >= 4, (
        f"related_deliverables_found 件数 {len(related) if isinstance(related, list) else 0}、"
        "最低 4 件 (= Charter / 本多 review / 直政 pre_audit / ashigaru1 schema 等) 要"
    )
    new_planned = section.get("new_artifacts_planned")
    assert isinstance(new_planned, list), "new_artifacts_planned は list 要"
    assert len(new_planned) == 4, (
        f"new_artifacts_planned 長 {len(new_planned)}、期待 4 (= inventory yaml + md + test + report)"
    )
    artifact_paths = {a.get("artifact_path") for a in new_planned}
    expected_artifact_endings = {
        "ashigaru3_subtask_cmd020_sc_specialty_inventory_inventory.yaml",
        "sc_specialty_inventory.md",
        "test_subtask_cmd020_sc_specialty_inventory_static_contract.py",
        "ashigaru3_subtask_cmd020_sc_specialty_inventory_report.yaml",
    }
    for expected in expected_artifact_endings:
        assert any(expected in (p or "") for p in artifact_paths), (
            f"new_artifacts_planned に '{expected}' が無い"
        )


def test_inventory_yaml_no_runtime_config_paths(inventory: dict) -> None:
    """new_artifacts_planned に runtime config path (= config/, instructions/, queue/tasks/,
    queue/inbox/) が含まれない、direct 編集の意図が無いことを invariant 化。"""
    section = inventory.get("ac0_anti_dup_inventory") or {}
    new_planned = section.get("new_artifacts_planned") or []
    forbidden_prefixes = (
        "config/",
        "instructions/",
        "queue/tasks/",
        "queue/inbox/",
    )
    offenders: list[str] = []
    for entry in new_planned:
        path = entry.get("artifact_path") or ""
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                offenders.append(path)
    assert not offenders, (
        "new_artifacts_planned に runtime config path が混入: "
        f"{offenders} (= 直政 pre_audit AC condition 違反)"
    )


def test_md_nine_department_table_present(md_text: str) -> None:
    """docs/sc_specialty_inventory.md に 9 部署 + 9 agent_id が表現される。"""
    # 9 部署
    missing_dept = [d for d in EXPECTED_DEPARTMENTS if d not in md_text]
    assert not missing_dept, f"docs/sc_specialty_inventory.md に部署 anchor 欠落: {missing_dept}"
    # 9 agent_id
    missing_agents = [a for a in EXPECTED_AGENT_IDS if a not in md_text]
    assert not missing_agents, (
        f"docs/sc_specialty_inventory.md に agent_id anchor 欠落: {missing_agents}"
    )


def test_md_no_runtime_change_declaration(md_text: str) -> None:
    """docs/sc_specialty_inventory.md に「no runtime config change」明示文言 + runtime 対象列挙 anchor が存在。"""
    assert "no runtime config change" in md_text, (
        "docs/sc_specialty_inventory.md に 'no runtime config change' 明示 anchor が無い "
        "(= 直政 pre_audit AC condition 反映必須)"
    )
    runtime_targets = (
        "config/settings.yaml",
        "instructions/ashigaru.md",
        "queue/tasks/",
        "queue/inbox/",
    )
    missing_targets = [t for t in runtime_targets if t not in md_text]
    assert not missing_targets, (
        f"docs/sc_specialty_inventory.md に runtime target 明示欠落: {missing_targets}"
    )


def test_md_timestamp_evidence_anchor(md_text: str) -> None:
    """docs/sc_specialty_inventory.md に timestamp evidence (= 2026-05-1[123]、queue/tasks / queue/reports 参照) 表現。"""
    # 直政 pre_audit "source list with timestamp" condition の docs 側 evidence
    assert "2026-05-1" in md_text, (
        "docs/sc_specialty_inventory.md に timestamp anchor (= 2026-05-1*) が無い"
    )
    # ashigaru4 / ashigaru5 / ashigaru1 の done timestamp は yaml側に明示、md でも参照
    expected_timestamps = ("2026-05-11T22:18:45", "2026-05-12T11:22:28", "2026-05-12T11:17:58")
    missing = [ts for ts in expected_timestamps if ts not in md_text]
    assert not missing, (
        f"docs/sc_specialty_inventory.md に done timestamp evidence 欠落: {missing}"
    )

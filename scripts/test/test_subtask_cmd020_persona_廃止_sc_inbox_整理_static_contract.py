"""Static source-contract tests for subtask_cmd020_persona_廃止_sc_inbox_整理.

Targets:
    - queue/reports/ashigaru4_subtask_cmd020_persona_廃止_sc_inbox_整理_inventory.yaml
    - docs/sc_inbox_整理_plan.md

Test nature: yaml schema + markdown grep + read-only static invariants.
No runtime config change / live inbox mutation / watcher process operation.
pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。

Acceptance conditions:
    AC2 (= read-only inventory + plan 文書化完遂、live inbox file mutation 0 件 +
          watcher process 操作 0 件、(a) alias 統合判定 / (b) persona 廃止候補 /
          (c) watcher args 整合 verify / (d) warning #1 解消 path)
    AC3 (= static source-contract test 3-5 件 PASS SKIP=0)
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
    / "ashigaru4_subtask_cmd020_persona_廃止_sc_inbox_整理_inventory.yaml"
)
MD_TARGET = REPO_ROOT / "docs" / "sc_inbox_整理_plan.md"

EXPECTED_LIVE_WIRED_AGENT_IDS = {
    "shogun",
    "karo",
    "ashigaru1",
    "ashigaru2",
    "ashigaru3",
    "ashigaru4",
    "ashigaru5",
    "ashigaru6",
    "ashigaru7",
    "gunshi",
}

EXPECTED_ORPHAN_ALIAS_INBOX_FILES = {
    "queue/inbox/gunshi2.yaml",
    "queue/inbox/ieyasu.yaml",
    "queue/inbox/shogun_from_main.yaml",
    "queue/inbox/shogun_from_sc.yaml",
    "queue/inbox/maeda.yaml",
}

REQUIRED_PLAN_SECTIONS = (
    "## 1. 背景 + scope",
    "## 2. 現行 state inventory",
    "## 3. alias 統合判定",
    "## 4. bridge mechanism",
    "## 5. SessionStart hook warning #1 解消 path",
    "## 6. `inbox_watcher.sh` args 整合 verify 規範",
    "## 7. 実行範囲外明示",
    "## 8. 完了基準",
)


@pytest.fixture(scope="module")
def inventory() -> dict:
    assert YAML_TARGET.is_file(), f"inventory yaml missing: {YAML_TARGET}"
    with YAML_TARGET.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "inventory yaml は root mapping である必要"
    return data


@pytest.fixture(scope="module")
def plan_md() -> str:
    assert MD_TARGET.is_file(), f"sc_inbox_整理_plan.md missing: {MD_TARGET}"
    return MD_TARGET.read_text(encoding="utf-8")


def test_sc_inbox_整理_plan_doc_has_required_sections(plan_md: str) -> None:
    """plan 文書は §1〜§8 を全件含む (= AC2 (a)-(d) 全 section covered)。"""
    missing = [section for section in REQUIRED_PLAN_SECTIONS if section not in plan_md]
    assert not missing, f"必須 section が plan 文書に欠落: {missing}"


def test_sc_inbox_整理_plan_doc_mentions_alias_candidates(plan_md: str) -> None:
    """plan 文書は AC2 (b) persona 廃止候補 5 件 (= gunshi2 / ieyasu / shogun_from_main /
    shogun_from_sc / maeda) を mention する。"""
    aliases = ["gunshi2", "ieyasu", "shogun_from_main", "shogun_from_sc", "maeda"]
    missing = [a for a in aliases if a not in plan_md]
    assert not missing, f"alias 候補 mention 欠落: {missing}"
    # AC2 (c) watcher args 整合 verify 規範 + AC2 (d) warning #1 解消 path も mention 必須
    assert "warning #1" in plan_md, "SessionStart hook warning #1 mention 欠落 (= AC2 (d))"
    assert "inbox_watcher.sh" in plan_md, "inbox_watcher.sh mention 欠落 (= AC2 (c))"
    assert "auto_forward_shogun_to_ieyasu.sh" in plan_md, (
        "bridge mechanism mention 欠落 (= ieyasu 滞留真因)"
    )


def test_inventory_yaml_orphan_alias_entries_present(inventory: dict) -> None:
    """inventory yaml の existing_assets_inventoried.orphan_alias_inbox に 5 件 alias を含む。"""
    existing = inventory.get("existing_assets_inventoried")
    assert isinstance(existing, dict), "existing_assets_inventoried mapping 欠落"
    orphan_section = existing.get("orphan_alias_inbox")
    assert isinstance(orphan_section, dict), "orphan_alias_inbox mapping 欠落"
    entries = orphan_section.get("entries")
    assert isinstance(entries, list), "orphan_alias_inbox.entries list 欠落"
    observed_files = {e.get("inbox_file") for e in entries}
    assert observed_files == EXPECTED_ORPHAN_ALIAS_INBOX_FILES, (
        f"orphan alias inbox file set 不一致:\n"
        f"  observed={sorted(observed_files)}\n"
        f"  expected={sorted(EXPECTED_ORPHAN_ALIAS_INBOX_FILES)}"
    )
    # 各 entry に watcher_status / candidate_action が必須
    for entry in entries:
        assert entry.get("watcher_status"), (
            f"watcher_status 欠落: {entry.get('inbox_file')}"
        )
        assert entry.get("candidate_action"), (
            f"candidate_action 欠落: {entry.get('inbox_file')}"
        )


def test_inventory_yaml_live_wired_count_matches_expected(inventory: dict) -> None:
    """inventory yaml の existing_assets_inventoried.live_wired_inbox は 10 体
    (= shogun + karo + ashigaru1-7 + gunshi) を含み、各 entry に watcher_args 必須。"""
    existing = inventory.get("existing_assets_inventoried")
    assert isinstance(existing, dict), "existing_assets_inventoried mapping 欠落"
    live_wired_section = existing.get("live_wired_inbox")
    assert isinstance(live_wired_section, dict), "live_wired_inbox mapping 欠落"
    entries = live_wired_section.get("entries")
    assert isinstance(entries, list), "live_wired_inbox.entries list 欠落"
    observed_ids = {e.get("agent_id") for e in entries}
    assert observed_ids == EXPECTED_LIVE_WIRED_AGENT_IDS, (
        f"live wired agent_id set 不一致:\n"
        f"  observed={sorted(observed_ids)}\n"
        f"  expected={sorted(EXPECTED_LIVE_WIRED_AGENT_IDS)}"
    )
    for entry in entries:
        assert entry.get("watcher_args"), (
            f"watcher_args 欠落: agent_id={entry.get('agent_id')}"
        )
        assert entry.get("inbox_file"), (
            f"inbox_file 欠落: agent_id={entry.get('agent_id')}"
        )
    # scope_exclusion で live inbox mutation 禁 + watcher process 操作禁が明示済
    scope_exclusion = inventory.get("scope", {}).get("scope_exclusion") or []
    joined = " ".join(scope_exclusion)
    assert "live inbox file mutation 禁" in joined, (
        "scope_exclusion: live inbox file mutation 禁 明示欠落"
    )
    assert "watcher process 操作禁" in joined, (
        "scope_exclusion: watcher process 操作禁 明示欠落"
    )

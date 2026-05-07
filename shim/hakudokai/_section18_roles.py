"""§18 PC×アカウント配置 — 役名・PC マッピング共通定義 (理事長殿御指示 2026-05-06)。

CLAUDE.md §18 PC × アカウント × エージェント配置ルールに基づき、博道会 watcher
群が参照する VALID_ROLES / ROLE_TO_PC / MAINPC_ROLES / SECONDPC_ROLES を一元化。

複数ファイルにハードコードされていた役名定義を本モジュールに集約することで:
  - §18 配置改訂時の修正点を 1 箇所に集約 (DRY)
  - 役名の不整合バグを未然防止 (single source of truth)
  - watcher 追加時の参照コスト削減

配置 (CLAUDE.md §18.1):
  - MainPC (sasebo@sasebo.or.jp):
      通常 5 体: shogun / karo / gunshi / ashigaru1 / ashigaru2
      非常時 +1: ashigaru3
  - SecondPC (hakudoukai@gmail.com):
      通常 3 体: ashigaru5 / ashigaru6 / ashigaru7
      非常時 +1: ashigaru8
  - ashigaru4: 欠番 (PC 境界の視覚的区切り)

旧体制 (fukuincho / yama / kuro / sakura / kouchan / 副医院長) は §18 移行で廃止。
本モジュールには旧体制名は一切含めない (旧名拒否は呼出側 VALID_ROLES 検証で担保)。

Reference:
  - CLAUDE.md §18 PC × アカウント × エージェント配置ルール
  - docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md (quota 暴走対策)
  - memory/account_pc_allocation.md
"""
from __future__ import annotations


# §18 MainPC 配置 (通常 5 体 + 非常時 1 体)
MAINPC_ROLES: tuple[str, ...] = (
    "shogun",
    "karo",
    "gunshi",
    "ashigaru1",
    "ashigaru2",
    "ashigaru3",
)

# §18 SecondPC 配置 (通常 3 体 + 非常時 1 体)
SECONDPC_ROLES: tuple[str, ...] = (
    "ashigaru5",
    "ashigaru6",
    "ashigaru7",
    "ashigaru8",
)

# 全有効 role (watcher の VALID_ROLES として利用)
VALID_ROLES: tuple[str, ...] = MAINPC_ROLES + SECONDPC_ROLES

# role → 所属 PC マッピング (inbox_watcher の _build_role_to_pc 等で利用)
ROLE_TO_PC: dict[str, str] = {
    **{role: "main_pc" for role in MAINPC_ROLES},
    **{role: "second_pc" for role in SECONDPC_ROLES},
}


def is_valid_role(role: str) -> bool:
    """role が §18 有効 role か。旧体制名 (fukuincho/yama/kuro/sakura/kouchan) は False。"""
    return role in VALID_ROLES


def get_pc_for_role(role: str) -> str | None:
    """role の所属 PC を返す (main_pc or second_pc)。無効 role は None。"""
    return ROLE_TO_PC.get(role)


__all__ = [
    "MAINPC_ROLES",
    "SECONDPC_ROLES",
    "VALID_ROLES",
    "ROLE_TO_PC",
    "is_valid_role",
    "get_pc_for_role",
]

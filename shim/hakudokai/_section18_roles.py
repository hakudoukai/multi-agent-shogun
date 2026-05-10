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


# §18 MainPC 配置 (通常 5 体 + 非常時 1 体 + Phase 15 新設 takenaka)
# Phase 15 (2026-05-08): takenaka (竹中半兵衛、信長直轄軍師) 追加。
MAINPC_ROLES: tuple[str, ...] = (
    "nobunaga",     # 信長 (= 旧 shogun)
    "hideyoshi",    # 秀吉 (= 旧 karo)
    "ieyasu",       # 家康 (= 旧 gunshi、Phase 5 で kuroda 置換予定)
    "takenaka",     # 竹中半兵衛 — 信長直轄軍師、Phase 15 新設 (2026-05-08)
    "ashigaru1",
    "ashigaru2",
    "ashigaru3",
)

# §18 SecondPC 配置 (Phase 1 2026-05-07 改訂: maeda 新設、通常 4 体 + 非常時 1 体)
SECONDPC_ROLES: tuple[str, ...] = (
    "maeda",       # SecondPC 家老 (前田利家) — Phase 1 新設
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


# Phase 3 partial (2026-05-07): persona 名乗り変更に伴う新名 → 旧 internal_id alias
# 完全 rename (= 旧名削除) は別途、明朝着手予定。移行期間中は両名で参照可。
# Phase 3 full (2026-05-07): 旧名 → 新名 alias (= 移行期間互換)
ROLE_ALIASES: dict[str, str] = {
    "shogun": "nobunaga",
    "karo": "hideyoshi",
    "gunshi": "ieyasu",
}


def resolve_role(name: str) -> str:
    """旧名 (shogun/karo/gunshi) → 新名 (nobunaga/hideyoshi/ieyasu) に解決。
    新名はそのまま返す。未知名もそのまま返す。"""
    return ROLE_ALIASES.get(name, name)

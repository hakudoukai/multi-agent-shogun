#!/usr/bin/env bash
# lib/_section18_roles.sh — §18 PC×アカウント配置 役名定義 (shell 版)
#
# CLAUDE.md §18 PC×アカウント×エージェント配置ルールに基づき、shell スクリプト
# (agent_status.sh / switch_cli.sh / ratelimit_check.sh 等) が参照する
# §18 配置を一元化する。
#
# Python 版 (shim/hakudokai/_section18_roles.py) と同期する単純な mirror。
# 配置改訂時は本ファイル + Python 版 + tests/test_section18_migration.py を
# 同時に更新する (single source of truth は CLAUDE.md §18.1 配置表)。
#
# 配置 (CLAUDE.md §18.1):
#   - MainPC (sasebo@sasebo.or.jp):
#       通常 5 体: shogun / karo / gunshi / ashigaru1 / ashigaru2
#       非常時 +1: ashigaru3
#   - SecondPC (hakudoukai@gmail.com):
#       通常 3 体: ashigaru5 / ashigaru6 / ashigaru7
#       非常時 +1: ashigaru8
#   - ashigaru4: 欠番 (PC 境界の視覚的区切り)
#
# Reference:
#   - CLAUDE.md §18 PC × アカウント × エージェント配置ルール
#   - shim/hakudokai/_section18_roles.py (Python 版 SoT)
#   - docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md

# 多重 source 防止 (idempotent)
if [[ -n "${_SECTION18_ROLES_LOADED:-}" ]]; then
    return 0
fi
_SECTION18_ROLES_LOADED=1

# ─── MainPC tmux pane 配置順 (multiagent:agents 内 0..4) ───
# pane_base + index で実 pane を解決する。
# 注意: shogun は別 tmux session (shogun:0.0) のため本配列に含めない。
SECTION18_MAINPC_PANE_ORDER=(
    "karo"        # pane index 0
    "ashigaru1"   # pane index 1
    "ashigaru2"   # pane index 2
    "ashigaru3"   # pane index 3 (非常時 +1)
    "gunshi"      # pane index 4
)

# ─── SecondPC tmux pane 配置順 (multiagent:agents 内 0..4) ───
# Phase 1 (2026-05-07): SecondPC 家老 maeda (前田利家) 新設、agents.0 に配置。
# 旧構成 (a5/6/7 のみ) → 新構成 (maeda + a5/6/7、+8 非常時) に統一。
SECTION18_SECONDPC_PANE_ORDER=(
    "maeda"        # pane index 0 — SecondPC 家老 (前田利家)
    "ashigaru5"   # pane index 1
    "ashigaru6"   # pane index 2
    "ashigaru7"   # pane index 3
    "ashigaru8"   # pane index 4 (非常時 +1)
)

# ─── SecondPC エージェント (= 上記 pane_order と同期、互換維持の alias) ───
SECTION18_SECONDPC_AGENTS=(
    "${SECTION18_SECONDPC_PANE_ORDER[@]}"
)

# ─── 全 §18 役名 (shogun + MainPC pane order + SecondPC, ashigaru4 欠番) ───
SECTION18_ALL_ROLES=(
    "shogun"
    "${SECTION18_MAINPC_PANE_ORDER[@]}"
    "${SECTION18_SECONDPC_AGENTS[@]}"
)

# ─── role が §18 SecondPC 配置か判定 ───
section18_is_secondpc_agent() {
    local agent="$1"
    local r
    for r in "${SECTION18_SECONDPC_AGENTS[@]}"; do
        if [[ "$r" == "$agent" ]]; then
            return 0
        fi
    done
    return 1
}

# ─── role が §18 MainPC pane 配置か判定 (shogun を除く) ───
section18_is_mainpc_pane_agent() {
    local agent="$1"
    local r
    for r in "${SECTION18_MAINPC_PANE_ORDER[@]}"; do
        if [[ "$r" == "$agent" ]]; then
            return 0
        fi
    done
    return 1
}

# ─── role の MainPC pane index を返す (見つからなければ非0 終了) ───
section18_mainpc_pane_index() {
    local agent="$1"
    local i
    for i in "${!SECTION18_MAINPC_PANE_ORDER[@]}"; do
        if [[ "${SECTION18_MAINPC_PANE_ORDER[$i]}" == "$agent" ]]; then
            echo "$i"
            return 0
        fi
    done
    return 1
}


# ─── Phase 3 partial (2026-05-07): persona 新名 → 旧 internal_id alias ───
declare -A SECTION18_ROLE_ALIASES=(
    [nobunaga]=shogun
    [hideyoshi]=karo
    [ieyasu]=gunshi
)

# 新 persona 名 → 旧 internal_id 解決 (旧名はそのまま返す)
section18_resolve_alias() {
    local name="$1"
    local resolved="${SECTION18_ROLE_ALIASES[$name]:-$name}"
    echo "$resolved"
}

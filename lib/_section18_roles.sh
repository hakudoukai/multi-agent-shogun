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
# km-167 ⓐ (委員長裁 seq332367・2026-09-18): 識別子を persona 内部 id (hideyoshi/ieyasu)
# から ★役名★ (karo/gunshi) へ戻す。呼び手 (switch_cli.sh / agent_status.sh) と
# Python SoT (tests/test_section18_migration.py) と本 lib の test は役名を渡す。
# 旧 persona 名は下の SECTION18_ROLE_ALIASES で逆向き (persona→役名) に生かす。
# takenaka (Phase 15, 旧 index 5) は §18.1 配置表 (通常 5 + 非常時 1) に無いため配列から
# 外し alias にのみ残す (pane 構成は不変・可逆)。
SECTION18_MAINPC_PANE_ORDER=(
    "karo"        # pane index 0
    "ashigaru1"   # pane index 1
    "ashigaru2"   # pane index 2
    "ashigaru3"   # pane index 3 (非常時 +1)
    "gunshi"      # pane index 4
)

# ─── SecondPC tmux pane 配置順 (multiagent:agents 内 0..3) ───
# §18.1 配置表: 通常 3 体 (ashigaru5/6/7) + 非常時 +1 (ashigaru8)。
# km-167 ⓐ: maeda (Phase 1 の SecondPC 家老 persona) は配置表に無く、Python SoT
# (SECONDPC_ROLES) と test (T-003/T-402) も a5-8 の 4 件 ∴ 配列から外し alias にのみ残す。
SECTION18_SECONDPC_PANE_ORDER=(
    "ashigaru5"   # pane index 0
    "ashigaru6"   # pane index 1
    "ashigaru7"   # pane index 2
    "ashigaru8"   # pane index 3 (非常時 +1)
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


# ─── persona 内部 id → 役名 alias (km-167 ⓐ・委員長裁 seq332367: ★逆向き★) ───
# 旧: 役名→persona (karo→hideyoshi)。新: persona→役名 (hideyoshi→karo)。
# 旧 persona 名は消さず alias として生かす。役名は identity。
# 呼び手 scripts/checks/pane_identity.sh は actual/expected の両側を本関数で正規化して
# 比べるため、向きが変はつても同値判定は保たれる (可逆: 本 map を旧に戻せば旧挙動)。
declare -A SECTION18_ROLE_ALIASES=(
    [nobunaga]=shogun
    [hideyoshi]=karo
    [ieyasu]=gunshi
    # 役名はそのまま返す (= identity)
    [shogun]=shogun
    [karo]=karo
    [gunshi]=gunshi
    # 配置表に役名の無い persona は identity で生かす (消さぬ)
    [maeda]=maeda
    [takenaka]=takenaka
)

# 名 → 正規化 (= persona 内部 id なら役名に変換、役名はそのまま、未知名もそのまま)
section18_resolve_alias() {
    local name="$1"
    local resolved="${SECTION18_ROLE_ALIASES[$name]:-$name}"
    echo "$resolved"
}

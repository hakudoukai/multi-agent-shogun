#!/usr/bin/env bats
# test_section18_roles.bats — lib/_section18_roles.sh 実関数テスト
#
# §18 polish 任意 should T1 (Phase 3 cycle3 deferred): pytest 側 (test_section18_migration.py
# TestSection18ShellHelper / TestSection18ShellPythonSotDrift) と同じ shell helper を
# bats で実関数モックテスト化、既存 pytest 側との SoT 整合検証を二重化する。
#
# pytest 側は subprocess.run 経由の文字列比較。bats 側は実 source した bash 環境で
# 配列内容 / return code を直接検証するため、リグレッション検出を相補的に強化する。
#
# テスト構成:
#   T-001: helper ファイル存在
#   T-002~T-004: 配列定義 (MAINPC_PANE_ORDER / SECONDPC_AGENTS / ALL_ROLES)
#   T-005: 多重 source idempotency (_SECTION18_ROLES_LOADED ガード)
#   T-101~T-104: section18_is_secondpc_agent (positive/negative/gap/shogun)
#   T-201~T-204: section18_is_mainpc_pane_agent (positive/negative/gap/shogun)
#   T-301~T-304: section18_mainpc_pane_index (each pane index / SecondPC reject / gap reject)

# --- セットアップ ---

setup_file() {
    export PROJECT_ROOT
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export HELPER="$PROJECT_ROOT/lib/_section18_roles.sh"
    [ -f "$HELPER" ] || return 1
}

setup() {
    # 各テスト毎に新規 source (idempotency 検査以外は独立環境で実行)。
    # 同一 bats プロセスでの SECTION18_ROLES_LOADED 残存を回避するため unset。
    unset _SECTION18_ROLES_LOADED
    unset SECTION18_MAINPC_PANE_ORDER
    unset SECTION18_SECONDPC_AGENTS
    unset SECTION18_ALL_ROLES
    # shellcheck disable=SC1090
    source "$HELPER"
}

# ============================================================
# T-001: helper ファイル存在
# ============================================================

@test "T-001: lib/_section18_roles.sh が存在する" {
    [ -f "$HELPER" ]
}

# ============================================================
# T-002~T-004: 配列定義の整合性
# ============================================================

@test "T-002: SECTION18_MAINPC_PANE_ORDER が pane 配置順 5 件" {
    [ "${#SECTION18_MAINPC_PANE_ORDER[@]}" -eq 5 ]
    [ "${SECTION18_MAINPC_PANE_ORDER[0]}" = "karo" ]
    [ "${SECTION18_MAINPC_PANE_ORDER[1]}" = "ashigaru1" ]
    [ "${SECTION18_MAINPC_PANE_ORDER[2]}" = "ashigaru2" ]
    [ "${SECTION18_MAINPC_PANE_ORDER[3]}" = "ashigaru3" ]
    [ "${SECTION18_MAINPC_PANE_ORDER[4]}" = "gunshi" ]
}

@test "T-003: SECTION18_SECONDPC_AGENTS が ashigaru5-8 の 4 件" {
    [ "${#SECTION18_SECONDPC_AGENTS[@]}" -eq 4 ]
    [ "${SECTION18_SECONDPC_AGENTS[0]}" = "ashigaru5" ]
    [ "${SECTION18_SECONDPC_AGENTS[1]}" = "ashigaru6" ]
    [ "${SECTION18_SECONDPC_AGENTS[2]}" = "ashigaru7" ]
    [ "${SECTION18_SECONDPC_AGENTS[3]}" = "ashigaru8" ]
}

@test "T-004: SECTION18_ALL_ROLES に shogun 含む / ashigaru4 を含まない / 旧体制名なし" {
    # shogun 含む
    local found_shogun=0
    local found_ashigaru4=0
    local r
    for r in "${SECTION18_ALL_ROLES[@]}"; do
        [ "$r" = "shogun" ] && found_shogun=1
        [ "$r" = "ashigaru4" ] && found_ashigaru4=1
    done
    [ "$found_shogun" -eq 1 ]
    [ "$found_ashigaru4" -eq 0 ]
    # 旧体制名 (fukuincho/yama/sakura/kouchan) が含まれていない
    for old in fukuincho yama sakura kouchan; do
        for r in "${SECTION18_ALL_ROLES[@]}"; do
            [ "$r" != "$old" ] || {
                echo "FAIL: 旧体制名 $old が ALL_ROLES に残存" >&2
                return 1
            }
        done
    done
    # 全件数: shogun(1) + MainPC pane(5) + SecondPC(4) = 10
    [ "${#SECTION18_ALL_ROLES[@]}" -eq 10 ]
}

# ============================================================
# T-005: 多重 source idempotency
# ============================================================

@test "T-005: 多重 source で配列が再定義されず _SECTION18_ROLES_LOADED ガードが効く" {
    # setup() で一度 source 済 → 再 source しても変化なし
    local before_count="${#SECTION18_ALL_ROLES[@]}"
    [ -n "$_SECTION18_ROLES_LOADED" ]
    # 同一 shell で再 source (return 0 で即抜けるはず)
    # shellcheck disable=SC1090
    source "$HELPER"
    local after_count="${#SECTION18_ALL_ROLES[@]}"
    [ "$before_count" -eq "$after_count" ]
}

# ============================================================
# T-101~T-104: section18_is_secondpc_agent
# ============================================================

@test "T-101: section18_is_secondpc_agent が ashigaru5/6/7/8 を accept" {
    section18_is_secondpc_agent ashigaru5
    section18_is_secondpc_agent ashigaru6
    section18_is_secondpc_agent ashigaru7
    section18_is_secondpc_agent ashigaru8
}

@test "T-102: section18_is_secondpc_agent が MainPC role を reject" {
    ! section18_is_secondpc_agent karo
    ! section18_is_secondpc_agent ashigaru1
    ! section18_is_secondpc_agent ashigaru2
    ! section18_is_secondpc_agent ashigaru3
    ! section18_is_secondpc_agent gunshi
}

@test "T-103: section18_is_secondpc_agent が ashigaru4 (欠番) を reject" {
    ! section18_is_secondpc_agent ashigaru4
}

@test "T-104: section18_is_secondpc_agent が shogun を reject (別 session)" {
    ! section18_is_secondpc_agent shogun
}

# ============================================================
# T-201~T-204: section18_is_mainpc_pane_agent
# ============================================================

@test "T-201: section18_is_mainpc_pane_agent が karo/ashigaru1-3/gunshi を accept" {
    section18_is_mainpc_pane_agent karo
    section18_is_mainpc_pane_agent ashigaru1
    section18_is_mainpc_pane_agent ashigaru2
    section18_is_mainpc_pane_agent ashigaru3
    section18_is_mainpc_pane_agent gunshi
}

@test "T-202: section18_is_mainpc_pane_agent が SecondPC role を reject" {
    ! section18_is_mainpc_pane_agent ashigaru5
    ! section18_is_mainpc_pane_agent ashigaru6
    ! section18_is_mainpc_pane_agent ashigaru7
    ! section18_is_mainpc_pane_agent ashigaru8
}

@test "T-203: section18_is_mainpc_pane_agent が ashigaru4 (欠番) を reject" {
    ! section18_is_mainpc_pane_agent ashigaru4
}

@test "T-204: section18_is_mainpc_pane_agent が shogun を reject (別 session)" {
    ! section18_is_mainpc_pane_agent shogun
}

# ============================================================
# T-301~T-304: section18_mainpc_pane_index
# ============================================================

@test "T-301: section18_mainpc_pane_index が pane 配置順を返す" {
    [ "$(section18_mainpc_pane_index karo)" = "0" ]
    [ "$(section18_mainpc_pane_index ashigaru1)" = "1" ]
    [ "$(section18_mainpc_pane_index ashigaru2)" = "2" ]
    [ "$(section18_mainpc_pane_index ashigaru3)" = "3" ]
    [ "$(section18_mainpc_pane_index gunshi)" = "4" ]
}

@test "T-302: section18_mainpc_pane_index が SecondPC role に non-zero exit" {
    run section18_mainpc_pane_index ashigaru5
    [ "$status" -ne 0 ]
    [ -z "$output" ]
}

@test "T-303: section18_mainpc_pane_index が ashigaru4 に non-zero exit" {
    run section18_mainpc_pane_index ashigaru4
    [ "$status" -ne 0 ]
    [ -z "$output" ]
}

@test "T-304: section18_mainpc_pane_index が shogun に non-zero exit (別 session)" {
    run section18_mainpc_pane_index shogun
    [ "$status" -ne 0 ]
    [ -z "$output" ]
}

# ============================================================
# T-401: pytest 側 (test_section18_migration.py) の helper との整合性 mirror 検査
# ============================================================

@test "T-401: pytest 側 TestSection18ShellHelper と同一の SECTION18_MAINPC_PANE_ORDER" {
    # pytest test_mainpc_pane_order_matches_section18 と同じ期待値で二重保険
    local actual="${SECTION18_MAINPC_PANE_ORDER[*]}"
    [ "$actual" = "karo ashigaru1 ashigaru2 ashigaru3 gunshi" ]
}

@test "T-402: pytest 側 TestSection18ShellHelper と同一の SECTION18_SECONDPC_AGENTS" {
    local actual="${SECTION18_SECONDPC_AGENTS[*]}"
    [ "$actual" = "ashigaru5 ashigaru6 ashigaru7 ashigaru8" ]
}

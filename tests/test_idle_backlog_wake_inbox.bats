#!/usr/bin/env bats
# test_idle_backlog_wake_inbox.bats — P2 93829374 受入試験
# 設計正本: queue/reports/gunshi-second_p2_93829374_bats_acceptance_design_20260910.md
#           sha256=3858f47d4ab840643b4c83b2cfc3866180ec45d5a17f6d9ea63ba65e49dffcf9
#
# 対象は scripts/idle_backlog_wake.sh の yaml_unread_count() ★のみ★。
#   ★本 script を実行しない★ — timer / tmux / curl / creds 検査へは一切触れぬ。
#   函数だけを sed で抜き出して eval する。★写しを置かぬ★ゆゑ本体が動けば試験も動き、
#   本体が変れば試験も其の儘変る(写しを置くと黙つて古びる)。
# ★live の queue/inbox は読まぬ★ — IBW_INBOX_DIR を $BATS_TEST_TMPDIR/inbox へ振り、
#   setup にて「其の下に在る事」を実際に検める(作法に頼らず器で縛る)。
#
# T-P2-01 canonical 三箱すべて既読 → 0
# T-P2-02 canonical 一件 read:false → 1 ★陽性対照★(0 しか返さぬ器でない事の證)
# T-P2-03 壊れた YAML → MEAS_FAIL (★0 ではない★)
# T-P2-04 箱が無い     → MEAS_FAIL (★0 ではない★)
# T-P2-05 legacy 別名 ashigaru{1,2,3}.yaml が在つても canonical の値は変らぬ
# T-P2-06 関はりなき役職 → 0
# 全 test は出力に加へ ★exit status 0★ を併せて検める。

setup_file() {
    export PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export TARGET_SCRIPT="$PROJECT_ROOT/scripts/idle_backlog_wake.sh"
    [ -f "$TARGET_SCRIPT" ] || return 1
}

setup() {
    export IBW_INBOX_DIR="$BATS_TEST_TMPDIR/inbox"
    # ★live の箱を指して居らぬ事を器で縛る★
    case "$IBW_INBOX_DIR" in
        "$BATS_TEST_TMPDIR"/*) : ;;
        *) return 1 ;;
    esac
    mkdir -p "$IBW_INBOX_DIR"
    # ★函数のみを抜く★ — 本体の creds 検査・loop・tmux・curl は読み込まぬ
    eval "$(sed -n '/^yaml_unread_count() {/,/^}/p' "$TARGET_SCRIPT")"
}

# $1=path  $2..=各件の read 値(true/false)
write_box() {
    local f="$1"; shift
    local i=0 r
    printf 'messages:\n' > "$f"
    for r in "$@"; do
        i=$((i+1))
        printf '  - id: m%d\n    read: %s\n' "$i" "$r" >> "$f"
    done
}

@test "T-P2-01: canonical 三箱すべて既読 → 0" {
    local role
    for role in ashigaru-second-1 ashigaru-second-2 ashigaru-second-3; do
        write_box "$IBW_INBOX_DIR/$role.yaml" true true true
        run yaml_unread_count "$role"
        [ "$status" -eq 0 ]
        [ "$output" = "0" ]
    done
}

@test "T-P2-02: canonical 一件 read:false → 1 (陽性対照)" {
    write_box "$IBW_INBOX_DIR/ashigaru-second-2.yaml" true false true
    run yaml_unread_count ashigaru-second-2
    [ "$status" -eq 0 ]
    [ "$output" = "1" ]
}

@test "T-P2-03: 壊れた YAML → MEAS_FAIL (0 ではない)" {
    printf 'messages:\n  - id: m1\n\tread: true\n' > "$IBW_INBOX_DIR/ashigaru-second-1.yaml"
    run yaml_unread_count ashigaru-second-1
    [ "$status" -eq 0 ]
    [ "$output" = "MEAS_FAIL" ]
    [ "$output" != "0" ]
}

@test "T-P2-04: 箱が無い → MEAS_FAIL (0 ではない)" {
    [ ! -e "$IBW_INBOX_DIR/ashigaru-second-3.yaml" ]
    run yaml_unread_count ashigaru-second-3
    [ "$status" -eq 0 ]
    [ "$output" = "MEAS_FAIL" ]
    [ "$output" != "0" ]
}

@test "T-P2-05: legacy 別名が在つても canonical の値は変らぬ" {
    write_box "$IBW_INBOX_DIR/ashigaru-second-1.yaml" true false
    write_box "$IBW_INBOX_DIR/ashigaru1.yaml" false false false
    write_box "$IBW_INBOX_DIR/ashigaru2.yaml" false false false
    write_box "$IBW_INBOX_DIR/ashigaru3.yaml" false false false
    run yaml_unread_count ashigaru-second-1
    [ "$status" -eq 0 ]
    [ "$output" = "1" ]
    run yaml_unread_count ashigaru1
    [ "$status" -eq 0 ]
    [ "$output" = "0" ]
}

@test "T-P2-06: 関はりなき役職 → 0" {
    run yaml_unread_count karo-second
    [ "$status" -eq 0 ]
    [ "$output" = "0" ]
}

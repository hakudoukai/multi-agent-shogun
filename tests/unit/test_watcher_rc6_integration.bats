#!/usr/bin/env bats
# tests/unit/test_watcher_rc6_integration.bats — archive watcher.sh × safe_nudge rc の統合 (裁 seq327040)
#
# 対象: scripts/archive/message_delivery_v2_full_20260508/watcher.sh (+ dedup.sh / dead_letter.sh / heartbeat.sh)
# 目的: safe_nudge.sh が rc=6 (= send-keys 済・cooldown 書込のみ失敗) を返した便を、watcher が
#       「送達済」として閉ぢ (既読化 + dedup)、次の巡回で ★再送しない★ 事を、watcher 本体を実走して測る。
#
# 仕組み: sandbox に watcher 一式を <root>/scripts/message_delivery_v2/ へ写し (= ../.. が根へ解ける深さ)、
#   safe_nudge.sh を mock (呼出を記録し MOCK_NUDGE_RC で exit)、inotifywait を mock
#   (1 回目: 即 0 = 2 巡目を起こす / 2 回目: disable flag を置いて 0 = 3 巡目の後に watcher が自ら exit 0)。
#   ∴ watcher は initial sweep (1 巡) + inotify 2 回 (2,3 巡) を回つて自然終了する。timeout は保険。
#
# 検証ケース (3):
#   T-WRC6-001: rc=6 → 呼出 1 (3 巡で再送 0)・read=true・acknowledged_by=delivered・dedup 記録・retry file 無・log WARN delivered_cooldown_write_failed・unknown_rc 0
#   T-WRC6-002: rc=0 → 呼出 1・delivered (従前不変の対照)
#   T-WRC6-003: rc=1 → 呼出 3 (queued は巡回毎に再送)・read=false・dedup 無 (= rc=1 の意味は保たれる)

setup_file() {
    export WRC_ROOT
    WRC_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    export WRC_SRC="$WRC_ROOT/scripts/archive/message_delivery_v2_full_20260508"
    [ -f "$WRC_SRC/watcher.sh" ] || return 1
    [ -f "$WRC_ROOT/scripts/lib/inbox_path.sh" ] || return 1
    python3 -c "import yaml" 2>/dev/null || return 1
}

setup() {
    : "${BATS_TEST_TMPDIR:?BATS_TEST_TMPDIR must be set}"
    export SB="${BATS_TEST_TMPDIR}/sandbox"
    mkdir -p "$SB/scripts/message_delivery_v2" "$SB/scripts/lib" "$SB/queue/inbox" "$SB/queue/watchers" \
             "$SB/queue/session_health" "$SB/queue/dead_letter" "$SB/logs/message_delivery_v2" "$SB/bin"
    for f in watcher.sh dedup.sh dead_letter.sh heartbeat.sh; do
        cp "$WRC_SRC/$f" "$SB/scripts/message_delivery_v2/$f"
    done
    cp "$WRC_ROOT/scripts/lib/inbox_path.sh" "$SB/scripts/lib/inbox_path.sh"
    export FAKE_HOME="${BATS_TEST_TMPDIR}/home"
    mkdir -p "$FAKE_HOME/.openclaw"
    export NUDGE_CALLS="$SB/nudge_calls.log"
    # mock safe_nudge.sh: 引数を記録し MOCK_NUDGE_RC で終了
    cat > "$SB/scripts/message_delivery_v2/safe_nudge.sh" <<'MOCK'
#!/usr/bin/env bash
echo "$*" >> "$NUDGE_CALLS"
exit "${MOCK_NUDGE_RC:-0}"
MOCK
    chmod +x "$SB/scripts/message_delivery_v2/safe_nudge.sh"
    # mock inotifywait: 1 回目 → 0 / 2 回目 → disable flag を置いて 0 / 以降 → 1
    export INOTIFY_CNT="$SB/inotify_cnt"
    echo 0 > "$INOTIFY_CNT"
    cat > "$SB/bin/inotifywait" <<'MOCK'
#!/usr/bin/env bash
n=$(cat "$INOTIFY_CNT"); n=$((n+1)); echo "$n" > "$INOTIFY_CNT"
if [ "$n" -eq 1 ]; then exit 0; fi
if [ "$n" -eq 2 ]; then touch "$HOME/.openclaw/disable_watcher_test_agent"; exit 0; fi
exit 1
MOCK
    chmod +x "$SB/bin/inotifywait"
    export INBOX="$SB/queue/inbox/test_agent.yaml"
    cat > "$INBOX" <<'YAML'
messages:
- id: msg_20260917_000000_wrc6test
  from: shogun
  to: test_agent
  type: task
  content: integration probe
  correlation_id: corr-wrc6
  read: false
YAML
    export WLOG="$SB/logs/message_delivery_v2/watcher_test_agent_$(date +%Y%m%d).log"
}

# 出力は file へ (= 背景の heartbeat_loop が run の stdout を握り、cleanup の kill が sleep 明けまで効かぬ 60s を避ける)
wrc_run_watcher() {
    HOME="$FAKE_HOME" PATH="$SB/bin:$PATH" MOCK_NUDGE_RC="$1" \
        timeout 30 bash "$SB/scripts/message_delivery_v2/watcher.sh" test_agent test:0.0 doppler \
        > "$SB/watcher.out" 2>&1 3>&-
}
wrc_calls() { if [ -f "$NUDGE_CALLS" ]; then wc -l < "$NUDGE_CALLS" | tr -d ' '; else echo 0; fi; }
wrc_log_count() { if [ -f "$WLOG" ]; then grep -c "$1" "$WLOG" || true; else echo 0; fi; }
wrc_field() { python3 -c "import yaml,sys; d=yaml.safe_load(open(sys.argv[1])); m=d['messages'][0]; print(m.get(sys.argv[2],''))" "$INBOX" "$1"; }

@test "T-WRC6-001: safe_nudge rc=6 -> watcher closes as delivered, no resend on later sweeps" {
    run wrc_run_watcher 6
    [ "$status" -eq 0 ]
    [ "$(cat "$INOTIFY_CNT")" -eq 2 ]
    [ "$(wrc_calls)" -eq 1 ]
    [ "$(wrc_field read)" = "True" ]
    [ "$(wrc_field acknowledged_by)" = "delivered" ]
    [ "$(wrc_field delivery_state)" = "delivered" ]
    grep -q 'msg_id: msg_20260917_000000_wrc6test' "$SB/queue/message_dedup.yaml"
    [ ! -f "$SB/queue/watchers/test_agent.retry.msg_20260917_000000_wrc6test" ]
    [ "$(wrc_log_count '"msg":"delivered_cooldown_write_failed"')" -eq 1 ]
    [ "$(wrc_log_count 'safe_nudge_unknown_rc')" -eq 0 ]
}

@test "T-WRC6-002: safe_nudge rc=0 -> delivered (unchanged baseline)" {
    run wrc_run_watcher 0
    [ "$status" -eq 0 ]
    [ "$(wrc_calls)" -eq 1 ]
    [ "$(wrc_field read)" = "True" ]
    [ "$(wrc_field acknowledged_by)" = "delivered" ]
    [ "$(wrc_log_count '"msg":"delivered"')" -eq 1 ]
    [ "$(wrc_log_count 'delivered_cooldown_write_failed')" -eq 0 ]
}

@test "T-WRC6-003: safe_nudge rc=1 (queued) -> retried on every sweep, never marked read (rc=1 semantics kept)" {
    run wrc_run_watcher 1
    [ "$status" -eq 0 ]
    [ "$(wrc_calls)" -eq 3 ]
    [ "$(wrc_field read)" = "False" ]
    [ ! -f "$SB/queue/message_dedup.yaml" ] || ! grep -q 'msg_20260917_000000_wrc6test' "$SB/queue/message_dedup.yaml"
    [ "$(wrc_log_count 'queued_cooldown')" -eq 3 ]
}

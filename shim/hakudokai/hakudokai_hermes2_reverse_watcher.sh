#!/usr/bin/env bash
# hakudokai_hermes2_reverse_watcher.sh — 環境部長(hermes2) 専用 wakeup watcher
#   副院長令 seq67427 (理事長令): Hermes 本物経路 (hakudokai_hermes_reverse_watcher.sh) と同型で
#   hermes2 pane 着火経路を新設。pc_handshake to_pc='hermes2' 未ACK を polling し、
#   /tmp/hermes2.sock の hermes2:0.0 pane へ tmux send-keys (文字+自動Enter) で起床通知 → ACK。
#
# 着火先が hermes user の private socket ゆえ送出は sudo -n -u hermes tmux -S /tmp/hermes2.sock 経由。
# Watcher Design Principles 順守: 単一instance lock / graceful exit / 手動停止flag / dedup /
#   rate-limit / max-fails alert / idempotency(ACK後 processed記録)。暴走防止 (2026-05-05事故教訓)。
#
# 実行: doppler run --project openhands --config dev -- bash <this> [--interval 5]
# 前提: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (doppler 注入)

set -u
GUARD_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/hermes2_reverse_guard.sh"
# shellcheck disable=SC1090
source "$GUARD_LIB"
SB_AUTH_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/sb_auth.sh"
# shellcheck disable=SC1090
source "$SB_AUTH_LIB"
SOCK="${H2_SOCK:-/tmp/hermes2.sock}"
H2_PANE="${H2_PANE:-hermes2:0.0}"
POLL_INTERVAL="${2:-5}"
PROCESSED_FILE="${H2_PROCESSED_FILE:-/tmp/hakudokai_hermes2_reverse_processed.txt}"
HEALTH_FILE="${H2_HEALTH_FILE:-/tmp/hakudokai_hermes2_reverse_health.json}"
LOG="${H2_WATCHER_LOG:-/tmp/hakudokai_hermes2_reverse_watcher.log}"
LAST_POKE_FILE="${H2_LAST_POKE_FILE:-/tmp/hakudokai_hermes2_reverse_lastpoke.ts}"
POKE_RATE_LIMIT_SEC="${H2_POKE_RATE_LIMIT_SEC:-120}"
DEFER_FILE="${H2_DEFER_FILE:-/tmp/hakudokai_hermes2_reverse_defer.count}"
DEFER_ALERT_AFTER="${H2_DEFER_ALERT_AFTER:-10}"
DEFER_ALERT_FILE="${H2_DEFER_ALERT_FILE:-/tmp/hakudokai_hermes2_reverse_defer.alert}"
FAIL_COUNT=0
MAX_FAILS=5
POLL_COUNT=0
PAYLOAD="New pc_handshake rows to_pc=hermes2 are waiting. Please SELECT unacknowledged rows and process them. -- Commander reverse-watcher"

GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
WATCHER_DISABLE="$HOME/.openclaw/disable_hermes2_reverse_watcher"

# 単一 instance lock
_LOCK_FILE="${H2_LOCK_FILE:-/tmp/hakudokai_hermes2_reverse_watcher.lock}"
exec 200>"$_LOCK_FILE"
if ! flock -n 200; then
  echo "[$(date -Iseconds)] [hermes2_reverse] another instance running, exit 0" >&2; exit 0
fi
trap 'echo "[$(date -Iseconds)] [hermes2_reverse] SIGTERM graceful exit" >&2; exit 0' SIGTERM SIGINT

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY required (run via doppler run)" >&2; exit 1
fi
touch "$PROCESSED_FILE"
export H2_LOG="$LOG"
log(){ h2_log "$1"; }
health(){ printf '{"timestamp":"%s","poll_count":%d,"fail_count":%d,"status":"running","interval":%d,"pane":"%s","socket":"%s"}\n' \
  "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$POLL_COUNT" "$FAIL_COUNT" "$POLL_INTERVAL" "$H2_PANE" "$SOCK" > "$HEALTH_FILE"; }

log "started (interval=${POLL_INTERVAL}s pane=${H2_PANE} socket=${SOCK})"
while true; do
  sleep "$POLL_INTERVAL"
  if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHER_DISABLE" ]; then log "DISABLED by flag — graceful exit"; rm -f "$HEALTH_FILE"; exit 0; fi
  POLL_COUNT=$((POLL_COUNT+1))

  RESP=$(sb_curl -sS -w "\n%{http_code}" \
    "${SUPABASE_URL}/rest/v1/pc_handshake?to_pc=eq.hermes2&acknowledged_at=is.null&order=created_at.desc&limit=20&select=id,seq,from_pc,created_at,requires_response,message_type,priority,topic,context_data" \
    2>/dev/null)
  CODE=$(echo "$RESP" | tail -1); BODY=$(echo "$RESP" | sed '$d')
  if [ "$CODE" != "200" ]; then
    FAIL_COUNT=$((FAIL_COUNT+1)); log "poll FAILED http=$CODE fail=$FAIL_COUNT"
    [ "$FAIL_COUNT" -ge "$MAX_FAILS" ] && log "ALERT: ${MAX_FAILS} consecutive poll failures"
    health; continue
  fi
  FAIL_COUNT=0
  [ "$BODY" = "[]" ] || [ -z "$BODY" ] && { health; continue; }

  # Telemetry is durable machine state, not a human letter. ACK it silently and
  # remove it before pane eligibility so telemetry can never generate H2WAKE.
  TELEMETRY_BODY=$(H2_INBOUND_JSON="$BODY" h2_filter_telemetry_json)
  TELEMETRY_IDS=$(echo "$TELEMETRY_BODY" | python3 -c 'import json,sys; print(" ".join(r["id"] for r in json.load(sys.stdin) if r.get("id")))')
  for id in $TELEMETRY_IDS; do
    ACK_BODY="/tmp/hakudokai_hermes2_telemetry_ack-${id}.json"
    ACODE=$(sb_curl -sS -o "$ACK_BODY" -w "%{http_code}" -X PATCH \
      "${SUPABASE_URL}/rest/v1/pc_handshake?id=eq.${id}&acknowledged_at=is.null" \
      -H "Content-Type: application/json" -H "Prefer: return=minimal" \
      -d "{\"acknowledged_at\":\"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\",\"acknowledged_by\":\"system\",\"verification_context\":{\"ack_actor\":\"hermes2-delivery-bridge\",\"basis\":\"telemetry_silent_route_filtered_no_pane_delivery\"}}" 2>/dev/null)
    if [ "$ACODE" = "204" ] || [ "$ACODE" = "200" ]; then
      echo "$id" >> "$PROCESSED_FILE"
      log "telemetry silently ACKed without pane wake id=${id:0:8}"
    else
      log "telemetry ACK failed id=${id:0:8} http=$ACODE; left unprocessed"
    fi
  done
  BODY=$(H2_INBOUND_JSON="$BODY" h2_filter_actionable_json)
  [ "$BODY" = "[]" ] || [ -z "$BODY" ] && { health; continue; }

  # ACK is a delivery marker, not task state. Rows can remain unACKed after
  # Hermes2 has already returned a parented work_started/answer/blocker. Do not
  # wake the pane for those completed deliveries; otherwise the same backlog is
  # re-injected forever when the ACK bridge is unavailable.
  PARENT_IDS=$(echo "$BODY" | python3 -c 'import json,sys; print(",".join(r["id"] for r in json.load(sys.stdin) if r.get("id")))')
  CHILD_RESP=$(sb_curl -sS -w "\n%{http_code}" \
    "${SUPABASE_URL}/rest/v1/pc_handshake?parent_message_id=in.(${PARENT_IDS})&select=parent_message_id&limit=200" \
    2>/dev/null)
  CHILD_CODE=$(echo "$CHILD_RESP" | tail -1); CHILD_BODY=$(echo "$CHILD_RESP" | sed '$d')
  if [ "$CHILD_CODE" != "200" ]; then
    FAIL_COUNT=$((FAIL_COUNT+1)); log "child-state poll FAILED http=$CHILD_CODE fail=$FAIL_COUNT; fail closed without pane poke"
    health; continue
  fi
  BEFORE_COUNT=$(echo "$BODY" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))')
  BODY=$(H2_INBOUND_JSON="$BODY" H2_CHILD_JSON="$CHILD_BODY" h2_filter_unanswered_json)
  AFTER_COUNT=$(echo "$BODY" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))')
  SUPPRESSED_COUNT=$((BEFORE_COUNT-AFTER_COUNT))
  [ "$SUPPRESSED_COUNT" -gt 0 ] && log "suppressed $SUPPRESSED_COUNT already-parented rows"
  [ "$BODY" = "[]" ] || [ -z "$BODY" ] && { health; continue; }

  # 新規(未processed)行を抽出
  NEW_IDS=$(echo "$BODY" | python3 -c '
import sys,json
seen=set(open("'"$PROCESSED_FILE"'").read().split()) if __import__("os").path.exists("'"$PROCESSED_FILE"'") else set()
rows=json.load(sys.stdin)
fresh=[r["id"] for r in rows if r.get("id") and r["id"] not in seen]
print(" ".join(fresh))')
  [ -z "$NEW_IDS" ] && { health; continue; }
  NCOUNT=$(echo "$NEW_IDS" | wc -w)
  log "detected $NCOUNT fresh to_pc=hermes2 rows"

  # 1 poll = 1 bundled pane poke, rate-limited. Do not ACK before a real
  # pane poke succeeds; otherwise a failed/stuck paste can hide the row forever.
  NOW=$(date +%s); LAST=$(cat "$LAST_POKE_FILE" 2>/dev/null || echo 0)
  if [ $((NOW-LAST)) -lt "$POKE_RATE_LIMIT_SEC" ]; then
    log "poke rate-limited ($((NOW-LAST))s<${POKE_RATE_LIMIT_SEC}s) — left unACKed for next poll"
    health
    continue
  fi

  SEQ_LIST=$(echo "$BODY" | NEW_IDS="$NEW_IDS" python3 -c 'import os,sys,json; wanted=set(os.environ.get("NEW_IDS","").split()); rows=json.load(sys.stdin); print(",".join(str(r.get("seq")) for r in rows if r.get("id") in wanted))')
  # Keep the pane notice short. A token on the first composer line makes the
  # conditional repeat and positive-delivery checks reliable even when seqs wrap.
  DELIVERY_TOKEN="H2WAKE:${NOW}"
  FULL_PAYLOAD="${DELIVERY_TOKEN} ${PAYLOAD} seqs=${SEQ_LIST}"

  if sudo -n -u hermes tmux -S "$SOCK" has-session -t hermes2 2>/dev/null; then
    # ★2026-08-13 iincho: 壊れているpaneは叩かない(死のスパイラル封じ)★
    # 相手が context 超過で応答不能な時、起床通知は「起こす」ではなく「埋める」。
    # 叩くたびに context が増え、二度と圧縮できなくなる(実測 479k->499k)。
    BROKEN_CAP="/tmp/hakudokai_hermes2_broken_check.txt"
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -40 >"$BROKEN_CAP" 2>/dev/null || true
    if grep -qE "Context length exceeded|Cannot compress further" "$BROKEN_CAP" 2>/dev/null; then
      BROKEN_MARK="/tmp/hakudokai_hermes2_broken_notified"
      BNOW=$(date +%s); BLAST=$(cat "$BROKEN_MARK" 2>/dev/null || echo 0)
      log "poke SUPPRESSED: pane is context-broken (叩けば悪化する). unACKed rows kept for later."
      if [ $((BNOW-BLAST)) -ge 3600 ]; then
        echo "$BNOW" > "$BROKEN_MARK"
        log "escalate: hermes2 context-broken >=1h notice (委員長へ)"
      fi
      health; continue
    fi

    # Require three unchanged explicit idle+empty-composer captures. Absence of
    # a busy word is never idle proof; modal/no-composer screens fail closed.
    CAPTURE_PRE1="/tmp/hakudokai_hermes2_delivery-${NOW}-pre1.txt"
    CAPTURE_PRE2="/tmp/hakudokai_hermes2_delivery-${NOW}-pre2.txt"
    CAPTURE_PRE3="/tmp/hakudokai_hermes2_delivery-${NOW}-pre3.txt"
    # shellcheck disable=SC2024
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -80 >"$CAPTURE_PRE1" 2>>"$LOG" || { log "poke deferred: preflight capture1 failed"; health; continue; }
    sleep 2
    # shellcheck disable=SC2024
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -80 >"$CAPTURE_PRE2" 2>>"$LOG" || { log "poke deferred: preflight capture2 failed"; health; continue; }
    sleep 2
    # shellcheck disable=SC2024
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -80 >"$CAPTURE_PRE3" 2>>"$LOG" || { log "poke deferred: preflight capture3 failed"; health; continue; }
    if ! h2_stable_idle "$CAPTURE_PRE1" "$CAPTURE_PRE2" "$CAPTURE_PRE3"; then
      DEFER_COUNT=$(cat "$DEFER_FILE" 2>/dev/null || echo 0)
      case "$DEFER_COUNT" in (*[!0-9]*) DEFER_COUNT=0;; esac
      DEFER_COUNT=$((DEFER_COUNT+1)); printf '%s\n' "$DEFER_COUNT" >"$DEFER_FILE"
      log "poke deferred: no stable explicit idle+empty composer across 3 samples; defer_count=$DEFER_COUNT; no paste/send"
      if [ "$DEFER_COUNT" -ge "$DEFER_ALERT_AFTER" ]; then
        # Durable handoff signal. Never force-paste into an unproven composer.
        printf '{"status":"delegation_required","defer_count":%s,"seqs":"%s","detected_at":"%s","owner_order":["iincho","shogun-third","shogun-second","shogun-main"]}\n' \
          "$DEFER_COUNT" "$SEQ_LIST" "$(date -Is)" >"$DEFER_ALERT_FILE.tmp"
        mv "$DEFER_ALERT_FILE.tmp" "$DEFER_ALERT_FILE"
        log "DEFER_LIMIT_REACHED count=$DEFER_COUNT delegation alert=$DEFER_ALERT_FILE"
      fi
      health
      continue
    fi
    printf '0\n' >"$DEFER_FILE"
    # Empty composer is proven; never send C-u. Paste via tmux buffer.
    sudo -n -u hermes tmux -S "$SOCK" set-buffer -- "$FULL_PAYLOAD" 2>>"$LOG" || { log "poke failed: set-buffer"; health; continue; }
    sudo -n -u hermes tmux -S "$SOCK" paste-buffer -t "$H2_PANE" 2>>"$LOG" || { log "poke failed: paste-buffer"; health; continue; }
    sleep 1
    # Target-calibrated Hermes contract: literal CSI-u (ESC [ 1 3 u) submits.
    # Extra submissions can enqueue duplicate turns, so never send an unconditional submit×N.
    # One repeat is allowed only when a fresh capture proves the token remains.
    sudo -n -u hermes tmux -S "$SOCK" send-keys -t "$H2_PANE" -H 1b 5b 31 33 75 2>>"$LOG" || { log "poke failed: CSI-u submit-one"; health; continue; }
    sleep 1
    CAPTURE_POST1="/tmp/hakudokai_hermes2_delivery-${NOW}-post1.txt"
    # shellcheck disable=SC2024
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -80 >"$CAPTURE_POST1" 2>>"$LOG" || { log "poke failed: post1 capture"; health; continue; }
    if h2_payload_in_composer "$CAPTURE_POST1" "$DELIVERY_TOKEN"; then
      sudo -n -u hermes tmux -S "$SOCK" send-keys -t "$H2_PANE" -H 1b 5b 31 33 75 2>>"$LOG" || { log "poke failed: CSI-u fallback"; health; continue; }
    fi
    sleep 2
    CAPTURE_POST2="/tmp/hakudokai_hermes2_delivery-${NOW}-post2.txt"
    # shellcheck disable=SC2024
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -80 >"$CAPTURE_POST2" 2>>"$LOG" || { log "poke failed: post2 capture"; health; continue; }
    sleep 2
    CAPTURE_POST3="/tmp/hakudokai_hermes2_delivery-${NOW}-post3.txt"
    # shellcheck disable=SC2024
    sudo -n -u hermes tmux -S "$SOCK" capture-pane -p -t "$H2_PANE" -S -80 >"$CAPTURE_POST3" 2>>"$LOG" || { log "poke failed: post3 capture"; health; continue; }
    if ! h2_delivery_positive_multi "$DELIVERY_TOKEN" "$CAPTURE_POST1" "$CAPTURE_POST2" "$CAPTURE_POST3"; then
      log "submission not positively confirmed across multiple captures; left unACKed and unprocessed"
      health
      continue
    fi
    echo "$NOW" > "$LAST_POKE_FILE"
    log "POKED hermes2 pane (bundled $NCOUNT rows seqs=$SEQ_LIST); captures=$CAPTURE_POST1,$CAPTURE_POST2,$CAPTURE_POST3"
  else
    log "hermes2 session absent on $SOCK — left unACKed for next poll"
    health
    continue
  fi

  # Hermes2 has no direct ACK credential. Only after positive visible processing
  # evidence (never input-clear alone), the existing delivery bridge records a machine ACK under a
  # distinct identity. This is not evidence of task completion or an answer.
  for id in $NEW_IDS; do
    ACK_BODY="/tmp/hakudokai_hermes2_ack-${id}.json"
    ACODE=$(sb_curl -sS -o "$ACK_BODY" -w "%{http_code}" -X PATCH \
      "${SUPABASE_URL}/rest/v1/pc_handshake?id=eq.${id}&acknowledged_at=is.null" \
      -H "Content-Type: application/json" -H "Prefer: return=minimal" \
      -d "{\"acknowledged_at\":\"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\",\"acknowledged_by\":\"system\",\"verification_context\":{\"ack_actor\":\"hermes2-delivery-bridge\",\"basis\":\"positive_multi_capture_after_three_stable_idle_samples\"}}" 2>/dev/null)
    if [ "$ACODE" = "204" ] || [ "$ACODE" = "200" ]; then
      echo "$id" >> "$PROCESSED_FILE"
      log "machine ACK recorded after visible submit id=${id:0:8} capture=$CAPTURE_POST3"
    else
      ACK_ERROR=$(tr '\n' ' ' <"$ACK_BODY" | head -c 500)
      log "machine ACK failed id=${id:0:8} http=$ACODE error=$ACK_ERROR; left unprocessed"
    fi
  done
  health
done

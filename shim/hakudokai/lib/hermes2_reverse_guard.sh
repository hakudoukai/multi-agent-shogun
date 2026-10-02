#!/usr/bin/env bash
# Pure, side-effect-bounded guards shared by the ThirdPC hermes2 reverse watcher.

h2_owner_identity() {
  local host="${1:-}"
  case "$host" in
    momizi-dx) printf '%s\n' 'third_pc|ThirdPC|hakudoukai_main' ;;
    *) printf 'refusing non-Third owner host: %s\n' "$host" >&2; return 78 ;;
  esac
}

h2_pane_safe_to_inject() {
  # ★starvefix-20260808(委員長)★ busy語の検査帯を分離した。
  #   旧実装はtail30行へ一括grepし、過去turnの「Tool calls」履歴表示を現在busyと誤読
  #   →新着18件を検知しながら42分poke deferの飢餓(実測15:0x-15:4x)。
  #   現在の状態はstatus/composer帯(末尾6行)にしか出ない。modal系だけ全域で見る。
  local capture="$1" tail_text status_zone composer hard_busy soft_processing
  [ -r "$capture" ] || return 2
  tail_text=$(tail -n 30 "$capture")
  status_zone=$(printf '%s\n' "$tail_text" | tail -n 6)
  if printf '%s\n' "$tail_text" | grep -Eiq -- 'approval required|security scan|allow once|allow this session|always allow|quick pick|are you sure|confirm(ation)? required'; then
    return 1
  fi
  composer=$(printf '%s\n' "$tail_text" | grep -E '^[[:space:]]*(❯|>)[[:space:]]*' | tail -n 1 || true)
  # No explicit composer means a modal/approval/alternate screen: fail closed.
  [ -n "$composer" ] || return 1
  composer=$(printf '%s' "$composer" | python3 -c 'import re,sys; s=sys.stdin.read(); s=re.sub(r"^\s*(❯|>)", "", s); print(s.replace("\u00a0", "").strip(), end="")')
  [ -z "$composer" ] || return 1

  # Hermes 0.20.5 keeps a static border/status label containing the bare word
  # "processing" after the turn has returned to an explicit empty composer.
  # Treating that one stale label as live activity starved the role for 47+
  # consecutive polls.  Hard activity indicators remain fail-closed.  A bare
  # processing label is admitted only on a box-drawing status row; the caller's
  # three-sample stability gate must still pass.
  hard_busy=$(printf '%s\n' "$status_zone" | grep -Eic -- 'queued \([1-9][0-9]*\)|reasoning|contemplating|thinking|working|retrying|Ctrl[+-]C to interrupt|stop(ping)? button|…[[:space:]]*·' || true)
  [ "$hard_busy" -eq 0 ] || return 1
  soft_processing=$(printf '%s\n' "$status_zone" | grep -Ei -- 'processing' || true)
  if [ -n "$soft_processing" ]; then
    printf '%s\n' "$soft_processing" | grep -Eq '^[[:space:]]*[─━┄┅┈┉╌╍]' || return 1
  fi
  return 0
}

h2_stable_idle() {
  # ★starvefix-20260808★ 安定性はcomposer行の同一性で判る。
  #   旧実装のtail30 cmpは秒針つきstatus行(✓ 18m 57s等)を含み、毎サンプル差分→永遠に不安定。
  [ "$#" -ge 3 ] || return 2
  local first="$1" f ref cur ref_status cur_status
  h2_pane_safe_to_inject "$first" || return 1
  ref=$(tail -n 30 "$first" | grep -E '^[[:space:]]*(❯|>)' | tail -n 1)
  ref_status=$(tail -n 30 "$first" | tail -n 6)
  shift
  for f in "$@"; do
    h2_pane_safe_to_inject "$f" || return 1
    cur=$(tail -n 30 "$f" | grep -E '^[[:space:]]*(❯|>)' | tail -n 1)
    [ "$cur" = "$ref" ] || return 1
    # When the admitted soft 0.20.5 label is present, its complete status zone
    # must also be byte-stable across all three samples.
    if printf '%s\n' "$ref_status" | grep -Eiq -- 'processing'; then
      cur_status=$(tail -n 30 "$f" | tail -n 6)
      [ "$cur_status" = "$ref_status" ] || return 1
    fi
  done
}

h2_filter_unanswered_json() {
  python3 - <<'PY'
import json
import os

rows = json.loads(os.environ.get("H2_INBOUND_JSON", "[]"))
children = json.loads(os.environ.get("H2_CHILD_JSON", "[]"))
answered = {row.get("parent_message_id") for row in children if row.get("parent_message_id")}
unanswered = [
    row for row in rows
    if row.get("id") not in answered
]
print(json.dumps(unanswered, separators=(",", ":")))
PY
}

h2_filter_telemetry_json() {
  python3 - <<'PY'
import json
import os
rows=json.loads(os.environ.get("H2_INBOUND_JSON", "[]"))
def is_telemetry(row):
    ctx=row.get("context_data") or {}
    if isinstance(ctx,str):
        try: ctx=json.loads(ctx)
        except Exception: ctx={}
    known={"inbox_unread_alert","inbox_adjudication_alert","inbox_watermark_registration_alert","inbox_head_of_line_alert","desktop_bell_bounce","inbox_read_watermark"}
    return ctx.get("telemetry") is True or str(row.get("topic") or "").startswith("telemetry_") or ctx.get("kind") in known
print(json.dumps([row for row in rows if is_telemetry(row)],separators=(",", ":")))
PY
}

h2_filter_actionable_json() {
  python3 - <<'PY'
import json
import os
rows=json.loads(os.environ.get("H2_INBOUND_JSON", "[]"))
def is_telemetry(row):
    ctx=row.get("context_data") or {}
    if isinstance(ctx,str):
        try: ctx=json.loads(ctx)
        except Exception: ctx={}
    known={"inbox_unread_alert","inbox_adjudication_alert","inbox_watermark_registration_alert","inbox_head_of_line_alert","desktop_bell_bounce","inbox_read_watermark"}
    return ctx.get("telemetry") is True or str(row.get("topic") or "").startswith("telemetry_") or ctx.get("kind") in known
print(json.dumps([row for row in rows if not is_telemetry(row)],separators=(",", ":")))
PY
}

h2_payload_in_composer() {
  local capture="$1" payload_token="$2" tail_text
  [ -r "$capture" ] || return 2
  tail_text=$(tail -n 30 "$capture")
  printf '%s\n' "$tail_text" | grep -E '^[[:space:]]*(❯|>)' | tail -n 1 | grep -Fq -- "$payload_token"
}

h2_delivery_positive_multi() {
  local payload_token="$1" f tail_text positives=0
  shift
  [ "$#" -ge 2 ] || return 2
  for f in "$@"; do
    [ -r "$f" ] || return 2
    tail_text=$(tail -n 40 "$f")
    if printf '%s\n' "$tail_text" | grep -Eiq -- 'approval required|security scan|allow once|allow this session|always allow|quick pick|(^|[^[:alpha:]])deny([^[:alpha:]]|$)|are you sure|confirm(ation)? required|select.*enter'; then
      return 1
    fi
    h2_payload_in_composer "$f" "$payload_token" && return 1
    if printf '%s\n' "$tail_text" | grep -Fq -- "$payload_token"; then
      positives=$((positives+1))
    elif printf '%s\n' "$tail_text" | grep -Eiq -- 'reasoning|contemplating|thinking|processing|working|retrying|Ctrl[+-]C to interrupt|tool calls|…[[:space:]]*·'; then
      positives=$((positives+1))
    fi
  done
  [ "$positives" -ge 2 ]
}

# Compatibility wrapper for focused single-capture unit checks only.
h2_delivery_positive() {
  local capture="$1" payload_token="${2:-}" tail_text
  [ -r "$capture" ] || return 2
  tail_text=$(tail -n 30 "$capture")
  h2_payload_in_composer "$capture" "$payload_token" && return 1
  printf '%s\n' "$tail_text" | grep -Eiq -- 'reasoning|contemplating|thinking|processing|working|Ctrl[+-]C to interrupt|tool calls|…[[:space:]]*·'
}

h2_log() {
  local msg="$1"
  : "${H2_LOG:?H2_LOG must be set}"
  printf '[hermes2_reverse][%s] %s\n' "$(date '+%H:%M:%S')" "$msg" >>"$H2_LOG"
}

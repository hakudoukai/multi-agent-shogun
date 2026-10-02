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

# ★a6c0f720 ⑴★ 同じ seq の組は状態が変わるまで再び起こさない。
#   旧版は「processed 済み id 以外」を毎 poll 新着と見做した。ところが machine ACK は
#   門(HUMAN_ACK_ONLY)に拒まれて processed に入らず、同じ組が rate-limit 毎に再着火した。
#   ここでは行の状態キー(id|seq|priority|requires_response|message_type)を起こした記録と比べ、
#   初めて見たキーか状態の変はつたキーが在る時だけ起こす。減つただけ・同じだけなら起こさない。
# 入力: env H2_ROWS_JSON(起こす候補の行) / H2_WOKEN_STATE(起こした記録の file)
# 出力: 1行目 wake|quiet、2行目 起こすべき id(空白区切り)
h2_wake_select() {
  python3 - <<'PY'
import json
import os

rows = json.loads(os.environ.get("H2_ROWS_JSON", "[]") or "[]")
path = os.environ.get("H2_WOKEN_STATE", "")
woken = set()
if path and os.path.exists(path):
    with open(path) as f:
        woken = {line.strip() for line in f if line.strip()}

def key(row):
    return "|".join(str(row.get(k)) for k in ("id", "seq", "priority", "requires_response", "message_type"))

fresh = [row["id"] for row in rows if row.get("id") and key(row) not in woken]
print("wake" if fresh else "quiet")
print(" ".join(fresh))
PY
}

# 起こした行の状態キーを記録へ足す(和集合・末尾 H2_WOKEN_KEEP 行だけ残す)。
# 入力: env H2_ROWS_JSON / H2_WOKEN_STATE / H2_WAKE_IDS(今回起こした id)
h2_wake_record() {
  python3 - <<'PY'
import json
import os

rows = json.loads(os.environ.get("H2_ROWS_JSON", "[]") or "[]")
path = os.environ["H2_WOKEN_STATE"]
ids = set(os.environ.get("H2_WAKE_IDS", "").split())
keep = int(os.environ.get("H2_WOKEN_KEEP", "5000"))
old = []
if os.path.exists(path):
    with open(path) as f:
        old = [line.strip() for line in f if line.strip()]
seen = set(old)
for row in rows:
    if row.get("id") in ids:
        k = "|".join(str(row.get(c)) for c in ("id", "seq", "priority", "requires_response", "message_type"))
        if k not in seen:
            old.append(k)
            seen.add(k)
tmp = path + ".tmp"
with open(tmp, "w") as f:
    f.write("".join(line + "\n" for line in old[-keep:]))
os.replace(tmp, path)
PY
}

# ★a6c0f720 ⑶★ system の ack が門に拒まれた時は黙らず記録する。
#   門の拒否(http 400 かつ P0001 / HUMAN_ACK_ONLY)は一行の JSONL として id ごとに一度だけ帳へ書く。
#   使ひ方: h2_ack_reject_record <ledger> <id> <seq> <http> <body_file> <kind>
#   戻り値: 0=門の拒否として今回初めて記録 / 3=門の拒否で記録済み / 1=門の拒否ではない(他の失敗)
h2_ack_reject_record() {
  H2_REJ_LEDGER="$1" H2_REJ_ID="$2" H2_REJ_SEQ="$3" H2_REJ_HTTP="$4" H2_REJ_BODY="$5" H2_REJ_KIND="$6" python3 - <<'PY'
import datetime
import json
import os
import sys

body = ""
try:
    with open(os.environ["H2_REJ_BODY"], errors="replace") as f:
        body = f.read()
except OSError:
    pass
code = message = ""
try:
    parsed = json.loads(body)
    code = str(parsed.get("code") or "")
    message = str(parsed.get("message") or "")
except Exception:
    message = body
gate = os.environ["H2_REJ_HTTP"] == "400" and (code == "P0001" or "HUMAN_ACK_ONLY" in body)
if not gate:
    sys.exit(1)
ledger = os.environ["H2_REJ_LEDGER"]
rid = os.environ["H2_REJ_ID"]
if os.path.exists(ledger):
    with open(ledger) as f:
        for line in f:
            try:
                if json.loads(line).get("id") == rid:
                    sys.exit(3)
            except Exception:
                continue
entry = {
    "recorded_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "id": rid,
    "seq": os.environ["H2_REJ_SEQ"],
    "kind": os.environ["H2_REJ_KIND"],
    "http": os.environ["H2_REJ_HTTP"],
    "code": code,
    "message_head": message.replace("\n", " ")[:200],
}
with open(ledger, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
PY
}

# 帳に門の拒否として載つてゐる id か(載つてゐれば PATCH を繰り返さない)。
h2_ack_gate_rejected() {
  local ledger="$1" id="$2"
  [ -r "$ledger" ] || return 1
  grep -Fq -- "\"id\": \"$id\"" "$ledger"
}

h2_log() {
  local msg="$1"
  : "${H2_LOG:?H2_LOG must be set}"
  printf '[hermes2_reverse][%s] %s\n' "$(date '+%H:%M:%S')" "$msg" >>"$H2_LOG"
}

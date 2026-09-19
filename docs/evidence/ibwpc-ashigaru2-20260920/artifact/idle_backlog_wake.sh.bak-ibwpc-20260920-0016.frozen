#!/bin/bash
# idle_backlog_wake.sh — IDLE-BACKLOG-WAKE(canon self-work-pull 機械部B) 2026-08-31 総監督
# 「idle席 × 未処理>0」へ★seq-only 1行★を注入しturnを立てる。受け渡しネックの根治(グリル3adc1664 案B)。
# 器4要件: 0件/測れないを別値・陽性対照(自己検定)・母数明示・★限界=注入の実効はpane形式に依存(下記gap)★
# gap: ⑴走行中/ダイアログ席には注入しない(安全側スキップ=その席は次tickまで残る)
#      ⑵「未処理」は板assigned+要返答未ackのみ(local yaml箱は数えない)
#      ⑶wake自身の生死はfleet-guard.timerと同居で相互可視(単独では誰も見ない)
set -u
ENVF="${IBW_ENV_FILE:-/mnt/c/DentalBI/backend/.env}"
STATE_DIR="${IBW_STATE_DIR:-$HOME/.local/state/idle-backlog-wake}"; mkdir -p "$STATE_DIR"
COOLDOWN=2700  # 45min
NOW=$(date +%s)
TS=$(date +%H:%M)

# STALL-WAKE marker consumer (board 8546ccad). The existing timer owns
# scheduling; this source only classifies markers and consumes after a
# successful one-line wake. Unknown/empty/stale markers are retained.
STALL_WAKE_LIB="${STALL_WAKE_LIB:-$HOME/bin/stall_wake_lib.sh}"
STALL_MARKER_DIR="${STALL_MARKER_DIR:-$HOME/multi-agent-shogun/queue/goals}"
STALL_STATE_DIR="${STALL_STATE_DIR:-${STATE_DIR}/stall-markers}"
STALL_ROSTER="${STALL_ROSTER:-ashigaru-third-1 ashigaru-third-2 ashigaru-third-3 ashigaru-third-4 ashigaru-third-5 ashigaru-third-6 karo-third shogun-third}"

# --- creds: 環境変数優先(doppler run対応)→ENVF fallback。測れなければfail-loud
SB_URL="${SUPABASE_URL:-}"
SB_KEY="${SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_KEY:-}}"
if { [ -z "$SB_URL" ] || [ -z "$SB_KEY" ]; } && [ -f "$ENVF" ]; then
  SB_URL=$(grep -E '^SUPABASE_URL=' "$ENVF" | head -1 | cut -d= -f2- | tr -d '"\r')
  SB_KEY=$(grep -E '^SUPABASE_(SERVICE_ROLE_KEY|KEY)=' "$ENVF" | head -1 | cut -d= -f2- | tr -d '"\r')
fi
if [ -z "${SB_URL:-}" ] || [ -z "${SB_KEY:-}" ]; then
  echo "$TS MEASUREMENT_FAILED creds不在($ENVF) — 0件ではない"; exit 3
fi

# P2 93829374: canonical queue/inbox/<agent>.yaml の未読も wake 条件に含める。
# legacy ashigaru{1,2,3}.yaml の実体名を焼き込まず、canonical 名で読む。
IBW_INBOX_DIR="${IBW_INBOX_DIR:-/home/hakudokai/projects/multi-agent-shogun/queue/inbox}"
yaml_unread_count() { # $1=canonical role -> integer or MEAS_FAIL
  local role="$1" f
  case "$role" in
    ashigaru-second-1|ashigaru-second-2|ashigaru-second-3)
      f="$IBW_INBOX_DIR/${role}.yaml" ;;
    *) echo 0; return 0 ;;
  esac
  [ -f "$f" ] || { echo MEAS_FAIL; return 0; }
  python3 - "$f" <<'PY' 2>/dev/null || echo MEAS_FAIL
import sys, yaml
try:
    d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
    print(sum(1 for m in (d.get("messages") or []) if not m.get("read")))
except Exception:
    print("MEAS_FAIL")
PY
}

rest_count() { # $1=path+query  → prints integer or MEAS_FAIL
  local r
  r=$(curl -sf -m 12 -H "apikey: $SB_KEY" -H "Authorization: Bearer $SB_KEY" \
      -H "Prefer: count=exact" -H "Range: 0-0" "$SB_URL/rest/v1/$1" -o /dev/null -w '%{header_json}' 2>/dev/null \
      | grep -o '"content-range":\["[^"]*"\]' | grep -o '/[0-9]*' | tr -d /)
  if [ -z "$r" ]; then echo MEAS_FAIL; else echo "$r"; fi
}

rest_json() { # $1=path+query → JSON or MEAS_FAIL
  local r
  r=$(curl -sf -m 12 -H "apikey: $SB_KEY" -H "Authorization: Bearer $SB_KEY" "$SB_URL/rest/v1/$1" 2>/dev/null) || { echo MEAS_FAIL; return; }
  echo "$r"
}
board_top() { # $1=query(select/order/limit以外) → "id8|title40|owner|prio|age_h" or "" or MEAS_FAIL
  local j
  j=$(rest_json "task_tracker?select=id,task_title,owner_role,priority,updated_at&$1&order=priority.asc.nullslast,sort_order.asc&limit=1")
  [ "$j" = MEAS_FAIL ] && { echo MEAS_FAIL; return; }
  python3 -c 'import sys,json,datetime
r=json.load(sys.stdin)
if not r: print(""); sys.exit()
x=r[0]; u=x.get("updated_at") or ""
try:
    t=datetime.datetime.fromisoformat(u.replace("Z","+00:00")); age=(datetime.datetime.now(datetime.timezone.utc)-t).total_seconds()/3600
except Exception: age=-1
print("%s|%s|%s|%s|%.1f" % (x["id"][:8], (x.get("task_title") or "")[:40].replace("\n"," ").replace("|","/"), x.get("owner_role") or "-", x.get("priority") if x.get("priority") is not None else "-", age))' <<< "$j"
}
notify_kantoku() { # $1=content  機械便(sender=idle-backlog-wake)を監督の箱へ1通。呼び手が「行ごと1回」を保証する
  if [ "${IBW_DRY_RUN:-0}" = 1 ]; then echo "$TS DRY letter→fukuincho: $1"; return 0; fi
  local body
  body=$(python3 -c 'import sys,json
print(json.dumps({"from_pc":"third_pc","to_pc":"third_pc","topic":"telemetry_fukuincho","message_type":"status_update","requires_response":False,
 "content":sys.argv[1],"context_data":{"sender_agent":"idle-backlog-wake","origin_agent":"idle-backlog-wake","machine":True,"kind":"情報共有"}},ensure_ascii=False))' "$1")
  curl -sf -m 12 -X POST -H "apikey: $SB_KEY" -H "Authorization: Bearer $SB_KEY" -H "Content-Type: application/json" -H "Prefer: return=minimal" \
    "$SB_URL/rest/v1/pc_handshake" -d "$body" >/dev/null 2>&1 && return 0
  echo "$TS LETTER_FAIL fukuincho"; return 1
}

# --- 席表: name|pane|kind(claude/hermes)|pc|role
# 4PC統一配置(理事長ご下命 2026-08-31 15:5x)=各PCの★將軍+事業部長★。既定はIBW_PC(third/main/second/mac)で自PC分を選ぶ。
case "${IBW_PC:-third}" in
  third)  DEF="shogun-third|shogun-third:0.0|claude|third_pc|shogun-third
handoverdocs|hermes-handoverdocs:0.0|hermes|third_pc|handoverdocs
commander|commander-third:0.0|hermes|third_pc|commander
sodanyaku|hermes-sodanyaku:0.0|hermes|third_pc|sodanyaku
fukuincho|hermes-kantoku:0.0|hermes|third_pc|fukuincho" ;;
  main)   DEF="shogun-main|shogun-main:0.0|claude|main_pc|shogun-main
training-main|training-consult-main:0.0|hermes|main_pc|training-main" ;;
  second) DEF="honbucho|hermes-honbucho:0.0|hermes|second_pc|honbucho
ashigaru-second-1|multiagent-second:0.0|claude|second_pc|ashigaru-second-1
ashigaru-second-2|multiagent-second:0.1|claude|second_pc|ashigaru-second-2
ashigaru-second-3|multiagent-second:0.2|claude|second_pc|ashigaru-second-3" ;;
  mac)    DEF="shogun-mac|shogun-mac:0.0|claude|mac_pc|shogun-mac
gakushu-bucho|gakushu-bucho:0.0|hermes|mac_pc|gakushu-bucho" ;;
  *) DEF="" ;;
esac
SEATS="${IBW_SEATS:-$DEF}"

stall_wake_one() {
  local marker="$1" agent pane
  agent="$(_stall_wake_agent_from_path "$marker")" || return 2
  case "$agent" in
    ashigaru-third-1) pane="multiagent-third:0.1" ;;
    ashigaru-third-2) pane="multiagent-third:0.2" ;;
    ashigaru-third-3) pane="multiagent-third:0.3" ;;
    ashigaru-third-4) pane="multiagent-third:0.4" ;;
    ashigaru-third-5) pane="multiagent-third:0.5" ;;
    ashigaru-third-6) pane="multiagent-third:0.6" ;;
    karo-third) pane="multiagent-third:0.0" ;;
    shogun-third) pane="shogun-third:0.0" ;;
    *) return 2 ;;
  esac
  tmux display-message -t "$pane" -p '#{@agent_id}' 2>/dev/null | grep -qx "$agent" || return 3
  tmux send-keys -t "$pane" -l '[STALL-WAKE] API断で中断した所から再開せよ。何をしていたかを1行書いてから続けよ。' 2>/dev/null || return 4
  tmux send-keys -t "$pane" Enter 2>/dev/null || return 5
  return 0
}

stall_seen=0; stall_wake_n=0; stall_fail=0
if [ "${IBW_PC:-third}" = third ] && [ -r "$STALL_WAKE_LIB" ]; then
  # shellcheck source=/home/hakudoukai/bin/stall_wake_lib.sh
  . "$STALL_WAKE_LIB"
  for marker in "$STALL_MARKER_DIR"/stall-*.marker; do
    [ -e "$marker" ] || continue
    stall_seen=$((stall_seen+1))
    out=$(stall_wake_process "$marker" "$STALL_ROSTER" "$STALL_STATE_DIR" -- stall_wake_one "$marker")
    case "$out" in
      fresh*consumed*) stall_wake_n=$((stall_wake_n+1)) ;;
      fresh*wake_failed*|fresh*consume_failed*) stall_fail=$((stall_fail+1)) ;;
    esac
    echo "$TS STALL $out"
  done
elif [ "${IBW_PC:-third}" = third ]; then
  echo "$TS STALL MEAS_FAIL unreadable_lib=$STALL_WAKE_LIB"
  stall_fail=$((stall_fail+1))
fi

# --- PC最上段の放置検知(理事長ご提案 2026-09-03「他者所有が最上段に居座り席が待つ→スキップし監督へ報せる仕組み」)
PCNAME=$(printf '%s\n' "$SEATS" | head -1 | cut -d'|' -f4)
TOP_STALE_H="${IBW_TOP_STALE_H:-6}"
if [ -n "$PCNAME" ]; then
  ptop=$(board_top "assigned_pc=eq.$PCNAME&status=eq.assigned&started_at=is.null")
  if [ "$ptop" = MEAS_FAIL ]; then echo "$TS PCTOP MEAS_FAIL"
  elif [ -n "$ptop" ]; then
    pid8=${ptop%%|*}; rest=${ptop#*|}; ptitle=${rest%%|*}; rest=${rest#*|}; powner=${rest%%|*}; rest=${rest#*|}; pprio=${rest%%|*}; page=${rest#*|}
    stale=$(python3 -c "import sys;print(1 if float('$page')>=float('$TOP_STALE_H') else 0)")
    tf="$STATE_DIR/top-$pid8"
    if [ "$stale" = 1 ] && [ ! -f "$tf" ]; then
      notify_kantoku "[機械wake] 板${pid8}「${ptitle}」(owner=${powner}/p=${pprio}/更新${page}h前)が${PCNAME}の最上段で未着手。各席は自分owner以外を対象外(スキップ)にする→監督が差配/再仕分け/起こしを。行ごと1回のみ通知" \
        && { echo "$NOW $powner" > "$tf"; echo "$TS PCTOP_STALE_NOTIFIED $pid8 owner=$powner age=${page}h"; }
    else
      echo "$TS PCTOP $pid8 owner=$powner age=${page}h stale=$stale notified=$([ -f "$tf" ] && echo yes || echo no)"
    fi
  else echo "$TS PCTOP none"; fi
fi

total=0; idle_n=0; wake_n=0; skip_busy=0; meas_fail=0
while IFS='|' read -r name pane kind pc role; do
  [ -z "$name" ] && continue
  total=$((total+1))
  cap=$(tmux capture-pane -p -t "$pane" 2>/dev/null | tail -8)
  if [ -z "$cap" ]; then echo "$TS $name MEAS_FAIL pane_capture"; meas_fail=$((meas_fail+1)); continue; fi
  # idle述語(kind別) — 走行中マーカーがあればbusy
  if [ "${IBW_FORCE_IDLE:-0}" != 1 ] && echo "$cap" | grep -qE 'interrupt|mulling|contemplating|formulating|musing|Compacting|esc to'; then
    skip_busy=$((skip_busy+1)); continue
  fi
  if [ "${IBW_FORCE_IDLE:-0}" = 1 ]; then :
  elif [ "$kind" = "claude" ]; then
    # 2026-09-09 是正(dev_qa#957): ❯ 行は Claude Code 2.x で常在＝idle の証にならず、tail -8 の窓から流れ出ると静かな盤が busy と裁かれる(家老second 実測)。
    # ∴ 肯定条件は「Claude Code の盤である」(footer/prompt 記号が窓内のどこかに在る)だけにし、busy は L154 の走行中マーカーで判ずる。shell に落ちた盤は起こさない(安全側)。
    echo "$cap" | grep -qE '❯|⏵⏵|bypass permissions|new task\?' || { skip_busy=$((skip_busy+1)); continue; }
  else
    echo "$cap" | grep -qE '─ ready │' || { skip_busy=$((skip_busy+1)); continue; }
  fi
  # ダイアログ/残骸は触らない(安全側)
  if echo "$cap" | grep -qE 'Enter to select|[0-9]\. Yes|Do you want'; then skip_busy=$((skip_busy+1)); continue; fi
  idle_n=$((idle_n+1))
  # 未処理カウント(2系)
  # 自分owner分だけ数える(他者所有は対象外=理事長ご提案 2026-09-03)。owner_role列 or current_step「owner=<role>」
  OWNQ="status=eq.assigned&started_at=is.null&or=(owner_role.eq.$role,owner_role.like.$role*,current_step.ilike.*owner%3D$role*)"
  b=$(rest_count "task_tracker?select=id&$OWNQ")
  top=$(board_top "$OWNQ"); [ "$top" = MEAS_FAIL ] && top=""
  f=$(rest_count "task_tracker?select=id&assigned_pc=eq.$pc&status=eq.assigned&started_at=is.null&owner_role=not.is.null&owner_role=neq.$role&owner_role=not.like.$role*")
  [ "$f" = MEAS_FAIL ] && f="?"
  CUT24=$(python3 -c "import datetime;print((datetime.datetime.utcnow()-datetime.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S'))")
  m=$(rest_count "pc_handshake?select=seq&requires_response=eq.true&acknowledged_at=is.null&context_data-%3E%3Etarget_agent=eq.$role&created_at=gt.$CUT24")
  mold=$(rest_json "pc_handshake?select=seq&requires_response=eq.true&acknowledged_at=is.null&context_data-%3E%3Etarget_agent=eq.$role&created_at=gt.$CUT24&order=seq.asc&limit=1" | python3 -c "import sys,json\ntry:\n d=json.load(sys.stdin); print(d[0][\"seq\"] if d else \"\")\nexcept Exception: print(\"\")" 2>/dev/null)
  y=$(yaml_unread_count "$role")
  if [ "$b" = MEAS_FAIL ] || [ "$m" = MEAS_FAIL ] || [ "$y" = MEAS_FAIL ]; then echo "$TS $name MEAS_FAIL rest(b=$b m=$m y=$y)"; meas_fail=$((meas_fail+1)); continue; fi
  backlog=$((b+m+y))
  if [ "$backlog" -eq 0 ]; then continue; fi
  # cooldown + 状態変化のみ
  sf="$STATE_DIR/$name"; prev_ts=0; prev_sig=""
  [ -f "$sf" ] && { prev_ts=$(cut -d' ' -f1 "$sf"); prev_sig=$(cut -d' ' -f2- "$sf"); }
  sig="b${b}m${m}y${y}o${mold}t${top%%|*}"
  if [ $((NOW-prev_ts)) -lt $COOLDOWN ] && [ "$sig" = "$prev_sig" ]; then continue; fi
  topid=${top%%|*}; toptitle=$(printf '%s' "$top" | python3 -c 'import sys;f=sys.stdin.read().split("|");print(f[1][:28] if len(f)>1 else "")')
  if [ -n "$topid" ]; then MSG="[機械wake] 板(自分owner)=${b} 最上段=${topid}「${toptitle}」/箱未読=${y}/要返答=${m}(最古seq${mold}から順に)。他者所有${f}件は対象外。WORK-PULLで処理せよ"
  else MSG="[機械wake] 板(自分owner)=${b}/箱未読=${y}/要返答=${m}(最古seq${mold}から順に) が未処理。他者所有${f}件は対象外。WORK-PULLで処理せよ"; fi
  if [ "${IBW_DRY_RUN:-0}" = 1 ]; then echo "$TS DRY $name MSG=$MSG"; echo "$NOW $sig" > "$sf"; wake_n=$((wake_n+1)); continue; fi
  tmux send-keys -t "$pane" -l "$MSG" 2>/dev/null || { echo "$TS $name INJECT_FAIL"; meas_fail=$((meas_fail+1)); continue; }
  if [ "$kind" = "hermes" ]; then tmux send-keys -t "$pane" -H 1b 5b 31 33 75 2>/dev/null
  else tmux send-keys -t "$pane" Enter 2>/dev/null; fi
  echo "$NOW $sig" > "$sf"
  wake_n=$((wake_n+1))
  echo "$TS WAKE $name (board=$b mail=$m)"
done <<< "$SEATS"

echo "$TS summary: 母数=$total idle=$idle_n wake=$wake_n busy_skip=$skip_busy 測れない=$meas_fail stall_seen=$stall_seen stall_wake=$stall_wake_n stall_fail=$stall_fail (wake0件でも検査済)"

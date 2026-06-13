#!/usr/bin/env bash
#
# Shogun Bash-Fallback / Stuck-Retry Watchdog (各PC ローカル, oneshot 60s cycle)
#
# 由来: 副院長追命 670ffbfe(2) via Commander msg_20260613_104819
#       (shogun bash 落ち再発防止)。task=subtask_thirdpc_shogun_bash_fallback_watchdog。
#
# ═══ 防ぐ事象 (enter_restart_common_watchdog.sh とは別 failure mode) ═══
#   enter_restart 系 = 「idle 時に既入力 buffer を C-m で確定」(Enter のみ)。
#   本書       = 「Claude プロセスが落ちた/詰まった時に doppler env 付きで再起動」。
#   両者は補完関係 (重複ではない、Anti-Duplication 順守)。
#
#   shogun launch wrapper (setup_shogun_standard.sh):
#     `... && doppler run --project openhands --config dev -- claude 2>>log`
#   Claude が exit (crash / OOM / 完了 / API 致命 / retry 枯渇) すると `&&` chain が
#   終わり、pane は素の bash prompt に落ちる (= 概念上の `exec bash`)。
#   pane は tmux 上で見かけ alive だが agent は不在。以後 inboxN nudge が bash に
#   当たり「inboxN: command not found」を連発する (second_pc inbox808 堆積が症状)。
#   さらに bare `claude` 再起動は doppler/ccflare env 欠落で API retry 滞留 (env-gap)。
#
# ═══ 検知 2 failure mode ═══
#   (A) bash-fallback : pane が bash prompt + 「command not found」/ shell prompt、
#                       かつ Claude TUI chrome 不在。pane_current_command=bash で補強。
#   (B) stuck-retry   : Claude TUI chrome 在り + 「Retrying… attempt N/M」/ spinner が
#                       ★SBW_STUCK_MIN 分継続 (fingerprint 不変で persistence 判定)★。
#                       spinner 語 (Crunching 等) は正常時も出るため persistence 必須。
#
# ═══ 復旧 ═══
#   ① @agent_id 取得 (永続) ② (B のみ) Claude を停止し pane 解放 (Esc→C-c→必要なら
#      claude stack へ SIGTERM。★ローカルのみ・cross-PC kill 無★。誤 TERM 防止に cycle3 hardening:
#      送出前に ①PANE_PID subtree 再帰列挙 + 事前 ps 証跡 log ②ancestry 確証 かつ claude stack の
#      確定検証 (claude は doppler 配下の孫) → ③単一PID形 kill -TERM (mode_b_term_children 参照))
#   ③ ★doppler env 付き relaunch★ (SBW_RELAUNCH_CMD 既定 = doppler run … claude
#      --permission-mode auto。bare claude 禁 = env-gap 回避)
#   ④ kickoff directive (自己識別→CLAUDE.md/instructions→停滞 task 再開) を boot 後送出
#   ⑤ incident 記録 (shireiko_audit_log + pc_handshake)。
#
# ═══ 安全 (Watcher Design Principles 6 原則順守) ═══
#   - 冪等: restart_in_progress flag (TTL=SBW_INPROGRESS_TTL_SEC) で二重起動防止
#   - 連続再起動上限: SBW_RESTART_CAP/SBW_RESTART_WINDOW_MIN、超過で human_required escalate
#     (2026-05-05 SecondPC 暴走事件教訓 = enter_restart fire-cap と同型)
#   - 手動停止 flag 尊重: ~/.openclaw/global_disable / <log_dir>/DISABLE があれば一切起動しない
#   - 高頻度 heartbeat を DB に流さない (305 件 heartbeat 堆積教訓) = fire/escalate 時のみ INSERT
#   - restart/freefail history は append 後に window 外を prune (無制限肥大防止、cycle6 MED B2)
#   - 監査ログ終端理由を残す
#
# 終了コード: 0 = 通常完遂 (skip / fire / halt / escalate 含む)、2 = 必須 envvar 欠落
#
# テスト用フック (DoD fixture 再現に使用):
#   SBW_CLASSIFY_ONLY=1   classification だけ実行し MODE を stdout に出して exit
#   SBW_FINGERPRINT_PROBE=path その file 内容の stuck fingerprint を stdout に出して exit
#                         (cycle4 RED②: spinner 不変性の DoD 検証用)
#   SBW_CAPTURE_FILE=path tmux capture の代わりに file 内容を pane tail として読む
#   SBW_PANE_CMD_OVERRIDE pane_current_command の代わりにこの値を使う
#   SBW_NO_DB=1           Supabase INSERT を全 skip (fixture 用)
#   SBW_DEBUG_TAIL=1      classify log に pane capture の base64 tail を出力 (既定 off。
#                         pane 表示内容 = PHI 等を含み得る為 debug 時のみ opt-in。cycle6 MED S1)
#   SBW_DRY_RUN=1         send-keys / kill を実行せず "would …" を log するのみ
#   SBW_NOW_EPOCH         now() を固定 (cap / persistence の決定的テスト用)
#   SBW_RELAUNCH_ALLOW_UNSAFE=1  RELAUNCH_CMD invariant 検証を bypass (test 無害 stand-in /
#                         運用者の意図的 override 用。既定は doppler-safe 強制 = cycle4 RED①)
#   SBW_MODE_B_TERM_PROBE_PID=pid mode_b_term_children だけを probe して exit (誤TERM防止検証用)
#   SBW_NOT_FREED_PROBE=cmd  mode_b_handle_not_freed だけを probe して exit (cycle5 RED②:
#                         pane 解放失敗時に flag 抑止せず retry / cap で escalate する DoD 検証用)
#
# 安全 heredoc パターン (quoted <<'PYEOF' + os.environ + json.dumps) は
# enter_restart_common_watchdog.sh の S1 (Python source injection) 根治系譜を踏襲。

set -uo pipefail

# ─── 必須 envvar ───
for var in SBW_PANE_TARGET SBW_SESSION_NAME SBW_ROLE_NAME; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: shogun_bash_fallback_watchdog: required envvar $var is unset" >&2
    exit 2
  fi
done

PANE_TARGET="$SBW_PANE_TARGET"
SESSION_NAME="$SBW_SESSION_NAME"
ROLE_NAME="$SBW_ROLE_NAME"
REPO_DIR="${SBW_REPO_DIR:-/home/hakudoukai/multi-agent-shogun}"
TARGET_PC="${SBW_TARGET_PC:-third_pc}"
FROM_PC="${SBW_FROM_PC:-third_pc}"
STUCK_MIN="${SBW_STUCK_MIN:-5}"
RESTART_CAP="${SBW_RESTART_CAP:-3}"
RESTART_WINDOW_MIN="${SBW_RESTART_WINDOW_MIN:-60}"
INPROGRESS_TTL_SEC="${SBW_INPROGRESS_TTL_SEC:-150}"
BOOT_DELAY_SEC="${SBW_BOOT_DELAY_SEC:-30}"
KICKOFF="${SBW_KICKOFF:-1}"
HARD_KILL="${SBW_HARD_KILL:-1}"
NO_DB="${SBW_NO_DB:-0}"
DRY_RUN="${SBW_DRY_RUN:-0}"
# DB INSERT は urllib/json/os (stdlib) のみ使用ゆえ任意の python3 で可。
# third の hermes venv を既定にしつつ、無い PC では PATH の python3 に fallback (portable)。
PYTHON3_BIN="${SBW_PYTHON3_BIN:-}"
if [ -z "$PYTHON3_BIN" ]; then
  if [ -x /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 ]; then
    PYTHON3_BIN=/home/hakudoukai/.local/share/hermes-agent/venv/bin/python3
  else
    PYTHON3_BIN=python3
  fi
fi
LOG_DIR="${SBW_LOG_DIR:-$HOME/.local/share/shogun_bash_fallback_${ROLE_NAME}}"
# 既定の relaunch コマンド: doppler env 付き + --permission-mode auto (bare claude 禁)。
# 各 PC の thin wrapper が必要に応じ override (例 second_pc の bundle 版)。
# \$HOME/\$PATH は relaunch 時に pane shell が展開するよう literal で残し、$REPO_DIR は
# watchdog が今展開して typed command に埋め込む。
_SBW_DEFAULT_RELAUNCH="export PATH=\"\$HOME/.npm-global/bin:\$PATH\" && cd \"$REPO_DIR\" && doppler run --project openhands --config dev -- claude --permission-mode auto"
RELAUNCH_CMD="${SBW_RELAUNCH_CMD:-$_SBW_DEFAULT_RELAUNCH}"
KICKOFF_TEXT="${SBW_KICKOFF_TEXT:-【watchdog 再起動 directive】貴殿の Claude session は再起動された。CLAUDE.md Session Start 手順 (自己識別→memory/instructions 読込→YAML 再構築) を実行し、停滞していた task を再開せよ。}"

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y%m%d).log"
RESTART_HISTORY="$LOG_DIR/restarts.log"
FREEFAIL_HISTORY="$LOG_DIR/freefails.log"
INPROGRESS_FLAG="$LOG_DIR/restart_in_progress.flag"
STUCK_STATE="$LOG_DIR/stuck_state"
DISABLE_LOCAL="$LOG_DIR/DISABLE"
DISABLE_GLOBAL="$HOME/.openclaw/global_disable"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG" >&2; }

now_epoch() { echo "${SBW_NOW_EPOCH:-$(date +%s)}"; }

# ─── history prune (cycle6 MED B2 — 長期運用での無制限肥大を防ぐ) ───
# RESTART_HISTORY / FREEFAIL_HISTORY は append-only で cap 判定は window 内 epoch のみ数える。
# ∴ window 外の古い行は cap 判定に二度と寄与しない = prune して file を bounded に保つ。
# append 直後に呼び、window 内 (= now - RESTART_WINDOW_MIN 分) の epoch 行だけ残す。
_sbw_prune_history() {
  local f="$1" keep_from
  [ -f "$f" ] || return 0
  keep_from=$(( $(now_epoch) - RESTART_WINDOW_MIN * 60 ))
  # 数値 epoch 行のみ + window 内のみ残す (不正行も同時に除去)。失敗時は原本温存。
  if awk -v c="$keep_from" '/^[0-9]+$/ && ($1+0)>=c' "$f" > "$f.tmp" 2>/dev/null; then
    mv "$f.tmp" "$f"
  else
    rm -f "$f.tmp"
  fi
}

# ─── RELAUNCH_CMD invariant 検証 (cycle4 RED① + cycle5 RED① — env-gap / injection 防止) ───
# 根因分析: bare claude 再起動 = doppler/ccflare env 欠落で API retry 滞留 (second 実例)。
# ∴ relaunch は必ず `doppler run … claude` 形 (env 付き) でなければならない。
#
# cycle4 は「文字列が doppler run を含み claude を語として含む」★部分一致★ だった為、
#   doppler run --project openhands --config dev -- claude; rm -rf / # PWNED
# が validated 扱いとなり、send-keys で逐語 type→pane shell が実行する injection 面が残った
# (cycle5 RED① Codex 9faac50c DRY_RUN 再現)。
# cycle5 修復: override は ★素の (bare) `doppler run … claude` 形★ を anchored で要求し、
#   shell の連鎖/置換/redirect/background を可能にする metachar
#   — ; (separator) & (bg / &&) | (pipe / ||) < > (redirect) ` (backtick) $( (subshell) 改行 —
#   を一切拒否する。連鎖を含む正当な前置 (export…&&cd…&&doppler) は ★既定 (code 定義・信頼)★
#   側 (_SBW_DEFAULT_RELAUNCH) が担い、外部 override は素の doppler-run-claude に限定。
#   それ以上を意図する運用者は明示 SBW_RELAUNCH_ALLOW_UNSAFE=1 で escape hatch を使う。
_sbw_relaunch_is_safe() {
  # rc=0 iff $1 は安全な bare `doppler run … claude` 形 (shell metachar/連鎖/改行 無)。
  local cmd="$1"
  # (1) 改行 (複数行注入) 拒否
  case "$cmd" in *$'\n'*) return 1 ;; esac
  # (2) shell metachar / 連鎖 / 置換 / redirect / background 拒否
  #     ; (separator) & (bg / &&) | (pipe / ||) < > (redirect) ` (backtick) $ ($(…)/${…}/$VAR 展開)。
  #     bare override に $ は不要 ($HOME/$PATH 前置は信頼 default 専用) ゆえ $ は一律拒否で
  #     subshell/変数展開注入を最も単純かつ厳格に塞ぐ。
  case "$cmd" in
    *';'*|*'&'*|*'|'*|*'<'*|*'>'*|*'`'*|*'$'*) return 1 ;;
  esac
  # (3) anchored: 先頭 (空白許容) から doppler run … claude 形であること (末尾 junk 排除)
  printf '%s' "$cmd" | grep -Eq '^[[:space:]]*doppler run[[:space:]].*[[:space:]]claude([[:space:]]|$)' || return 1
  return 0
}

if [ -n "${SBW_RELAUNCH_CMD:-}" ]; then
  if [ "${SBW_RELAUNCH_ALLOW_UNSAFE:-0}" = "1" ]; then
    # cycle6 MED S2: escape hatch でも ★改行 (複数行注入) だけは無条件拒否★。send-keys は
    # text→Enter で 1 行を確定する流儀ゆえ、override に改行が混じると複数コマンドが連続確定する
    # 最悪面が残る。それ以外の metachar は明示 opt-in 運用者の責任範囲とし honored。
    case "$RELAUNCH_CMD" in
      *$'\n'*)
        log "WARN: SBW_RELAUNCH_ALLOW_UNSAFE=1 でも改行を含む override は拒否 (multi-line injection 面) — doppler-safe default に fallback"
        RELAUNCH_CMD="$_SBW_DEFAULT_RELAUNCH"
        ;;
      *)
        log "RELAUNCH_CMD override honored via SBW_RELAUNCH_ALLOW_UNSAFE=1 (unsafe opt-in, newline-rejected): [$RELAUNCH_CMD]"
        ;;
    esac
  elif _sbw_relaunch_is_safe "$RELAUNCH_CMD"; then
    log "RELAUNCH_CMD override validated (strict bare doppler-run-claude, no shell metachar): [$RELAUNCH_CMD]"
  else
    log "WARN: SBW_RELAUNCH_CMD override [$RELAUNCH_CMD] is NOT a strict 'doppler run … claude' form (shell metachar/chaining/newline or non-anchored = injection / env-gap risk) — fallback to doppler-safe default"
    RELAUNCH_CMD="$_SBW_DEFAULT_RELAUNCH"
  fi
fi

# ─── Supabase INSERT (fire/escalate 時のみ。安全 heredoc) ───
db_audit_insert() {
  # $1=event_type $2=action_taken $3=result $4=detail
  [ "$NO_DB" = "1" ] && { log "[NO_DB] skip shireiko_audit_log INSERT ($2/$3)"; return 0; }
  SBW_EVENT_TYPE_PY="$1" SBW_ACTION_PY="$2" SBW_RESULT_PY="$3" SBW_DETAIL_PY="$4" \
  SBW_TARGET_PC_PY="$TARGET_PC" \
  doppler run --project openhands --config dev -- \
    "$PYTHON3_BIN" - <<'PYEOF' >>"$LOG" 2>&1 || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": os.environ.get('SBW_EVENT_TYPE_PY', ''),
    "detail": os.environ.get('SBW_DETAIL_PY', ''),
    "judgment_level": 2,
    "action_taken": os.environ.get('SBW_ACTION_PY', ''),
    "result": os.environ.get('SBW_RESULT_PY', ''),
    "engine": "shogun_bash_fallback_watchdog",
    "target_pc": os.environ.get('SBW_TARGET_PC_PY', ''),
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"shireiko_audit_log INSERT rc={r.status}")
PYEOF
}

db_handshake_insert() {
  # $1=topic $2=content $3=priority
  [ "$NO_DB" = "1" ] && { log "[NO_DB] skip pc_handshake INSERT ($1)"; return 0; }
  SBW_TOPIC_PY="$1" SBW_CONTENT_PY="$2" SBW_PRIORITY_PY="$3" SBW_FROM_PC_PY="$FROM_PC" \
  doppler run --project openhands --config dev -- \
    "$PYTHON3_BIN" - <<'PYEOF' >>"$LOG" 2>&1 || true
import os, json, urllib.request, uuid
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
payload = {
    "id": str(uuid.uuid4()),
    "from_pc": os.environ.get('SBW_FROM_PC_PY', ''),
    "to_pc": "fukuincho",
    "topic": os.environ.get('SBW_TOPIC_PY', ''),
    "content": os.environ.get('SBW_CONTENT_PY', ''),
    "priority": os.environ.get('SBW_PRIORITY_PY', 'low'),
    "message_type": "status_update",
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"pc_handshake INSERT rc={r.status}")
PYEOF
}

# ─── pane 操作 (DRY_RUN 尊重) ───
send_keys_line() {
  # $1=literal text to type, then Enter (separate, 0.3s gap = 既存 nudge 流儀)
  if [ "$DRY_RUN" = "1" ]; then log "[DRY_RUN] would send-keys: $1"; return 0; fi
  tmux send-keys -t "$PANE_TARGET" "$1" 2>>"$LOG"
  sleep 0.3
  tmux send-keys -t "$PANE_TARGET" Enter 2>>"$LOG"
}
send_key_special() {
  # $1=tmux key name (Escape / C-c)
  if [ "$DRY_RUN" = "1" ]; then log "[DRY_RUN] would send key: $1"; return 0; fi
  tmux send-keys -t "$PANE_TARGET" "$1" 2>>"$LOG"
}

# ─── MODE B: stuck claude stack を 証跡付き・検証付きで SIGTERM (cycle3 hardening) ───
# 由来: cycle3 fix (Codex 1771c08f 実RED2件) = cycle2 の SIGTERM 対象が pane_pid 直系子限定
#       (pgrep -P) で、launch wrapper=`doppler run … claude` ゆえ claude が ★孫プロセス★
#       (pane shell→doppler→claude or →node→claude) になる構造を停止できなかった。
#       cycle1=広すぎ / cycle2=狭すぎ (直系子のみ) の振れを是正し、PANE_PID subtree 全体を
#       再帰列挙 + ancestry 確証 + claude-stack 確定検証 で過不足なく TERM する。
#       pane shell 配下のローカル process のみ対象 (cross-PC kill 無 ∴ DD-169 例外):
#   ① 事前 ps 証跡   : TERM 送出前に PANE_PID subtree 全 descendant の full ps を log。
#   ② per-PID 確定検証: (a) ancestry — 発見 PID の親 chain に PANE_PID が含まれる事を確証
#                           (他 pane 混入 / TOCTOU reparent 排除)
#                       (b) claude-stack — comm が claude 本体、もしくは comm が node/doppler
#                           かつ args が claude を指す (generic runtime/launcher の誤 TERM 防止)。
#                       ★検証は TERM 前に一括実行 (verify-then-term)★ — 親(doppler)を先に
#                       TERM して孫(claude)が reparent し ancestry 落ちする self-orphan を防ぐ。
#   ③ 単一PID形 TERM : 検証を通った PID のみ `kill -TERM <pid>` (DD-169 例外形)。DRY_RUN は尊重。

# PANE_PID subtree の全 descendant PID を再帰列挙 (直系子限定を撤廃 = cycle3)。
_sbw_collect_descendants() {
  local p="$1" kid
  for kid in $(pgrep -P "$p" 2>/dev/null || true); do
    echo "$kid"
    _sbw_collect_descendants "$kid"
  done
}

# 候補 PID の親 chain に root が含まれるか (ancestry 確証、他 pane 混入排除)。
_sbw_has_ancestor() {
  # $1=candidate pid $2=root pid ; rc=0 if root is an ancestor of candidate
  local cur="$1" root="$2" guard=0 pp
  while [ -n "$cur" ] && [ "$cur" != "1" ] && [ "$cur" != "0" ]; do
    [ "$cur" = "$root" ] && return 0
    pp=$(ps -o ppid= -p "$cur" 2>/dev/null | tr -d ' ')
    [ -z "$pp" ] && return 1
    cur="$pp"
    guard=$((guard+1)); [ "$guard" -gt 64 ] && return 1
  done
  return 1
}

mode_b_term_children() {
  local pane_pid="$1"
  [ -z "$pane_pid" ] && { log "MODE B term: empty pane_pid — skip"; return 0; }
  # cycle3: 直系子限定を撤廃し subtree 全体を再帰列挙 (claude は孫 pane→doppler→claude)
  local descendants
  descendants=$(_sbw_collect_descendants "$pane_pid")
  if [ -z "$descendants" ]; then
    log "MODE B ps-evidence (subtree of pane_pid=$pane_pid): (no descendants)"
    log "MODE B term summary: verified_termed=0 (pane_pid=$pane_pid)"
    return 0
  fi
  # ① 事前 ps 証跡 (subtree 全 descendant を pid/ppid/comm/args で log)
  log "MODE B ps-evidence (subtree of pane_pid=$pane_pid):"
  local d ev
  for d in $descendants; do
    ev=$(ps -o pid=,ppid=,comm=,args= -p "$d" 2>/dev/null | sed 's/^[[:space:]]*//')
    [ -n "$ev" ] && log "  ps| $ev"
  done
  # ② per-PID 確定検証 → verified list 構築 (★TERM 前に一括確証 = self-orphan 防止★)
  local child cppid cname cargs expected
  local -a verified_pids=() verified_desc=()
  for child in $descendants; do
    cppid=$(ps -o ppid= -p "$child" 2>/dev/null | tr -d ' ')
    cname=$(ps -o comm= -p "$child" 2>/dev/null || echo "")
    cargs=$(ps -o args= -p "$child" 2>/dev/null || echo "")
    # 検証(a): ancestry — 親 chain に pane_pid を含む事を確証 (他 pane 混入 / reparent 排除)
    if ! _sbw_has_ancestor "$child" "$pane_pid"; then
      log "MODE B skip pid=$child ($cname): pane_pid=$pane_pid not in ancestor chain (ppid=$cppid)"
      continue
    fi
    # 検証(b): claude-stack か (generic node/doppler の誤 TERM 防止)
    expected=0
    case "$cname" in
      claude) expected=1 ;;
      node|doppler) printf '%s' "$cargs" | grep -qi 'claude' && expected=1 ;;
    esac
    if [ "$expected" -ne 1 ]; then
      log "MODE B skip pid=$child ($cname): not claude-stack (args=[$cargs]) — avoid generic TERM"
      continue
    fi
    verified_pids+=("$child")
    verified_desc+=("pid=$child ($cname) ppid=$cppid args=[$cargs]")
  done
  # ③ 単一PID形 TERM (検証済のみ。verify-then-term ゆえ親子同時でも取りこぼし無)
  local i termed=0
  if [ "${#verified_pids[@]}" -gt 0 ]; then
    for i in "${!verified_pids[@]}"; do
      if [ "$DRY_RUN" = "1" ]; then
        log "[DRY_RUN] would SIGTERM verified child ${verified_desc[$i]}"
      else
        log "SIGTERM verified child ${verified_desc[$i]}"
        kill -TERM "${verified_pids[$i]}" 2>>"$LOG" || true
      fi
      termed=$((termed+1))
    done
  fi
  log "MODE B term summary: verified_termed=$termed (pane_pid=$pane_pid)"
  return 0
}

# ─── MODE B: pane 解放失敗時の処理 (cycle5 RED② — 無限抑止しない) ───
# 由来: cycle5 fix (Codex 9faac50c 実RED2件) = 旧版は free 失敗時 restart_in_progress flag を
#       残したまま exit した為、次 cycle 以降 Step 1 が flag TTL (既定 150s) で skip し続け、
#       stuck pane が ★再試行も escalate もされず★ 抑止された (flag による無限抑止)。
# 修復方針: free 失敗を検知したら ①抑止源の in-progress flag を ★必ず解除★ (relaunch して
#       いない ∴ boot grace は不要・次 cycle が再評価=再試行できるようにする) ②free 失敗回数を
#       window 内で数え cap 未満は次 cycle 再試行・cap 到達で human_required escalate。
#       SIGTERM の再試行は quota を消費しない (既存 stuck process への signal) ので 2026-05-05
#       relaunch 暴走教訓には抵触せず、cap 到達後の DB escalate は ★初回 (== cap) のみ★ に
#       絞り heartbeat spam (305 件教訓) も避ける。echo: "retry" | "halt"。
mode_b_handle_not_freed() {
  local cur="$1"
  # ① 抑止源を除去 (★cycle5 RED② core cure★ — flag による無限抑止を断つ)
  rm -f "$INPROGRESS_FLAG"
  # ② free 失敗回数を window 内で計上
  now_epoch >> "$FREEFAIL_HISTORY"
  _sbw_prune_history "$FREEFAIL_HISTORY"   # cycle6 MED B2: 無制限肥大防止
  local ff_window ff_recent
  ff_window=$(( $(now_epoch) - RESTART_WINDOW_MIN * 60 ))
  ff_recent=$(awk -v c="$ff_window" 'BEGIN{n=0}{if($1+0>=c)n++}END{print n}' "$FREEFAIL_HISTORY" 2>/dev/null || echo 0)
  if [ "$ff_recent" -ge "$RESTART_CAP" ]; then
    log "★HALT★ MODE B pane free failed (current=$cur) ${ff_recent}x >= cap ${RESTART_CAP} in ${RESTART_WINDOW_MIN}min — escalate human_required (no suppression flag, 再試行は継続)"
    if [ "$ff_recent" -eq "$RESTART_CAP" ]; then
      # cap への初回到達のみ DB escalate (以降は quiet retry = heartbeat spam 防止)
      db_audit_insert "shogun_bash_fallback_freefail_halt" "halted" "escalated" \
        "${ROLE_NAME} MODE B stuck pane not freed (current=${cur}); free-fail cap ${ff_recent}/${RESTART_CAP} 到達。human_required。"
      db_handshake_insert "[human_required] ${ROLE_NAME} stuck pane not freed (${ff_recent}x)" \
        "${TARGET_PC} ${ROLE_NAME} pane=${PANE_TARGET}: stuck-retry 停止に ${ff_recent} 回失敗 (current_command=${cur})。自動解放を断念し人手介入要請。in-progress flag は抑止せず解除済。" \
        "high"
    else
      log "free-fail ${ff_recent} は cap 超過済 (escalate 発報済) — quiet retry (DB spam 抑止)"
    fi
    echo "halt"; return 0
  fi
  log "WARN: MODE B pane not freed (current=$cur), free-fail ${ff_recent}/${RESTART_CAP} — in-progress flag 解除済・retry next cycle (抑止せず)"
  echo "retry"; return 0
}

# ─── MODE B: caller が not-freed verdict を明示受領し分岐 (cycle6 RED① — verdict を捨てない) ───
# 由来: cycle6 fix (Codex e4e938a5 高 1件) = 旧 caller が `mode_b_handle_not_freed "$CUR" >/dev/null`
#       で retry/halt verdict を ★破棄★ し、halt/retry の状態制御が caller 外側で不可視だった
#       (標準 Codex 監査 = red)。本関数で verdict を受領→★明示 log で区別★し、caller が verdict
#       を消費して動作する事を可視化・assert 可能にする。
# 動作: いずれも本 cycle は relaunch せず (pane 未解放ゆえ)、次 cycle が再評価する。差分 =
#       retry (cap 未満) は次 cycle で free 再試行 / halt (cap 到達) は escalate 済→operator 待ち。
mode_b_on_not_freed_verdict() {
  local v="$1"
  case "$v" in
    halt)
      log "MODE B caller: not-freed verdict=halt — human_required escalate 済、本 cycle は relaunch せず停止 (次 cycle が operator 介入後に再評価)"
      ;;
    retry)
      log "MODE B caller: not-freed verdict=retry — relaunch 見送り、次 cycle で pane 解放を再試行 (in-progress flag 解除済)"
      ;;
    *)
      log "WARN: MODE B caller: not-freed 想定外 verdict=[$v] — 安全側 (no relaunch) で停止"
      ;;
  esac
}

# ─── classification (capture-content 主, pane_cmd 副) ───
# Claude TUI chrome (= Claude 稼働中の指標)
CHROME_RE='esc to interrupt|bypass permissions|\? for shortcuts|context (used|left)|shift\+tab|⏵⏵|tab to (cycle|expand)|❯|│[[:space:]]*>'
# stuck-retry signal
STUCK_RE='Retrying[^[:alnum:]]{0,40}attempt [0-9]+/[0-9]+|API Error.*[Rr]etry|overloaded_error|Crunching|Zigzagging|Reticulating|Hibernating|Marinating|Simmering'
# bash-fallback signal
BASH_RE='command not found|: not found|[A-Za-z0-9._-]+@[A-Za-z0-9._-]+:[^#$]*[#$][[:space:]]*$'

classify() {
  # reads $PANE_TAIL and $PANE_CMD; echoes one of: A B HEALTHY EMPTY
  local tail="$1" cmd="$2"
  if [ -z "$tail" ]; then echo "EMPTY"; return; fi
  local has_chrome=0 has_stuck=0 has_bash=0
  printf '%s' "$tail" | grep -qE "$CHROME_RE" && has_chrome=1
  printf '%s' "$tail" | grep -qE "$STUCK_RE"  && has_stuck=1
  printf '%s' "$tail" | grep -qE "$BASH_RE"   && has_bash=1
  # (A) bash-fallback: chrome 不在 + bash 兆候 (+ pane_cmd=bash で補強だが必須にしない:
  #     doppler mask の逆 = bash 落ち時は確実に bash になる)
  if [ "$has_chrome" -eq 0 ] && { [ "$has_bash" -eq 1 ] || [ "$cmd" = "bash" ]; }; then
    echo "A"; return
  fi
  # (B) stuck-retry: chrome 在り + stuck 兆候 (persistence は呼出側で判定)
  if [ "$has_chrome" -eq 1 ] && [ "$has_stuck" -eq 1 ]; then
    echo "B"; return
  fi
  echo "HEALTHY"
}

# Claude TUI spinner の rotating gerund 群 (フレーム毎に語が回る = 不変化対象)。
# STUCK_RE の spinner 語を含む superset。stuck 中はこの語だけが変わり進捗 0 ゆえ正規化必須。
SPINNER_WORD_RE='Crunching|Zigzagging|Reticulating|Hibernating|Marinating|Simmering|Pondering|Noodling|Percolating|Schlepping|Vibing|Channelling|Computing|Cogitating|Conjuring|Deliberating|Effecting|Finagling|Forging|Germinating|Honking|Imagining|Incubating|Mustering|Mulling|Musing|Processing|Puzzling|Ruminating|Shucking|Spinning|Stewing|Synthesizing|Transmuting|Wibbling|Wrangling|Baking|Brewing|Calculating|Cooking|Distilling|Generating|Grokking|Herding|Jamming|Moseying|Pixelating|Polishing|Tinkering|Whirring'

fingerprint() {
  # cycle4 RED②: 安定 fingerprint。spinner の可変部 — ①glyph アニメ (braille 等の非 ASCII
  # 装飾) ②rotating gerund 語 ③経過秒 / attempt N/M 等の counter — を normalize し、
  # 「進捗が真に止まっているか」を安定 signal (Retrying attempt #/# 等) で判定する。
  # 旧版は数字潰しのみで glyph/語の変動に弱く、stuck 中も fp が毎フレーム変わり persistence
  # に到達できなかった (= MODE B が発火しない回帰)。逆に assistant の実出力行は残すので、
  # 真に進捗していれば fp は変化し timer reset = 誤発火しない。
  printf '%s' "$1" \
    | grep -v '^[[:space:]]*$' \
    | tail -8 \
    | LC_ALL=C sed -E \
        -e 's/[^[:print:][:space:]]+/ /g' \
        -e "s/\\b(${SPINNER_WORD_RE})\\b/SPIN/g" \
        -e 's/[0-9]+/#/g' \
        -e 's/[[:space:]]+/ /g' \
        -e 's/^ //; s/ $//' \
    | sha1sum | cut -d' ' -f1
}

# テストフック: fingerprint だけを probe して exit (cycle4 RED② spinner 不変性 DoD 検証用)
if [ -n "${SBW_FINGERPRINT_PROBE:-}" ]; then
  fingerprint "$(cat "$SBW_FINGERPRINT_PROBE" 2>/dev/null)"
  exit 0
fi

# テストフック: MODE B child-TERM の証跡+検証ロジックだけを単体 probe して exit
# (real tmux pane 無しで誤TERM防止ロジックを DoD 検証する為。DRY_RUN は呼出側が指定)
if [ -n "${SBW_MODE_B_TERM_PROBE_PID:-}" ]; then
  mode_b_term_children "$SBW_MODE_B_TERM_PROBE_PID"
  exit 0
fi

# テストフック: pane-not-freed 処理 (cycle5 RED②) だけを単体 probe して exit
# (real tmux 無しで「flag 抑止せず retry / cap で escalate」の DoD を機械検証する為)
if [ -n "${SBW_NOT_FREED_PROBE:-}" ]; then
  # cycle6 RED①: real caller (Step 5) と ★同一の 2 行配線★ — verdict を受領し分岐 (>/dev/null 廃止)。
  # この probe が caller の verdict 消費を機械検証する (verdict 破棄回帰の pin)。
  _nf_verdict=$(mode_b_handle_not_freed "$SBW_NOT_FREED_PROBE")
  mode_b_on_not_freed_verdict "$_nf_verdict"
  exit 0
fi

# ════════════════════ main ════════════════════
log "=== ${ROLE_NAME} bash-fallback watchdog cycle start (pane=$PANE_TARGET) ==="

# Step 0: 手動停止 flag 尊重 (Watcher 原則 3)
if [ -f "$DISABLE_GLOBAL" ] || [ -f "$DISABLE_LOCAL" ]; then
  log "manual disable flag present (global=$([ -f "$DISABLE_GLOBAL" ] && echo 1 || echo 0) local=$([ -f "$DISABLE_LOCAL" ] && echo 1 || echo 0)) — no action"
  exit 0
fi

# capture 取得 (test override 可)
if [ -n "${SBW_CAPTURE_FILE:-}" ]; then
  PANE_TAIL=$(cat "$SBW_CAPTURE_FILE" 2>/dev/null || echo "")
  PANE_CMD="${SBW_PANE_CMD_OVERRIDE:-bash}"
else
  if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    log "WARN: tmux session '$SESSION_NAME' not found, skip"; exit 0
  fi
  if ! tmux display-message -t "$PANE_TARGET" -p '#{pane_id}' >/dev/null 2>&1; then
    log "WARN: pane '$PANE_TARGET' not found, skip"; exit 0
  fi
  PANE_CMD="${SBW_PANE_CMD_OVERRIDE:-$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")}"
  PANE_TAIL=$(tmux capture-pane -t "$PANE_TARGET" -p -S -40 2>/dev/null || echo "")
  PANE_TAIL=$(printf '%s' "$PANE_TAIL" | sed 's/\xc2\xa0/ /g')
fi

MODE=$(classify "$PANE_TAIL" "$PANE_CMD")
# cycle6 MED S1: pane 表示内容 (PHI 等を含み得る) を ★既定では log に残さない★。
# 障害解析時のみ SBW_DEBUG_TAIL=1 で base64 tail を opt-in 出力する (debug gating)。
if [ "${SBW_DEBUG_TAIL:-0}" = "1" ]; then
  log "classify: mode=$MODE pane_cmd=$PANE_CMD tail_b64=$(printf '%s' "$PANE_TAIL" | tail -6 | base64 -w0)"
else
  log "classify: mode=$MODE pane_cmd=$PANE_CMD (tail_b64 gated; set SBW_DEBUG_TAIL=1 to log pane content)"
fi

# テストフック: classification だけ確認して exit (persistence/relaunch を回さない)
if [ "${SBW_CLASSIFY_ONLY:-0}" = "1" ]; then
  echo "$MODE"
  exit 0
fi

# (B) persistence 判定: 同一 fingerprint が STUCK_MIN 分継続して初めて発火
if [ "$MODE" = "B" ]; then
  FP=$(fingerprint "$PANE_TAIL")
  NOW=$(now_epoch)
  if [ -f "$STUCK_STATE" ]; then
    PREV_FP=$(cut -d'|' -f1 "$STUCK_STATE" 2>/dev/null || echo "")
    PREV_TS=$(cut -d'|' -f2 "$STUCK_STATE" 2>/dev/null || echo "$NOW")
  else
    PREV_FP=""; PREV_TS="$NOW"
  fi
  if [ "$FP" = "$PREV_FP" ]; then
    ELAPSED=$(( NOW - PREV_TS ))
    log "stuck persistence: fp unchanged ${ELAPSED}s (need $((STUCK_MIN*60))s)"
    if [ "$ELAPSED" -lt $((STUCK_MIN * 60)) ]; then
      log "stuck not yet persistent enough — defer (no relaunch)"; exit 0
    fi
    # persistent enough → fall through to recovery
  else
    # 新しい fingerprint = 進捗あり or 別の stuck → タイマ reset
    printf '%s|%s\n' "$FP" "$NOW" > "$STUCK_STATE"
    log "stuck fp changed/new — reset timer, defer (no relaunch)"; exit 0
  fi
fi

if [ "$MODE" = "HEALTHY" ] || [ "$MODE" = "EMPTY" ]; then
  # 健全 = stuck timer クリア
  [ -f "$STUCK_STATE" ] && rm -f "$STUCK_STATE"
  log "no failure detected (mode=$MODE) — no action"
  exit 0
fi

# ─── ここから MODE = A or B (要復旧) ───

# Step 1: 冪等 — restart 進行中なら skip (boot 猶予)
if [ -f "$INPROGRESS_FLAG" ]; then
  FLAG_AGE=$(( $(now_epoch) - $(stat -c %Y "$INPROGRESS_FLAG" 2>/dev/null || echo 0) ))
  if [ "$FLAG_AGE" -lt "$INPROGRESS_TTL_SEC" ]; then
    log "restart in progress (flag age ${FLAG_AGE}s < ${INPROGRESS_TTL_SEC}s) — skip (idempotency)"
    exit 0
  fi
  log "stale restart flag (age ${FLAG_AGE}s) — clearing"
  rm -f "$INPROGRESS_FLAG"
fi

# Step 2: 連続再起動上限 (暴走防止)
NOW=$(now_epoch)
WINDOW_EPOCH=$(( NOW - RESTART_WINDOW_MIN * 60 ))
if [ -f "$RESTART_HISTORY" ]; then
  RECENT=$(awk -v c="$WINDOW_EPOCH" 'BEGIN{n=0}{if($1+0>=c)n++}END{print n}' "$RESTART_HISTORY" 2>/dev/null || echo 0)
else
  RECENT=0
fi
log "restart cap check: recent=${RECENT} in ${RESTART_WINDOW_MIN}min cap=${RESTART_CAP}"
if [ "$RECENT" -ge "$RESTART_CAP" ]; then
  log "★HALT★ restart cap exceeded (${RECENT} >= ${RESTART_CAP}) — escalate human_required, NO relaunch"
  db_audit_insert "shogun_bash_fallback_halt" "halted" "escalated" \
    "${ROLE_NAME} ${MODE}-mode failure but restart cap exceeded (${RECENT}>=${RESTART_CAP} in ${RESTART_WINDOW_MIN}min). human_required."
  db_handshake_insert "[human_required] ${ROLE_NAME} bash-fallback restart cap exceeded" \
    "${TARGET_PC} ${ROLE_NAME} pane=${PANE_TARGET} mode=${MODE}: 連続再起動が上限 ${RESTART_CAP}/${RESTART_WINDOW_MIN}min に到達。watchdog は自動再起動を停止。人手確認が必要 (real crash か誤検知か切り分け)。" \
    "high"
  exit 0
fi

# Step 3: @agent_id 取得 (永続、log/incident 用)
AGENT_ID="${SBW_AGENT_ID_FALLBACK:-$ROLE_NAME}"
if [ -z "${SBW_CAPTURE_FILE:-}" ]; then
  AID=$(tmux display-message -t "$PANE_TARGET" -p '#{@agent_id}' 2>/dev/null || echo "")
  [ -n "$AID" ] && AGENT_ID="$AID"
fi
log "agent_id=$AGENT_ID"

# Step 4: 冪等 flag を立てる
touch "$INPROGRESS_FLAG"

# Step 5: (B) のみ — Claude を停止し pane を解放
if [ "$MODE" = "B" ]; then
  log "MODE B: interrupt + free pane (Esc → C-c → SIGTERM child if needed)"
  send_key_special "Escape"; sleep 2
  send_key_special "C-c";    sleep 2
  send_key_special "C-c";    sleep 3
  # pane が bash に戻ったか確認
  if [ -z "${SBW_CAPTURE_FILE:-}" ]; then
    CUR=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")
    if [ "$CUR" != "bash" ] && [ "$HARD_KILL" = "1" ]; then
      PANE_PID=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_pid}' 2>/dev/null || echo "")
      if [ -n "$PANE_PID" ]; then
        # pane shell 配下の claude stack を 証跡付き・検証付きで TERM (cycle2 hardening)。
        # DRY_RUN は helper 内で尊重 (would-SIGTERM log のみ、実 kill 無)。
        mode_b_term_children "$PANE_PID"
        [ "$DRY_RUN" != "1" ] && sleep 3
      fi
      CUR=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")
    fi
    if [ "$CUR" != "bash" ]; then
      # cycle5 RED②: flag を残して TTL 抑止せず、解除→cap 未満は次 cycle 再試行・cap で escalate。
      # cycle6 RED①: verdict を ★caller が明示受領して分岐★ (旧 >/dev/null 破棄を撤廃)。
      NOT_FREED_VERDICT=$(mode_b_handle_not_freed "$CUR")
      mode_b_on_not_freed_verdict "$NOT_FREED_VERDICT"
      exit 0
    fi
  fi
fi

# Step 6: relaunch (doppler env 付き)
log "★RELAUNCH★ mode=$MODE cmd=$RELAUNCH_CMD"
send_keys_line "$RELAUNCH_CMD"
now_epoch >> "$RESTART_HISTORY"
_sbw_prune_history "$RESTART_HISTORY"   # cycle6 MED B2: 無制限肥大防止

# Step 7: incident 記録
db_audit_insert "shogun_bash_fallback_relaunch" "relaunch_${MODE}" "success" \
  "${ROLE_NAME} (${AGENT_ID}) ${MODE}-mode failure detected on ${PANE_TARGET}; relaunched with doppler env (--permission-mode auto)."
db_handshake_insert "[watchdog] ${ROLE_NAME} relaunched (mode=${MODE})" \
  "${TARGET_PC} ${ROLE_NAME} pane=${PANE_TARGET} agent=${AGENT_ID}: ${MODE}-mode (A=bash-fallback / B=stuck-retry) 検知→doppler env 付き relaunch 実行。restart count=$((RECENT+1))/${RESTART_CAP}." \
  "normal"

# Step 8: kickoff directive (boot 待機後)
if [ "$KICKOFF" = "1" ]; then
  log "kickoff: sleep ${BOOT_DELAY_SEC}s for boot, then send directive"
  if [ "$DRY_RUN" != "1" ] && [ -z "${SBW_CAPTURE_FILE:-}" ]; then sleep "$BOOT_DELAY_SEC"; fi
  send_keys_line "$KICKOFF_TEXT"
fi

# Step 9: stuck timer クリア + 冪等 flag は次 cycle の TTL で自然消滅
[ -f "$STUCK_STATE" ] && rm -f "$STUCK_STATE"
log "=== cycle complete (mode=$MODE relaunched, restart_in_progress flag set, TTL=${INPROGRESS_TTL_SEC}s) ==="
exit 0

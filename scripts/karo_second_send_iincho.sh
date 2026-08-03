#!/usr/bin/env bash
# karo_second_send_iincho.sh — karo-second → 委員長(iincho) canonical uplink helper
#
# 封筒4点は本 helper が固定・強制する(呼出側の指定は反映されず、正規化されるのみ):
#   from_pc=second_pc / to_pc=iincho / topic=cross_pc_inbox_iincho /
#   context_data.target_agent=iincho / context_data.sender_agent=karo-second / priority=high
#
# デフォルトは dry-run(封筒を組み立てて標準出力へ表示するのみ・POSTしない)。
# --live を明示した場合のみ実POSTする。
#
# Usage:
#   scripts/karo_second_send_iincho.sh [--live] [--type TYPE] [--target-agent VAL] [--topic VAL] [--requires-response] -- "content"
#
# set -u のみを用いる(-e/pipefail は用いない): PAYLOAD/HTTP_CODE/RESPONSE_BODY はいずれも
# command substitution 代入であり、set -e 下では代入先コマンド(python3/sb_curl)が非ゼロ終了した
# 瞬間に代入行そのもので launcher 全体が即 abort し、後続の明示チェック(|| fatal 等・HTTP_CODE
# 判定)へ到達できぬ(lane A v6 redo で実証済の同型 trap= _fqm_read="$(python3 ...)" が
# set -e 下で意図せず launcher を殺した事故と同じ構造)。本 script は代入直後に明示的な
# `|| fatal ...` および if 判定で終了状態を必ず検査しており、fatal() が失敗の届き先を保証する
# 設計であるため set -e には依存しない。set -u は「未定義変数の誤参照」という別種の
# (意図的な非ゼロ終了と衝突しない) 誤り検出のみを担うため維持する。
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB_AUTH_LIB="$SCRIPT_DIR/shim/hakudokai/lib/sb_auth.sh"
FAIL_LOG="${KARO_SECOND_SEND_IINCHO_LOG:-/tmp/karo_second_send_iincho.log}"

fatal() {
  # 失敗の届き先: stderr のみで終わらせず、恒久ログへも追記する(沈黙投棄防止)。
  local msg="[FATAL][karo_second_send_iincho.sh] $1"
  echo "$msg" >&2
  echo "$(date -Iseconds) $msg" >> "$FAIL_LOG"
  exit 1
}

# sb_auth.sh 不在時 hard fail (2>/dev/null や || true は使わぬ)。
if [ ! -r "$SB_AUTH_LIB" ]; then
  fatal "sb_auth.sh not found/readable at ${SB_AUTH_LIB} — refusing to start"
fi
source "$SB_AUTH_LIB"

# --- 固定封筒(書換禁・呼出側からの上書き不可) ---
declare -r -x FROM_PC="second_pc"
declare -r -x TO_PC="iincho"
declare -r -x TOPIC="cross_pc_inbox_iincho"
declare -r -x TARGET_AGENT="iincho"
declare -r -x SENDER_AGENT="karo-second"
declare -r -x PRIORITY="high"
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"

DRY_RUN=true
MSG_TYPE="status_update"
CALLER_TARGET_AGENT=""
CALLER_TOPIC=""
CONTENT=""
# requires_response の既定は false とする(理由: 本 helper の主用途は status_update 通知であり、
# 大半の呼出は返信追跡を要さぬため。blocker escalation/裁定要求など返信追跡が要る呼出のみ
# 呼出側が明示的に --requires-response を付す=既定を安全側(返信不要)に置き、必要な時だけ
# opt-in させる設計)。
REQUIRES_RESPONSE=false

while [ $# -gt 0 ]; do
  case "$1" in
    --live) DRY_RUN=false; shift ;;
    --type) MSG_TYPE="${2:-}"; shift 2 ;;
    --target-agent) CALLER_TARGET_AGENT="${2:-}"; shift 2 ;;
    --topic) CALLER_TOPIC="${2:-}"; shift 2 ;;
    --requires-response) REQUIRES_RESPONSE=true; shift ;;
    --) shift; CONTENT="${1:-}"; break ;;
    *) CONTENT="$1"; shift ;;
  esac
done

if [ -z "$CONTENT" ]; then
  echo "Usage: $0 [--live] [--type TYPE] [--target-agent VAL] [--topic VAL] [--requires-response] -- \"content\"" >&2
  exit 1
fi

# --- 非canonical引数の正規化(拒否ではなく強制上書き。呼出側に返る形=標準出力で明示) ---
NORMALIZED_NOTES=""
if [ -n "$CALLER_TARGET_AGENT" ] && [ "$CALLER_TARGET_AGENT" != "$TARGET_AGENT" ]; then
  NORMALIZED_NOTES="${NORMALIZED_NOTES}NORMALIZED: target_agent caller指定='${CALLER_TARGET_AGENT}' は無視し固定値 '${TARGET_AGENT}' を用いた(本helperはkaro-second→iincho専用・他宛先へは送れぬ)
"
fi
if [ -n "$CALLER_TOPIC" ] && [ "$CALLER_TOPIC" != "$TOPIC" ]; then
  NORMALIZED_NOTES="${NORMALIZED_NOTES}NORMALIZED: topic caller指定='${CALLER_TOPIC}' は無視し固定値 '${TOPIC}' を用いた
"
fi

# 封筒組み立て(python3 json.dumpsでエスケープを一任・argvではなくenv経由でcontentを渡す)。
# FROM_PC/TO_PC/TOPIC/TARGET_AGENT/SENDER_AGENT/PRIORITY は declare -r -x 済ゆえ既に子環境へ継承される。
PAYLOAD="$(
  CONTENT="$CONTENT" MSG_TYPE="$MSG_TYPE" CLINIC_ID="$CLINIC_ID" REQUIRES_RESPONSE="$REQUIRES_RESPONSE" \
  python3 -c '
import json, os
payload = {
    "from_pc": os.environ["FROM_PC"],
    "to_pc": os.environ["TO_PC"],
    "topic": os.environ["TOPIC"],
    "content": os.environ["CONTENT"],
    "message_type": os.environ["MSG_TYPE"],
    "requires_response": os.environ["REQUIRES_RESPONSE"] == "true",
    "priority": os.environ["PRIORITY"],
    "clinic_id": os.environ["CLINIC_ID"],
    "context_data": {
        "target_agent": os.environ["TARGET_AGENT"],
        "sender_agent": os.environ["SENDER_AGENT"],
    },
}
print(json.dumps(payload, ensure_ascii=False))
'
)" || fatal "payload construction failed (python3 json build)"

if [ -n "$NORMALIZED_NOTES" ]; then
  printf '%s' "$NORMALIZED_NOTES"
fi

if [ "$DRY_RUN" = true ]; then
  echo "DRY-RUN (no POST sent):"
  echo "$PAYLOAD"
  exit 0
fi

# --live: 実送信。secret値はargvに出さず、SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY はsb_authが
# 一時curl configへ書く(argv非露出)。process env のみを見る — $HOME/.hakudokai/env は
# 失効鍵を返す(実測既知)上、汝の契約が探索を禁ずるため参照しない。不在ならここで hard fail する。
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  fatal "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY unset in process env — refusing --live send"
fi

SUPABASE_API="${SUPABASE_URL}/rest/v1"
CURL_ERR_FILE="$(mktemp "${TMPDIR:-/tmp}/karo_second_send_iincho_curlerr.XXXXXX")" \
  || fatal "mktemp failed while preparing curl stderr capture"
RESPONSE_FILE="$(mktemp "${TMPDIR:-/tmp}/karo_second_send_iincho_resp.XXXXXX")" \
  || fatal "mktemp failed while preparing curl response capture"
# return=representation(旧: return=minimal): 沈黙送達を塞ぐために作った helper 自身が
# 送った証拠(挿入行 id)を呼出側へ返さねば本末転倒である。id を取得し stdout へ出す。
HTTP_CODE=$(sb_curl -sS -o "$RESPONSE_FILE" -w "%{http_code}" -X POST \
  "${SUPABASE_API}/pc_handshake" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "$PAYLOAD" 2>"$CURL_ERR_FILE")
CURL_ERR="$(cat "$CURL_ERR_FILE")"
RESPONSE_BODY="$(cat "$RESPONSE_FILE")"
rm -f "$CURL_ERR_FILE" "$RESPONSE_FILE"

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
  ROW_ID="$(printf '%s' "$RESPONSE_BODY" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data[0].get("id", "") if isinstance(data, list) and data else "")
except Exception:
    print("")
')"
  if [ -z "$ROW_ID" ]; then
    # HTTP は成功したが id が取れぬ = 「送った証拠が返らぬ」病そのものの再発ゆえ、
    # 沈黙成功(silent success)として扱わず fatal で失敗の届き先へ落とす。
    fatal "LIVE POST returned http_code=${HTTP_CODE} but no row id in response (return=representation not honored?) response_body=${RESPONSE_BODY:-<empty>}"
  fi
  echo "LIVE POST OK: http_code=${HTTP_CODE} id=${ROW_ID}"
  exit 0
else
  fatal "LIVE POST failed: http_code=${HTTP_CODE:-<empty>} curl_stderr=${CURL_ERR:-<empty>}"
fi

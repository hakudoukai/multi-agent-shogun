#!/usr/bin/env bash
# commander_send_shogun_second.sh — Commander→shogun-second 送信 preflight helper
#
# 目的: SecondPC shogun 宛 pc_handshake の context_data.target_agent 欠落再発防止
#       (seq114762→114764, seq114984→114985 の同型欠陥の恒久是正・fukuincho令 2026-07-10)。
#
# 必須 hygiene (fukuincho): to_pc=second_pc + topic が cross_pc_inbox_shogun-second で始まる場合、
#                           context_data.target_agent='shogun-second' が必須。本 helper が★常時強制★する。
#
# Usage:
#   bash scripts/commander_send_shogun_second.sh [--dry-run] "<topic>" "<content>" [message_type] [priority] [requires_response]
#   (message_type default=answer, priority default=normal, requires_response default=false)
#   env: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 必須。
#   --dry-run: DBへ送らず、正規化・preflight済みpayloadだけをstdoutへ出す（資格情報不要）。
#
# 出力: 送信した seq を stdout。preflight 失敗時は非0 exit + stderr。

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB_AUTH_LIB="$SCRIPT_DIR/shim/hakudokai/lib/sb_auth.sh"
# shellcheck disable=SC1090
source "$SB_AUTH_LIB"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  shift
fi

RAW_TOPIC="${1:?topic required}"
CONTENT="${2:?content required}"
MSGTYPE="${3:-answer}"
PRIORITY="${4:-normal}"
REQRESP="${5:-false}"

CANONICAL_PREFIX="cross_pc_inbox_shogun-second"
if [[ "$RAW_TOPIC" == "$CANONICAL_PREFIX" || "$RAW_TOPIC" == "$CANONICAL_PREFIX:"* ]]; then
  TOPIC="$RAW_TOPIC"
else
  TOPIC="$CANONICAL_PREFIX: $RAW_TOPIC"
fi

if [[ "$DRY_RUN" != true ]]; then
  : "${SUPABASE_URL:?SUPABASE_URL unset}"
  : "${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY unset}"
fi

# --- build payload with GUARANTEED target_agent, then preflight-assert before POST ---
PAYLOAD=$(TOPIC="$TOPIC" CONTENT="$CONTENT" MSGTYPE="$MSGTYPE" PRIORITY="$PRIORITY" REQRESP="$REQRESP" python3 - <<'PYEOF'
import json, os
topic = os.environ["TOPIC"]
reqresp = os.environ["REQRESP"].lower() in ("true","1","yes")
msg = {
    "message_type": os.environ["MSGTYPE"],
    "from_pc": "commander",
    "to_pc": "second_pc",
    "topic": topic,
    "content": os.environ["CONTENT"],
    "context_data": {
        "target_agent": "shogun-second",
        "sender_helper": "commander_send_shogun_second.sh",
    },   # ★ALWAYS enforced★
    "requires_response": reqresp,
    "priority": os.environ["PRIORITY"],
    "clinic_id": "hakudoukai_main",
    "bypass_5round_limit": False,
    "is_meta_only": False,
}
# PREFLIGHT (fail-closed): Commander→SecondPC は常に役職とcanonical topicを明示する。
ta = (msg.get("context_data") or {}).get("target_agent")
if msg.get("from_pc") != "commander":
    raise SystemExit("PREFLIGHT FAIL: from_pc!=commander")
if msg.get("to_pc") != "second_pc":
    raise SystemExit("PREFLIGHT FAIL: to_pc!=second_pc")
if ta != "shogun-second":
    raise SystemExit("PREFLIGHT FAIL: target_agent!=shogun-second")
if not topic.startswith("cross_pc_inbox_shogun-second"):
    raise SystemExit("PREFLIGHT FAIL: noncanonical topic")
print(json.dumps(msg, ensure_ascii=False))
PYEOF
)

if [[ "$DRY_RUN" == true ]]; then
  printf '%s\n' "$PAYLOAD"
  exit 0
fi

RESP=$(sb_curl -sS -m 15 -X POST "${SUPABASE_URL}/rest/v1/pc_handshake" \
  -H "Content-Type: application/json" -H "Prefer: return=representation" \
  --data-binary "$PAYLOAD")

# verify the stored row actually has target_agent (post-write assertion)
echo "$RESP" | python3 -c "
import json,sys
d=json.load(sys.stdin)
if not isinstance(d,list) or not d: raise SystemExit('POST FAILED: '+str(d)[:200])
r=d[0]
ta=(r.get('context_data') or {}).get('target_agent')
checks = {
    'from_pc': r.get('from_pc') == 'commander',
    'to_pc': r.get('to_pc') == 'second_pc',
    'target_agent': ta == 'shogun-second',
    'topic': str(r.get('topic') or '').startswith('cross_pc_inbox_shogun-second'),
}
failed = [k for k,v in checks.items() if not v]
if failed: raise SystemExit('POST-ASSERT FAIL: '+','.join(failed))
print('sent seq=%s from_pc=commander target_agent=%s topic=canonical (verified)' % (r.get('seq'), ta))
"

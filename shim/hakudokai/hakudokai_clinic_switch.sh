#!/usr/bin/env bash
# hakudokai_clinic_switch.sh — clinic 切替 wrapper (Phase B-4 task 5)
#
# 7 医院 SaaS 運用時に副医院長 / クロちゃん / 山ちゃん が clinic を切替えるための wrapper。
# 例: 副医院長が佐世保 (hakudoukai_main) → マークイズ (marquise) へ切替
#
# 操作内容:
#   1. clinic_id format 検証 (^[a-z0-9_]+$ 3-64)
#   2. ~/.openclaw/role.json の clinic_id を更新
#   3. shell rc に export を追記 (option、--persist 指定時)
#   4. 切替後 env を verbatim 出力
#
# Usage:
#   bash scripts/hakudokai_clinic_switch.sh --to marquise
#   bash scripts/hakudokai_clinic_switch.sh --to hakudoukai_main --persist
#   bash scripts/hakudokai_clinic_switch.sh --print           # 現在の clinic_id を表示
#
# 注意: shell の現在 session に env を反映するには `source` で呼ぶ必要がある。
#   eval "$(bash scripts/hakudokai_clinic_switch.sh --to marquise --eval-export)"
#
# License: MIT (shogun upstream credit 保持)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROLE_JSON="$HOME/.openclaw/role.json"

CLINIC_ID=""
ACTION="switch"
PERSIST=0
EVAL_EXPORT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --to)            CLINIC_ID="$2"; shift 2;;
    --print)         ACTION="print"; shift;;
    --persist)       PERSIST=1; shift;;
    --eval-export)   EVAL_EXPORT=1; shift;;
    -h|--help)       sed -n '2,30p' "$0"; exit 0;;
    *) echo "[clinic_switch] unknown arg: $1" >&2; exit 2;;
  esac
done

# print mode
if [ "$ACTION" = "print" ]; then
  if [ ! -f "$ROLE_JSON" ]; then
    echo "[clinic_switch] $ROLE_JSON not found" >&2
    exit 3
  fi
  CURRENT=$(python3 -c "import json;print(json.load(open('$ROLE_JSON')).get('clinic_id','(unset)'))" 2>/dev/null || echo "(parse failed)")
  echo "[clinic_switch] current clinic_id=$CURRENT"
  exit 0
fi

# switch mode
if [ -z "$CLINIC_ID" ]; then
  echo "[clinic_switch] FATAL: --to <clinic_id> required (or --print)" >&2
  exit 2
fi

# format check (^[a-z0-9_]+$ 3-64)
if ! echo "$CLINIC_ID" | grep -qE '^[a-z0-9_]+$'; then
  echo "[clinic_switch] FATAL: clinic_id '$CLINIC_ID' does not match ^[a-z0-9_]+$" >&2
  exit 2
fi
LEN=${#CLINIC_ID}
if [ "$LEN" -lt 3 ] || [ "$LEN" -gt 64 ]; then
  echo "[clinic_switch] FATAL: clinic_id length $LEN must be 3-64" >&2
  exit 2
fi

# role.json 更新 (~/.openclaw/role.json が存在しなければ作成不可、role_init.py 経由必須)
if [ ! -f "$ROLE_JSON" ]; then
  echo "[clinic_switch] FATAL: $ROLE_JSON not found" >&2
  # Codex audit B-4-3 #5 修正: Python 実行例として python3 を明示
  echo "  hint: python3 scripts/hakudokai_role_init.py --role <role> --clinic-id $CLINIC_ID" >&2
  exit 3
fi

# atomic update via tmp file
TMP_JSON="${ROLE_JSON}.tmp.$$"
python3 - "$ROLE_JSON" "$TMP_JSON" "$CLINIC_ID" <<'PYEOF'
import json, sys
src, dst, cid = sys.argv[1], sys.argv[2], sys.argv[3]
with open(src, 'r', encoding='utf-8') as fh:
    data = json.load(fh)
data['clinic_id'] = cid
import datetime, datetime as _dt
data.setdefault('switched_history', []).append({
    'to': cid,
    'at': _dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
})
with open(dst, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
PYEOF
mv "$TMP_JSON" "$ROLE_JSON"
# Codex audit B-4-3 #4 修正: chmod 失敗を warn 出力 (POSIX 非対応環境では権限手動調整必要)
if ! chmod 600 "$ROLE_JSON" 2>/dev/null; then
  echo "[clinic_switch] WARN chmod 600 failed on $ROLE_JSON (POSIX 権限非対応環境? secret 露出リスクあり、適切な権限を別途設定してください)" >&2
fi

echo "[clinic_switch] role.json clinic_id → $CLINIC_ID (updated)"

# shell rc persist (option)
if [ "$PERSIST" -eq 1 ]; then
  RC_FILE="$HOME/.bashrc"
  [ -f "$HOME/.zshrc" ] && RC_FILE="$HOME/.zshrc"
  # 既存 export を除去 + 新規追記
  if [ -f "$RC_FILE" ]; then
    sed -i '/^export HAKUDOKAI_CLINIC_ID=/d' "$RC_FILE"
  fi
  echo "export HAKUDOKAI_CLINIC_ID=$CLINIC_ID" >> "$RC_FILE"
  echo "[clinic_switch] persisted to $RC_FILE (next shell)"
fi

# eval-export mode (caller can `eval $(... --eval-export)`)
if [ "$EVAL_EXPORT" -eq 1 ]; then
  echo "export HAKUDOKAI_CLINIC_ID=$CLINIC_ID"
fi

echo ""
echo "[clinic_switch] verbatim 確認:"
cat "$ROLE_JSON"
echo ""
echo "[clinic_switch] 注意: 現 shell に env を即反映するには:"
echo "  eval \"\$(bash $0 --to $CLINIC_ID --eval-export)\""
echo "  または、新 shell を起動 (--persist 済の場合)"

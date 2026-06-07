#!/usr/bin/env bash
# box_setup.sh — Box CCG App 接続 setup (副院長裁定 4728acd7、DD-164)
# 役割: boxsdk install (idempotent) + Doppler slot 存在確認 + CCG token 取得 verify
# DD-164: secret 値投入は理事長専権、本 script は read のみ
set -euo pipefail

echo "[box_setup] $(date -Is) host=$(hostname)"

# 1. python boxsdk install (idempotent)
if python3 -c "import boxsdk" 2>/dev/null; then
  echo "[boxsdk] already installed"
else
  echo "[boxsdk] installing via pip --user"
  pip install --user --break-system-packages boxsdk 2>&1 || pip install --user boxsdk 2>&1 || {
    echo "ERR: boxsdk install failed" >&2; exit 1
  }
fi
python3 -c "import boxsdk; print('boxsdk version:', getattr(boxsdk,'__version__','?'))"

# 2. Doppler slot presence check (値は出さない)
echo "[doppler] slot presence check"
for slot in BOX_CLIENT_ID BOX_CLIENT_SECRET BOX_ENTERPRISE_ID BOX_FOLDER_CLAUDE_ROOT_ID BOX_FOLDER_KARTE_SAMPLES_ID; do
  if doppler secrets get "$slot" --project openhands --config dev --plain >/dev/null 2>&1; then
    echo "  $slot: present"
  else
    echo "  $slot: MISSING (理事長 credential 投入待ち or folder id 案件)" >&2
  fi
done

# 3. CCG token 取得 verify (secret 3 本投入後にのみ成功)
echo "[ccg] token acquire test"
doppler run --project openhands --config dev -- python3 - <<'PY' || true
import os, sys
try:
    from boxsdk import CCGAuth, Client
except ImportError as e:
    print(f"FATAL: boxsdk import failed: {e}", file=sys.stderr); sys.exit(2)
cid = os.environ.get("BOX_CLIENT_ID","")
csec = os.environ.get("BOX_CLIENT_SECRET","")
eid = os.environ.get("BOX_ENTERPRISE_ID","")
if not (cid and csec and eid):
    print("SKIP: secret 3 本未投入 (理事長 credential 投入待ち)", file=sys.stderr); sys.exit(3)
try:
    auth = CCGAuth(client_id=cid, client_secret=csec, enterprise_id=eid)
    client = Client(auth)
    me = client.user().get()
    print(f"OK CCG token, service account id={me.id} login={me.login}")
except Exception as e:
    print(f"FAIL CCG token acquire: {e}", file=sys.stderr); sys.exit(4)
PY

echo "[box_setup] done"

#!/usr/bin/env bash
# box_scope_verify.sh — claude フォルダ (386318571891) のみ access / 他フォルダ denied 実証
# 副院長裁定 4728acd7 Q2: scope 制限の必須実証
# 期待: claude root = success / enterprise root '0' = denied (403/404)
set -euo pipefail

echo "[box_scope_verify] $(date -Is)"

doppler run --project openhands --config dev -- python3 - <<'PY'
import os, sys
try:
    from boxsdk import CCGAuth, Client
    from boxsdk.exception import BoxAPIException
except ImportError:
    print("FATAL: boxsdk not installed", file=sys.stderr); sys.exit(2)

cid = os.environ.get("BOX_CLIENT_ID","")
csec = os.environ.get("BOX_CLIENT_SECRET","")
eid = os.environ.get("BOX_ENTERPRISE_ID","")
if not (cid and csec and eid):
    print("SKIP: secret 3 本未投入 (理事長 credential 投入待ち)", file=sys.stderr); sys.exit(3)
auth = CCGAuth(client_id=cid, client_secret=csec, enterprise_id=eid)
client = Client(auth)

claude_root = os.environ.get("BOX_FOLDER_CLAUDE_ROOT_ID","386318571891")
karte_samples = os.environ.get("BOX_FOLDER_KARTE_SAMPLES_ID","387023559660")

scope_ok = True
# 1. claude scope = success
try:
    f = client.folder(claude_root).get()
    print(f"PASS  claude scope id={claude_root} name='{f.name}'")
except BoxAPIException as e:
    print(f"FAIL  claude scope id={claude_root}: {e.status} {e.code}", file=sys.stderr); scope_ok = False

# 2. karte samples (claude subtree) = success
try:
    f = client.folder(karte_samples).get()
    print(f"PASS  karte_samples id={karte_samples} name='{f.name}'")
except BoxAPIException as e:
    print(f"FAIL  karte_samples id={karte_samples}: {e.status} {e.code}", file=sys.stderr); scope_ok = False

# 3. enterprise root '0' = denied 期待
try:
    items = list(client.folder("0").get_items(limit=1))
    print(f"FAIL  enterprise root '0' accessible (items={len(items)}) — scope 不完全！", file=sys.stderr)
    scope_ok = False
except BoxAPIException as e:
    print(f"PASS  enterprise root '0' denied: status={e.status} code={e.code}")

# 4. dummy non-claude folder id (例: known different folder) = denied 期待
# (test skip — claude フォルダ外の specific id を知らないため、root '0' denied が代理証拠)

sys.exit(0 if scope_ok else 1)
PY

echo "[box_scope_verify] done"

#!/usr/bin/env bash
# box_get_carte_pdfs.sh — Box claude/見本カルテ (folder 387023559660) から PDF 11本取得
# 副院長裁定 4728acd7 Q4: 取得先 = tests/visual/baseline_pdfs/
# DD-164: secret は Doppler 経由のみ、本 script は credential を直接扱わない
set -euo pipefail

DEST="${1:-tests/visual/baseline_pdfs}"
mkdir -p "$DEST"
echo "[box_get_carte_pdfs] $(date -Is) dest=$DEST"

doppler run --project openhands --config dev -- python3 - "$DEST" <<'PY'
import os, sys, pathlib
try:
    from boxsdk import CCGAuth, Client
except ImportError:
    print("FATAL: boxsdk not installed (run box_setup.sh first)", file=sys.stderr); sys.exit(2)

dest = pathlib.Path(sys.argv[1])
dest.mkdir(parents=True, exist_ok=True)

cid = os.environ.get("BOX_CLIENT_ID","")
csec = os.environ.get("BOX_CLIENT_SECRET","")
eid = os.environ.get("BOX_ENTERPRISE_ID","")
folder_id = os.environ.get("BOX_FOLDER_KARTE_SAMPLES_ID","387023559660")
if not (cid and csec and eid):
    print("SKIP: secret 3 本未投入 (理事長 credential 投入待ち)", file=sys.stderr); sys.exit(3)

auth = CCGAuth(client_id=cid, client_secret=csec, enterprise_id=eid)
client = Client(auth)
folder = client.folder(folder_id)
items = list(folder.get_items(limit=200))
count = 0
for it in items:
    if it.type != "file": continue
    if not it.name.lower().endswith(".pdf"): continue
    path = dest / it.name
    print(f"[get] {it.name} -> {path}")
    with open(path, "wb") as f:
        it.download_to(f)
    count += 1
print(f"DONE: {count} PDFs fetched into {dest}")
PY

echo "[box_get_carte_pdfs] done"

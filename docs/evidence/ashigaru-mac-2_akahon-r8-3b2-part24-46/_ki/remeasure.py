# -*- coding: utf-8 -*-
"""現 qc で母數を再測し、入力の sha256 を刷る(讀取のみ)。usage: python3 -B remeasure.py <akahon_root> <conflict_pages.txt>"""
import sys, json, hashlib, os, datetime
from pathlib import Path
R = Path(sys.argv[1]); mine = {int(l) for l in open(sys.argv[2]) if l.strip()}
cur = set(); allc = set(); rng = []
for n in range(24, 47):
    q = R / f"qc/赤本R8_Part{n}_qc.jsonl"; rec = R / f"qc/赤本R8_Part{n}_qc_reconciled.jsonl"
    pages = [json.loads(l) for l in open(q, encoding="utf-8") if l.strip()]
    rng += [p["page"] for p in pages]
    c = {p["page"] for p in pages if p.get("tag") == "conflict"}; allc |= c
    if not rec.exists(): cur |= c
    print(f"Part{n} rows={len(pages)} conflict={len(c)} reconciled={'有' if rec.exists() else '無'} mtime={datetime.datetime.fromtimestamp(os.path.getmtime(q)).isoformat(timespec='seconds')}")
ov = {json.loads(l).get("page") for l in open(R / "qc/overrides.jsonl", encoding="utf-8") if l.strip()}
adj = sorted(int(f.name[6:10]) for f in (R / "qc/adjudications").glob("*_adjudication.json"))
print(f"頁範囲={min(rng)}..{max(rng)} 行={len(rng)}")
print(f"conflict(全Part)={len(allc)} conflict(reconciled無Part)={len(cur)} 本束={len(mine)}")
print(f"cur-mine={sorted(cur-mine)} mine-cur={sorted(mine-cur)}")
print(f"overrides∩本束={sorted(ov & mine)} adjudications∩本束={sorted(set(adj) & mine)} adjudications={adj}")

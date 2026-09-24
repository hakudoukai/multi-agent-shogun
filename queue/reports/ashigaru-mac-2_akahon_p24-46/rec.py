# -*- coding: utf-8 -*-
"""裁き1頁を追記。usage: python3 -B rec.py <page> <decision> "<reason>" ["<ai_error1>" ...]
decision: AI | AI_要訂正 | machine | 両方欠 """
import json, sys, datetime
from pathlib import Path
import os
F = Path(__file__).with_name(os.environ.get("ADJ_OUT", "adjudication_p24-46.jsonl"))
BY = os.environ.get("ADJ_BY", "ashigaru-mac-2")
p, d, why = int(sys.argv[1]), sys.argv[2], sys.argv[3]
assert d in ("AI", "AI_要訂正", "machine", "両方欠"), d
assert 346 <= p <= 690, p
done = {json.loads(l)["page"] for l in F.read_text(encoding="utf-8").splitlines() if l.strip()} if F.exists() else set()
assert p not in done, f"page {p} 既に在り"
r = {"page": p, "part": (p - 1) // 15 + 1, "png": f"赤本R8_p{p:04d}.png", "decision": d, "reason": why,
     "ai_errors": sys.argv[4:], "method": "原画像を専任2(Claude)が直に目視し AI 本文・機械源の鍵と突合", "by": BY,
     "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
with open(F, "a", encoding="utf-8") as f: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("rec", p, d, "total", len(done) + 1)

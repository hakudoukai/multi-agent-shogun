# -*- coding: utf-8 -*-
"""旧束 100 件(不変)＋Part25 追加 12 件を現 qc の conflict 集合と突合して judgments を建て、入力の sha256 を刷る(讀取のみ)。
usage: python3 -B combine.py <akahon_root> <旧束dir> <追加jsonl> <出力dir>"""
import sys, json, hashlib, collections
from pathlib import Path
R, OLD, ADD, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
def rd(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
old = []
for f in sorted(OLD.glob("adj_batch*.jsonl")) + [OLD / "adjudication_p24-46.jsonl"]: old += rd(f)
add = rd(ADD)
cur = set()
for n in range(24, 47):
    if (R / f"qc/赤本R8_Part{n}_qc_reconciled.jsonl").exists(): continue
    cur |= {p["page"] for p in rd(R / f"qc/赤本R8_Part{n}_qc.jsonl") if p.get("tag") == "conflict"}
allr = old + add
pages = [r["page"] for r in allr]
dup = [p for p, c in collections.Counter(pages).items() if c > 1]
print(f"旧束={len(old)} 追加={len(add)} 計={len(allr)} 重複={dup} 現conflict={len(cur)}")
print(f"cur-judged={sorted(cur - set(pages))} judged-cur={sorted(set(pages) - cur)}")
assert not dup and set(pages) == cur, "突合不一致"
allr.sort(key=lambda r: r["page"])
with open(OUT / "judgments_part24-46.jsonl", "w", encoding="utf-8") as f:
    for r in allr: f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(OUT / "judgments_part24-46.tsv", "w", encoding="utf-8") as f:
    f.write("page\tpart\tdecision\tn_ai_errors\tby\tsource\treason\n")
    oldp = {r["page"] for r in old}
    for r in allr:
        f.write(f'{r["page"]}\t{r["part"]}\t{r["decision"]}\t{len(r["ai_errors"])}\t{r["by"]}\t{"旧束" if r["page"] in oldp else "追加"}\t{r["reason"]}\n')
for name, rs in (("全", allr), ("旧束", old), ("追加", add)):
    print(name, dict(sorted(collections.Counter(r["decision"] for r in rs).items())))
print("by", dict(collections.Counter(r["by"] for r in allr)))
with open(OUT / "raw/input_sha256.txt", "w", encoding="utf-8") as f:
    ins = []
    for n in range(24, 47):
        ins += [R / f"qc/赤本R8_Part{n}_qc.jsonl", R / f"ai/赤本R8_Part{n}_extracted.json", R / f"ocr/赤本R8_Part{n}_ocr.jsonl"]
    ins.append(R / "qc/overrides.jsonl")
    for p in ins:
        f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(R.parent.parent)}\n")
print("inputs", len(ins))

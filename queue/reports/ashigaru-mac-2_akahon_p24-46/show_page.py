# -*- coding: utf-8 -*-
"""赤本R8 衝突頁の材料を1頁分並べて刷る(読取専用)。usage: python3 -B show_page.py <page> [maxchars]"""
import json, sys, re, importlib.util
from pathlib import Path
R = Path.home() / "akahon-r8"; O = R / "out/akahon"
spec = importlib.util.spec_from_file_location("pl", R / "akahon_r8_pipeline.py"); pl = importlib.util.module_from_spec(spec); spec.loader.exec_module(pl)
p = int(sys.argv[1]); mx = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
part = (p - 1) // 15 + 1
qc = [json.loads(l) for l in open(O / f"qc/赤本R8_Part{part:02d}_qc.jsonl", encoding="utf-8") if l.strip()]
row = next(r for r in qc if r["page"] == p)
layer = pl._load_jsonl(O / "layer/赤本R8_layer.jsonl").get(p, "")
ocr = pl._load_jsonl(O / f"ocr/赤本R8_Part{part:02d}_ocr.jsonl").get(p, "")
ai = json.load(open(O / f"ai/赤本R8_Part{part:02d}_extracted.json", encoding="utf-8"))
ents = [e for e in ai.get("pages", []) if int(e["page"]) == p]
ait = "\n".join(pl._ai_text_of_page(e) for e in ents)
print(f"== page {p} Part{part:02d} png={O}/png/赤本R8_p{p:04d}.png")
print("qc:", json.dumps(row, ensure_ascii=False))
print("keys layer:", sorted(pl._keys(layer))); print("keys ocr:", sorted(pl._keys(ocr))); print("keys ai:", sorted(pl._keys(ait)))
print("ai types:", [e.get("type") for e in ents])
miss = row.get("nums_missing_in_ai", [])
print("missing→bare-in-AI:", {m: (re.sub(r"\D", "", m) in re.sub(r"[,，]", "", ait)) for m in miss})
lines=[x.strip() for x in layer.strip().splitlines() if x.strip()]
print("layer last line (nombre?):", lines[-1] if lines else None)
print("---- AI text ----"); print(ait[:mx])
if "--ocr" in sys.argv: print("---- OCR(tesseract) ----"); print(ocr[:mx])
if "--layer" in sys.argv: print("---- layer ----"); print(layer[:mx])

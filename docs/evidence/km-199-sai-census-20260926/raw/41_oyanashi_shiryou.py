# -*- coding: utf-8 -*-
# 親なしの送出行を ★器 agent_letter.py L335-336 の f-string そのもの★ で組み（ctx に parent_seq 無し）、40 の五形へ掛ける。
# 糊した試料であり実の便ではない（母數 127 に数へぬ）。
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "40_chuushutsu.py"))
src = open(spec.origin, encoding="utf-8").read().split("FORMS = ")[0]
ns = {"__file__": spec.origin}; exec(src, ns)
for to_role, seq, ctx in (("karo-mac", 999001, {}), ("gunshi-mac", 999002, {"parent_seq": 999000})):
    line = (f"★{to_role} へ送出した★ seq={seq}" + (f"（parent_seq={ctx.get('parent_seq')}）" if ctx.get("parent_seq") else "")) + "\n"
    print(repr(line.strip()), "→", " ".join(f"{k}={ns[k](line)}" for k in ("A", "B", "C", "C2", "D")))

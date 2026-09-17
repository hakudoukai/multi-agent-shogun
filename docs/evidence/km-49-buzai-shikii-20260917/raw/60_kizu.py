#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋔ ―― 第48弾の「己の疵」を ★器で数へる★。札は七・紙は六 ∴ 差の在り所を名指す。
   ★見出しの方言で數が動く★(疵の見出しは方言二形)ゆゑ、当てた形と拾つた行を悉く刷る。"""
import io, re, sys, os
kami, hako = sys.argv[1], sys.argv[2]
for _p in (kami, hako):
    if not os.path.isfile(_p):
        sys.stderr.write("★讀む物が無い(「%s」)★\n" % _p); sys.exit(3)
s = io.open(kami, encoding="utf-8").read()
lines = s.split("\n")
# ―― ㋖ の節を切る(節の境は次の `## ` 見出し)
st = [i for i, l in enumerate(lines) if l.startswith("## ㋖")]
if len(st) != 1:
    sys.stderr.write("★㋖ の見出しが %d 本 ―― 一本でなければ切れぬ★\n" % len(st)); sys.exit(3)
i0 = st[0]
i1 = next((j for j in range(i0 + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
setsu = lines[i0:i1]
print("紙 = %s" % kami)
print("㋖ の節 = %d 行目〜%d 行目(%d 行)" % (i0 + 1, i1, len(setsu)))
print("")
katachi = [("甲 番号列 `^\\d+\\. `", re.compile(r"^(\d+)\. ")),
           ("乙 中黒列 `^- `",       re.compile(r"^- ")),
           ("丙 太字頭 `^\\d+\\. \\*\\*`", re.compile(r"^\d+\. \*\*"))]
for na, rx in katachi:
    hit = [(i0 + 1 + k, l) for k, l in enumerate(setsu) if rx.match(l)]
    print("―― 形 %s : ★%d 本★" % (na, len(hit)))
    for n, l in hit:
        print("     L%-4d %s" % (n, l[:78]))
    print("")
# ―― 便が名乗つた數
box = io.open(hako, encoding="utf-8", errors="replace").read()
rx2 = re.compile(r"疵\s*([0-9]+)")
mm = [(m.group(0), box[max(0, m.start()-60):m.start()].splitlines()[-1][-50:]) for m in rx2.finditer(box)]
print("―― 箱 %s に在る「疵N」の名乗り = ★%d 件★" % (hako, len(mm)))
for g, ctx in mm:
    print("     「%s」 … 直前 ≪%s≫" % (g, ctx))
print("")
tsui = [l for l in box.split("\n") if "㋖追補" in l]
print("―― 「㋖追補」を載せた便 = ★%d 行★" % len(tsui))
for l in tsui:
    print("     %s" % l.strip()[:200])

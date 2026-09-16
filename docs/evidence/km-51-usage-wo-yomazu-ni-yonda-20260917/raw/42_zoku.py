# -*- coding: utf-8 -*-
"""㋐ の 母數を族(家/束/外)へ割る ―― 41_boshu.out の「器別」表を讀んで畳む。
使ひ方: python3 raw/42_zoku.py raw/41_boshu.out
★多行の器名(heredoc の胴)が在る★ ゆゑ行単位では数へられぬ。數の行から族の語までを一件とする。"""
import re, sys, collections
src = sys.argv[1]
lines = open(src, encoding="utf-8").read().split("\n")
try:
    i = lines.index("--- 器別(器 / 族 / 契約の出所 / 判 / 回数) ---") + 1
except ValueError:
    print("★表の頭が見つからぬ★"); sys.exit(1)
ZOKU = ("家の器", "束の器", "外の器")
hon = collections.Counter(); kai = collections.Counter()
han = collections.Counter()
n = None; buf = []
rec = 0
while i < len(lines):
    L = lines[i]
    if L.startswith("---") or L.strip() == "" and n is None:
        if L.startswith("---"): break
        i += 1; continue
    m = re.match(r"^\s*(\d+)\s+(.*)$", L)
    if m and (any(z in L for z in ZOKU) or n is None or any(z in "\n".join(buf) for z in ZOKU)):
        n = int(m.group(1)); buf = [m.group(2)]
    elif n is not None:
        buf.append(L)
    else:
        i += 1; continue
    body = "\n".join(buf)
    z = next((z for z in ZOKU if z in body), None)
    if z:
        rec += 1
        hon[z] += 1; kai[z] += n
        v = body.split(z, 1)[1].split()
        han[(z, v[-1] if v else "?")] += n
        n = None; buf = []
    i += 1
print("★族の別(器の本数 / 呼びの回数)★  ―― 出所 %s" % src)
for z in ZOKU:
    print("  %s  器 %3d 本 / 呼び %4d 回" % (z, hon[z], kai[z]))
print("  ―――― 合計 器 %d 本 / 呼び %d 回(件 %d)" % (sum(hon.values()), sum(kai.values()), rec))
print("★判の別(族 × 判 / 呼びの回数)★")
for (z, v), c in sorted(han.items()):
    print("  %s %-6s %4d 回" % (z, v, c))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐ の四つの候補を ★同じ束★ で測つて並べる(選ばなかつた物も數で退ける)。
   加へて ㋑ ―― 7,896,856 を ★どの定義なら出せるか★ を實測する。
   讀む(sha を取る)ゆゑ ★之は閾の器ではない。比べる為の器である。★"""
import hashlib, os, sys, collections

root = sys.argv[1]
SHIKII = int(sys.argv[2]) if len(sys.argv) > 2 else 1048576
reg = []
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        if os.path.isfile(p) and not os.path.islink(p):
            reg.append(p)
reg.sort()
size = {p: os.path.getsize(p) for p in reg}
wa = sum(size.values())
print("根 = %s / 常なる file = %d 本 / byte和 = %d / 部材閾 = %d" % (root, len(reg), wa, SHIKII))
print("")

print("―― 定義一 ★一本の file★(本器が採る)")
koe = sorted([p for p in reg if size[p] >= SHIKII], key=lambda p: -size[p])
print("   閾超 = %d 本 / 和 = %d(束の %.1f%%)" % (len(koe), sum(size[p] for p in koe), 100.0 * sum(size[p] for p in koe) / wa))
for p in koe:
    print("     %10d  %s" % (size[p], os.path.relpath(p, root)))
noko = [size[p] for p in reg if size[p] < SHIKII]
print("   閾直下の最大 = %d / 閾超の最小 = %d ―― ★不感帯 = %d〜%d(広さ %.1f 倍)★"
      % (max(noko), min(size[p] for p in koe), max(noko) + 1, min(size[p] for p in koe),
         1.0 * min(size[p] for p in koe) / max(noko)))
print("")

print("―― 定義二 ★一つの dir★(段ごと・累積の二形を出す ―― 属し方が一意でない證)")
dan = collections.Counter()
rui = collections.Counter()
for p in reg:
    d = os.path.dirname(os.path.relpath(p, root)) or "."
    dan[d] += size[p]
    parts = d.split(os.sep)
    for i in range(len(parts)):
        rui[os.sep.join(parts[: i + 1])] += size[p]
print("   dir の數 = %d" % len(dan))
for d, v in dan.most_common(4):
    print("     段  %10d  %s" % (v, d))
for d, v in rui.most_common(4):
    print("     累積%10d  %s" % (v, d))
print("   ★段の和 = %d / 累積の和 = %d ―― 同じ束で二つの數が出る(二重に数へる)★" % (sum(dan.values()), sum(rui.values())))
print("")

print("―― 定義三 ★一つの拡張子★")
kaku = collections.Counter()
for p in reg:
    b = os.path.basename(p)
    e = ("." + b.split(".")[-1]) if "." in b[1:] else "(無)"
    kaku[e] += size[p]
for e, v in kaku.most_common(4):
    print("     %10d  %s" % (v, e))
print("   ★.tsv の和 = %d ―― 誰が重いかは出ぬ。二重拡張子(.tsv.json)は %s に数へた★"
      % (kaku.get(".tsv", 0), ".json"))
print("")

print("―― 定義四 ★同内容の群(sha 一致)★")
h = {}
for p in reg:
    h[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()
gun = collections.defaultdict(list)
for p in reg:
    gun[h[p]].append(p)
modoseru = 0
kazu = 0
for s, ps in gun.items():
    if len(ps) > 1:
        kazu += 1
        modoseru += sum(size[p] for p in ps) - max(size[p] for p in ps)
        print("     群(%d 本) 戻せる %d byte : %s" % (len(ps), sum(size[p] for p in ps) - max(size[p] for p in ps),
              " / ".join(os.path.relpath(p, root) for p in ps)))
print("   ★sha 一致の群 = %d 組 / 戻せる和 = %d byte★" % (kazu, modoseru))
print("")

print("―― ㋑ ★7,896,856 を出せる定義は在るか★(頭 4096 byte の一致で括る = 近似重複)")
atama = collections.defaultdict(list)
for p in reg:
    if size[p] >= SHIKII:
        with open(p, "rb") as fh:
            atama[hashlib.sha256(fh.read(4096)).hexdigest()].append(p)
for s, ps in atama.items():
    if len(ps) > 1:
        wa_g = sum(size[p] for p in ps)
        dai = max(size[p] for p in ps)
        print("     近似群(%d 本) 群和 %d / 最大一本 %d / ★群和−最大 = %d★" % (len(ps), wa_g, dai, wa_g - dai))
        for p in sorted(ps, key=lambda q: -size[q]):
            print("        %10d  %s" % (size[p], os.path.relpath(p, root)))

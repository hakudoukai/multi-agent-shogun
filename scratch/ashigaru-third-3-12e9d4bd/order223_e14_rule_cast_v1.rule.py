# -*- coding: utf-8 -*-
"""order223 後継 ―― 條 二百六十三 の掛かり先を 本席の器の悉皆に当てる（走 0・讀取のみ）

條 二百六十三（家老が下した語）: ★『最初の当たり』で決める網は 当たりの数を先に数へよ★
"""
import os, io, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "order223_e14_rule_cast_v1.raw.txt")

# ★網★ = 「最初の当たりで決める」形の字（棲家は分けて居らぬ＝註釈・文字列も拾ふ）
PATS = [
    "re.search(",
    "re.match(",
    ".find(",
    "next(",
    "head -1",
    "grep -m1",
]

L = []
def say(x): L.append(x)

say("=== order223 後継 ―― 條 二百六十三 の掛かり先（本席の器の悉皆） ===")
say("條: ★『最初の当たり』で決める網は 当たりの数を先に数へよ★（家老が下した語）")
say("")

names = sorted([f for f in os.listdir(HERE) if f.endswith(".py")])
say("母 = 本席 dir の .py 悉く = " + str(len(names)) + " 枚")
say("網 = " + repr(PATS) + " ※★字の網ゆゑ 註釈・文字列も拾ふ（棲家は分けて居らぬ）★")
say("")

tot = {}
per = []
unread = 0
for nm in names:
    ap = os.path.join(HERE, nm)
    try:
        text = io.open(ap, encoding="utf-8").read()
    except Exception:
        unread += 1
        continue
    hits = {}
    for pt in PATS:
        c = text.count(pt)
        if c:
            hits[pt] = c
            tot[pt] = tot.get(pt, 0) + c
    if hits:
        per.append((nm, hits))

say("--- §A 当たつた file（一枚づつ） ---")
for nm, hits in per:
    say("  " + nm + " : " + ", ".join([k + "=" + str(v) for k, v in sorted(hits.items())]))
say("当たつた file = " + str(len(per)) + " / 讀めなんだ = " + str(unread))
say("")

say("--- §B 形ごとの和 ---")
s = 0
for k in sorted(tot.keys()):
    say("  " + k + " = " + str(tot[k]))
    s += tot[k]
say("★和 = " + str(s) + " 箇所（母 " + str(len(names)) + " 枚・当たつた file " + str(len(per)) + " 枚）★")
say("※★之は『疵の数』に非ず★ ―― 当たりが 2 件以上 立ち得る形のみが疵である。")
say("※★一つづつ読んで判ずるは 次弾（E16）★。本弾では 其の別は 測定不能。")
say("")

say("--- §C 負の対照 ---")
zz = "zzz_no_such_token_o223("
z = 0
for nm in names:
    try:
        z += io.open(os.path.join(HERE, nm), encoding="utf-8").read().count(zz)
    except Exception:
        pass
say("現に無い字 " + zz + " の和 = " + str(z) + " ―― ★器は 0 を出す口を現に持つ★")
missing = os.path.join(HERE, "no_such_file_for_negative_control_o223.py")
say("現に無い path を讀まうとした結果: exists=" + str(os.path.exists(missing)))
say("")

# ★己の器 自身にも掛ける（條 百七十九 ―― 己が席に課す作法を 己の条の鋳り方にも掛けよ）★
me = io.open(os.path.abspath(__file__), encoding="utf-8").read()
say("--- §D ★己自身に掛ける★（條 百七十九） ---")
mine = dict([(pt, me.count(pt)) for pt in PATS if me.count(pt)])
say("本器の当たり = " + repr(sorted(mine.items())))
say("★本器は『最初の当たり』で決める形を 一つも用ゐて居らぬ（count は悉皆を数へる）★"
    if not [k for k in mine if k in ("re.search(", "re.match(", ".find(", "next(")]
    else "★本器も 当たりの数を先に数へよ★")

txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))

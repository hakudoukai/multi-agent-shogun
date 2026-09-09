# -*- coding: utf-8 -*-
"""order223 後継 ―― 條 二百六十三 の掛かり先を 本席の器の悉皆に当てる（走 0・讀取のみ）

條 二百六十三（家老が下した語）: ★『最初の当たり』で決める網は 当たりの数を先に数へよ★
"""
import os, io, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "order223_e14_rule_cast_v2.raw.txt")

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

say("=== order223 後継 v2 ―― 條 二百六十三 の掛かり先（本席の器の悉皆） ===")
say("★v2 の由★: v1 は ①負の対照が 1 と出た（因=★母に 己(器)自身を含み 器が其の字を持つ★）")
say("           ②★字の網が 己の網の定義行(PATS)を拾ふ★ ゆゑ 本器の当たりが 6 形 全てに立つた。")
say("★何れも 数が誤つたのではなく 母と網の説きが足りなんだ ―― v2 で 己を含む/除くを 欄で分ける★")
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
me_name = os.path.basename(os.path.abspath(__file__))
z_all = 0; z_ex = 0
for nm in names:
    try:
        c = io.open(os.path.join(HERE, nm), encoding="utf-8").read().count(zz)
    except Exception:
        continue
    z_all += c
    if nm != me_name:
        z_ex += c
say("現に無い字 " + zz + " の和（★己(器)を含む母★） = " + str(z_all))
say("現に無い字 " + zz + " の和（★己(器)を除く母★） = " + str(z_ex)
    + " ―― ★器は 0 を出す口を現に持つ★")
say("★差 " + str(z_all - z_ex) + " = 器自身が 其の字を持つ分（母に己を含めた故）★")
missing = os.path.join(HERE, "no_such_file_for_negative_control_o223.py")
say("現に無い path を讀まうとした結果: exists=" + str(os.path.exists(missing)))
say("")

# ★己の器 自身にも掛ける（條 百七十九 ―― 己が席に課す作法を 己の条の鋳り方にも掛けよ）★
me = io.open(os.path.abspath(__file__), encoding="utf-8").read()
say("--- §D ★己自身に掛ける★（條 百七十九） ---")
mine = dict([(pt, me.count(pt)) for pt in PATS if me.count(pt)])
say("本器の当たり（★網の定義行を含む★） = " + repr(sorted(mine.items())))
# ★網の定義行(PATS)を除いた 本器の当たり★
lines = [x for x in me.split(chr(10))]
body = chr(10).join([x for x in lines if not x.strip().startswith('"') or "PATS" not in me[:0] ])
inpats = {}
for pt in PATS:
    c = 0
    for x in lines:
        t = x.strip()
        # PATS の定義行（'…',形）と say(repr(PATS)) の行は 網の自己参照ゆゑ除く
        if t.startswith('"' + pt) or t.startswith("'" + pt):
            continue
        c += x.count(pt)
    if c: inpats[pt] = c
say("本器の当たり（★網の定義行を除く★） = " + repr(sorted(inpats.items())))
real = [k for k in inpats if k in ("re.search(", "re.match(", ".find(", "next(")]
say("★本器が 現に用ゐて居る『最初の当たり』形 = " + repr(sorted(real)) + "★")
say("※`.count(` と `for` の悉皆走査は ★最初の当たりで決めて居らぬ★ ゆゑ 條 二百六十三 の外である。")

txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))

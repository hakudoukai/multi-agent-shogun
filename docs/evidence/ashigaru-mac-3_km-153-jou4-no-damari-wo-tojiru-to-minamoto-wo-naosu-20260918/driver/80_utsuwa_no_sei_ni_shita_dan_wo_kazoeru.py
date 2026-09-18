# -*- coding: utf-8 -*-
"""★己が『疵を器の所為にした』断を数へる★(家老令 km-153 ㋒ 前段 ―― 検出のみ・再判は 81 弾)
歩き根 = docs/evidence/ashigaru-mac-3_*(當席の束のみ)／深さ = 無制限／読む物 = .md/.txt/.tsv(器の source は読まぬ)。
★己を除く★: 本弾の束(km-153)は ★母數から除かず、別列で数へる★ ―― 「除いた」は「歩いて居らぬ」に非ず(裁の條)。
方言は下の HOUGEN に逐語で列べ、★一行が幾つの方言に当たるか(排他性)も刷る★ ―― 同じ行を二度数へた數を隠さぬ。
四札: 刻=冠 / 根と深さ=上記 / rc=本器の returncode / 陽性対照=本弾が自ら書いた逐語一行(必ず当たる筈の物)。"""
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

NE = os.path.join("docs", "evidence")
ORE = "ashigaru-mac-3_"
KONKAI = os.path.basename(BUNDLE)
YOMU = (".md", ".txt", ".tsv")

HOUGEN = [
    ("甲", "器の性"),            # 「器の性であり本紙の疵ではない」の形
    ("乙", "器の所為"),
    ("丙", "本紙の疵ではない"),
    ("丁", "本紙の疵に非ず"),
    ("戊", "濡れ衣"),
    ("己", "器を疑へ"),
    ("庚", "器の疵"),
]
TAISHOU = "★陽性対照(㋒)★ 本弾が自ら書いた此の一行は方言 甲『器の性』を含む ―― 検出子が働く事の證"

# ―― ★陽性対照は歩く前に置く★ ―― 後から書いた紙は其の歩きに乗つて居らぬ(乗せねば對照に成らぬ) ――
TAISHOU_P = os.path.join(BUNDLE, "raw", "80_taishou.txt")
kaku(TAISHOU_P, TAISHOU + "\n")

rows = []
taba_kazu = {}
files = 0
for taba in sorted(os.listdir(NE)):
    if not taba.startswith(ORE):
        continue
    d = os.path.join(NE, taba)
    if not os.path.isdir(d):
        continue
    for cur, dirs, fs in os.walk(d):
        if "__pycache__" in cur:
            continue
        for f in sorted(fs):
            if not f.endswith(YOMU):
                continue
            p = os.path.join(cur, f)
            files += 1
            try:
                body = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                rows.append([taba, os.path.relpath(p, d), 0, "★読めぬ ―― 測れぬは通さぬ★", ""])
                continue
            for i, ln in enumerate(body.split("\n"), 1):
                atta = [na for na, kg in HOUGEN if kg in ln]
                if not atta:
                    continue
                taba_kazu[taba] = taba_kazu.get(taba, 0) + 1
                rows.append([taba, os.path.relpath(p, d), i, "/".join(atta), ln.strip()[:120]])

hondan = [r for r in rows if r[0] == KONKAI]
kako = [r for r in rows if r[0] != KONKAI]
futatsu = [r for r in rows if "/" in str(r[3])]
kaku_tsv(os.path.join(BUNDLE, "raw", "80_utsuwa_no_sei_kouho.tsv"),
         [[("★本弾★" if r[0] == KONKAI else "過去"), r[0][:46], r[1], r[2], r[3], r[4]] for r in rows],
         header=["弾", "束", "紙", "行", "方言", "逐語(120字で截つ)"])
kaku_tsv(os.path.join(BUNDLE, "raw", "80_hougen_no_hai.tsv"),
         [[na, kg, sum(1 for r in rows if na in str(r[3]).split("/"))] for na, kg in HOUGEN]
         + [["―", "★二方言以上に当たつた行★", len(futatsu)],
            ["―", "★過去の束の当たり(母數)★", len(kako)],
            ["―", "★本弾自身の当たり(別列)★", len(hondan)]],
         header=["方言", "逐語の鍵", "当たり行"])
kaku(os.path.join(BUNDLE, "raw", "80_kensaku_no_shi.txt"),
     "as-of %s(UTC)\n根=%s/%s*(當席の束のみ)／深さ=無制限／読む拡張子=%s\n"
     "歩いた紙=%d 本／束=%d 個\n"
     "当たり行=%d(内 ★過去の束 %d★ / 本弾 %d)／二方言以上に当たつた行=%d\n"
     "%s\n"
     "【之が意味せぬ事】\n"
     "・当たり行の數は ★『器の所為にした断』の數ではない★ ―― 方言は語であり、註や引用にも現れる。\n"
     "  再判(81 弾)で一件づつ読み、断でない物を落とす。∴ 此の數は ★上限★ である。\n"
     "・本弾自身の当たりを母數に混ぜて居らぬ(別列)。混ぜれば己の紙で己を膨らませる。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), NE, ORE,
        "/".join(YOMU), files, len(taba_kazu) or 0, len(rows), len(kako), len(hondan), len(futatsu),
        TAISHOU))
TA_REL = os.path.relpath(TAISHOU_P, os.path.join(NE, KONKAI))
atatta = [r for r in hondan if r[1] == TA_REL]
assert len(atatta) == 1, "★陽性対照が %d 件 ―― 検出子が働いて居らぬ(測れぬは通さぬ)★" % len(atatta)
print("陽性対照: %s 行%d 方言%s ―― 検出子は働いて居る" % (TA_REL, atatta[0][2], atatta[0][3]))
print("紙 %d 本 ―― 当たり %d 行(過去 %d / 本弾 %d)・二方言以上 %d" % (files, len(rows), len(kako), len(hondan), len(futatsu)))
for na, kg in HOUGEN:
    print("  %s『%s』 %d 行" % (na, kg, sum(1 for r in rows if na in str(r[3]).split("/"))))

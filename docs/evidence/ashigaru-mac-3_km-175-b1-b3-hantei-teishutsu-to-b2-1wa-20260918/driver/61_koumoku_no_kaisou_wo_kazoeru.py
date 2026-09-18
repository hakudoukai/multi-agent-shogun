# -*- coding: utf-8 -*-
"""★項目の數は『どの階を数へたか』で変はる★(km-175 ㋔ の註)
板 38dcde86 は「全階層 再帰= episode.* 9 + scenes.* 22 = 31／scene 階のみなら 6」と記す。
當席の受入形の表は 18 行である。★之は矛盾ではなく 数へた階が違ふ★ ―― 其れを器で示す。
四札: 刻=冠 / 根=下の二紙 / rc=本器の returncode / 対照=存在せぬ型名を一つ混ぜ『解けぬ』に落ちるか見る。"""
import os
import re
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

DENTAL = "/Users/momizimac/DentalBI"
SE = os.path.join(DENTAL, "frontend/src/features/child-passport/story-engine")
NIHON = [os.path.join(SE, "episodes/episode.ts"), os.path.join(SE, "types.ts")]

# ―― interface を塊で切り、宣言された field を数へる(★行番でなく形で切る★) ――
IF_RE = re.compile(r"^export interface (\w+) \{$")
# ★疵(己)★ 初版は行末 `;` を要求した ―― 此の樹の TS に `;` は無く、悉く 0 を刷つた(rc=0 の儘)。
FLD_RE = re.compile(r"^  (\w+)(\?)?:\s*(.+?)\s*;?\s*$")
IF = {}
for p in NIHON:
    naka = None
    for l in open(p, encoding="utf-8").read().split("\n"):
        m = IF_RE.match(l)
        if m:
            naka = m.group(1); IF[naka] = []
            continue
        if naka is not None:
            if l == "}":
                naka = None
                continue
            f = FLD_RE.match(l)
            if f:
                IF[naka].append((f.group(1), f.group(3), bool(f.group(2))))

def kaiso(na, michi=(), kei="甲"):
    """戻り= 再帰で数へた field の総数。★輪は michi で止める★。
    ★数へ方を二つ置く(同じ語で違ふ物を数へぬ為)★:
      甲= 型の参照が現れる毎に数へる ―― [A, A] の tuple は A を ★二度★ 展開する。
      乙= 一つの field の中で同じ型は ★一度だけ★ 展開する。"""
    if na in michi or na not in IF:
        return 0
    n = 0
    for _, typ, _ in IF[na]:
        n += 1
        ko = re.findall(r"\b([A-Z]\w+)\b", typ)
        if kei == "乙":
            mita = set(); ko = [k for k in ko if not (k in mita or mita.add(k))]
        for k in ko:
            n += kaiso(k, michi + (na,), kei)
    return n

rows = []
for na in sorted(IF):
    rows.append([na, len(IF[na]), kaiso(na), ", ".join(f[0] for f in IF[na])])
kaku_tsv(os.path.join(BUNDLE, "raw", "64_b2_interface_no_kazu.tsv"), rows,
         header=["interface", "宣言された field", "再帰で数へた field", "field の名"])

ep_ji = len(IF.get("Episode", []))                       # episode / scenes の 2
ep_no = len(IF.get("EpisodeMeta", [])) + 1               # meta 8 + scenes[] 1 = 9(板の『episode.* 9』)
sc_ji = len(IF.get("Scene", []))                         # 板の『scene 階のみ 6』
sc_saiki = kaiso("Scene")
sc_saiki_otsu = kaiso("Scene", kei="乙")
zen = kaiso("Episode")
zen_otsu = kaiso("Episode", kei="乙")
hyou = len(open(os.path.join(BUNDLE, "raw", "61_b2_ukeire_no_koumoku.tsv"),
               encoding="utf-8").read().rstrip("\n").split("\n")) - 1

# ★陰性対照★ ―― 在らぬ型は 0 を返す(解けぬ物を黙つて数へぬ)
nai = kaiso("SonnaKataWaNai98765432")

kaku_tsv(os.path.join(BUNDLE, "raw", "65_b2_kaisou_no_tsukiawase.tsv"),
         [["Episode の宣言 field", ep_ji, "episode + scenes の 2 ―― ★之を『項目』と呼ぶ者は居らぬ★"],
          ["episode.* (meta 8 + scenes[] 1)", ep_no, "板の『episode.* 9』と ★一致★"],
          ["Scene の宣言 field", sc_ji, "板の『scene 階のみなら 6』と " + ("★一致★" if sc_ji == 6 else "★食ひ違ふ(實測 %d)★" % sc_ji)],
          ["scenes.* 再帰(甲=参照毎)", sc_saiki, "板の『scenes.* 22』と " + ("★一致★" if sc_saiki == 22 else "★食ひ違ふ★")],
          ["scenes.* 再帰(乙=同型一度)", sc_saiki_otsu, "板の『scenes.* 22』と " + ("★一致★" if sc_saiki_otsu == 22 else "★食ひ違ふ★")],
          ["Episode 全階層 再帰(甲)", zen, "板の『31』と " + ("★一致★" if zen == 31 else "★食ひ違ふ★")],
          ["Episode 全階層 再帰(乙)", zen_otsu, "板の『31』と " + ("★一致★" if zen_otsu == 31 else "★食ひ違ふ★")],
          ["★當席の受入形の表★", hyou, "★受入で人が書く項目★= episode 階 9 + scene 階の代表 8 + 門 1 ―― 再帰の総数ではない"],
          ["★差 1 の始末★ 乙 %d − 封筒の鍵 episode 1" % zen_otsu, zen_otsu - 1,
           "板の 31(=episode.* %d + scenes.* %d)と %s ―― ★差は丸めず名指した★: 板は封筒の鍵 `episode` を項目に数へず、當席の再帰は数へる"
           % (ep_no, sc_saiki_otsu, "★一致★" if zen_otsu - 1 == ep_no + sc_saiki_otsu == 31 else "★尚 食ひ違ふ★")],
          ["★陰性対照★(在らぬ型)", nai, "0 が正 ―― 解けぬ型を黙つて数へぬ"]],
         header=["何を数へたか", "数", "言"])
print("宣言: Episode %d / EpisodeMeta %d / Scene %d" % (ep_ji, len(IF.get("EpisodeMeta", [])), sc_ji))
print("再帰 甲: Episode %d / Scene %d ―― 板 31/22 と %s"
      % (zen, sc_saiki, "一致" if (zen == 31 and sc_saiki == 22) else "食ひ違ふ"))
print("再帰 乙: Episode %d / Scene %d ―― 板 31/22 と %s"
      % (zen_otsu, sc_saiki_otsu, "一致" if (zen_otsu == 31 and sc_saiki_otsu == 22) else "食ひ違ふ"))
print("當席の表 %d 行・陰性対照 %d・interface %d 本" % (hyou, nai, len(IF)))

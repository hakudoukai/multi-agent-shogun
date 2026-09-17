# -*- coding: utf-8 -*-
"""★員外は門の後も増える★(memory「員外 counts grow after the gate」)。
   ゆゑ二度歩き、★食ひ違ひを隠さず★、己が之から書く物は★名で宣して★数に入れる。"""
import io, os, stat, sys, time
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(B, "driver"))
from kaki import kaku

SELF = ["raw/91_ingai.txt"]            # ★己が之から書く物 ―― 歩きには映らぬゆゑ宣する
man = io.open(os.path.join(B, "manifest.txt"), encoding="utf-8").read().split("\n")
rows = [l for l in man if l.startswith("path=")]
ledger = set(l.split(" ", 1)[0][len("path="):] for l in rows)

aruita, hi_reg = [], []
for dp, dn, fn in os.walk(B):
    for f in fn:
        p = os.path.join(dp, f)
        r = os.path.relpath(p, B)
        if stat.S_ISREG(os.lstat(p).st_mode): aruita.append(r)
        else: hi_reg.append(r)
ing = sorted(set(aruita) - ledger - {"manifest.txt"})
zen = sorted(set(ing) | set(SELF))

o = ["# km-114 員外 ★二度目の歩き★ ―― 門の後に増えた物を名で出す",
     "# 刻 " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
     "# 歩き根 = 束のみ(1本) / S_ISREG のみ数へた / 非regular = %d 本" % len(hi_reg),
     "",
     "臺帳の行(門が通した本数)\t%d" % len(rows),
     "歩いた file(regular)\t%d" % len(aruita),
     "一度目の歩き(99_shimai.txt・刻 19:09:06)の員外\t4",
     "二度目の歩き(本紙)の員外\t%d" % len(ing),
     "★宣した己の産物(歩きに映らぬ)★\t%d\t%s" % (len(SELF), " ".join(SELF)),
     "★員外 合計(二度目+宣)★\t%d" % len(zen),
     "",
     "## 員外の名 ―― ★悉く★",
     ]
for x in zen:
    tag = "(宣・本紙自身)" if x in SELF else ""
    o.append("  " + x + tag)
o += ["",
      "## 何故 4 → %d に増えたか" % len(zen),
      "  臺帳は 19:08 に凍つた。其の後 ★便の器と便の本文★(driver/90_fumi.py・raw/90_fumi.txt)を書き、",
      "  更に本紙(raw/91_ingai.txt)を書いた。★増えたのは疵ではなく、臺帳が時点の写しである事の帰結★である。",
      "",
      "## 之が意味せぬ事",
      "  ・員外 %d 本は「門を通つた」を意味せぬ ―― ★通つたのは臺帳の %d 本だけ★。" % (len(zen), len(rows)),
      "  ・本紙の %d 本は「最終の数」を意味せぬ ―― 次に一字書けば又増える。" % len(zen),
      "    ★臺帳を追ひ掛けて建て直す事は、受入⑷(門の後に臺帳を触らぬ)と衝つ★ゆゑ、",
      "    数を合はせるのではなく ★食ひ違ひを名で出す★ 方を採つた。",
      ]
kaku(os.path.join(B, "raw", "91_ingai.txt"), "\n".join(o))
print("\n".join(o))

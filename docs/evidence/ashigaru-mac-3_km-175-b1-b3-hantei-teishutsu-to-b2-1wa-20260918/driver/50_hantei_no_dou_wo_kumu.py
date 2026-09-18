# -*- coding: utf-8 -*-
"""★判定提出の胴を組む★(km-175 ㋓)
條が二つ噛み合はぬ: ⑴一便 300 字 ⑵★識別子を略すな★(總監督令 326424)。
40hex が 3 本 + sha256 が 2 本 + path 95 字 で 300 を軽く超ゆる ∴ ★便を割る★ ―― 略さぬ方を採る。
割つた事は ★各便の冠に書く★(受け手が片便を全部と読まぬ為)。四札: 字数=下記(送る前に数へる)。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

TEGAMI = [
 ("50_hantei_b1_1", "專任3 km-175 B1判定提出(1/5・300字の條ゆゑ五便に割る・識別子は略さぬ=總監督令326424)。"
  "repo=/Users/momizimac/DentalBI 枝=a2/b1-episodes-playback-20260910 "
  "tip=7a99e7556c3839293e6525671c042cb19e2c1ebe tree=35493aac21c0363f80348b63357f79fa39151ea0 "
  "親=96eb9a045d6e4f975dcf83f86e0e74abaa8f5313 刻=2026-09-10T18:46:21+0900 1file+117行。"),
 ("51_hantei_b1_2", "專任3 B1判定提出(2/5)。現物=frontend/src/features/child-passport/story-engine/"
  "__tests__/episodes.playback.test.tsx 117行/6058byte "
  "blob=81e9ec0b31cd688b20fe59acf13e74ba34f7ebc9 "
  "sha256=d9a8e3178d64aad065ed438e813a74731a0191468fa5bc72e9f3ea407f6a7a9c。rc悉く0・管を通さず。"),
 ("52_hantei_b1_3", "專任3 B1判定提出(3/5)。ls-remote rc=0 母數599で當枝1件=押し済(押したは委員長・裁332324)。"
  "網のmain=088961e193c7bb569b41e40e58e0cc49bb23a21d は地のorigin/main="
  "405fed71da517b45123e5aa2d38de48f9b41d873 と ★親子に非ず★(merge-base両向rc=1・読取のみ・触れず)。"
  "b5892684f は別commit別枝別現物(schema-types-parity.test.ts 182行)★畳まず★。"),
 ("53_hantei_b3_1", "專任3 km-175 B3判定提出(4/5・B1とは別物ゆゑ畳まず)。★原本は不在★ ―― 板38dcde86の三本(★板は頭8字しか刻まず★)"
  "(紙a1e6d2ff…10944byte/門控0e1228fd…253byte/臺帳a012d6b4…1401byte)は"
  "隔離樹/private/tmp/b3poc(dir1620・★常の紙0本★)・解けるlink先node_modules(29694本)・"
  "DentalBI blob48480・multi-agent-shogun blob11349 の何處にも0件。陽性対照2件当たり・陰性0・rc0。"),
 ("54_hantei_b3_2", "專任3 B3判定提出(5/5)。∴板38dcde86のcurrent_step逐語(1675字・"
  "sha256=ebf52ff350a990e1bcfefdf81aa7590aea46094efacb22b09f8bed01fdb3bc56)から★再生★紙を焼いた="
  "_saisei/00_b3_saisei_no_kami.md 7829byte "
  "sha256=7cca363849d4332764f2de58d0d34310eee67b348f412f3498edbafb8de88e14。★冠に再生と明記・原本と偽らず★。"),
]
rows = []
for na, dou in TEGAMI:
    p = os.path.join(BUNDLE, "_letters", na + ".txt")
    kaku(p, dou)
    rows.append([na, len(dou), ("★超★ %d 字截れ" % (len(dou) - 300)) if len(dou) > 300 else "條内(余 %d)" % (300 - len(dou))])
kaku_tsv(os.path.join(BUNDLE, "raw", "50_hantei_no_jisuu.tsv"), rows, header=["胴の紙", "字", "條 300 字"])
for r in rows:
    print("%s %d 字 %s" % (r[0], r[1], r[2]))

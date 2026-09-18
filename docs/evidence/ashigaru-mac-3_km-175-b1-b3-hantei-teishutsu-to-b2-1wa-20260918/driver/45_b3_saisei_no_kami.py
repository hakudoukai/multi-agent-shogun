# -*- coding: utf-8 -*-
"""★B3 の紙を再生する ―― 原本と偽らぬ★(km-175 ㋒③・家老mac 13:36 の命)
命の逐語: 「★無ければ『原本は不在』と一行で宣し★、板の current_step の逐語から ★再生した紙★ を束へ焼け
(★再生である事を紙の冠に書け★・原本と偽るな)」。
∴ 本器は raw/42(板の逐語)を ★字を一つも改めず★ 貼り、冠に再生の札を打ち、原本の三 sha256 と
再生紙の sha256 が ★別物である事★ を数で示す。"""
import os
import sys
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
CHIKUGO = open(os.path.join(BUNDLE, "raw", "42_ban_current_step_chikugo.txt"), encoding="utf-8").read().rstrip("\n")
SHA_CH = hashlib.sha256(CHIKUGO.encode("utf-8")).hexdigest()
DEST = os.path.join(BUNDLE, "_saisei", "00_b3_saisei_no_kami.md")

HON = """# ★再生★ B3 證紙 ―― 原本は不在、之は板の逐語から再生した紙である

> **★此の紙は原本ではない。★** 板 38dcde86 が名指す原本三本(紙 `a1e6d2ff…` 10944byte/105行・
> 門控 `0e1228fd…` 253byte・臺帳 `a012d6b4…` 1401byte)は ★現に不在★ であり、
> 本紙は ★板 `38dcde86-1f5f-464f-b7e7-7dce71197fa4` の `current_step` の逐語★ のみを材に、
> 專任3 が %s に再生した物である。★原本の代りに数へてはならぬ。★
> 再生紙の sha256 は原本の何れとも ★一致せぬ★(当然である ―― 別の紙ゆゑ)。

## 一 ―― ★原本は不在★(一行の宣)

**★B3 の證紙・門控・臺帳の三本は、當席が歩ける何處にも無い。★**

其の宣を支へる四札(★宣は一行だが、札は四つ要る★):

| 札 | 實測 |
|---|---|
| 根と深さ | ⑴隔離樹 `%s`(深さ 9・dir 1620 箇・★常の紙 0 本★)⑵其の中の唯一解ける link の先 `/Users/momizimac/DentalBI/frontend/node_modules`(dir 4812・常の紙 29694 本)⑶`/Users/momizimac/DentalBI` 全object(blob 48480 本)⑷`/Users/momizimac/multi-agent-shogun` 全object(blob 11349 本) |
| rc | 歩きの器 rc=0・`git cat-file --batch-all-objects --batch-check` rc=0・`find` rc=0(★悉く管を通さず採つた★) |
| 陽性対照 | ⑴本束の着手便(436byte・sha256 `b7876c96…`)を ★同じ歩き・同じ寸法の篩★ に乗せ 1 件当たる ⑵B1 の現物 blob(6058byte・sha256 `d9a8e317…`)を git 掃討の路で 1 件当たる ∴ ★器の黙りではない★ |
| 刻 | %s |

当たりの數: 紙 `a1e6d2ff` **0 件** / 門控 `0e1228fd` **0 件** / 臺帳 `a012d6b4` **0 件** / 陰性対照 `98765432` 0 件。

## 二 ―― 不在の姿(★紙だけが消えた樹★)

隔離樹 `/tmp/b3poc` は消えて居らぬ。★dir は 1620 箇 現に在り、常の紙だけが 0 本★ である。
dir の mtime は **1104 箇が `2026-09-17 00:00` へ寄る**(最古 2026-09-10T18:47:33+0900)。
掃き手の候補として `/etc/periodic/daily/110.clean-tmps` が此の mac に在るが、
**★掃いた者の log は當席は見て居らぬ★** ―― 「紙が無い」は實測、「其の器が消した」は ★未だ測れぬ★。
一つの符合で因と断ぜぬ。

## 三 ―― 再生の材(★板の `current_step` 逐語・字を一つも改めず★)

出所: `~/bin/sb read board-one 38dcde86` rc=0(出目 2343字/19行・控 `raw/40_ban_38dcde86.txt`)。
抜き出しは器の手(`driver/40_ban_wo_hikiutsusu.py`・鍵の名を焼き込まず「二字下げ+小文字鍵+コロン」の形で切る)。
逐語 **%d 字 / 1 行・sha256 `%s`**(控 `raw/42_ban_current_step_chikugo.txt`)。

```text
%s
```

## 四 ―― 再生では ★取り戻せぬ★ 物(之を書かねば偽と成る)

| 原本 | 板が言ふ姿 | 再生紙で復せたか |
|---|---|---|
| 證紙 | sha256 `a1e6d2ff…` / 10944 byte / 105 行 | ★復せぬ★ ―― 本紙は板の 1675 字のみを材とし、原本の 105 行の本文は何處にも無い |
| 門控 | sha256 `0e1228fd…` / 253 byte | ★復せぬ★ ―― 門の出目其の物は板に書かれて居らぬ(「門 RC=0」の一語のみ) |
| 臺帳 | sha256 `a012d6b4…` / 1401 byte / 一致 5/母數 5 / byte和 12598 | ★復せぬ★ ―― 行の並びも path も板に無い(數のみ) |

∴ **本紙が證立てるのは「板が何を受けたと書いたか」までであり、「專任1 が何を作つたか」は
★板の記述を信ずる★ 以外に此の mac では確かめられぬ。** 現物に当たり直せるのは
板が別に名指した frontend の三点(package.json:31-32 / adapters/assetSize.ts:5 / types.ts:27)だけである。

## 五 ―― 本節を作る間に當席が犯した疵(★己で捕へた★)

1. **link を 8 本と刷つた ―― 實は 9 本。** `os.walk` は ★dir を指す symlink を `files` ではなく `dirs` に入れる★
   ゆゑ、器は ★解ける唯一の一本★(`frontend/node_modules`)を link として数へず dir として数へて居た。
   `find -type l` の 9 と己の 8 の差が其れである。辿り直して 29694 本を掃討し、当たり 0 を採り直した。
2. **「find -L = 29694」を根を控へずに刷つた。** 根を書かぬ数は使へぬ ∴ 同じ根で取り直し、
   ★29694 は隔離樹の常の紙ではなく link の先(node_modules)の数★ と名を正した。
3. **鍵の名を器へ焼き込んだ。** `current_step` の切り出しで鍵名の表を焼き込み、
   知らぬ鍵(`checkpoint_log` / `pdca_loop_count`)を呑んで 1717 字と刷つた。形で切り直し 1675 字。
""" % (KOKU, os.path.realpath("/tmp/b3poc"), KOKU, len(CHIKUGO), SHA_CH, CHIKUGO)

kaku(DEST, HON)
sha_d = hashlib.sha256(open(DEST, "rb").read()).hexdigest()
kaku_tsv(os.path.join(BUNDLE, "raw", "45_saisei_no_hakari.tsv"),
         [["再生紙", os.path.relpath(DEST, BUNDLE), os.path.getsize(DEST), len(HON.split("\n")), sha_d],
          ["材(板 current_step 逐語)", "raw/42_ban_current_step_chikugo.txt", len(CHIKUGO.encode("utf-8")), 1, SHA_CH],
          ["★原本(不在)★ 紙", "-", 10944, 105, "a1e6d2ff…(当たり 0 件)"],
          ["★原本(不在)★ 門控", "-", 253, "-", "0e1228fd…(当たり 0 件)"],
          ["★原本(不在)★ 臺帳", "-", 1401, "-", "a012d6b4…(当たり 0 件)"]],
         header=["何を", "在処", "byte", "行", "sha256"])
print("再生紙= %s  %d byte / %d 行" % (os.path.relpath(DEST, BUNDLE), os.path.getsize(DEST), len(HON.split("\n"))))
print("  sha256(再生紙)= %s" % sha_d)
print("  材 sha256= %s (%d 字)" % (SHA_CH, len(CHIKUGO)))
print("  ★原本三本の sha256 と一致せぬ事を紙に明記した★")

# -*- coding: utf-8 -*-
u"""15 ―― 其の一(後半) 36 箇所を ⑴真に危ふい ⑵危ふからぬ の二群へ排他に仕分ける。
判の條(下命の逐語): ⑴=session 名を渡して前方一致し得る(実行される tmux 命に bare `multiagent` を渡す行)
                   ⑵=危ふからぬ(%N・pane_id・=名・★字面が別物★・echo/comment 内で実行されぬ行)
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

gyo = [l for l in io.open(os.path.join(BUNDLE, "raw", "10_zengyo.txt"), encoding="utf-8")
       .read().split("\n") if l]
assert len(gyo) == 36, u"★母數が 36 でなく %d★" % len(gyo)

kiken = []
anzen = []
riyu = {}

for l in gyo:
    # "path:lineno:body" ―― body は ":" の第三分割以降(値中に ":" が在り得る為 maxsplit=2)
    _, _, body = l.split(":", 2)
    mi = body.strip()
    if mi.startswith("echo "):
        anzen.append(l)
        riyu[l] = u"echo 文の中の文字列 ―― 端末に文字を刷るのみで tmux へ渡らぬ"
    elif mi.startswith("#"):
        anzen.append(l)
        riyu[l] = u"comment で無効化(コメントアウト) ―― 実行されぬ"
    elif "multiagent-third" in body:
        anzen.append(l)
        riyu[l] = u"★字面が別物★ ―― literal が `multiagent-third` であり、`multiagent` の前方一致対象ではない"
    else:
        kiken.append(l)
        riyu[l] = u"実行される tmux 命に bare `multiagent`(又は `multiagent:agents.…`)を渡す ―― 現に `multiagent-mac` が前方一致し得る(実測済)"

K.kaku(os.path.join(BUNDLE, "raw", "15_shiwake.txt"), u"""★其の一(後半) ―― 36 箇所を排他に仕分けた★

■ ⑴ 真に危ふい({nk} 箇所) ―― session 名を渡して前方一致し得る
{kiken}

■ ⑵ 危ふからぬ({na} 箇所) ―― echo/comment 内・又は字面が別物
{anzen}

■ 排他性の檢:
  {nk} + {na} = {sum}（★母數 36 と一致★）
  重複(両群に在る行) = {ju} 行
  漏れ(何れの群にも無い行) = {more} 行

★此の數が意味せぬ事★:
  ・⑴={nk} は「⑴の内 何本が實際に危害を及ぼすか」を測つた數ではない ―― kill-session/send-keys の様な★書込・制御系★と、
    show-options の様な★読取系★を ★同じ條(前方一致し得るか)★ で束ねて居る。書込/読取の別は下記別表(raw/16_kiken_naiyou.txt 未作・要すれば追測)。
  ・⑵={na} は「安全である事の證」ではなく「此の一行が ★此の刻 此の版★ で tmux へ渡らぬ事」の證に留まる。
    echo 文の中身は将来 eval される変更が入れば危ふく成り得る(現に此の版ではさうなつて居らぬ、といふ事)。
  ・分類は ★歩き根 = 己の枝(origin/main {oya})の此の刻の版★ に対する物。共用樹の作業中の版では行番号・分類とも動き得る。
""".format(nk=len(kiken), na=len(anzen), sum=len(kiken) + len(anzen),
           ju=len(set(kiken) & set(anzen)), more=36 - len(set(kiken) | set(anzen)),
           kiken=u"\n".join(u"  {0}\n    ―― {1}".format(l, riyu[l]) for l in kiken),
           anzen=u"\n".join(u"  {0}\n    ―― {1}".format(l, riyu[l]) for l in anzen),
           oya="6bde7170ce574090a6139ba2dfe3aa4cb6db8634"))

print("危険=%d 安全=%d 和=%d 母數=36" % (len(kiken), len(anzen), len(kiken) + len(anzen)))
assert len(kiken) + len(anzen) == 36
assert not (set(kiken) & set(anzen)), u"★両群に重複★"
assert len(set(kiken) | set(anzen)) == 36, u"★漏れが在る★"

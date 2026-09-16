#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問二 ―― 己の疵 十三「便より後にしか定まらぬ刻を同じ file に書く循環」を ★形で閉ぢる★。

★之は測るだけの器ではない ―― ★番★ である。★
  破れて居れば ★何も書かず rc≠0 で落ちる★(数を刷つても通さぬ)。

【循環の形】
  便 が X の sha を宣る(辺 甲: 便 → X)
  X が 便 の後にしか定まらぬ事(便の刻・seq)を容れる(辺 乙: X → 便)
  ∴ 甲・乙 の二辺で ★輪★ に成る。輪が在る限り宣は ★出した刹那に死ぬ★。

【道の母數 ―― 生成規則を宣る】
  輪は ★二辺★。各辺に打てる手は ★消す / 遅らす / 弱める★ の ★三手★。
  ∴ 母數 = ★2 × 3 = 6 道★。(札の手掛り ㋐㋑㋒㋓ は此の 6 の中に入る ―― 対応は下表)
"""
import os
import sys

FUDA = "queue/tasks/ashigaru-mac-3.yaml"
KAMI = ("queue/reports/ashigaru-mac-3_km-39-chu-to-jissou-no-sa-wo-obi-de-hakare-"
        "soshite-koku-no-junkan-wo-toji-yo-20260916.md")
DAICHOU = ("queue/reports/ashigaru-mac-3_km-39-chu-to-jissou-no-sa-wo-obi-de-hakare-"
           "soshite-koku-no-junkan-wo-toji-yo-20260916_manifest.txt")

# ★本弾の便で sha を宣る物★(＝凍る集合に限る)
CITE = [KAMI, DAICHOU]
# ★門に渡す物★(＝門の後 一byte も動かぬ事を禁則が約す集合)
GATE_ARGS = [KAMI, DAICHOU]
# ★便で sha を宣らぬ物★と、その理由
NO_CITE = [
    ("報 yaml(queue/reports/…_report.yaml)", "便の刻・seq を後から容れる ∴ 便より後に動く(疵十三の現場)"),
    ("札(queue/tasks/ashigaru-mac-3.yaml)", "印(status/done_at/done_note)を便の後に打つ ∴ 後から動く"),
    ("門控(…_evidence/mon/mon39_*)", "便の直前に生まれるが、便自身は其の sha を測る間に古びる ―― 名と母數で宣る"),
    ("便 其の物", "己の sha を己の中に書けぬ(自己言及) ―― ★之が閉ぢ得ぬ残り★"),
]

# 6 道(生成規則 = 2 辺 × 3 手)
MICHI = [
    ("一", "辺 甲を ★消す★", "便に sha を宣らぬ(札の㋑)",
     "宣が無い ∴ 家老は ★己で測る★ 迄 中身を検められぬ。誤りの発見が一往復遅れる。",
     "★何が測れなくなるか★= 便 単体での ★中身の同一性★"),
    ("二", "辺 甲を ★遅らす★", "便を最後に出す(札の㋒)",
     "束が凍つた後に宣る ∴ 宣は生きる。然れど ★便の刻は何處にも残らぬ★。",
     "★何が測れなくなるか★= 束の中からの ★便の着いた刻★"),
    ("三", "辺 甲を ★弱める★", "sha でなく ★名と母數★ で宣る(札の㋓)",
     "名は動かぬ ∴ 死なぬ。然れど ★中身が入れ替つても気附けぬ★。",
     "★何が測れなくなるか★= ★中身の同一性★(名は同じで中身が別、を見逃す)"),
    ("四", "辺 乙を ★消す★", "便の刻を書かぬ",
     "循環は消えるが ★便が着いた事の現物が束に無い★ ―― 送つたと言ふだけに成る。",
     "★何が測れなくなるか★= ★送達の事実★(memory: 送つた≠着いた)"),
    ("五", "辺 乙を ★遅らす★", "便の刻を ★次弾の束★ へ書く(札の㋐)",
     "本弾の束は凍る。刻は失はれず ★次弾の 00_start に残る★。代償 = ★一弾遅れる★。",
     "★何が測れなくなるか★= ★本弾の束だけを見た者★には送達が見えぬ(次弾を要る)"),
    ("六", "辺 乙を ★弱める★", "刻を別 file(束外)へ書く",
     "束は凍る。然れど其の file は ★門を通らぬ★ ∴ 誰も検めぬ紙が一枚増える。",
     "★何が測れなくなるか★= 其の file 自身の ★完全性★(門の外ゆゑ條②③④が当らぬ)"),
]

CHOSEN = ("五+三", "辺 乙を遅らせ(刻は次弾へ)、辺 甲は ★凍る集合に限つて★ 残す",
          "便で sha を宣るのは ★門に渡した物★ のみ。門の後は禁則が一byte も許さぬ ∴ 宣は死なぬ。"
          "門控だけは名と母數で宣る(道 三)。")


def main():
    print(__doc__.strip())
    print()
    print("【六道と代償】")
    for no, ha, na, dai, sok in MICHI:
        print("  ★道 %s★ %s ―― %s" % (no, ha, na))
        print("      代償: %s" % dai)
        print("      %s" % sok)
    print()
    print("【選んだ道】 ★道 %s★ ―― %s" % (CHOSEN[0], CHOSEN[1]))
    print("  %s" % CHOSEN[2])
    print()

    fail = 0
    print("【番 一 ―― 宣る物は悉く ★門に渡す物★ か】")
    for p in CITE:
        ok = p in GATE_ARGS
        print("  %-22s → 門の引数 %s" % (os.path.basename(p)[-40:], "★是★" if ok else "★否★"))
        if not ok:
            fail = 1
    print("【番 二 ―― 宣る物は悉く ★札が宣つた path★ か(名を推して居らぬか)】")
    try:
        fuda = open(FUDA, encoding="utf-8").read()
    except OSError as e:
        print("  ★札が讀めぬ: %s★" % e); return 2
    for p in CITE:
        ok = ('"%s"' % p) in fuda
        print("  %-22s → 札に逐語 %s" % (os.path.basename(p)[-40:], "★在り★" if ok else "★無し★"))
        if not ok:
            fail = 1
    print("【番 三 ―― 宣らぬ物を名指しで数へたか】")
    print("  宣らぬ物 = ★%d 件★" % len(NO_CITE))
    for nm, why in NO_CITE:
        print("    %s" % nm)
        print("        理由: %s" % why)
    print()

    print("【対照】")
    # 陽性 = 第38弾の宣り方(報 yaml を宣つた)を本規則に当てる → 弾かねばならぬ
    r38_cite = CITE + ["queue/reports/ashigaru-mac-3_km-38-…_report.yaml"]
    caught = [p for p in r38_cite if p not in GATE_ARGS]
    print("  陽性(第38弾の集合を当てる) 弾いた物 = ★%d 件★ %s"
          % (len(caught), caught[0][-30:] if caught else ""))
    # 陰性 = 本弾の集合には弾く物が無い
    neg = [p for p in CITE if p not in GATE_ARGS]
    print("  陰性(本弾の集合)          弾いた物 = ★%d 件★" % len(neg))
    if len(caught) != 1 or len(neg) != 0:
        print("  ★対照が通らぬ ―― 番として立たぬ★"); return 3
    print("  ★対照 二本 通つた ―― 此の番は ★第38弾の宣り方を現に弾く★★")
    print()

    if fail:
        print("★番が鳴つた ―― 宣る物の中に ★凍らぬ物★ が在る。便を出すな。★")
        return 1
    print("★番 通つた ―― 本弾の便は ★凍る物だけを宣る★。輪は閉ぢた。★")
    print("★閉ぢ得ぬ残り(residue)★:")
    print("  ⑴ 便 其の物の sha(自己言及) ⑵ 便の seq と着いた刻 ⑶ 札の印の後の sha")
    print("  ★此の三つは ★第40弾の 00_start★ に錨として書く ―― 道 五 の代償である。★")
    return 0


if __name__ == "__main__":
    sys.exit(main())

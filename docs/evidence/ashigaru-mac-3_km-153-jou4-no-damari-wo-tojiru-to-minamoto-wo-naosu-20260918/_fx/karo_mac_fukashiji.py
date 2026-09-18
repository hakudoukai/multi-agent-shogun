#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""karo_mac_fukashiji.py ―― 不可視字を ★codepoint の類★ で判ずる(裁 seq330497)。

由来: 出す前門 の 條② は `grep -cE $'[ \t]+\r?$'` 一行であり、
      ★ASCII の空白と TAB しか当たらなんだ★。條④ は末尾二字の `0a0a` 一致だけを見た。
      二つが重なると ★末尾に U+3000 一字の見えぬ空行を持つ紙が「出してよい」と通る★
      ―― 家老mac 第28弾 で十形を通して実測(10形中8形が黙つた)。

★形で数へる目録は決して閉ぢぬ★ ∴ 本器は形を並べず ★Unicode の類★ で判ずる:
      Zs(空白区切) / Zl / Zp / Cc(制御・TAB と DEL を含む) / Cf(書式・ZWSP U+200B と BOM U+FEFF を含む)。
      之で U+0020 U+0009 U+00A0 U+2003 U+2007 U+202F U+3000 U+007F U+200B U+FEFF の十形を悉く覆ふ
      (家老mac 実測 2026-09-18 ―― ['Zs','Cc','Zs','Zs','Zs','Zs','Zs','Cc','Cf','Cf'])。

usage: python3 karo_mac_fukashiji.py <file>
  stdout: "<條②の行數> <條④の札>"
  條④の札: 0=末尾改行丁度1で末尾行は可視を含む / 1=末尾改行が無い
            2=末尾行が不可視のみ(空行を含む) / 3=0byte
  rc=0: 測れた / rc=2: ★測れぬ★(呼び手は default-deny へ落とす事)

不可視のみの行を「鳴らす」向きに倒す理由: 見えぬ物は讀み手が直せぬ。
★測れぬ時は數を出さぬ★ ―― 出目が空なら呼び手が通してしまふ故、rc と stdout の双方で告げる。
"""
import os
import stat
import sys
import unicodedata

INVIS_CATS = ("Zs", "Zl", "Zp", "Cc", "Cf")


def is_invisible(ch):
    return unicodedata.category(ch) in INVIS_CATS


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: karo_mac_fukashiji.py <file>\n")
        return 2
    p = argv[1]
    try:
        st = os.lstat(p)
    except OSError as e:
        sys.stderr.write("★測れぬ(lstat 不可: %s)★\n" % e)
        return 2
    # ★開かぬ が第一★ ―― FIFO / device は `open()` で永久に待つ(家老mac 実測 120秒)。
    if not stat.S_ISREG(st.st_mode):
        sys.stderr.write("★測れぬ(常なる file に非ず ―― mode=%o)★\n" % st.st_mode)
        return 2
    try:
        with open(p, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        sys.stderr.write("★測れぬ(read 不可: %s)★\n" % e)
        return 2
    # surrogateescape ―― UTF-8 で無い byte も落ちずに讀む(類 Cs は不可視に数へぬ)。
    text = raw.decode("utf-8", "surrogateescape")

    lines = text.split("\n")
    # 末尾の空要素は「最後の改行の後」であつて行ではない。
    body = lines[:-1] if lines and lines[-1] == "" else lines

    jou2 = 0
    for ln in body:
        # 條③(CR混入)が別に鳴る故、行末の \r 一つは剥いでから行末を見る
        # ―― 剥がねば CRLF が不可視字を隠す(総監督裁 seq307918 の止血を継ぐ)。
        s = ln[:-1] if ln.endswith("\r") else ln
        if s and is_invisible(s[-1]):
            jou2 += 1

    if len(raw) == 0:
        jou4 = 3
    elif not text.endswith("\n"):
        jou4 = 1
    else:
        last = body[-1] if body else ""
        # 空行も「不可視のみ」に数へる ―― 舊版の `0a0a` 一致は此の一形だけを見て居た。
        if all(is_invisible(c) for c in last):
            jou4 = 2
        else:
            jou4 = 0

    sys.stdout.write("%d %d\n" % (jou2, jou4))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

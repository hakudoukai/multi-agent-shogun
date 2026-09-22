#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""candidate_a2_fukashiji.py ―― km-272 案A改(candidate_a試験中に發見した相互作用の穴を塞いだ形)。

★候補A(candidate_a_fukashiji.py)を其の儘 raw/fixtures/hi_seiki_nulbin_utsushi_NOT_EVIDENCE.bin
  へ當てたところ、條④(jou4)は 1→0 で直つたが 條②(jou2)は 1 の儘であつた(raw/51 實測)。
  ―― NUL終端の末尾byteは Unicode 類 Cc(制御)ゆゑ、契約5が條④を救つても條②が同じ紙を
  ★別の路から★落とし續ける。check_one_file() は `fk2>0` だけで fail=1 にする故、
  條④だけ直しても total の rc は変はらぬ。★之は候補Aの試験で實測して初めて判つた穴である★。
本形は契約5の判定を jou2 の走査より★先に★行ひ、NUL終端と判じた紙に限り
  ★最後の行の末尾一字の不可視判定を免じる★(其の一字は汚れではなく git の仕様上の境界故)。
  他の全ての行・他の紙型は candidate_a と同じ挙動(契約2/3/4/6 は不変)。
"""
import os
import re
import stat
import sys
import unicodedata

INVIS_CATS = ("Zs", "Zl", "Zp", "Cc", "Cf")


def is_invisible(ch):
    return unicodedata.category(ch) in INVIS_CATS


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: candidate_a2_fukashiji.py <file>\n")
        return 2
    p = argv[1]
    try:
        st = os.lstat(p)
    except OSError as e:
        sys.stderr.write("★測れぬ(lstat 不可: %s)★\n" % e)
        return 2
    if not stat.S_ISREG(st.st_mode):
        sys.stderr.write("★測れぬ(常なる file に非ず ―― mode=%o)★\n" % st.st_mode)
        return 2
    try:
        with open(p, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        sys.stderr.write("★測れぬ(read 不可: %s)★\n" % e)
        return 2
    text = raw.decode("utf-8", "surrogateescape")

    # ★契約5(先取り)★ ―― jou2 の走査より先に NUL終端か否かを判ずる
    nul_terminated_ok = (b"\n" not in raw) and raw.endswith(b"\x00") and not raw.endswith(b"\x00\x00")

    lines = text.split("\n")
    body = lines[:-1] if lines and lines[-1] == "" else lines

    jou2 = 0
    last_idx = len(body) - 1
    for i, ln in enumerate(body):
        s = ln[:-1] if ln.endswith("\r") else ln
        if not s:
            continue
        if s == " ":
            continue
        if s.endswith(" ") and not s.endswith("  ") and "=" in s and re.match(r'^\S+=', s):
            continue
        # ★契約5の適用範囲★ ―― NUL終端と判じた紙の★最後の行だけ★免じる(其の他の行は従前通り判ずる)
        if nul_terminated_ok and i == last_idx:
            continue
        if is_invisible(s[-1]):
            jou2 += 1

    if len(raw) == 0:
        if p.endswith(".err"):
            jou4 = 0
        else:
            jou4 = 3
    elif not text.endswith("\n"):
        if nul_terminated_ok:
            jou4 = 0
        elif re.fullmatch(r'-?[0-9]{1,3}', text) and len(raw) <= 4:
            jou4 = 0
        else:
            jou4 = 1
    else:
        last = body[-1] if body else ""
        if all(is_invisible(c) for c in last):
            jou4 = 2
        else:
            jou4 = 0

    sys.stdout.write("%d %d\n" % (jou2, jou4))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

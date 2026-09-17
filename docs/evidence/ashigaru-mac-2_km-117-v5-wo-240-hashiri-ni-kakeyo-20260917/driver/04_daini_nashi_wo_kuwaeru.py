#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒ の二本(第二の for を除いた版)を 10_menseki.py の器列へ足す ―― 九本 → 十一本。

★字面で行番号を打たぬ★(逐語の錠)。★置換の件数を検める★(1 本でなければ rc=3)。
之を据ゑると 10_menseki.tsv は 10区 × 3方言 × 11器 = ★330 行★に成る。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
TGT = os.path.join(HERE, "10_menseki.py")

JOU = '    ("v5_PR23", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),   # ★九本目★ PR#23 head\n'
NEW = (JOU +
       '    ("v5_第二無", os.path.join(AN, "v5_daini_nashi.py")),        # ★十本目★ v5 − 第二の for\n'
       '    ("案甲鎖_第二無", os.path.join(AN, "an_kusari_daini_nashi.py")),  # ★十一本目★ 鎖 − 第二の for\n')
OLD_DOC = "出目: raw/10_menseki.tsv(全 270 行 = 10区 × 3方言 × 9器)"
NEW_DOC = "出目: raw/10_menseki.tsv(全 330 行 = 10区 × 3方言 × 11器)"


def swap(s, old, new, what):
    n = s.count(old)
    if n != 1:
        print(f"★落ち★ {what}: 錠が {n} 本(1 本でなければ据ゑぬ)", file=sys.stderr)
        raise SystemExit(3)
    return s.replace(old, new, 1)


def main():
    with open(TGT, encoding="utf-8") as fh:
        s = fh.read()
    if "v5_第二無" in s:
        print("既に据ゑ済(冪等)")
        return 0
    s = swap(s, JOU, NEW, "器の列")
    s = swap(s, OLD_DOC, NEW_DOC, "冠の出目行")
    with open(TGT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)
    import py_compile
    py_compile.compile(TGT, cfile=os.path.join(BUNDLE, "raw", "_x.pyc"), doraise=True)
    os.remove(os.path.join(BUNDLE, "raw", "_x.pyc"))
    print("据ゑた: 器 9 → 11 本(330 行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

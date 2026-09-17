#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-114 の 240走器(10_menseki.py)へ ★v5 を九本目として★ 足す器 ―― km-117 ㋐ の前段。

★字面で行番号を打たぬ★(錠は逐語)。★置換は必ず件数を検める★(合はねば rc=3)。
足す物 = ("v5_PR23", <束>/_ki/v5_pr23.py)  ―― PR#23 head 571f3387… が運ぶ家老の第二版。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
TGT = os.path.join(HERE, "10_menseki.py")

JOU = '    ("案丁", os.path.join(AN, "an_tei.py")),\n'
NEW = JOU + '    ("v5_PR23", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),   # ★九本目★ PR#23 head\n'
OLD_DOC = "出目: raw/10_menseki.tsv(全 210 行)"
NEW_DOC = "出目: raw/10_menseki.tsv(全 270 行 = 10区 × 3方言 × 9器)"


def swap(s, old, new, what):
    n = s.count(old)
    if n != 1:
        print(f"★落ち★ {what}: 錠が {n} 本(1 本でなければ据ゑぬ)", file=sys.stderr)
        raise SystemExit(3)
    return s.replace(old, new, 1)


def main():
    with open(TGT, encoding="utf-8") as fh:
        s = fh.read()
    if "v5_PR23" in s:
        print("★既に足されて居る★(二度は足さぬ)")
        return 0
    s = swap(s, JOU, NEW, "KI 表へ v5 を足す")
    s = swap(s, OLD_DOC, NEW_DOC, "頭註の走り数")
    with open(TGT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)
    import py_compile
    py_compile.compile(TGT, cfile=os.path.join(HERE, "_x.pyc"), doraise=True)
    os.remove(os.path.join(HERE, "_x.pyc"))
    print("据ゑた: driver/10_menseki.py へ v5_PR23 を九本目として足した")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""案丁 ―― 則②を先へ置き、★食ひ過ぎた捕りに番を付ける★案(專任2 の derived 案)。

案甲鎖の 則② の捕り B に『'=' を含む語』が在れば B を棄てて 則①へ落とす。
之で「方言乙(欄が挟まる行)を壊す」疵が消える ―― 但し其の行の空白名は治らぬ(治せる材が無い)。
錠は★逐語★で引き、本数を宣して合はねば据ゑぬ(memory「str.replace patch must assert count」)。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
AN = os.path.join(BUNDLE, "_an")

MOTO = os.path.join(AN, "an_kou_kusari.py")
SAKI = os.path.join(AN, "an_tei.py")

JOU = '''    m = re.search(r"(?:^|\\s)path=(.+?)[ \\t]+sha256=", line)  # ②非貪欲
    if not m:'''
GE = '''    m = re.search(r"(?:^|\\s)path=(.+?)[ \\t]+sha256=", line)  # ②非貪欲
    if m and any("=" in _tok for _tok in m.group(1).split()):
        m = None  # ★番★ 捕りに欄('=' を含む語)が混じれば★食ひ過ぎ★ゆゑ棄て、則①へ落とす
    if not m:'''


def main():
    s = io.open(MOTO, encoding="utf-8").read()
    n = s.count(JOU)
    if n != 1:
        sys.stderr.write("★落ち★ 錠が %d 本(1 本でなければ据ゑぬ)\n" % n)
        return 3
    s = s.replace(JOU, GE)
    s = s.replace("案甲(鎖)", "案丁(鎖+番)", 1)
    io.open(SAKI, "w", encoding="utf-8").write(s)
    ln = s.count("\n")
    print("案丁 を据ゑた: %s / %d 行 / 番の行 = %d"
          % (os.path.relpath(SAKI, BUNDLE), ln, s.count("★番★ 捕りに欄")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

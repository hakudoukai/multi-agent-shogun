# -*- coding: utf-8 -*-
"""焼いた一行目と ★最終巡の門の出目★ が合ふかを検める(合はねば紙が嘘に成る)。

  usage: python3 -B driver/98_awase.py <束の根> <最終巡>
rc=0 一致 / rc=6 食ひ違ひ(何處が違ふかを刷る)
"""
import os
import re
import sys


def main():
    root, made = sys.argv[1], sys.argv[2]
    g = os.path.join(root, "_gate")
    rc = open(os.path.join(g, made + "_gate.rc"), encoding="utf-8").read().strip()
    out = open(os.path.join(g, made + "_gate.out"), encoding="utf-8").read()
    err = open(os.path.join(g, made + "_gate.err"), encoding="utf-8").read()
    m = re.search(r"一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)", out)
    vr = re.search(r"manifest_verify\.py rc=(\d+)", err)
    if not m or not vr:
        sys.stderr.write("★最終巡の出目が讀めぬ★\n")
        return 6
    icchi, soui, jittai, yomenu, bogen = m.groups()
    ichi = open(os.path.join(root, "README.md"), encoding="utf-8").read().split("\n")[0]
    hoshii = [("rc", "門 rc=%s " % rc), ("臺帳母數", "★臺帳 %s 行★" % bogen),
              ("一致", "條①=一致 %s(" % icchi), ("相違", "相違 %s・" % soui),
              ("実体無", "実体無 %s・" % jittai), ("讀めぬ行", "讀めぬ行 %s・" % yomenu),
              ("verify", "manifest_verify.py rc=%s)" % vr.group(1)),
              ("最終巡", "`_gate/%s_gate.*`" % made)]
    chigai = [n for n, s in hoshii if s not in ichi]
    if chigai:
        sys.stderr.write("★食ひ違ひ: %s★\n一行目: %s\n" % (" ".join(chigai), ichi))
        return 6
    sys.stderr.write("一行目と %s 巡の出目 = 一致(%d 点悉く)\n" % (made, len(hoshii)))
    return 0
sys.exit(main())

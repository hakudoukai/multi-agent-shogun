#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐'' 10_menseki.tsv を ★方言別★ の判定表に開く器(合算は疵の在処を隠す)。

出目は必ず kaki 経由(memory「Every raw text product goes through kaki」)。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

SRC = os.path.join(BUNDLE, "raw", "10_menseki.tsv")
DST = os.path.join(BUNDLE, "raw", "11_hougen_betsu.txt")


def main():
    rows = [l.rstrip("\n").split("\t") for l in io.open(SRC, encoding="utf-8")]
    hd = rows[0]
    i = {k: hd.index(k) for k in ("方言", "区", "期待", "器", "rc", "判定")}
    top = max(i.values())
    body = [r for r in rows[1:] if len(r) > top]
    ki, ku, hou = [], [], []
    for r in body:
        for lst, col in ((ki, "器"), (ku, "区"), (hou, "方言")):
            if r[i[col]] not in lst:
                lst.append(r[i[col]])
    d = {(r[i["方言"]], r[i["区"]], r[i["器"]]): (r[i["rc"]], r[i["判定"]]) for r in body}
    exp = {(r[i["方言"]], r[i["区"]]): r[i["期待"]] for r in body}
    o = ["# ㋐'' 方言別の判定表 ―― 三方言を別々に(合算は疵の在処を隠す)",
         "#   方言甲 = path= の次が sha256=(★本形・隣接★) / 方言乙 = 間に bytes= lines= が挟まる",
         "#   方言丙 = sha256= が path= の★前★",
         "#   母數 = 10 区 × 3 方言 × %d 器 = %d 走" % (len(ki), len(ku) * len(hou) * len(ki))]
    for h in hou:
        o += ["", "## 方言" + h, "\t".join(["区", "期待"] + ki)]
        for k in ku:
            line = [k, exp.get((h, k), "?")]
            for g in ki:
                rc, han = d.get((h, k, g), ("-", "-"))
                line.append("rc%s/%s" % (rc, han))
            o.append("\t".join(line))
    o += ["", "# 器毎・方言毎の ★偽★ の本数(母數 10 区)",
          "\t".join(["器"] + ["方言" + h + "(偽の通/偽の赤)" for h in hou])]
    for g in ki:
        cells = []
        for h in hou:
            t = sum(1 for k in ku if d.get((h, k, g), ("", ""))[1] == "★偽の通★")
            a = sum(1 for k in ku if d.get((h, k, g), ("", ""))[1] == "★偽の赤★")
            cells.append("%d/%d" % (t, a))
        o.append("\t".join([g] + cells))
    o += ["", "# 残る疵の★名指し★(器 × 方言 × 区) ―― 本数だけでは直せぬ"]
    for g in ki:
        bad = ["%s%s:%s" % (h, k, d[(h, k, g)][1].strip("★")) for h in hou for k in ku
               if d.get((h, k, g), ("", ""))[1].startswith("★")]
        o.append("%s\t%d 個\t%s" % (g, len(bad), " ".join(bad) if bad else "―"))
    kaku(DST, "\n".join(o))
    print("据ゑた: raw/11_hougen_betsu.txt / %d 行" % (len(o)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

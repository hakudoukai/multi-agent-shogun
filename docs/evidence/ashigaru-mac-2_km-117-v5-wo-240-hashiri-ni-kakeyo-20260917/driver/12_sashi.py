#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑-1 v5 と他器の ★差★ を 30 区(10区×3方言)で逐一出す器。

★rc が同じでも内は違ひ得る★ ―― ゆゑに rc だけで「同じ」と言はぬ。
比べる欄 = rc / 一致 / 相違 / 実体無 / 読めぬ行 / 名指し の★六つ悉く★。
六つ悉く一致した時に限り「同」と書く。一つでも違へば ★異★ と名指す。

入 = raw/10_menseki.tsv(360 行)   出 = raw/12_sashi.txt
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

SRC = os.path.join(BUNDLE, "raw", "10_menseki.tsv")
DST = os.path.join(BUNDLE, "raw", "12_sashi.txt")
JIKU = "v5_PR23"
AITE = ["案甲鎖", "案甲列", "v4_家老の直し", "案乙", "案丁",
        "v5_第二無", "案甲鎖_第二無", "案戊"]  # ★km-117 で三本追加★
KURA = ["rc", "一致", "相違", "実体無", "読めぬ行", "名指し"]


def main():
    rows = [l.rstrip("\n").split("\t") for l in io.open(SRC, encoding="utf-8")]
    hd = rows[0]
    i = {k: hd.index(k) for k in hd}
    top = max(i.values())
    body = [r for r in rows[1:] if len(r) > top]
    cell = {(r[i["方言"]], r[i["区"]], r[i["器"]]): r for r in body}
    hou, ku = [], []
    for r in body:
        if r[i["方言"]] not in hou:
            hou.append(r[i["方言"]])
        if r[i["区"]] not in ku:
            ku.append(r[i["区"]])
    o = ["# ㋑-1 ★v5 と他器の差★ ―― 30 区(10区×3方言)を逐一",
         "#   比べる欄 = " + " / ".join(KURA) + " の★六つ悉く★",
         "#   ★同★ = 六欄悉く一致 / ★異★ = 一欄でも違ふ",
         "#   ★之が言はぬ事★: 此の盤は ★型見 10 区★ の話であり、"
         "現物の臺帳で差が出るか否かは別に測る(raw/30_genbutsu.txt)。",
         ""]
    tot = {}
    detail = []
    for a in AITE:
        n_same = n_diff = 0
        for h in hou:
            for k in ku:
                x = cell.get((h, k, JIKU))
                y = cell.get((h, k, a))
                if x is None or y is None:
                    detail.append(f"{a}\t{h}{k}\t★測れぬ★(片方の行が無い)")
                    continue
                sa = [c for c in KURA if x[i[c]] != y[i[c]]]
                if sa:
                    n_diff += 1
                    detail.append("%s\t%s%s\t★異★\t%s" % (
                        a, h, k, " ".join(
                            "%s(%s→%s)" % (c, y[i[c]], x[i[c]]) for c in sa)))
                else:
                    n_same += 1
        tot[a] = (n_same, n_diff)
    o.append("\t".join(["相手", "同(六欄悉く一致)", "異", "母數"]))
    for a in AITE:
        s, d = tot[a]
        o.append("\t".join([a, str(s), str(d), str(s + d)]))
    o += ["", "# ★異★ の名指し(相手 × 方言区 × 違つた欄) ―― 本数だけでは讀めぬ",
          "\t".join(["相手", "方言区", "判", "違つた欄(相手→v5)"])]
    o += detail if detail else ["―\t―\t―\t★一つも無い★"]
    kaku(DST, "\n".join(o))
    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main())

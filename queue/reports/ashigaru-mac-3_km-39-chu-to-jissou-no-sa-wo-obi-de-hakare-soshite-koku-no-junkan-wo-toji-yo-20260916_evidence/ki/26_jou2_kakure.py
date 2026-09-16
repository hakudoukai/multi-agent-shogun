#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問一 ㋔ の裁 ―― 門 條② の註「★偽の青は作れぬ★」を ★己の手で測る★。

註(scripts/checks/karo_mac_dasumae_gate.sh L42 逐語):
  「★偽の青は作れぬ★ ―― 條②を隠す紙は必ず條③を鳴らす故、此の疵は『數を少なく言ふ』疵である。」
∴ 宣は ★「條②が黙る ⇒ 條③が鳴る」★ ―― ★必ず★ と書かれて居る。
反例が一枚でも在れば ★偽★。

★門は据ゑ替へぬ・走らせぬ★。門の中の ★形★ だけを grep で再現して当てる。
  旧形 = [ \t]+$      新形 = [ \t]+\r?$      條③ = \r
出目は 鳴った行數(grep -c)。★grep -c は 0 の時 rc=1 を返す★ ゆゑ rc も併記する。
"""
import os
import subprocess
import sys

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixture")
D = os.path.normpath(D)

# 名 → (中身 bytes, 何の為の紙か)
PAPERS = [
    ("a_kiyoshi.txt",  b"abc\ndef\n",                 "陰性対照 ―― 末尾空白も \\r も無い"),
    ("b_kuuhaku.txt",  b"abc \ndef\n",                "陽性対照 ―― 素の末尾空白(條②が鳴る筈)"),
    ("c_crlf.txt",     b"abc \r\ndef\r\n",            "旧形が黙り條③が鳴る紙(註の言ふ通りの筈)"),
    ("d_nbsp.txt",     "abc  \ndef\n".encode(),  "★反例の候補★ 空白の後に NBSP(U+00A0)"),
    ("e_zenkaku.txt",  "abc 　\ndef\n".encode(),  "★反例の候補★ 空白の後に 全角空白(U+3000)"),
]

FORMS = [
    ("條②旧 [ \\t]+$",    ["grep", "-cE", "[ \t]+$"]),
    ("條②新 [ \\t]+\\r?$", ["grep", "-cE", "[ \t]+\r?$"]),
    ("條③   \\r",          ["grep", "-c", "\r"]),
]


def run(cmd, path):
    p = subprocess.run(cmd + [path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode().strip(), p.returncode


def main():
    print("【測る物】 門 條② の註 L42「條②を隠す紙は ★必ず★ 條③を鳴らす」")
    print("  ★門は走らせぬ・据ゑぬ。中の ★形★ を grep で当て直すのみ。★")
    print("  紙の置き場 = %s" % os.path.relpath(D, os.getcwd()))
    print("  ★註★ 此の 5 枚は ★門の引数には渡さぬ★ ―― 渡せば條②が鳴る(渡さぬ事を紙に書く)。")
    print()
    rows = []
    for name, body, why in PAPERS:
        path = os.path.join(D, name)
        with open(path, "wb") as fh:
            fh.write(body)
        cells = []
        for label, cmd in FORMS:
            out, rc = run(cmd, path)
            cells.append((label, out, rc))
        rows.append((name, why, cells))

    w = "%-16s %-14s %-14s %-12s"
    print(w % ("紙(名)", "條②旧(行/rc)", "條②新(行/rc)", "條③(行/rc)"))
    for name, why, cells in rows:
        print(w % (name,
                   "%s/rc%d" % (cells[0][1], cells[0][2]),
                   "%s/rc%d" % (cells[1][1], cells[1][2]),
                   "%s/rc%d" % (cells[2][1], cells[2][2])))
        print("      %s" % why)
    print()

    # ★対照の検め★ ―― 通らねば數を刷らず落ちる(fail-closed)
    def cell(i, j):
        return rows[i][2][j][1]
    if cell(0, 0) != "0" or cell(0, 1) != "0" or cell(0, 2) != "0":
        print("★陰性対照が鳴つた ―― 器を疑へ。數を讀むな。★"); return 3
    if cell(1, 0) == "0" or cell(1, 1) == "0":
        print("★陽性対照が黙つた ―― 器は末尾空白を見て居らぬ。數を讀むな。★"); return 3
    print("★対照 二本 通つた ―― 陰性 悉く 0 / 陽性 條②旧新 共に鳴つた★")
    print()

    print("【裁】")
    print("  ⑴ c_crlf: 條②旧 %s ・ 條③ %s" % (cell(2, 0), cell(2, 2)))
    print("     ∴ ★CRLF の紙に就いては註の言ふ通り★ ―― 隠れても條③が鳴る。")
    hansei = []
    for i, nm in ((3, "d_nbsp"), (4, "e_zenkaku")):
        if cell(i, 0) == "0" and cell(i, 1) == "0" and cell(i, 2) == "0":
            hansei.append(nm)
    print("  ⑵ 隠れて ★條③も黙つた★ 紙 = ★%d 枚★ %s" % (len(hansei), " ".join(hansei) or "(無し)"))
    if hansei:
        print("     ∴ ★註 L42 の『必ず』は 偽である。★ 末尾空白の後に ★[ \\t] でない空白★")
        print("       (NBSP U+00A0 / 全角空白 U+3000)を一字置けば、條②旧・新 共に黙り、")
        print("       條③(\\r)も鳴らぬ ―― ★偽の青が作れる。★")
        print("     ★但し限界★: 此れは『條②の帯の外に空白の種が在る』話であり、")
        print("       CRLF の隠れ(註が治した物)とは ★別の疵★ である。註の治療自体は正しい。")
    else:
        print("     ∴ 反例を見附けられず ―― ★註の『必ず』を偽とは言へぬ(未判)★")
    return 0


if __name__ == "__main__":
    sys.exit(main())

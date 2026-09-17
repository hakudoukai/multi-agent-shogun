#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒ の為の器を二本建てる ―― ★第二の for(tok.split で '/' を含む語を足す)を除いた版★。

  _an/v5_daini_nashi.py   = v5(PR#23 head) から 第二の for ★のみ★ を除く
  _an/an_kusari_daini_nashi.py = 案甲鎖 から 同じ塊 を除く

★何故要るか★: 第二の for は ★v5 が新たに書いた物ではない★ ―― v1_127行 から
九本悉くが持つ(raw/32_daini_for_dokoni.txt)。ゆゑに「案甲鎖 と比べて第二の for の
効きを測る」事は出来ぬ(両方が持つ)。★持たぬ版を建てて初めて測れる。★

★字面で行番号を打たぬ★。★除いた件数を検める★(合はねば rc=3)。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)

BLOCK = """    # '=' の右・sha256 でない・'/' を含む語
    for tok in line.split():
        if tok.startswith("sha256=") or tok.startswith("bytes=") or tok.startswith("lines="):
            continue
        t = tok.split("=", 1)[-1] if tok.startswith("path=") else tok
        t = _dequote(t)
        if "/" in t and t not in out:
            out.append(t)
"""
ATO = "    # ★第二の for(tok.split の '/' 語)は★除いた★(km-117 ㋒ の為の版)\n"

TANE = [
    ("v5_daini_nashi.py", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),
    ("an_kusari_daini_nashi.py", os.path.join(BUNDLE, "_an", "an_kou_kusari.py")),
]


def main():
    out = os.path.join(BUNDLE, "_an")
    rows = ["# ★第二の for を除いた版★ を建てた証(km-117 ㋒)",
            "# name\t種\t除いた塊の本数\t元 行数\t後 行数"]
    for name, seed in TANE:
        with open(seed, encoding="utf-8") as fh:
            s = fh.read()
        n = s.count(BLOCK)
        if n != 1:
            print(f"★落ち★ {name}: 除く塊が {n} 本(1 本でなければ据ゑぬ)", file=sys.stderr)
            return 3
        t = s.replace(BLOCK, ATO, 1)
        dst = os.path.join(out, name)
        with open(dst, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(t)
        import py_compile
        py_compile.compile(dst, cfile=os.path.join(out, "_x.pyc"), doraise=True)
        rows.append("%s\t%s\t%d\t%d\t%d" % (
            name, os.path.relpath(seed, BUNDLE), n,
            len(s.split("\n")), len(t.split("\n"))))
    if os.path.exists(os.path.join(out, "_x.pyc")):
        os.remove(os.path.join(out, "_x.pyc"))
    sys.path.insert(0, HERE)
    from kaki import kaku
    kaku(os.path.join(BUNDLE, "raw", "03_daini_nashi_tateta.txt"), "\n".join(rows))
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""70_totonoe.py ―― 束の紙を 條②③④ の形へ整へる。

  條② 行末の空白を落とす / 條③ CR を落とす / 條④ EOF 改行 丁度一つ。
  0byte の file は ★消さず★、空であつた旨の一行を入れる(條④ は 0byte を落とす故)。

  ★根は argv から取る★(器に焼くな)。除く根も argv。
  ★己の産物(此の報せ)も 同じ形で書く★ ―― 報せ自身が 條②③④ に落ちぬ様に。
"""
import os, stat, sys

def totonoe(b: bytes):
    """bytes -> (新bytes, 疵の札)"""
    fuda = []
    if b.replace(b"\r\n", b"\n").find(b"\r") >= 0 or b.find(b"\r") >= 0:
        fuda.append("CR")
    s = b.decode("utf-8", "surrogateescape").replace("\r\n", "\n").replace("\r", "\n")
    gyou = s.split("\n")
    kezu = [g.rstrip(" \t") for g in gyou]
    if any(a != b2 for a, b2 in zip(gyou, kezu)):
        fuda.append("末尾空白")
    s2 = "\n".join(kezu)
    while s2.endswith("\n"):
        s2 = s2[:-1]
    if s2 == "":
        s2 = "★空★ ―― 此の器は一字も出さなんだ(0byte は 條④ に落ちる故、此の一行を入れた)"
        fuda.append("空file")
    s2 += "\n"
    n = s2.encode("utf-8", "surrogateescape")
    if n != b and not fuda:
        fuda.append("EOF改行")
    return n, fuda

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 70_totonoe.py <根> [<除く相対path> ...]\n")
        return 2
    ne = os.path.abspath(sys.argv[1])
    nozoku = [x.rstrip("/") for x in sys.argv[2:]]
    hou = []
    kazu = {"見": 0, "直": 0, "非regular": 0, "除": 0}
    for dirpath, dirnames, filenames in os.walk(ne):
        dirnames.sort()
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, ne)
            if any(rel == x or rel.startswith(x + "/") for x in nozoku):
                kazu["除"] += 1
                continue
            st = os.lstat(p)
            if not stat.S_ISREG(st.st_mode):
                kazu["非regular"] += 1
                hou.append("非regular %s" % rel)
                continue
            kazu["見"] += 1
            with open(p, "rb") as f:
                b = f.read()
            n, fuda = totonoe(b)
            if n != b:
                with open(p, "wb") as f:
                    f.write(n)
                kazu["直"] += 1
                hou.append("直 %s ★%s★ %d byte → %d byte" % (rel, "・".join(fuda) or "?", len(b), len(n)))
    atama = [
        "刻 は呼手が別に焼く(此の器は刻を打たぬ ―― 二度走らせて差が出ぬ事を示す為)",
        "根 = %s" % ne,
        "除く根 = %s" % (" / ".join(nozoku) if nozoku else "(無し)"),
        "見た本数=%d / 直した本数=%d / 非regular=%d / 除いた本数=%d" % (
            kazu["見"], kazu["直"], kazu["非regular"], kazu["除"]),
        "―― 直した物 ――",
    ]
    if not hou:
        atama.append("(一本も無し ―― 既に悉く 條②③④ の形)")
    honbun = "\n".join(atama + hou)
    sys.stdout.write(honbun + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""書き器 ―― 出目を disk へ置く時の作法(第31/32弾と同じ形・本弾で再掲)。
行末の空白を落とし、LF のみ、末尾改行は丁度一つ。空なら「空である旨の一行」を書く(0byte を産まぬ)。"""
import os

KARA = "# 空(此の出目は一行も無い ―― 器が書いた印・0byte ではない)"

def kaku(path, text):
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        lines = [KARA]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

def kaku_tsv(path, rows, header=None):
    out = []
    if header:
        out.append("\t".join(header))
    for r in rows:
        out.append("\t".join(str(x) for x in r))
    kaku(path, "\n".join(out))

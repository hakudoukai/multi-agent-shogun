# -*- coding: utf-8 -*-
"""書き器 ―― 出目を disk へ置く時の作法(第31/32/58弾と同じ形・本弾で再掲)。
行末の空白を落とし、LF のみ、末尾改行は丁度一つ。空なら「空である旨の一行」を書く(0byte を産まぬ)。
★kaku_tsv は空欄を `-` で埋める★ ―― rstrip が末尾の空欄を食ひ、欄数が行毎に変はるのを防ぐ。"""
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
        out.append("\t".join(str(x) if str(x) != "" else "-" for x in header))
    for r in rows:
        # ★dict を渡すと for が鍵を回し「見出しの複製」を黙つて書く(第59弾で踏んだ)★ ∴ 撥ねる。
        if not isinstance(r, (list, tuple)):
            raise TypeError("kaku_tsv の行は list/tuple である事(受けた型=%s)" % type(r).__name__)
        out.append("\t".join(str(x) if str(x) != "" else "-" for x in r))
    kaku(path, "\n".join(out))

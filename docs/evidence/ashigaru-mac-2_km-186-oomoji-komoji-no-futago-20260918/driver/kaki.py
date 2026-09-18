# -*- coding: utf-8 -*-
"""書き器 ―― 出目を disk へ置く時の作法(第31/32/117弾と同じ形・本弾で再掲)。
行末の空白を落とし、LF のみ、末尾改行は丁度一つ。空なら「空である旨の一行」を書く(0byte を産まぬ)。
★本弾の追加★: 値を刷らぬ為の伏せ器 fuse() を同居させる ―― 器が値を持つても紙へは出さぬ。"""
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


def fuse(value):
    """★当つた値は決して紙へ出さぬ★ ―― 長さだけを返す。
    (0字でも `<伏:0字>` と書く ―― 空文字が「当らなんだ」と見分けが付かぬ事を防ぐ)"""
    return "<伏:%d字>" % len(value if value is not None else "")

def esc(name):
    """★行器を壊す名を、戻せる形で潰す★ ―― km-122 実測: 歩き根の下に
    TAB入り1本・末尾改行2本が在り、素の TSV は byte欄が5ずれ行が+2に成つた。
    順序が肝 ―— \\ を先に置換せねば \\n が二重に戻る。"""
    return (name.replace("\\", "\\\\").replace("\t", "\\t")
                .replace("\r", "\\r").replace("\n", "\\n"))

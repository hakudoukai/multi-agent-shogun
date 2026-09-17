# -*- coding: utf-8 -*-
"""書き器 ―― 正記(軍師mac 令 2026-09-07)。行末空白を落し・LF のみ・末尾改行丁度一つ。
空なら「空である旨の一行」を書く(0byte を産まぬ)。★写し(_utsushi/)へは当てぬ★ ―― 生器との sha 一致が証ゆゑ。"""
KARA = "# 空(此の出目は一行も無い ―― 器が書いた印・0byte ではない)"

def kaku(path, text):
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        lines = [KARA]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

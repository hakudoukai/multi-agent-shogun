# -*- coding: utf-8 -*-
"""K.py ―― 束内の文字產物は悉く此處を通す(門 條②③④: 末尾空白無・CR無・EOF改行丁度一)。
kaku() の返りは ★意圖した長さ★ であつて disk の長さではない ∴ 呼び手は stat で測り直せ。"""
import os

def seikei(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [l.rstrip(" \t") for l in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"

def kaku(path, text):
    body = seikei(text)
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    return os.path.getsize(path)   # ★disk を stat した長さ★(記憶札: 意圖長を返すな)

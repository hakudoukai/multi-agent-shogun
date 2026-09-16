#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""書き物の法 ―― 出す前に ①末尾空白を削り ②CR を除き ③EOF 改行を丁度一つにし
④空の流れは一行に改める。★削つた場所は隠さず控へる★(削り＝情報の喪失ゆゑ)。"""
import sys, os
KARA = "(空 ―― 器は此の流れへ一字も出さなんだ。0 byte を此の一行に改めた ―― 書き物の法④)\n"
log = []
for p in sys.argv[1:]:
    b = open(p, "rb").read()
    before = (len(b), b.count(b"\r"))
    if b == b"":
        new = KARA.encode("utf-8"); log.append((p, "空→一行", []))
    else:
        lines = b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")
        hit = [i+1 for i, l in enumerate(lines) if l != l.rstrip()]
        lines = [l.rstrip() for l in lines]
        while lines and lines[-1] == "":
            lines.pop()
        new = ("\n".join(lines) + "\n").encode("utf-8")
        log.append((p, f"末尾空白を削つた行 {len(hit)}", hit))
    if new != b:
        open(p, "wb").write(new)
    after = (len(new), new.count(b"\r"))
    print(f"{p}\n    before bytes={before[0]} CR={before[1]} -> after bytes={after[0]} CR={after[1]}")
print("--- 削つた場所(隠さず控へる) ---")
for p, w, hit in log:
    print(f"  {p} :: {w} :: 行 {hit}")

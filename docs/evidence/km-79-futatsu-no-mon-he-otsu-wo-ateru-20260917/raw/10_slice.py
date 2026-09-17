#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ★閾の器だけを門から切り出し、8形の負テストへ掛ける台を建てる★
#   切り出しの範囲 = say() の一行 ＋ `num_same_op(){` の行から
#   ★最初の `fix_threshold <NAME>` 呼出の直前★ まで(=num_same_op/env_state/fix_threshold の三器と其の註)。
#   ★呼出行は入れぬ★ ゆゑ、他器の閾名が台へ乗る事は無い。
import sys, io
src = io.open(sys.argv[1], encoding="utf-8").read().split("\n")
say = [l for l in src if l.startswith("say(){")]
assert len(say) == 1, "say() が %d 本" % len(say)
beg = [i for i, l in enumerate(src) if l.startswith("num_same_op(){")]
end = [i for i, l in enumerate(src) if l.startswith("fix_threshold ")]
assert len(beg) == 1, "num_same_op が %d 本" % len(beg)
assert len(end) >= 1, "fix_threshold 呼出が無い"
body = src[beg[0]:end[0]]
out = ["#!/bin/bash", "# ★台 ―― %s から機械で切り出した(手写しに非ず)★" % sys.argv[1],
       "set -u", say[0]] + body + [
       'fix_threshold KM79_PROBE 50 OUT', 'printf %s\\\\n "${OUT}"']
io.open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
sys.stderr.write("切出 %d行 (num_same_op L%d → 呼出 L%d の前)\n" % (len(body), beg[0]+1, end[0]+1))

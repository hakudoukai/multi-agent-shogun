#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★紙の數を器で突き合はせる★ ―― README.md の表の値が raw/*.txt の實測と逐語一致するかを測る。
★節を限らねば同名の行を拾ふ★(初版は「②空文字」を §三(現形)の行と §五(直し形)の行の区別無く拾ひ、
紙の疵ではなく ★器の疵★ で六件 鳴いた)。かつ紙は讀み易さの為 `+1` `−1` と書く ∴ 符號三形を受ける。
使ひ方: 60_kami_awase.py <README.md> <matrix.txt>=<節の逐語> …
"""
import io, re, sys
kami = io.open(sys.argv[1], encoding="utf-8").read().split("\n")
NUM = re.compile(r"^[+\-−]?\d+$")
def seisu(s):
    return s.replace("−", "-").lstrip("+") if NUM.match(s) else None
def setsu(anchor):
    i = next(n for n, l in enumerate(kami) if l.startswith(anchor))
    j = next((n for n in range(i + 1, len(kami)) if kami[n].startswith("## ")), len(kami))
    return kami[i:j]
ok = ng = 0
warui = []
for spec in sys.argv[2:]:
    mx, anchor = spec.split("=", 1)
    han = setsu(anchor)
    for line in io.open(mx, encoding="utf-8").read().split("\n"):
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        nm, want = cells[0], [seisu(c) for c in cells[1:]]
        want = [w for w in want if w is not None]
        cand = [l for l in han if l.startswith("|") and nm in l.replace("**", "").replace(" ", "")]
        if len(cand) != 1:
            ng += 1; warui.append("%s %s: 節 %s に行が %d 本(1本でない)" % (mx, nm, anchor.strip(), len(cand))); continue
        got = [seisu(c.replace("**", "").strip()) for c in cand[0].strip("|").split("|")]
        got = [g for g in got if g is not None]
        if got == want:
            ok += 1
        else:
            ng += 1; warui.append("%s %s: 紙=%s 實測=%s" % (mx, nm, got, want))
print("一致=%d 食ひ違ひ=%d" % (ok, ng))
for w in warui:
    print("  ★" + w)
sys.exit(1 if ng else 0)

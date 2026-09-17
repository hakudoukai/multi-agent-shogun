#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★束の text を門の條②③④の形へ揃へる(kaki)★ ―― ㋐行末の空白/TAB/CR を削ぐ ㋑EOF の改行を一本にする ㋒LF のみ。
★前の寸を必ず控へる★(memory: Record the before-size ―― 揃へた後では差が推し測りに成る)。
`_before/` は ★控(原器の寫し)★ ゆゑ ★触らず、疵が在れば宣するのみ★。
使ひ方: 90_kaki.py <束dir> [--naose]   (--naose 無しは prescan=讀取のみ)
"""
import io, os, sys
base = sys.argv[1]
naose = "--naose" in sys.argv[2:]
rows = []
for dp, dn, fn in os.walk(base):
    dn[:] = [d for d in dn if d not in ("__pycache__", "_gate", ".git")]
    for f in sorted(fn):
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, base)
        b = io.open(p, "rb").read()
        kizu = []
        if b"\r" in b: kizu.append("CR")
        t = b.decode("utf-8", "replace")
        if any(l != l.rstrip(" \t\r") for l in t.split("\n")): kizu.append("行末空白")
        if not t.endswith("\n"): kizu.append("EOF改行無")
        if t.endswith("\n\n"): kizu.append("EOF空行多")
        mamoru = rel.startswith("_before" + os.sep)
        naoshita = "-"
        if kizu and naose and not mamoru:
            u = "\n".join(l.rstrip(" \t\r") for l in t.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
            u = u.rstrip("\n") + "\n"
            io.open(p, "w", encoding="utf-8", newline="\n").write(u)
            naoshita = "%d→%dbyte" % (len(b), len(u.encode()))
        elif kizu and mamoru:
            naoshita = "★控ゆゑ触らず(宣するのみ)★"
        rows.append((rel, len(b), ",".join(kizu) or "清い", naoshita))
w = 0
for r in rows:
    print("%-40s %8dbyte  %-24s %s" % r)
    if r[2] != "清い": w += 1
print("★%s★ 母數=%d 疵有=%d  (%s)" % ("清い" if w == 0 else "疵在り", len(rows), w,
      "naose 済" if naose else "prescan のみ"))
sys.exit(1 if (w and not naose) else 0)

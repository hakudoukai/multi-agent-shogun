#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★0byte を産まぬ★ ―― 空の流れを「空である旨の一行」へ直す(門 條④ は 0byte に鳴る)。

★何故 後から直すか★: shell の `>` は ★命令が走る前に file を作る★ 故、
己の出目 file は ★己が掃く刻には必ず 0byte★ である(自己言及)。
∴ 掃きは ★全ての走りの後★ に一度で行ひ、掃いた本を名指して刷る。
之は「隠す」ではない ―― KARA の一行は ★器が書いた印★ であり 0byte と読み分けられる。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
RAW = os.path.join(BUNDLE, "raw")
sys.path.insert(0, RAW)
from kaki import KARA, kaku, kaku_tsv    # noqa: E402


def main():
    naotta, rows = [], []
    for dp, dn, fn in os.walk(BUNDLE):
        dn.sort()
        if os.path.relpath(dp, BUNDLE).startswith("_gate"):
            continue          # ★門控は除外形★ ―― 門が走る度に生れる
        for f in sorted(fn):
            p = os.path.join(dp, f)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            rel = os.path.relpath(p, BUNDLE)
            n = os.path.getsize(p)
            if n == 0:
                with open(p, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(KARA + "\n")
                naotta.append(rel)
                rows.append([rel, 0, os.path.getsize(p), "0byte→KARA一行"])
            else:
                b = open(p, "rb").read()
                need = (not b.endswith(b"\n")) or b.endswith(b"\n\n") \
                    or b.count(b"\r") > 0 or any(
                        ln.rstrip(b" \t") != ln for ln in b.split(b"\n"))
                if need:
                    kaku(p, b.decode("utf-8", errors="replace"))
                    rows.append([rel, n, os.path.getsize(p), "整へ直した(kaki)"])
                    naotta.append(rel)
    print("★掃いた本 %d★" % len(naotta))
    for r in naotta:
        print("  %s" % r)
    kaku_tsv(os.path.join(RAW, "90_seikika.tsv"), rows,
             header=["path", "前bytes", "後bytes", "何をしたか"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

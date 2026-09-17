#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒' 案毎に ★現物で判定が動く行★ を数へる ―― 一案づつ、同じ歩き根で。

★讀み手が現に見る行だけを数へる★: main() は `SHA.search(line)` が外れた行を
``continue`` で ★飛ばす★(逐語 _ki/san_c1486ca1.py:167-169)。
∴ ③sha無 の行で候補が食ひ違つても ★判定は動かぬ★ ―― 之を「差」に数へれば嘘に成る。
其の事自体を ★陽性対照★ で示す(21_taishou.py)。
"""
import importlib.util
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))
SHA = re.compile(r"sha256=([0-9a-f]{64})")
HAS_PATH = re.compile(r"(?:^|\s)path=\S")

KI = [("⑶_c1486ca1", "_ki/san_c1486ca1.py"), ("案戊", "_an/an_bo_km120.py"),
      ("案庚", "_an/an_kou_km120.py"), ("案己", "_an/an_ki_km120.py")]


def yomu(rel, nm):
    spec = importlib.util.spec_from_file_location("ki_" + nm, os.path.join(BUNDLE, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod.paths_of


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    koku = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    fn = [(nm, yomu(rel, nm.replace("⑶", "san").replace("案", "an"))) for nm, rel in KI]
    files = []
    for dirpath, dirnames, filenames in os.walk(walk_root):
        if "__pycache__" in os.path.basename(dirpath):
            dirnames[:] = []
            continue
        for f in filenames:
            p = os.path.join(dirpath, f)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            if stat.S_ISREG(st.st_mode):
                files.append(p)
    # 集計: 器 → [讀む行, 候補が⑶と違ふ行, 昇る実体が⑶と違ふ行]
    tally = {nm: [0, 0, 0] for nm, _ in fn}
    meisai = []
    yomu_gyou = yomu_gyou_soto = 0
    for p in files:
        ono = os.path.abspath(p).startswith(os.path.abspath(BUNDLE) + os.sep)
        try:
            s = open(p, encoding="utf-8", errors="strict").read()
        except (UnicodeDecodeError, OSError):
            continue
        base = os.path.dirname(p)
        for no, line in enumerate(s.split("\n"), 1):
            if not HAS_PATH.search(line) or line.lstrip().startswith("#"):
                continue
            if not SHA.search(line):      # ★讀み手が飛ばす行★ ―― 数へぬ
                continue
            yomu_gyou += 1
            if not ono:
                yomu_gyou_soto += 1

            def noboru(ts):
                for t in ts:
                    q = os.path.join(base, t)
                    if os.path.isfile(q):
                        return t
                return None
            kijun_c = fn[0][1](line)
            kijun_n = noboru(kijun_c)
            for nm, f in fn:
                c = f(line)
                tally[nm][0] += 1
                if c != kijun_c:
                    tally[nm][1] += 1
                    n2 = noboru(c)
                    if n2 != kijun_n:
                        tally[nm][2] += 1
                        meisai.append([nm, "己束" if ono else "外",
                                       os.path.relpath(p, walk_root), no,
                                       repr(kijun_c)[:120], str(kijun_n)[:80],
                                       repr(c)[:120], str(n2)[:80], line[:200]])
    out = ["# ㋒' 案毎の現物での動き  刻=%s" % koku,
           "歩き根 = %s ★一本★ / 歩いた file = %d" % (walk_root, len(files)),
           "★讀み手が現に見る行★(`path=` 有 かつ `sha256=<64hex>` 有 かつ '#' 起しに非ず)",
           "  = %d 行(内 外 = %d / 己束 = %d)" % (yomu_gyou, yomu_gyou_soto, yomu_gyou - yomu_gyou_soto),
           "",
           "\t".join(["器", "讀んだ行", "候補が⑶と違ふ行", "★昇る実体が⑶と違ふ行★"])]
    for nm, _ in fn:
        out.append("\t".join([nm] + [str(x) for x in tally[nm]]))
    out += ["", "## 昇る実体が動いた行の明細(★之だけが判定を動かす★) = %d 件" % len(meisai)]
    if not meisai:
        out.append("  ★一件も無し★ ―― 三案の何れも、此の歩き根の現物では判定を一行も動かさぬ。")
    kaku_tsv(os.path.join(BUNDLE, "raw", "22_an_betsu.tsv"), meisai,
             header=["器", "所", "file(根から)", "行", "⑶の候補", "⑶で昇る", "案の候補", "案で昇る", "行"])
    kaku(os.path.join(BUNDLE, "raw", "22_an_betsu.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

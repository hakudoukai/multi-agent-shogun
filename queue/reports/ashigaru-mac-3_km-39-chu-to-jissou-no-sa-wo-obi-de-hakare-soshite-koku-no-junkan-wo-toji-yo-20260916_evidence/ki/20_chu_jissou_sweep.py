#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問一 ㋔ ―― 「註 ⇔ 實装」の同じ形が scripts/ に他に何本在るか。

★此の器が測るのは『矛盾』ではない。★ 矛盾は字の意味であり、器には讀めぬ。
器が測るのは ★候補★ ―― 即ち「★絶対を宣る語★ を含む註」の近くに「★条件分岐★」が在る形。
∴ 出す數は ★上限でも下限でもなく『候補の數』★ であり、★人が一本づつ裁いて初めて數に成る。★
  (法「A catalogue counted by form never closes」―― 形で数へる帳は閉ぢぬ)

母數の宣り:
  歩いた根 = scripts/   (再帰・regular file のみ)
  母數     = 其の下の regular file 全數。内 ⑴讀めた ⑵讀めぬ(binary 等) を分けて刷る。
  ★控(名に 'bak' を含む)も歩く★ ―― 除けば「除いた」と書かねば成らぬ故(法「除いた≠歩いて居らぬ」)。
  然れど控は生きた本の写しゆゑ ★二重に数へられる★ ―― 内訳を別に刷る。

窓 K = 註の行から ★後ろ 10 行★(前へは 3 行)。此の窓は ★恣意である★ ∴ 宣る。
"""
import os
import re
import sys

ROOT = "scripts"
K_FWD, K_BACK = 10, 3

# ★絶対を宣る語★(辞書は恣意 ∴ 逐一宣る)
LEX = [
    "regardless", "always", "ALWAYS", "never", "NEVER", "unconditional",
    "every time", "in all cases", "no matter",
    "必ず", "常に", "全て", "すべて", "いかなる", "拘らず", "かかわらず",
    "問わず", "関係なく", "一律", "例外なく", "無条件",
]
NEG_CONTROL = "zunbero39nonexistent"   # ★在らざる語★(陰性対照)
COND = re.compile(r"^\s*(if|elif)\b|^\s*\}\s*elif\b")
POSITIVE_CONTROL = ("scripts/stop_hook_inbox.sh", 71)


def comment_lines(path, lines):
    out = []
    for i, ln in enumerate(lines, 1):
        s = ln.lstrip()
        if s.startswith("#"):
            out.append((i, ln))
    return out


def main():
    files = []
    for dirpath, _dirs, names in os.walk(ROOT):
        for n in names:
            p = os.path.join(dirpath, n)
            if os.path.isfile(p) and not os.path.islink(p):
                files.append(p)
    files.sort()
    total = len(files)

    readable, unreadable = [], []
    for p in files:
        try:
            open(p, encoding="utf-8").read()
            readable.append(p)
        except Exception as e:
            unreadable.append((p, type(e).__name__))

    print("【母數の宣り】")
    print("  歩いた根 = %s/ (再帰・regular file のみ・symlink は除く)" % ROOT)
    print("  母數(本) = ★%d★  内 讀めた=%d / 讀めぬ=%d" % (total, len(readable), len(unreadable)))
    print("  内 名に 'bak' を含む(控) = %d 本 ―― ★歩いて居る。除いて居らぬ。★"
          % sum(1 for p in files if "bak" in os.path.basename(p)))
    for p, why in unreadable:
        print("    ★讀めぬ★ %s (%s)" % (p, why))
    print("  窓 K = 註の行から 後ろ %d 行 / 前 %d 行 ―― ★恣意である★" % (K_FWD, K_BACK))
    print("  辞書(絶対を宣る語) %d 語 = %s" % (len(LEX), " / ".join(LEX)))
    print("")

    cands = []
    neg_hits = 0
    total_lines = 0
    for p in readable:
        lines = open(p, encoding="utf-8").read().split("\n")
        total_lines += len(lines)
        for i, ln in comment_lines(p, lines):
            if NEG_CONTROL in ln:
                neg_hits += 1
            hit = [w for w in LEX if w in ln]
            if not hit:
                continue
            near = None
            for j in range(i + 1, min(i + K_FWD, len(lines)) + 1):
                if COND.search(lines[j - 1]):
                    near = (j, lines[j - 1].strip())
                    break
            if near is None:
                for j in range(max(1, i - K_BACK), i):
                    if COND.search(lines[j - 1]):
                        near = (j, lines[j - 1].strip())
                        break
            if near is not None:
                cands.append((p, i, ln.strip(), hit, near))

    print("【対照】")
    print("  陽性対照 = %s L%d が候補に在るか" % POSITIVE_CONTROL)
    pc = [c for c in cands if c[0] == POSITIVE_CONTROL[0] and c[1] == POSITIVE_CONTROL[1]]
    print("    → %s" % ("★在り(器は見えて居る)★" if pc else "★無し ―― 器が的を見て居らぬ。數を讀むな★"))
    print("  陰性対照 = 在らざる語 %r の當たり = %d 本 (0 で在るべし)" % (NEG_CONTROL, neg_hits))
    print("")

    print("【候補】 歩いた行(延べ)=%d / ★候補=%d 本★" % (total_lines, len(cands)))
    for p, i, ln, hit, (j, cj) in cands:
        print("  ── %s:%d  語=%s" % (p, i, ",".join(hit)))
        print("     註 | %s" % ln[:160])
        print("     枝 | L%d %s" % (j, cj[:140]))
    print("")
    by_file = {}
    for p, *_ in cands:
        by_file[p] = by_file.get(p, 0) + 1
    print("【file 別】")
    for p in sorted(by_file, key=lambda x: (-by_file[x], x)):
        print("  %3d  %s%s" % (by_file[p], p, "  ★控★" if "bak" in os.path.basename(p) else ""))
    print("")
    print("★此の數は『矛盾の數』ではない。『候補の數』である。★")
    print("★裁くのは人である ―― 紙で一本づつ当たり、確/否/未判 に分ける。★")

    if not pc:
        return 3
    if neg_hits != 0:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

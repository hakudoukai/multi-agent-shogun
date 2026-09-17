# -*- coding: utf-8 -*-
"""㋑補 ―― ★乖離は両側に在る★。⑴ だけでは片側しか見えぬ。

  usage: python3 driver/35_ryoumuki.py <束の根>

⑴(`main...X`)は git の定義上 ★merge-base から X まで★ の片側であり、
★main が己の向きへ何 file 進んだか★ は一切言はぬ。
本器は分岐点を名指し、main 側を測り、★main 側の file と各枝の自前差分の交はり★ を数へる
―― 之が「着地させる時に main と衝突する file」である。

陽性対照: ⑴ main 側 file 数が 0 なら(=分岐点が main tip)止まる / ⑵ 交はり器を
偽の path 表へ当てて 0 が出ねば止まる / ⑶ 14 本の分岐点が一つに揃はねば止まる。
"""
import os
import subprocess
import sys
from importlib import import_module

sys.path.insert(0, __file__.rsplit("/", 1)[0])
K = import_module("00_kaki")

MAIN = "4be3ee19e1c5"


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True)
    return p.returncode, p.stdout, p.stderr


def names(rc, out):
    if rc != 0:
        return None
    return [x for x in out.decode("utf-8", "surrogateescape").split("\0") if x]


def load(p):
    rows, h = [], None
    for ln in open(p, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if h is None:
            h = c
            continue
        if c and c[0]:
            rows.append(dict(zip(h, c)))
    return rows


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    raw = os.path.join(root, "raw")
    soku = load(raw + "/31_sokutei.tsv")
    if len(soku) != 14:
        sys.stderr.write("★母數が14でない(%d)★ ―― 一行も書かず止まる\n" % len(soku))
        return 5

    mbs = set(r["merge_base_main"] for r in soku)
    if len(mbs) != 1:
        sys.stderr.write("★分岐点が一つに揃はぬ(%d 種)★ ―― 本器は一点分岐を前提にする ∴ 止まる\n" % len(mbs))
        return 5
    mb = mbs.pop()

    rc, out, err = git("diff", "--name-only", "-z", mb, MAIN)
    omote = names(rc, out)
    if omote is None:
        sys.stderr.write("★main 側の差分が取れぬ rc=%d★: %s\n" % (rc, err.decode("utf-8", "replace")[:200]))
        return 5
    if not omote:
        sys.stderr.write("★対照が倒れた: main 側 file 数=0(分岐点が main tip と同じ)★ ―― 止まる\n")
        return 5
    rc2, out2, _ = git("diff", "--name-only", "-z", MAIN, mb)
    ura_same = names(rc2, out2)
    if ura_same is None or len(ura_same) != len(omote):
        sys.stderr.write("★対照が倒れた: 向きを入替へると file 数が変る(%s vs %d)★ ―― 止まる\n"
                         % (len(ura_same) if ura_same is not None else "取れぬ", len(omote)))
        return 5

    rc3, out3, _ = git("rev-list", "--count", "%s..%s" % (mb, MAIN))
    main_commit = out3.decode().strip() if rc3 == 0 else "測れぬ"

    oset = set(omote)
    # 陰性対照: 実在せぬ path 表と交はれば 0 でなければならぬ
    nise = {"__nai__/a", "__nai__/b"}
    if oset & nise:
        sys.stderr.write("★対照が倒れた: 偽 path と交はつた★ ―― 止まる\n")
        return 5

    K.kaku(os.path.join(raw, "36_ryoumuki_main.txt"),
           "分岐点(merge-base)= %s\nmain tip = %s\nmain 側 commit = %s\nmain 側 file = %d\n\n%s"
           % (mb, MAIN, main_commit, len(omote), "\n".join(sorted(omote))))

    rows = []
    for r in soku:
        br, sha = r["branch"], r["sha40"]
        base = r["(2)kiten_sha"] if "(2)kiten_sha" in r else None
        if not base:
            # 基点 sha は 31 に無い ∴ 枝名から臺帳で引く
            mei = {x["branch"]: x["sha40"] for x in load(raw + "/21_roster.tsv")}
            base = mei.get(r["(2)kiten_eda"])
        if not base:
            sys.stderr.write("★基点 sha が引けぬ: %s★ ―― 一行も書かず止まる\n" % r["(2)kiten_eda"])
            return 5
        rc4, out4, _ = git("diff", "--name-only", "-z", base, sha)
        jimae = names(rc4, out4)
        if jimae is None:
            sys.stderr.write("★自前差分が取れぬ: %s★ ―― 止まる\n" % br)
            return 5
        kasa = sorted(set(jimae) & oset)
        rc5, out5, _ = git("rev-list", "--count", "%s..%s" % (sha, MAIN))
        rows.append([
            br, r["(1)file_gyou"], r["(1)commit_main"],
            str(len(omote)), main_commit,
            out5.decode().strip() if rc5 == 0 else "測れぬ",
            str(len(kasa)),
            " ".join(kasa) if kasa else "-",
        ])
    K.kaku_tsv(os.path.join(raw, "37_ryoumuki.tsv"), rows,
               ["枝", "(1)枝側file", "(1)枝側commit", "main側file", "main側commit",
                "枝から見たmainの先行commit", "★自前 ∩ main側★", "其の path"])
    n = sum(1 for r in rows if r[6] != "0")
    sys.stderr.write("分岐点=%s / main側 %s commit %d file / 交はる枝=%d本\n"
                     % (mb[:12], main_commit, len(omote), n))
    return 0


sys.exit(main())

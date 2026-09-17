# -*- coding: utf-8 -*-
"""㋔ 版の系譜 ―― 四版の間に祖先關係が在るか。★實測のみ★(「新しい方が正しい」と決めつけぬ)。

道:
 ⑴ 門の path を触つた commit を refs 悉く(--all)から拾ひ、各 commit の門 blob を引く。
 ⑵ blob 毎に「其の blob を初めて載せた commit(刻の最も古い物)」を代表とする。
 ⑶ 代表同士へ git merge-base --is-ancestor を ★十二通り(4×3)★ 悉く当てる。
 ⑷ 版と版の差を git diff --numstat(blob 同士)で取る ―― ★行が増えた事は治つた事ではない★ を
    數で言へる様にする為。

usage: python3 driver/50_keifu.py <bundle_root> <repo_root>
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")

PATH = "scripts/checks/karo_mac_dasumae_gate.sh"
ORDER = ["9cd550fc2cf963ca0475b3448bb33483b9aede6b",
         "54e133c85832d48aa731d0ab0d105d399b9b8fbd",
         "b0bf5b05ededce4b06286dbab05cf0b616414ef2",
         "054c442eaee3886b2283f98f7c3a1ab8cb813b68"]
GYOU = {"9cd550fc2cf963ca0475b3448bb33483b9aede6b": 310,
        "54e133c85832d48aa731d0ab0d105d399b9b8fbd": 173,
        "b0bf5b05ededce4b06286dbab05cf0b616414ef2": 257,
        "054c442eaee3886b2283f98f7c3a1ab8cb813b68": 321}


def git(repo, *a):
    p = subprocess.run(["git", "-C", repo] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "surrogateescape"), p.stderr.decode("utf-8", "surrogateescape")


def main(argv):
    bundle, repo = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    raw = os.path.join(bundle, "raw")

    rc, out, err = git(repo, "log", "--all", "--format=%H\t%ct\t%cI\t%s", "--", PATH)
    assert rc == 0, err
    commits = [ln.split("\t", 3) for ln in out.split("\n") if ln.strip()]

    rows = []
    byblob = {}
    for h, ct, ci, subj in commits:
        rc2, b, _ = git(repo, "rev-parse", "--verify", "--quiet", "%s:%s" % (h, PATH))
        b = b.strip() if rc2 == 0 else ""
        rows.append([h, ci, b or "(門 無)", subj.replace("\t", " ")])
        if b:
            byblob.setdefault(b, []).append((int(ct), h, ci, subj))
    K.kaku_tsv(os.path.join(raw, "51_mon_wo_sawatta_commit.tsv"), rows,
               header=["commit", "刻(committer ISO)", "門blob(full)", "件名"])

    daihyou = {}
    lines = ["㋔ 系譜 ―― 門の path を触つた commit = %d 本(refs 悉く --all)" % len(commits), ""]
    for b in ORDER:
        lst = sorted(byblob.get(b, []))
        if not lst:
            lines.append("版%s(%d行): 門を触つた commit の中に ★一本も無い★" % (b[:16], GYOU[b]))
            continue
        daihyou[b] = lst[0][1]
        lines.append("版%s(%d行): 載せる commit=%d 本 / 最古=%s %s / 最新=%s %s"
                     % (b[:16], GYOU[b], len(lst), lst[0][1][:12], lst[0][2], lst[-1][1][:12], lst[-1][2]))
        lines.append("    最古の件名: %s" % lst[0][3])
    lines.append("")

    # ⑶ 祖先關係(代表 commit 同士・十二通り)
    t = []
    lines.append("★祖先關係(代表 commit = 其の版を最も古く載せた commit)★")
    for a in ORDER:
        for b in ORDER:
            if a == b or a not in daihyou or b not in daihyou:
                continue
            rc3, _, _ = git(repo, "merge-base", "--is-ancestor", daihyou[a], daihyou[b])
            t.append([b_short(a), b_short(b), daihyou[a][:12], daihyou[b][:12], str(rc3),
                      "祖先である" if rc3 == 0 else ("祖先でない" if rc3 == 1 else "★器の誤り★")])
            lines.append("  %s は %s の祖先か → %s (rc=%d)"
                         % (b_short(a), b_short(b), "★然り★" if rc3 == 0 else "否", rc3))
    K.kaku_tsv(os.path.join(raw, "52_sosen.tsv"), t,
               header=["版A", "版B", "代表A", "代表B", "is-ancestor rc", "判"])

    # ⑷ 版同士の差(行の増減)
    lines.append("")
    lines.append("★版と版の差(git diff --numstat blob blob ―― 足した行/引いた行)★")
    d = []
    for i, a in enumerate(ORDER):
        for b in ORDER[i + 1:]:
            rc4, o, _ = git(repo, "diff", "--numstat", a, b)
            f = o.strip().split("\t") if o.strip() else ["-", "-", "-"]
            d.append([b_short(a), b_short(b), str(GYOU[a]), str(GYOU[b]), f[0], f[1]])
            lines.append("  %s(%d行) → %s(%d行): 足した行 %s / 引いた行 %s"
                         % (b_short(a), GYOU[a], b_short(b), GYOU[b], f[0], f[1]))
    K.kaku_tsv(os.path.join(raw, "53_han_no_sa.tsv"), d,
               header=["版A", "版B", "A行", "B行", "足した行", "引いた行"])

    K.kaku(os.path.join(raw, "54_keifu_matome.txt"), "\n".join(lines))
    print("\n".join(lines))
    return 0


def b_short(b):
    return b[:16]


if __name__ == "__main__":
    sys.exit(main(sys.argv))

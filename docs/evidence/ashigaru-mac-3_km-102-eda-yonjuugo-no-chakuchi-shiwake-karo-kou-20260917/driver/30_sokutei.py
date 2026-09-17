# -*- coding: utf-8 -*-
"""㋑㋒ ―― ★二つの差分を測り分ける★(混ぜたら其れ自体が疵)。

  usage: python3 driver/30_sokutei.py <母數tsv(11_bogen.tsv)> <roster tsv(21_roster.tsv)> <main sha> <出目dir>

  ⑴ 対 origin/main: `git diff --name-only <main>...<X>` の行数。
     ★之は「此の枝が変へた file 数」では無い★ ―― 三点(...)は ★X 側の変更のみ★を映す。
     ∴ main が同じ file を触つて居ても其れは映らぬ。此の枝を含む鎖の ★積み上げ★ が出る。
  ⑵ ★自前★: 60 本の tip の内 X の ★真の祖先★ を悉く挙げ、`git rev-list --count B..X` が
     ★最小★ の B を基点に `git diff --name-only B..X`。祖先 tip が 0 本なら ★測れぬ★ と書く。
     同値(tie)が在れば ★枝名の辞書順で最小★ を採る ―― 其の旨と tie の数を刷る(黙つて選ばぬ)。

  ★數の取り方★: path は `-z`(NUL 区切り)で数へる ―― git は非 ASCII の path を括る為、
  行で数へると ★括られた一本★ と ★改行入りの名★ で數が狂ふ。
  併せて ★札が名指した「行数」★ も取り、二つが食ひ違つたら其の旨を欄に残す。
  rename は既定(検出有)と `--no-renames` の両方を取る ―― 前者は改名を 1 path、後者は 2 path と数へる。
"""
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from importlib import import_module  # noqa: E402

K = import_module("00_kaki")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def paths_z(rng, extra=()):
    rc, out, err = git("diff", "-z", "--name-only", *extra, rng)
    if rc != 0:
        return None, rc, err.strip()
    return [x for x in out.split("\0") if x], rc, ""


def lines_plain(rng, extra=()):
    rc, out, err = git("diff", "--name-only", *extra, rng)
    if rc != 0:
        return None, rc
    return len([x for x in out.split("\n") if x]), rc


def ryouiki(paths):
    seen = []
    for p in paths:
        top = p.split("/", 1)[0] if "/" in p else "(根)" + p
        if top not in seen:
            seen.append(top)
    return seen


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, ln in enumerate(fh):
            ln = ln.rstrip("\n")
            if i == 0 or not ln.strip():
                continue
            rows.append(ln.split("\t"))
    return rows


def main():
    if len(sys.argv) < 5:
        sys.stderr.write(__doc__)
        return 2
    bogen_tsv, roster_tsv, main_sha, outdir = sys.argv[1:5]
    mine = [(r[1], r[2]) for r in read_tsv(bogen_tsv) if len(r) > 2 and r[0].isdigit()]
    roster = [(r[0], r[1]) for r in read_tsv(roster_tsv) if len(r) > 1]

    rows, notes = [], []
    for sha, name in mine:
        # ⑴ 対 main(三点)
        p1, rc1, e1 = paths_z("%s...%s" % (main_sha, sha))
        l1, _ = lines_plain("%s...%s" % (main_sha, sha))
        p1nr, _, _ = paths_z("%s...%s" % (main_sha, sha), ("--no-renames",))
        mb = git("merge-base", main_sha, sha)[1].strip()
        c1 = git("rev-list", "--count", "%s..%s" % (main_sha, sha))[1].strip()

        # ⑵ 自前(60 tip 中の真の祖先で最小基点)
        anc = []
        for tsha, tname in roster:
            if tsha == sha:
                continue
            if git("merge-base", "--is-ancestor", tsha, sha)[0] == 0:
                n = int(git("rev-list", "--count", "%s..%s" % (tsha, sha))[1].strip() or 0)
                anc.append((n, tname, tsha))
        if not anc:
            base, p2, l2, c2, tie = "★測れぬ★", None, "★測れぬ★", "★測れぬ★", 0
            f2 = "★測れぬ(祖先 tip 0本)★"
            r2 = "★測れぬ★"
        else:
            anc.sort(key=lambda t: (t[0], t[1]))
            best = anc[0]
            tie = sum(1 for a in anc if a[0] == best[0]) - 1
            base = best[1]
            p2, rc2, e2 = paths_z("%s..%s" % (best[2], sha))
            l2, _ = lines_plain("%s..%s" % (best[2], sha))
            c2 = str(best[0])
            f2 = str(len(p2)) if p2 is not None else "★引けぬ rc=%d★" % rc2
            r2 = " ".join(ryouiki(p2)) if p2 else "(無)"
        f1 = str(len(p1)) if p1 is not None else "★引けぬ rc=%d★" % rc1
        if p1 is not None and l1 is not None and len(p1) != l1:
            notes.append("%s ⑴ NUL=%d 行=%d ―― ★括られた path が在る★" % (name, len(p1), l1))
        if p2 is not None and l2 is not None and len(p2) != l2:
            notes.append("%s ⑵ NUL=%d 行=%d ―― ★括られた path が在る★" % (name, len(p2), l2))
        rows.append([
            name, sha, f1, str(len(p1nr)) if p1nr is not None else "-", str(l1 if l1 is not None else "-"),
            c1, " ".join(ryouiki(p1)) if p1 else "(無)",
            f2, str(l2 if l2 is not None else "-"), c2, r2, base, len(anc), tie, mb[:12],
        ])
    K.kaku_tsv(outdir + "/31_sokutei.tsv", rows, header=[
        "branch", "sha40",
        "(1)file_main3ten_NUL", "(1)file_norename", "(1)file_gyou", "(1)commit_main", "(1)ryouiki",
        "(2)file_jimae_NUL", "(2)file_gyou", "(2)commit_jimae", "(2)ryouiki",
        "(2)kiten_eda", "sosen_tip_kazu", "tie_kazu", "merge_base_main",
    ])
    K.kaku(outdir + "/32_chuu.txt", "\n".join(notes) if notes else "")
    sys.stderr.write("測つた枝=%d / ⑵測れぬ=%d / 註=%d\n"
                     % (len(rows), sum(1 for r in rows if r[7].startswith("★測れぬ")), len(notes)))
    return 0


sys.exit(main())

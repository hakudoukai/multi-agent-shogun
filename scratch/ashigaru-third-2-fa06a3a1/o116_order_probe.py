#!/usr/bin/env python3
# o116: 第七の目「掃いた者は ★何の並び★ を辿つたか」。
#   ★当て★=logs/refs 樹の readdir 順（名の辞書順でも packed-refs の行順でもない）。
#   ★検め方★=200 本(空112+保つ88)の reflog mtime(ns) を ★真の順★ とし、三候補との ★逆転対の数★ を数へる。
#   ★外れる形（走る前に送つた）★=三つの逆転率に互ひに差が無い（㋐㋒同順・㋑も 5 点以内）なら ★棄てる★。
#   ★不利な証（走る前に送つた）★=㋐前科二つ ⇒ 名の一覧を落とす ／
#                                 ㋑readdir 順は『今の樹』の順で 当時の順である証は無い ／
#                                 ㋒packed-refs は git が辞書順に書く ∴ 候補は実は二つ。
#   ★受入①=『順が復元できた』と『順を決めた物差しが判つた』は別★。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import collections, datetime, os

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o116_order_%s.txt" % (D, TS)

# ── ① 母数（前弾の落した一覧のみを材料とする）──
rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)                      # 組/名/階層/在り処/…
grp = {c[1]: c[0] for c in rows}
band = [c[1] for c in rows if c[0] in ("空", "保つ")]     # ★帯 200 本★
assert len(rows) == 345, "母数 %d（345 を前提として居る）" % len(rows)
print("母数(引継) %d ／ 帯(空+保つ) %d 本" % (len(rows), len(band)))
print("  内訳: 空 %d ／ 保つ %d" % (sum(1 for n in band if grp[n]=="空"),
                                   sum(1 for n in band if grp[n]=="保つ")))

# ── ② 真の順 ＝ reflog file の mtime_ns ──
mt = {}; nomt = []
for nm in band:
    p = os.path.join(GIT, "logs", nm)
    try:
        mt[nm] = os.stat(p).st_mtime_ns
    except OSError as e:
        nomt.append((nm, type(e).__name__))
print("mtime 取れた %d ／ 取れぬ %d %s" % (len(mt), len(nomt), [n for n,_ in nomt][:5]))
tgt = [n for n in band if n in mt]
truth = sorted(tgt, key=lambda n: (mt[n], n))
ties  = len(tgt) - len(set(mt[n] for n in tgt))
print("★真の順★ mtime_ns の幅 %.6f 秒 ／ 同値(ties) %d 対" % (
      (max(mt[n] for n in tgt) - min(mt[n] for n in tgt)) / 1e9, ties))

# ── ③ 三候補の並び ──
# ㋐ 名の辞書順
cand_a = sorted(tgt)

# ㋑ logs/refs 樹の readdir 順（os.scandir の返す順を そのまま使ふ・sort せぬ）
walk = []
def rec(d, rel):
    try:
        ents = list(os.scandir(d))                  # ★sort せぬ＝readdir の順★
    except OSError:
        return
    for e in ents:
        r = rel + "/" + e.name if rel else e.name
        if e.is_dir(follow_symlinks=False):
            rec(e.path, r)
        else:
            walk.append("logs/" + r)
rec(os.path.join(GIT, "logs", "refs"), "refs")
pos_w = {nm: i for i, nm in enumerate(x[len("logs/"):] for x in walk)}
cand_b = [n for n in sorted(tgt, key=lambda n: pos_w.get(n, 10**9))]
print("readdir 走査 %d file ／ 帯のうち順の付いた本数 %d" % (
      len(walk), sum(1 for n in tgt if n in pos_w)))

# ㋒ packed-refs の行順
pos_p = {}; i = 0
with open(os.path.join(GIT, "packed-refs"), encoding="utf-8", errors="replace") as f:
    for ln in f:
        if ln.startswith(("#", "^")):
            continue
        p = ln.split()
        if len(p) >= 2:
            pos_p[p[1]] = i; i += 1
cand_c = [n for n in sorted(tgt, key=lambda n: pos_p.get(n, 10**9))]
print("packed-refs 行 %d ／ 帯のうち載る本数 %d" % (i, sum(1 for n in tgt if n in pos_p)))

# ── ④ 逆転対の数（真の順に対する）──
rank = {n: i for i, n in enumerate(truth)}
def inversions(seq):
    a = [rank[n] for n in seq]                      # O(n^2)・n=200 ゆゑ可
    return sum(1 for x in range(len(a)) for y in range(x+1, len(a)) if a[x] > a[y])
tot = len(tgt) * (len(tgt) - 1) // 2
res = {}
for lab, seq in (("㋐名の辞書順", cand_a), ("㋑readdir 順", cand_b), ("㋒packed-refs 行順", cand_c)):
    inv = inversions(seq)
    res[lab] = inv
    print("  %-18s 逆転 %6d / 全対 %6d ＝ ★%.2f%%★" % (lab, inv, tot, 100.0*inv/tot))
same_ac = (cand_a == cand_c)
print("㋐と㋒は同一順か: %s" % ("★同一★" if same_ac else "違ふ"))
lo = min(res.values()); best = [k for k, v in res.items() if v == lo]
spread = (max(res.values()) - lo) * 100.0 / tot
print("★最小＝%s（%.2f%%）／三者の開き %.2f 点★" % ("・".join(best), 100.0*lo/tot, spread))
print("★外れる形の判定★: 開き 5 点以内 → %s" % ("★棄てる★" if spread <= 5.0 else "棄てぬ（差が在る）"))

# ── ⑤ 空/保つ の交互（塊）を 各並びで数へる ──
def runs(seq):
    r = 1
    for x in range(1, len(seq)):
        if grp[seq[x]] != grp[seq[x-1]]:
            r += 1
    return r
print("塊の数（少ない＝まとまつて居る）: 真の順 %d ／ ㋐ %d ／ ㋑ %d ／ ㋒ %d（帯 %d 本）" % (
      runs(truth), runs(cand_a), runs(cand_b), runs(cand_c), len(tgt)))

# ── ⑥ 名の一覧を落とす（前科の手当）──
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o116 帯 %d 本の並び（組／名／真の順位(mtime)／㋐名／㋑readdir／㋒packed／mtime_ns）\n" % len(tgt))
    for n in truth:
        f.write("\t".join([grp[n], n, str(rank[n]),
                           str(cand_a.index(n)), str(cand_b.index(n)), str(cand_c.index(n)),
                           str(mt[n])]) + "\n")
    if nomt:
        f.write("# mtime 取れぬ %d 本\n" % len(nomt))
        for n, e in nomt:
            f.write("\t".join([grp.get(n, "?"), n, "-", "-", "-", "-", e]) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, len(tgt) + 1 + (len(nomt) + 1 if nomt else 0)))

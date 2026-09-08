#!/usr/bin/env python3
# o118（乙）: o116 第七の目の ★打ち直し★。当ての選び方は post-hoc の儘だが、
#   ★規則を走る前に宣言してから★ 打つ（宣言＝13:11:51〜13:11:56 の七便・一字も動かさぬ）。
#   ★①当て★=三候補のうち ㋑(readdir 順)が真の順に一致する ―― ★但し symref を除いた時に限る★。
#     ★除外規則は 族として 先に置く=『refs/**/HEAD を悉く除く』（一本の名を挙げるのでなく形で）★
#   ★②検め方★=帯 200 から 族 refs/**/HEAD を除いた本で ㋐名の辞書順／㋑readdir 順／㋒packed-refs 行順
#     の ★逆転対★ を数へる。除いた本数と名は ★器が己で刷る★。母数は assert で検算。
#   ★③外れる形★=★㋑の逆転対が ㋐の逆転対の 1/10 未満 でなければ ★棄てる★★（両の目が現に出得る尺）。
#   ★④不利な証★=㋐同じ帯を二度見る＝★外の標本に非ず★ ㋑★除く一本を選んだ動機は post-hoc の儘★
#     ㋒前科四つ（贋の名／組の名／出得ぬ閾／当ての向きを便に送らなんだ） ㋓真の順は名の順に近い
#     （隣接逆転 3/199）∴ どの候補も低い逆転率を出し易い＝『㋑が低い』は候補の別を示さぬ恐れ。
#   ★見込み値（走る前に便で送つた）★=㋑1／㋐60／㋒186 ―― ★器が実測より先に刷る★。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, os

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o118_order_excl_%s.txt" % (D, TS)
YOMI = {"㋐名の辞書順": 60, "㋑readdir 順": 1, "㋒packed-refs 行順": 186}

# ── ① 母数（前弾の落した一覧のみを材料とする）──
rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)
grp  = {c[1]: c[0] for c in rows}
band = [c[1] for c in rows if c[0] in ("空", "保つ")]
assert len(rows) == 345, "母数 %d（345 を前提として居る）" % len(rows)
assert len(band) == 200, "帯 %d（200 を前提として居る）" % len(band)
print("母数(引継) %d ／ 帯 200 本（空 %d ／ 保つ %d）" % (
      len(rows), sum(1 for n in band if grp[n]=="空"), sum(1 for n in band if grp[n]=="保つ")))

# ── ②-a ★除外＝族 refs/**/HEAD★（走る前に宣言した形・一本の名を挙げぬ）──
def is_symref_family(n):
    return n.startswith("refs/") and n.rsplit("/", 1)[-1] == "HEAD"
excl = [n for n in band if is_symref_family(n)]
keep = [n for n in band if not is_symref_family(n)]
print("★除いた本数 %d ／ 名 %s★" % (len(excl), excl))
print("★残る本数 %d（200 − %d）★" % (len(keep), len(excl)))
assert len(keep) + len(excl) == 200

# ── ②-b 真の順 ＝ reflog file の mtime_ns ──
mt = {}; nomt = []
for nm in keep:
    try:
        mt[nm] = os.stat(os.path.join(GIT, "logs", nm)).st_mtime_ns
    except OSError as e:
        nomt.append((nm, type(e).__name__))
print("mtime 取れた %d ／ 取れぬ %d %s" % (len(mt), len(nomt), [n for n,_ in nomt][:5]))
tgt   = [n for n in keep if n in mt]
truth = sorted(tgt, key=lambda n: (mt[n], n))
rank  = {n: i for i, n in enumerate(truth)}

# ── ③ 三候補の並び（o116 と同じ作り方・母数のみ替へる）──
cand_a = sorted(tgt)

walk = []
def rec(d, rel):
    try:
        ents = list(os.scandir(d))            # ★sort せぬ＝readdir の順★
    except OSError:
        return
    for e in ents:
        r = rel + "/" + e.name if rel else e.name
        if e.is_dir(follow_symlinks=False):
            rec(e.path, r)
        else:
            walk.append("logs/" + r)
rec(os.path.join(GIT, "logs", "refs"), "refs")
pos_w  = {nm: i for i, nm in enumerate(x[len("logs/"):] for x in walk)}
cand_b = sorted(tgt, key=lambda n: pos_w.get(n, 10**9))

pos_p = {}; i = 0
with open(os.path.join(GIT, "packed-refs"), encoding="utf-8", errors="replace") as f:
    for ln in f:
        if ln.startswith(("#", "^")):
            continue
        p = ln.split()
        if len(p) >= 2:
            pos_p[p[1]] = i; i += 1
cand_c = sorted(tgt, key=lambda n: pos_p.get(n, 10**9))
print("readdir 走査 %d file ／ 順の付いた本 %d ／ packed-refs 行 %d ／ 載る本 %d" % (
      len(walk), sum(1 for n in tgt if n in pos_w), i, sum(1 for n in tgt if n in pos_p)))

# ── ④ ★見込み値を 実測より先に刷る★ ──
print("★見込み（走る前に便で送つた）★ ㋑1 ／ ㋐60 ／ ㋒186 ―― ★実測はこの下に刷る★")

def inversions(seq):
    a = [rank[n] for n in seq]
    return sum(1 for x in range(len(a)) for y in range(x+1, len(a)) if a[x] > a[y])
tot = len(tgt) * (len(tgt) - 1) // 2
res = {}
for lab, seq in (("㋐名の辞書順", cand_a), ("㋑readdir 順", cand_b), ("㋒packed-refs 行順", cand_c)):
    inv = inversions(seq); res[lab] = inv
    print("  %-18s 逆転 %6d / 全対 %6d ＝ %.2f%%  ［見込 %d／差 %+d］" % (
          lab, inv, tot, 100.0*inv/tot, YOMI[lab], inv - YOMI[lab]))

# ── ⑤ ★宣言した尺★（走る前に送つた形の儘）──
ia, ib = res["㋐名の辞書順"], res["㋑readdir 順"]
thr = ia / 10.0
print("★宣言した尺★: ㋑(%d) < ㋐(%d)/10 (=%.1f) か ⇒ %s" % (
      ib, ia, thr, "★棄てぬ★" if ib < thr else "★棄てる★"))
print("㋐と㋒は同一順か: %s" % ("★同一★" if cand_a == cand_c else "違ふ"))
print("★最小＝%s★" % "・".join(k for k, v in res.items() if v == min(res.values())))

# ── ⑥ 名の一覧を落とす ──
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o118 除外後 %d 本（組／名／真の順位／㋐／㋑／㋒／mtime_ns）\n" % len(tgt))
    for n in truth:
        f.write("\t".join([grp[n], n, str(rank[n]), str(cand_a.index(n)),
                           str(cand_b.index(n)), str(cand_c.index(n)), str(mt[n])]) + "\n")
    f.write("# ★除いた本（族 refs/**/HEAD）★ %d\n" % len(excl))
    for n in excl:
        f.write("\t".join([grp.get(n, "?"), n, "除外", "-", "-", "-", "-"]) + "\n")
print("名の一覧 %s （%d 行）" % (OUT, len(tgt) + 2 + len(excl)))
print("[八条目] 母数 345・帯 200 は o112/o116/o117 の儘。★動かしたのは 除外(族 refs/**/HEAD %d 本)★。" % len(excl))
print("[八条目] ★尺も動かした★=o116 は『三者の開き 5 点以内』・本弾は『㋑ < ㋐/10』（比）。")

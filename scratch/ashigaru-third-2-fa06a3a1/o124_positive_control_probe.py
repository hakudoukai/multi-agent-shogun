#!/usr/bin/env python3
# o124: ★陽性対照★ ―― 「名を変へれば位置は現に動く」を ★同じ走で★ 示し、
#        o123 の結び（『位置』は作り直しの有無を原理として映さぬ）が ★測りの壊れ★ でない事を検める。
#   ★当て★=P群（別名へ rename）は動く／T・R・R2・C は動かぬ。
#   ★検め方★=htree が効く規模 N=2000 の dir を ★二つ★ 建てる。
#            dir_a = o123 の四群（T/R/R2/C）を ★再び打つ（再現を見る）★。
#            dir_b = ★陽性対照★＝500 本を別名へ rename し、
#                    (i) 絶対 index の変化 と (ii) ★不触の者同士の相対順の崩れ★ の二通りで数へる。
#   ★外れる形（走る前に便で送つた）★
#      ① P群(i) < 0.10 → ★測りが壊れて居る★ ⇒ o123 の結びを ★己で取り下げる★
#      ② 不触群(ii) > 0.05 → 相対順といふ尺其の物を捨てる
#      ③ dir_a の四群が o123 と違ふ → ★両走を疑ふ★
#   ★不利な証（走る前に便で送つた）★
#      (a) 名を変へれば動くは ★当然★ ∴ 之は説を立てぬ・己の測りを検めるだけ
#      (b) dir_b は ★別 dir★ ゆゑ四群と同一条件では無い（申告済）
#      (c) 押し出しゆゑ (i) は P 以外も動かす ―― (i) の高さを『陽性』と読み違へるな
#   ★門★=lsattr に I／dir が 4096 超（効かねば止まり 数を作らぬ）
#   ★git は一度も実行せぬ・共有 /mnt/c は stat すらせぬ・書込は scratch のみ★
import os, random, subprocess, datetime, shutil

D    = "scratch/ashigaru-third-2-fa06a3a1"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o124_pos_%s.txt" % (D, TS)
N    = 2000
PRE  = ["iincho","karo-main","karo-third","gunshi","ashigaru","shogun","commander","hermes"]

print("★見込み（走る前に便で刷つた・実測は此の下）★ P(i)0.95 ／ P(ii)0.95 ／ 不触(i)0.60(押し出し) ／ 不触(ii)0.00 ／ o123 四群の再現 悉く 0.0000=0.95")

def build(tag, seed):
    tree = os.path.join(D, "o124_tree_%s" % tag)
    dr   = os.path.join(tree, "logs", "refs", "heads")
    if os.path.isdir(tree):
        shutil.rmtree(tree)
    os.makedirs(dr)
    random.seed(seed)
    names = []
    for i in range(N):
        nm = "%s_%04d_%08x" % (PRE[i % len(PRE)], i, random.getrandbits(32))
        with open(os.path.join(dr, nm), "w") as f:
            f.write("0"*40 + " " + "1"*40 + " a2 <a2@x> 1757300000 +0900\tcommit: %s\n" % nm)
        names.append(nm)
    ls = subprocess.run(["lsattr","-d",dr], capture_output=True, text=True)
    flags = ls.stdout.split()[0] if ls.stdout.split() else "?"
    dbyte = os.stat(dr).st_size
    fs = subprocess.run(["stat","-f","-c","%T",dr], capture_output=True, text=True).stdout.strip()
    print("[%s] FS=%s ／ dir byte=%d ／ lsattr=%r ／ file %d 本" % (tag, fs, dbyte, flags, len(os.listdir(dr))))
    assert "I" in flags, "★門: %s に I 無し＝dir_index が効いて居らぬ ―― 止まる★" % tag
    assert dbyte > 4096, "★門: %s の dir が %d ＝一塊のまま ―― 止まる★" % (tag, dbyte)
    return dr, names

def readdir(dr, keep):
    return [e.name for e in os.scandir(dr) if e.is_file() and e.name in keep]

rows = []

# ── dir_a: o123 の四群を再び打つ（再現を見る）──
dr_a, na = build("a", 20260908)
OURS = set(na)
pre  = {nm: i for i, nm in enumerate(readdir(dr_a, OURS))}
grp  = {}
for i, nm in enumerate(na):
    g = ("T","R","R2","C")[i % 4]; grp[nm] = g
    p = os.path.join(dr_a, nm)
    body = open(p).read()
    if g == "T":
        open(p, "w").close()
    elif g == "R":
        os.remove(p); open(p, "w").write(body)
    elif g == "R2":
        os.remove(p)
        z = os.path.join(dr_a, "zzfill_" + nm)          # ★挟み＝母数から除く（宣言済）★
        open(z, "w").write("x\n")
        open(p, "w").write(body)
post = {nm: i for i, nm in enumerate(readdir(dr_a, OURS))}
res_a = {}
for g in ("T","R","R2","C"):
    mem = [n for n in na if grp[n] == g]
    mv  = sum(1 for n in mem if pre[n] != post[n])
    res_a[g] = (len(mem), mv, mv/len(mem))
    print("[a] %-2s 群 %4d 本: ★動いた %4d ＝ %.4f★" % (g, len(mem), mv, mv/len(mem)))
    for n in mem:
        rows.append(("a", g, n, n, pre[n], post[n], int(pre[n] != post[n])))

# ── dir_b: ★陽性対照★ ―― 500 本を別名へ rename ──
dr_b, nb = build("b", 20260909)
OURS_B = set(nb)
pre_b  = {nm: i for i, nm in enumerate(readdir(dr_b, OURS_B))}
P_set  = [nb[i] for i in range(len(nb)) if i % 4 == 0]      # 500 本
newname = {}
for nm in P_set:
    nn = "renamed_" + nm                                    # ★名が変はる ∴ hash も変はる★
    os.rename(os.path.join(dr_b, nm), os.path.join(dr_b, nn))
    newname[nm] = nn
keep_b = (OURS_B - set(P_set)) | set(newname.values())
post_b = {nm: i for i, nm in enumerate(readdir(dr_b, keep_b))}
untouched = [n for n in nb if n not in newname]

mvP = sum(1 for n in P_set if pre_b[n] != post_b[newname[n]])
mvU = sum(1 for n in untouched if pre_b[n] != post_b[n])
print("[b] P  群 %4d 本 (i)絶対 index: ★動いた %4d ＝ %.4f★" % (len(P_set), mvP, mvP/len(P_set)))
print("[b] 不触群 %4d 本 (i)絶対 index: 動いた %4d ＝ %.4f（★押し出し★）" % (len(untouched), mvU, mvU/len(untouched)))

# (ii) 相対順の崩れ ―― 不触群だけを取り出して順が保たれるか／P が其の列の何処へ入るか
u_pre  = sorted(untouched, key=lambda n: pre_b[n])
u_post = sorted(untouched, key=lambda n: post_b[n])
ii_untouched = sum(1 for x, y in zip(u_pre, u_post) if x != y) / len(untouched)
print("[b] 不触群 (ii)相対順の崩れ ＝ %.4f" % ii_untouched)

def rank_among(idx, ref):        # ref（不触の post index 列）の中での位置
    lo, hi = 0, len(ref)
    while lo < hi:
        mid = (lo + hi)//2
        if ref[mid] < idx: lo = mid+1
        else: hi = mid
    return lo
ref_pre  = sorted(pre_b[n]  for n in untouched)
ref_post = sorted(post_b[n] for n in untouched)
mvP_ii = 0
for n in P_set:
    a = rank_among(pre_b[n],  ref_pre)
    b = rank_among(post_b[newname[n]], ref_post)
    if a != b: mvP_ii += 1
    rows.append(("b", "P", n, newname[n], pre_b[n], post_b[newname[n]], int(a != b)))
for n in untouched:
    rows.append(("b", "U", n, n, pre_b[n], post_b[n], int(pre_b[n] != post_b[n])))
print("[b] P  群 (ii)★不触の列に対する順位の変化★ ＝ %.4f" % (mvP_ii/len(P_set)))

# ── 判定（外れる形は走る前に置いた）──
pi  = mvP/len(P_set); pii = mvP_ii/len(P_set)
print("★外れる形①★: P(i) <0.10 → %s" % ("★當たり ⇒ 測りが壊れて居る ⇒ o123 の結びを取り下げる★" if pi < 0.10 else "落ちず"))
print("★外れる形②★: 不触(ii) >0.05 → %s" % ("★當たり ⇒ 相対順といふ尺を捨てる★" if ii_untouched > 0.05 else "落ちず"))
same = all(abs(res_a[g][2] - 0.0) < 1e-9 for g in ("T","R","R2","C"))
print("★外れる形③★: o123 四群が再現せぬ → %s" % ("落ちず（四群 悉く 0.0000 で再現）" if same else "★當たり ⇒ 両走を疑ふ★"))
print("★陽性対照の結び★: P(i)=%.4f ／ P(ii)=%.4f → %s" % (pi, pii,
      "★測りは動きを見られる（陽性対照 立つ）★" if (pi >= 0.90 and pii >= 0.90) else "★立たず★"))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o124 dir/群/旧名/新名/前位置/後位置/動いたか\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, len(rows)+1))

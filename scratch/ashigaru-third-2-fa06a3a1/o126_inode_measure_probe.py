#!/usr/bin/env python3
# o126: ★inode 尺を 対照樹で検める★（order126・走 1）
#   ★之は o120 を判ずる弾に非ず（帯へ当てる裁は上に在る）―― ★尺が現に分けられるか★ を検める弾★（令の逐語）。
#   ★当て★=inode は『実体』に付く ∴ ★同名で作り直せば変はり truncate では変はらぬ★／
#           ctime は『触られた』を映す ∴ ★両者を対にすれば T と R を分けられる★。
#   ★検め方★=四群 各 500 本を ★同じ走★ に置く（条 十四＝陽性と ★陰性★ を同じ走に）:
#       R = 削除→同名再作成   … ★inode の陽性★
#       T = truncate          … ★inode の陰性・ctime の陽性★
#       A = 追記(append)      … ★inode の陰性・ctime の陽性★
#       C = 一指も触れぬ      … ★両尺の陰性★
#     尺 = (1) inode 番号の変化 (2) ctime の変化 (3) mtime（参考）
#   ★外れる形（走る前に便で送つた・三つ）★
#       ① R の inode 変化 <0.90        → ★inode 尺は作り直しを映さぬ＝立たず★
#       ② T か C の inode 変化 >0.05   → ★陰性が汚れる＝尺が雑音を拾ふ＝立たず★
#       ③ C の ctime 変化 >0.05        → ★何もして居らぬ物が動く＝測り方が壊れて居る★
#   ★不利な証（走る前に便で送つた・重い順）★
#       (b) ★inode は再利用される★ ―― 削除直後に作れば同じ番号が返り得る
#           ⇒ R で 0 が出ても『作り直しで無い』証に成らぬ ∴ ★再利用率を実測で刷る★
#       (a) inode が変はるは当然 ∴ 説を立てず ★尺を検めるのみ★
#       (c) ★帯には「掃きの前の inode」が無い★ ⇒ 尺が立つても ★遡つては使へぬ★
#   ★見込み（走る前に便で刷つた）★ inode: R 1.00／T 0.00／A 0.00／C 0.00
#                                   ctime: R 1.00／T 1.00／A 1.00／C 0.00
#                                   ★inode 再利用率 0.30★
#   ★git は一度も実行せぬ・共有 /mnt/c は stat すらせぬ・書込は scratch のみ★
import os, random, subprocess, datetime, shutil, time

D    = "scratch/ashigaru-third-2-fa06a3a1"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o126_inode_%s.txt" % (D, TS)
TREE = os.path.join(D, "o126_tree")
DIR  = os.path.join(TREE, "logs", "refs", "heads")
N    = 2000
PRE  = ["iincho","karo-main","karo-third","gunshi","ashigaru","shogun","commander","hermes"]

print("★見込み（走る前に便で刷つた・実測は此の下）★ inode: R1.00/T0.00/A0.00/C0.00 ／ ctime: R1.00/T1.00/A1.00/C0.00 ／ ★inode 再利用率 0.30★")

if os.path.isdir(TREE):
    shutil.rmtree(TREE)
os.makedirs(DIR)
random.seed(20260910)
names, grp = [], {}
for i in range(N):
    nm = "%s_%04d_%08x" % (PRE[i % len(PRE)], i, random.getrandbits(32))
    with open(os.path.join(DIR, nm), "w") as f:
        f.write("0"*40 + " " + "1"*40 + " a2 <a2@x> 1757300000 +0900\tcommit: %s\n" % nm)
    names.append(nm); grp[nm] = ("R","T","A","C")[i % 4]

ls    = subprocess.run(["lsattr","-d",DIR], capture_output=True, text=True)
flags = ls.stdout.split()[0] if ls.stdout.split() else "?"
fs    = subprocess.run(["stat","-f","-c","%T",DIR], capture_output=True, text=True).stdout.strip()
print("FS=%s ／ dir byte=%d ／ lsattr=%r ／ file %d 本" % (fs, os.stat(DIR).st_size, flags, len(os.listdir(DIR))))
assert len(os.listdir(DIR)) == N, "★門: file が %d 本でない ―― 止まる★" % N

def snap():
    d = {}
    for nm in names:
        st = os.stat(os.path.join(DIR, nm))
        d[nm] = (st.st_ino, st.st_ctime_ns, st.st_mtime_ns)
    return d

pre = snap()
time.sleep(1.1)                      # ★ctime の分解能に負けぬ為に 1 秒超 措く（走る前に器へ書いた）★
for nm in names:
    p = os.path.join(DIR, nm); g = grp[nm]
    if g == "R":
        body = open(p).read(); os.remove(p); open(p, "w").write(body)
    elif g == "T":
        open(p, "w").close()
    elif g == "A":
        open(p, "a").write("appended\n")
post = snap()

rows = []
res  = {}
for g in ("R","T","A","C"):
    mem = [n for n in names if grp[n] == g]
    di  = sum(1 for n in mem if pre[n][0] != post[n][0])
    dc  = sum(1 for n in mem if pre[n][1] != post[n][1])
    dm  = sum(1 for n in mem if pre[n][2] != post[n][2])
    res[g] = (len(mem), di/len(mem), dc/len(mem), dm/len(mem))
    print("%-2s 群 %4d 本: inode 変化 %.4f ／ ctime 変化 %.4f ／ mtime 変化 %.4f" % (g, len(mem), di/len(mem), dc/len(mem), dm/len(mem)))
    for n in mem:
        rows.append((g, n, pre[n][0], post[n][0], int(pre[n][0]!=post[n][0]), int(pre[n][1]!=post[n][1])))

# ── ★不利な証 (b) を数で刷る＝inode 再利用★ ──
memR  = [n for n in names if grp[n] == "R"]
reuse = sum(1 for n in memR if pre[n][0] == post[n][0])
oldset = set(pre[n][0] for n in memR)
reuse_any = sum(1 for n in memR if post[n][0] in oldset)      # 「R 群の誰かの旧番号」を貰つた数
print("★(b) inode 再利用★: 同じ番号が返つた %d/%d ＝ %.4f ／ R 群の旧番号の何れかを貰つた %d ＝ %.4f （見込 0.30）"
      % (reuse, len(memR), reuse/len(memR), reuse_any, reuse_any/len(memR)))

# ── 判定（外れる形は走る前に置いた）──
o1 = res["R"][1] < 0.90
o2 = (res["T"][1] > 0.05) or (res["C"][1] > 0.05)
o3 = res["C"][2] > 0.05
print("★外れる形①★: R の inode 変化 <0.90 → %s" % ("★當たり ⇒ 立たず★" if o1 else "落ちず"))
print("★外れる形②★: T か C の inode 変化 >0.05 → %s" % ("★當たり ⇒ 立たず★" if o2 else "落ちず"))
print("★外れる形③★: C の ctime 変化 >0.05 → %s" % ("★當たり ⇒ 測り方が壊れて居る★" if o3 else "落ちず"))
stand = (not o1) and (not o2) and (not o3)
print("★結び★: %s" % ("★尺は現に分けられる（inode＝作り直し／ctime＝触られた）★" if stand else "★立たず★"))
print("★分け方の表（実測）★ R=inode %.4f・ctime %.4f ／ T=inode %.4f・ctime %.4f ／ A=inode %.4f・ctime %.4f ／ C=inode %.4f・ctime %.4f"
      % (res["R"][1],res["R"][2],res["T"][1],res["T"][2],res["A"][1],res["A"][2],res["C"][1],res["C"][2]))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o126 群/名/前inode/後inode/inode変化/ctime変化\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, len(rows)+1))

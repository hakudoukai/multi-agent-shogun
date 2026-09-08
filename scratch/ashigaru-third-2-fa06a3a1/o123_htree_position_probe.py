#!/usr/bin/env python3
# o123 ㋐: ★dir_index(htree) が効く規模★ で「★truncate と 作り直し が 現に別の位置を作るか★」を示す。
#
# ★当て★= htree が効く dir でも ①truncate は entry を触らぬ ∴ 位置は動かぬ ／
#          ②削除→作り直しは entry を作り直す ∴ ★位置が動く★ ／
#          ③削除→(他の名を挟む)→作り直しは ★更に動く★。
# ★検め方★= 一つの dir に N=2000 本を作成順を記録しながら作り、readdir 順を前後で較べ ★移動した本数★ を数へる。
#            群は 四つ（T=truncate ／ R=削除→即 作り直し ／ R2=削除→挟み→作り直し ／ C=一指も触れぬ対照）。
# ★㋐ が立つ尺（走る前に固定）★= max(R, R2) − T ≥ 0.20。
# ★外れる形（走る前に固定・三つ）★
#   ①R と R2 が ★共に 0.10 未満★ → ★㋐ 示せず ⇒ ㋑（/mnt/c の帯へ当てる）は ★打たぬ★★
#   ②C（触らぬ群）が 0.05 を超えて動く → ★尺其の物が壊れて居る ⇒ 悉く捨てる★
#   ③門: `lsattr -d` に `I` が無い／dir の byte が 4096 のまま → ★htree が効いて居らぬ ⇒ 止まる（数を作らぬ）★
# ★見込み（実測より先に刷る）★ T 不動 0.98 ／ R 移動 0.30 ／ R2 移動 0.70 ／ C 不動 1.00
# ★不利な証（走る前に書く・三つ）★
#   (a) htree は ★名の hash★ で並ぶ ∴ ★同名で作り直せば同じ hash★ ⇒ 「動かぬ」は ★理として当然★ かも知れぬ
#       （∴ R が動かずとも ㋑-1 を否定せぬ ―― 之が起きたら ★尺が届かなんだ★ と書く）
#   (b) 材は ★素の file★ であり git が書いた reflog ではない ∴ o122 とは ★厳密には尺が揃はぬ★
#   (c) 対照樹は home(ext4)・本番の帯は /mnt/c(drvfs) ∴ ㋐ が立つても ★答を drvfs へ移せぬ★（㋑ は尺を当てるのみ）
# ★境界★ git は ★一度も実行せぬ★・共有 /mnt/c は ★一指も触れぬ★・書込は己の scratch 圏内のみ。
import os, shutil, subprocess, datetime, random

D    = "scratch/ashigaru-third-2-fa06a3a1"
TREE = os.path.join(D, "o123_tree")
DIR  = os.path.join(TREE, "logs", "refs", "heads")
N    = 2000
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o123_pos_%s.txt" % (D, TS)

print("★見込み（走る前に便で送つた・実測より先に刷る）★ T 不動 0.98 ／ R 移動 0.30 ／ R2 移動 0.70 ／ C 不動 1.00 ―― ★実測はこの下★")

if os.path.isdir(TREE):
    shutil.rmtree(TREE)
os.makedirs(DIR)

# ── ① 作成順を記録しながら N 本作る（名は reflog の形に似せる・★素の file★）──
random.seed(20260908)
PRE = ["iincho", "karo-main", "karo-third", "gunshi", "ashigaru", "shogun", "commander", "hermes"]
created = []
for i in range(N):
    nm = "%s_%04d_%08x" % (PRE[i % len(PRE)], i, random.getrandbits(32))
    with open(os.path.join(DIR, nm), "w") as f:
        f.write("0"*40 + " " + "1"*40 + " a2 <a2@x> 1 +0900\tbranch: o123\n")
    created.append(nm)
OURS = set(created)
assert len(OURS) == N, "★門: 名が重なつた ―― 止まる★"

# ── ② 門（★htree が効いて居るか★・受入の要）──
ls = subprocess.run(["lsattr", "-d", DIR], capture_output=True, text=True)
flags = ls.stdout.split()[0] if ls.stdout.strip() else "(取れず)"
dbyte = os.stat(DIR).st_size
print("樹の FS = %s ／ dir の byte = %d ／ lsattr = %r" % (
    subprocess.run(["stat","-f","-c","%T",DIR],capture_output=True,text=True).stdout.strip(), dbyte, flags))
made = [e.name for e in os.scandir(DIR) if e.is_file()]
extra = sorted(set(made) - OURS)
assert len(made) == N and not extra, "★門: dir の file が %d 本でない（余り %r）―― 止まる★" % (N, extra[:5])
assert "I" in flags, "★門: lsattr に I 無し＝dir_index が効いて居らぬ ―― 止まる（数を作らぬ）★"
assert dbyte > 4096, "★門: dir の byte が %d ＝一塊のまま ―― 止まる★" % dbyte

def readdir():
    return [e.name for e in os.scandir(DIR) if e.is_file() and e.name in OURS]

before = readdir()
pos0 = {n: i for i, n in enumerate(before)}
assert len(before) == N, "★門: readdir が %d 本 ―― 止まる★" % len(before)

# ── ③ 四群に分ける（作成順で 4 で割つた余り）──
BODY = open(os.path.join(DIR, created[0])).read()
grp = {}
for i, nm in enumerate(created):
    grp[nm] = ("T", "R", "R2", "C")[i % 4]

fillers = []
for nm in created:
    p = os.path.join(DIR, nm)
    g = grp[nm]
    if g == "T":                       # 中身のみ 0（entry は触らぬ）
        open(p, "w").close()
    elif g == "R":                     # 削除 → 即 作り直し
        os.remove(p)
        with open(p, "w") as f:
            f.write(BODY)
    elif g == "R2":                    # 削除 → 別の名を挟む → 作り直し
        os.remove(p)
        fn = os.path.join(DIR, "zzfill_%s" % nm)
        with open(fn, "w") as f:
            f.write(BODY)
        fillers.append(fn)
        with open(p, "w") as f:
            f.write(BODY)
for fn in fillers:                     # 挟んだ物は ★母数から除く★（走る前に宣言した）
    os.remove(fn)

after = readdir()
assert len(after) == N, "★門: 処置の後 readdir が %d 本 ―― 止まる★" % len(after)
pos1 = {n: i for i, n in enumerate(after)}

# ── ④ 群ごとの移動本数 ──
res = {}
for g in ("T", "R", "R2", "C"):
    ns = [n for n in created if grp[n] == g]
    mv = sum(1 for n in ns if pos0[n] != pos1[n])
    res[g] = (mv, len(ns), mv / len(ns))
    print("%-2s 群 %4d 本: ★動いた %4d ＝ %.4f★" % (g, len(ns), mv, mv / len(ns)))

gap = max(res["R"][2], res["R2"][2]) - res["T"][2]
print("★㋐ の尺★: max(R,R2) − T ＝ %.4f （立つ閾 ≥ 0.20）→ %s" % (
    gap, "★㋐ 立つ★" if gap >= 0.20 else "★㋐ 立たず★"))
print("★外れる形①★: R と R2 が共に <0.10 → %s" % (
    "★當たり ⇒ ㋑ は打たぬ★" if (res["R"][2] < 0.10 and res["R2"][2] < 0.10) else "落ちず"))
print("★外れる形②★: C が >0.05 動く → %s" % (
    "★當たり ⇒ 悉く捨てる★" if res["C"][2] > 0.05 else "落ちず"))
print("参考（宣言して居らぬ）: 前後の readdir が同一順か: %s" % ("同一" if before == after else "違ふ"))

with open(OUT, "w") as f:
    f.write("# o123 %d 本（名／群／作成順／前 readdir 位置／後 readdir 位置／動いたか）\n" % N)
    for i, n in enumerate(created):
        f.write("\t".join([n, grp[n], str(i), str(pos0[n]), str(pos1[n]),
                           "動" if pos0[n] != pos1[n] else "-"]) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, N + 1))

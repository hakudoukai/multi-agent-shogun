#!/usr/bin/env python3
# o122: 疑ひ(b)「drvfs が我らの書込を readdir 順に映さぬ」を ★ext4(home) の対照樹★ で分ける。
#   ★走る前に便で申した四つ揃へ（msg_20260908_1454xx 六通・一字も動かさず写す）★
#   ①当て = ext4 の対照樹でも readdir 順は ★作成順を映さず★・★名の辞書順に近く出る★
#            ∴ /mnt/c で見た「名の順に近い」は ★drvfs 固有に非ず★＝㋐の証にならぬ。
#     ★第二の当て（別に宣言する）★ = truncate(中身のみ) では readdir 位置は ★動かぬ★・
#            削除→再作成では ★動く★。（家老の条＝走は束ね・宣言は分けよ）
#   ②検め方 = home 配下・当席 scratch 圏内に ★新たに樹を作る★（o110 の樹は中身が判らぬゆゑ尺を揃へる）。
#            ref 200 本を ★作成順を記録しながら★ 作り、readdir 順と (ア)作成順 (イ)名の辞書順 の ★逆転率★。
#            半数を truncate・半数を削除→再作成し ★位置の移動本数★ を数へる。
#   ③外れる形（走る前に固定）= (ア)<0.05 ⇒ 第一の当て落ち／(イ)>0.20 ⇒ 当て落ち／
#            truncate 群の ★2 割超★ が動けば ⇒ 第二の当て落ち。
#   ④不利な証 = (a) 本数が少ないと dir_index が効かず線形 dir が作成順に見える ⇒ ★効いて居るかを同じ走で刷る★
#                (b) 当ては ★立つ側が弱い★（「映さぬ」は色々な因で起こる）
#                (c) 連番名は作成順と相関 ⇒ ★名を乱した群も併せ作る★
#   ★見込み（実測より先に刷る）★ = (ア)0.35・(イ)0.05 以下・truncate 群 不動 0.95・再作成群 移動 0.80
#   ★門★ = 作つた本数 200 を assert・合はねば ★止まる★（前弾で門が己を止めた 其の形を己で継ぐ）
#   ★境界★ = git は ★対照樹でのみ★ 実行・共有 /mnt/c は ★一指も触れぬ★・書込は己の scratch 圏内のみ。
#   ★★走 1 は 己の門で止まつた（数を一つも作らず・走 1 費消）★★
#     止まつた所 = reflog file が ★201★ ―― 我らの 200 に ★材の枝 `base` の reflog 1 本★ が混ざつた。
#     ★因は前弾と違ふ★: o121 は「★照らす数が 別の母数の数★」／本弾は「★母数に 己が作つた材が混ざつた★」。
#     ⇒ 家老が条に鋳た = ★★己で材を作つた時は ―― ★材そのものを 母数から除く宣言★ を ★走る前に★ 置け★★
#       （＝『手近な材を使はず 己で材を作つて尺を握る』の ★代償★ ―― ★握つた手そのものが 数に混ざる★）。
#   ★直し（検め方の直しであり ★尺の変更ではない★・走る前に便で申した）★
#     ① 門 = 我らの 200 本が悉く在り・dir の file は ★200 + 材 1 = 201★
#     ② 測るは ★我らの 200 本のみ★ ―― readdir 順から ★材 `base` を除く★（o118『族を宣言して除く』と同じ形）
#     ③ 外れる形・見込みは ★据置★（(ア)0.35 ／ (イ)0.05 以下 ／ 不動 0.95 ／ 移動 0.80）
import os, random, shutil, subprocess, datetime

D    = "scratch/ashigaru-third-2-fa06a3a1"
TREE = os.path.join(D, "o122_tree")
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o122_order_%s.txt" % (D, TS)
N_SEQ, N_RND = 100, 100

print("★見込み（走る前に便で送つた・実測より先に刷る）★ (ア)0.35 ／ (イ)0.05 以下 ／ truncate 群 不動 0.95 ／ 再作成群 移動 0.80 ―― ★実測はこの下★")

def git(*a):
    return subprocess.run(("git",)+a, cwd=TREE, capture_output=True, text=True,
                          env=dict(os.environ, GIT_AUTHOR_NAME="a2", GIT_AUTHOR_EMAIL="a2@local",
                                   GIT_COMMITTER_NAME="a2", GIT_COMMITTER_EMAIL="a2@local"))

# ── ① 材を己で作る（手近な材を使はぬ）──
if os.path.isdir(TREE):
    shutil.rmtree(TREE)
os.makedirs(TREE)
r = git("init", "-q", "-b", "base"); assert r.returncode == 0, r.stderr
git("config", "core.logAllRefUpdates", "true")
with open(os.path.join(TREE, "seed.txt"), "w", encoding="utf-8") as f:
    f.write("o122\n")
git("add", "seed.txt"); r = git("commit", "-q", "-m", "seed"); assert r.returncode == 0, r.stderr
base = git("rev-parse", "HEAD").stdout.strip()

rnd = random.Random(20260908)
names, created = [], []
for i in range(N_SEQ):                                  # 連番群（名の順＝作成順）
    names.append("seq%04d" % (i + 1))
pool = ["rnd_%08x" % rnd.getrandbits(32) for _ in range(N_RND)]   # 乱名群（名の順≠作成順）
names += pool
for i, nm in enumerate(names):                          # ★作成順を記録しながら★
    r = git("update-ref", "refs/heads/" + nm, base)
    assert r.returncode == 0, (nm, r.stderr)
    created.append(nm)

LOGD = os.path.join(TREE, ".git", "logs", "refs", "heads")
OURS = set(created)                                     # ★材 `base` は此処に入らぬ★
made = [e.name for e in os.scandir(LOGD) if e.is_file()]
extra = sorted(set(made) - OURS)                        # ★材そのもの（走る前に除くと宣言した）★
print("作つた本数 %d ／ reflog file %d ／ ★材（母数から除く）%d 本 %s★" % (len(created), len(made), len(extra), extra))
assert len(created) == 200, "★門: 作つた本数が 200 でない（%d）―― 止まる★" % len(created)
assert OURS <= set(made), "★門: 我らの 200 本が dir に揃はぬ ―― 止まる★"
assert len(made) == 201 and extra == ["base"], "★門: dir の file が 200+材 1 でない（%d / %s）―― 止まる★" % (len(made), extra)

# ── ② 樹の素性（不利な証 (a) を同じ走で刷る）──
fs = subprocess.run(["stat", "-f", "-c", "%T", TREE], capture_output=True, text=True).stdout.strip()
ls = subprocess.run(["lsattr", "-d", LOGD], capture_output=True, text=True)
print("樹の FS = %s ／ dir の byte = %d ／ lsattr = %r（`I` が dir_index の印）"
      % (fs, os.stat(LOGD).st_size, (ls.stdout.strip() or ls.stderr.strip())[:60]))

def readdir():                                          # ★sort せぬ＝readdir の順★・★材は除く（宣言済）★
    return [e.name for e in os.scandir(LOGD) if e.is_file() and e.name in OURS]

def inv(seq, rank):
    a = [rank[n] for n in seq]
    return sum(1 for x in range(len(a)) for y in range(x + 1, len(a)) if a[x] > a[y])

walk0 = readdir()
tot = len(walk0) * (len(walk0) - 1) // 2
r_created = {n: i for i, n in enumerate(created)}
r_name    = {n: i for i, n in enumerate(sorted(created))}
ia, ib = inv(walk0, r_created), inv(walk0, r_name)
print("(ア) readdir 順 対 ★作成順★     逆転 %5d / 全対 %5d ＝ ★%.4f★（見込 0.35）" % (ia, tot, ia / tot))
print("(イ) readdir 順 対 ★名の辞書順★ 逆転 %5d / 全対 %5d ＝ ★%.4f★（見込 0.05 以下）" % (ib, tot, ib / tot))
for lab, sub in (("連番群", created[:N_SEQ]), ("乱名群", created[N_SEQ:])):
    w = [n for n in walk0 if n in set(sub)]
    t2 = len(w) * (len(w) - 1) // 2
    ra = {n: i for i, n in enumerate([n for n in created if n in set(sub)])}
    rb = {n: i for i, n in enumerate(sorted(sub))}
    print("   %s %3d 本: 対作成順 %.4f ／ 対名順 %.4f（★連番群は 作成順＝名順★）" % (lab, len(w), inv(w, ra) / t2, inv(w, rb) / t2))
print("★③外れる形の判定★: (ア)<0.05 → %s ／ (イ)>0.20 → %s"
      % ("★第一の当て落ち★" if ia / tot < 0.05 else "落ちず", "★当て落ち★" if ib / tot > 0.20 else "落ちず"))

# ── ③ 第二の尺（別に宣言した）＝ truncate と 削除→再作成 ──
pos0 = {n: i for i, n in enumerate(walk0)}
trunc, recre = [], []
for g, sub in (("seq", created[:N_SEQ]), ("rnd", created[N_SEQ:])):
    for i, n in enumerate(sub):                          # ★各群の中で 偶数番/奇数番に分ける★
        (trunc if i % 2 == 0 else recre).append(n)
for n in trunc:                                          # 中身のみ 0（entry は触らぬ筈）
    with open(os.path.join(LOGD, n), "w", encoding="utf-8") as f:
        pass
for n in recre:                                          # 削除→再作成（entry を作り直す）
    p = os.path.join(LOGD, n)
    body = open(p, encoding="utf-8").read()
    os.remove(p)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
walk1 = readdir()
pos1 = {n: i for i, n in enumerate(walk1)}
assert len(walk1) == 200, "★門: 後の readdir（材を除く）が 200 本でない ―― 止まる★"
mt = sum(1 for n in trunc if pos1[n] != pos0[n])
mr = sum(1 for n in recre if pos1[n] != pos0[n])
print("truncate 群 %d 本: ★動いた %d（不動 %.4f・見込 0.95）★ ／ 削除→再作成 群 %d 本: ★動いた %.4f（見込 0.80）★"
      % (len(trunc), mt, 1 - mt / len(trunc), len(recre), mr / len(recre)))
print("★第二の外れる形★: truncate 群の 2 割超が動く → %s" % ("★第二の当て落ち★" if mt / len(trunc) > 0.20 else "落ちず"))
print("   後の readdir 対 作成順 %.4f ／ 対名順 %.4f（★参考＝宣言して居らぬ★）"
      % (inv(walk1, r_created) / tot, inv(walk1, r_name) / tot))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o122 対照樹 200 本（名／群／作成順／前 readdir 位置／後 readdir 位置／処置）\n")
    for n in created:
        f.write("\t".join([n, "連番" if n.startswith("seq") else "乱名", str(r_created[n]),
                           str(pos0[n]), str(pos1[n]), "truncate" if n in set(trunc) else "再作成"]) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, len(created) + 1))

#!/usr/bin/env python3
# o120: o119 で ★己が名指した疵★ を ★己で落としに行く★ 弾。
#   ★当て★=掃く行為 其の物が dir の entry を書き直した ⇒ ★同じ dir に両群が居る所★ で
#          帯(掃かれた)の file は readdir 順で ★対照より後ろ★ に寄る。
#   ★検め方★=両群を含む dir に限り 同 dir 内の ★帯×対照 の対★ で「帯が後」の率 R を数へ、
#          ★dir ごとの率も必ず刷る★(受入④・全体の R だけでは大 dir に引かれる)。
#   ★見込み R=0.70 を 実測より先に刷る★(受入①の形・o119 と同じ)。
#   ★外れる形(走る前に便で約した)★=R<=0.55 又は 正規化順位の平均差<+0.10 又は 過半の dir が 0.5 未満
#          ⇒ ★作り変へ説を降ろす★(己の残した二説の片方を 己で落とす)。
#   ★『立つ側』の判定は置かぬ★(受入②)。理=④(a)の交絡 ―― R が高く出ても
#          『掃いたから後ろ』と『新しいから後ろ』を分けられぬ ∴ 言へるは『落ちなかつた』迄。
#          閾を置いて『立つた』と書けば ★交絡を跨いで断ずる★ 事に成る。
#   ★不利な証(四つ・結びにも再掲する)★
#     (a)★最も重い★ 順位は生年と交絡 ∴ 立つても『掃いた事』の証に成らぬ＝★落とす事しか出来ぬ弾★
#     (b)/mnt/c は drvfs ゆゑ readdir 順を FS が決め ★我らの書込を映さぬかも★ ⇒ ★立たなんだ時の第一の疑ひ★
#     (c)帯の㋑1(o118) には dir 訪問順の功も混ざる  (d)866 対は 16 dir に偏在
#   ★母数(16dir/866対)は 本走の前に 調べる走行で当たつた ―― 打ち切り条を先に書く為であり
#     ★答の統計(R)には一切触れて居らぬ★(家老の条=『先に測つた』が覗き見か設計かは書かねば区別が付かぬ)。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, io, os

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o120_dirpos_%s.txt" % (D, TS)

print("★見込み（走る前に便で送つた・実測より先に刷る）★ R=0.70（帯が後ろ寄り）／母数 16 dir・866 対 ―― ★実測はこの下★")
print("★『立つ側』の判定は置かぬ★（理＝(a)の交絡・結びに再掲）")

# ── ① 母数 ──
rows = []
for ln in io.open(L112, encoding="utf-8"):
    if not ln.startswith("#"):
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 4:
            rows.append(c)
assert len(rows) == 345, "母数 %d" % len(rows)
grp = {c[1]: c[0] for c in rows}

def is_symref_family(n):
    return n.startswith("refs/") and n.rsplit("/", 1)[-1] == "HEAD"

band = [n for n in grp if grp[n] in ("空", "保つ") and not is_symref_family(n)]
ctrl = [n for n in grp if grp[n] == "別刻"        and not is_symref_family(n)]
print("母数(引継) %d ／ 帯(除外後) %d ／ 対照(除外後) %d" % (len(rows), len(band), len(ctrl)))

# ── ② readdir 順（sort せぬ）――dir ごとの entry 位置を持つ ──
pos = {}
nwalk = 0
def rec(d, rel):
    global nwalk
    try:
        ents = list(os.scandir(d))          # ★sort せぬ＝readdir の順★
    except OSError:
        return
    for i, e in enumerate(ents):
        r = rel + "/" + e.name if rel else e.name
        if e.is_dir(follow_symlinks=False):
            rec(e.path, r)
        else:
            pos[r] = i                       # ★同じ dir の中での位置★
            nwalk += 1
rec(os.path.join(GIT, "logs", "refs"), "refs")
print("readdir 走査 %d file（dir 内の位置のみ用ゐる）" % nwalk)

def dirof(n): return n.rsplit("/", 1)[0]

# ── ③ 両群を含む dir ──
db, dc = {}, {}
for n in band: db.setdefault(dirof(n), []).append(n)
for n in ctrl: dc.setdefault(dirof(n), []).append(n)
both = sorted(set(db) & set(dc))
nb = sum(len(db[x]) for x in both); nc = sum(len(dc[x]) for x in both)
npair = sum(len(db[x]) * len(dc[x]) for x in both)
print("★両群を含む dir %d ／ 其の中の 帯 %d ／ 対照 %d ／ 対 %d★" % (len(both), nb, nc, npair))
assert len(both) == 16 and npair == 866 and nb == 128 and nc == 96, "母数が動いた（帯dir/対照dir/対を検めよ）"

# ── ④ 対ごとの『帯が後』／dir ごとの率 ──
lost = [n for n in band + ctrl if n not in pos]
later = same = 0
lines = []
half_lt = 0
for x in both:
    b = [n for n in db[x] if n in pos]; c = [n for n in dc[x] if n in pos]
    la = sa = 0
    for u in b:
        for v in c:
            if pos[u] > pos[v]: la += 1
            elif pos[u] == pos[v]: sa += 1
    tot = len(b) * len(c)
    r = (la / tot) if tot else float("nan")
    if tot and r < 0.5: half_lt += 1
    later += la; same += sa
    lines.append((x, len(b), len(c), tot, la, r))
    print("   %-40s 帯%3d 対照%3d 対%4d 帯が後 %4d ＝ %6.2f%%" % (x, len(b), len(c), tot, la, 100.0 * r))
tot_all = sum(l[3] for l in lines)
R = later / tot_all
print("★全体★ 対 %d ／ 帯が後 %d ＝ ★R=%.4f（%.2f%%）★ ／ 同位置 %d ／ 位置の取れぬ %d %s"
      % (tot_all, later, R, 100.0 * R, same, len(lost), lost[:4]))
print("   ［見込 0.70 ／ 差 %+.4f］" % (R - 0.70))
print("★dir ごと★ 率が 0.5 未満の dir %d / %d（過半＝%d 以上で降ろす）" % (half_lt, len(lines), len(lines) // 2 + 1))

# ── ⑤ 正規化順位の平均差（dir 内で 帯+対照 のみを順に並べ 0..1）──
sb = sc = 0.0; cb = cc = 0
for x in both:
    fs = sorted([n for n in db[x] + dc[x] if n in pos], key=lambda n: pos[n])
    m = len(fs)
    for i, n in enumerate(fs):
        v = i / (m - 1) if m > 1 else 0.5
        if grp[n] == "別刻": sc += v; cc += 1
        else:               sb += v; cb += 1
mb = sb / cb; mc = sc / cc
print("★正規化順位の平均★ 帯 %.4f（%d 本）／ 対照 %.4f（%d 本）／ ★差 %+.4f★［閾 +0.10］" % (mb, cb, mc, cc, mb - mc))

# ── ⑥ 三択語（走る前に器へ入れた）──
drop = (R <= 0.55) or ((mb - mc) < 0.10) or (half_lt >= len(lines) // 2 + 1)
print("★三択語★ ①降ろす ②保留の儘 ③濃くする ―― 本弾は ★%s★" % ("①降ろす（外れる形に当たつた）" if drop
      else "②保留の儘（外れる形に当たらず・★併し『立つた』とは書かぬ＝(a)の交絡★）"))

# ── ⑦ 結び（受入①③・走る前に書いた字を そのまま刷る）──
print("★結び(a)★ 順位は生年と交絡 ―― 立つても『掃いた事』の証に成らぬ＝★落とす事しか出来ぬ弾★（二度目の勝ち目無き賭）")
print("★結び(b)★ 立たなんだ時の ★第一の疑ひ★＝/mnt/c は drvfs ゆゑ readdir 順を FS が決め ★我らの書込を映さぬ★ 事")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o120 両群を含む dir %d／対 %d（dir／帯本数／対照本数／対／帯が後／率）\n" % (len(both), tot_all))
    for x, a, b2, t, la, r in lines:
        f.write("\t".join([x, str(a), str(b2), str(t), str(la), "%.4f" % r]) + "\n")
    f.write("# 対ごと（帯／対照／帯の位置／対照の位置／帯が後か）\n")
    for x in both:
        for u in sorted([n for n in db[x] if n in pos]):
            for v in sorted([n for n in dc[x] if n in pos]):
                f.write("\t".join([u, v, str(pos[u]), str(pos[v]), "後" if pos[u] > pos[v] else "前"]) + "\n")
print("名の一覧: %s" % OUT)

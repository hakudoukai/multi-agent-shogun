#!/usr/bin/env python3
# o121: 第九の向き ★㋑-1（entry の作り直し）★ を dir の mtime で 独立に裏取る。
#   ★当て★=帯 200 本を含む各 dir の mtime は ★掃きの帯より前★ ⇒ entry は作り直されて居らぬ。
#          ★見込み＝帯より前の dir が 0.80★（実測より先に刷る）。
#   ★検め方★=帯を含む dir の mtime を ★前／帯の中／後★ に分け ★dir ごとに刷る★。
#            ★走る前に足した一つ＝対照（帯を含まぬ dir）の分布も刷る★（『前が多いのは樹一般の性質』を分ける為）。
#   ★外れる形★=帯を含む dir の ★過半★ が『中』か『後』なら ★当て落ち★。
#   ★不利な証★=(a)drvfs の dir mtime が我らの書込を映さぬかも ∴ ★立つても落ちても FS を跨げぬ★
#              (b)後の書込で上書きされ得る ―― ★誤りの向きは「後」へ偏る側のみ・「前」へ偏る誤りは原理として無い★
#                 ∴ ★『前』が多く出たなら 誤りの向きに ★逆らつて★ 出た数＝強い★（家老の条）
#              (c)`logs` dir が帯の 20ms 前なるは §18-4 で既知＝★新しさに非ず★
#              (d)★立つ側は弱い＝㋐（掃いた者が readdir を辿つた）を落とさぬ★
#   ★受入★=④(b)(d)を結びにも／dir ごとを必ず刷れ／★㋑-2 が落ちなかつたのは 弱いからでなく ★試が届かぬから★ と紙に★
#   ★条(百六十九)★=測りの誤りが一方向にしか効かぬ時 ―― 其の逆向きに出た数は ★強い★。
#   ★走 1 は 己の門で止まつた（数を作らず）★=幅 0.6511 秒 対 assert 0.6415 ―― 因は ★樹が動いた事に非ず★
#     ★§18-4 の 0.6415 は ★空 112 本★ の幅であり 器は ★空+保つ 198 本★ に当てて居た＝★照らす数が 別の母数の数★★。
#     ★走 2 の直し（走る前に便で申した）★=①門を ★同じ母数へ★（空 112・幅 0.641497±0.0010・★母数 112 も assert★）
#       ②分類に使ふ帯は ★空+保つの取れた 198★ から取り 幅と ★取れぬ 2 本★ を ★数として刷る（隠さぬ）★
#       ③★尺は一字も変へぬ★（見込 0.80・過半で落ちる・三択語）＝★検め方の直し であり 尺の変更ではない★。
#   ★file を讀まぬ（dir と file の stat のみ）。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, os

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o121_dirmtime_%s.txt" % (D, TS)

def hhmm(ns):
    return datetime.datetime.fromtimestamp(ns / 1e9).strftime("%m-%d %H:%M:%S.%f")

print("★見込み（走る前に便で送つた・実測より先に刷る）★ 帯を含む dir のうち ★『前』が 0.80★ ―― ★実測はこの下★")
print("★『立つ』側の判定は置かぬ★（(d)の限り ―― 立つても ㋐ は落ちぬ。結びに再掲）")

# ── ① 母数 ──
rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)
assert len(rows) == 345, "母数 %d（345 を前提として居る）" % len(rows)
grp  = {c[1]: c[0] for c in rows}
band = [c[1] for c in rows if c[0] in ("空", "保つ")]      # 帯 200
ctrl = [c[1] for c in rows if c[0] == "別刻"]              # 別刻 145
print("母数(引継) %d ／ 帯 %d ／ 別刻 %d" % (len(rows), len(band), len(ctrl)))

# ── ② 掃きの帯を 器が己で測り直す（§18-4 と突き合はせる）──
mt = {}
for nm in band:
    try:
        mt[nm] = os.stat(os.path.join(GIT, "logs", nm)).st_mtime_ns
    except OSError:
        pass
miss = [n for n in band if n not in mt]
# ★門＝§18-4 と ★同じ母数（空 112）★ に掛ける★
kara = {n: v for n, v in mt.items() if grp[n] == "空"}
wk = (max(kara.values()) - min(kara.values())) / 1e9
print("★門（§18-4 と同じ母数）★ 空 %d 本 ／ 幅 %.6f 秒" % (len(kara), wk))
assert len(kara) == 112, "★空の母数が 112 でない（%d）―― 止まる★" % len(kara)
assert abs(wk - 0.641497) <= 0.0010, "★空の幅が §18-4 と違ふ（%.6f）―― 止まる★" % wk
# ★分類に使ふ帯は 空+保つ の ★取れた分★ から取る（数として刷る・隠さぬ）★
T0, T1 = min(mt.values()), max(mt.values())
w = (T1 - T0) / 1e9
print("掃きの帯（分類に使ふ）: %s 〜 %s ／ 幅 %.4f 秒 ／ 取れた %d ／ ★取れぬ %d 本 %s★"
      % (hhmm(T0), hhmm(T1), w, len(mt), len(miss), miss))

# ── ③ dir を集める（帯を含む dir ／ 含まぬ dir）──
band_dirs, ctrl_dirs = {}, {}
for nm in band:
    band_dirs.setdefault(os.path.dirname(nm), []).append(nm)
allo = set()
for r, ds, fs in os.walk(os.path.join(GIT, "logs", "refs")):
    rel = "refs" + r[len(os.path.join(GIT, "logs", "refs")):]
    allo.add(rel)
for d in sorted(allo):
    if d not in band_dirs:
        ctrl_dirs[d] = [n for n in ctrl if os.path.dirname(n) == d]
print("dir 総数（logs/refs 以下）%d ／ 帯を含む dir %d ／ 含まぬ dir %d"
      % (len(allo), len(band_dirs), len(ctrl_dirs)))

# ── ④ 分類 ──
def cls(d):
    try:
        m = os.stat(os.path.join(GIT, "logs", d)).st_mtime_ns
    except OSError:
        return None, None
    return m, ("前" if m < T0 else ("中" if m <= T1 else "後"))

def tally(dd, label, show):
    cnt = {"前": 0, "中": 0, "後": 0}
    lines = []
    for d in sorted(dd):
        m, c = cls(d)
        if c is None:
            continue
        cnt[c] += 1
        lines.append((d, len(dd[d]), m, c))
    n = sum(cnt.values())
    print("★%s★ dir %d ―― 前 %d ／ 中 %d ／ 後 %d ＝ 前の率 %.4f"
          % (label, n, cnt["前"], cnt["中"], cnt["後"], (cnt["前"] / n) if n else 0.0))
    if show:
        for d, k, m, c in lines:
            print("   %-34s 本%3d  %s  ★%s★" % (d, k, hhmm(m), c))
    return cnt, n, lines

bc, bn, blines = tally(band_dirs, "帯を含む dir", True)
cc, cn, clines = tally(ctrl_dirs, "帯を含まぬ dir（対照・走る前に足した）", True)

# ── ⑤ 宣言した尺 ──
half = bn // 2 + 1
bad  = bc["中"] + bc["後"]
print("★外れる形の判定★ 『中』か『後』が %d ／ 過半 %d ―― %s"
      % (bad, half, "★当て落ち★" if bad >= half else "★落ちず★"))
print("   ［見込 0.80 ／ 実測 %.4f ／ 差 %+.4f］" % ((bc["前"]/bn) if bn else 0, ((bc["前"]/bn) if bn else 0) - 0.80))
if cn:
    print("★対照との差★ 帯 dir の前の率 %.4f ／ 対照 %.4f ／ ★差 %+.4f★"
          % (bc["前"]/bn, cc["前"]/cn, bc["前"]/bn - cc["前"]/cn))
print("★三択語★ ①降ろす ②保留の儘 ③濃くする ―― 本弾は ★%s★"
      % ("①降ろす（外れる形に當たつた）" if bad >= half else "②保留の儘（落ちず・併し (d) ゆゑ『立つた』とは書かぬ）"))
print("★結び(b)★ 誤りの向きは ★『後』へ偏る側のみ★ ∴ ★『前』は 誤りに逆らつて出た数★（家老の条・弱い証と強い証を分ける）")
print("★結び(d)★ 立つ側は弱い ―― ★㋐（掃いた者が readdir を辿つた）を落とさぬ★")
print("★㋑-2（truncate）が落ちなかつたのは ★弱いから★ ではなく ★試が届かぬから★★")

# ── ⑥ 名の一覧 ──
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o121 dir の mtime（帯 %s 〜 %s）\n" % (hhmm(T0), hhmm(T1)))
    for lab, lines in (("帯", blines), ("対照", clines)):
        for d, k, m, c in lines:
            f.write("\t".join([lab, d, str(k), str(m), hhmm(m), c]) + "\n")
print("名の一覧: %s (%d 行)" % (OUT, len(blines) + len(clines) + 1))

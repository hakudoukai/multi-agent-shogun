#!/usr/bin/env python3
# o136: 順 10（order134）＝★母の減り方★ ―― o112 の 345 本を ★今★ 当たり、幾つ・どの層から減つたかを数へる。
#   ★走る前に一つ決めた定め（同じ手番で ★便にも出した★・msg_20260909_045448_b7e9d133）★
#     ①★「帳が在る」と「ref が在る」は 別語★ ―― 帳=$GIT/logs/<名> が讀める／ref=loose($GIT/<名>) か packed-refs の行。
#        ★両方 数へ 別々に刷る★（片方だけで「消えた」と言はぬ）。
#     ②★三つ止まり★= ㋐幾つ減つた ㋑どの層（空 112／保つ 88／別の刻 145）から ㋒★何時より後か（範で挟む）★。
#        範の左端 = ★o116 の生出力の mtime（2026-09-08 12:49・帯 200 本が悉く測れた刻）★／右端 = 本走の刻。
#     ③★対照★= home 樹（/home/hakudoukai/multi-agent-shogun/.git）で同じ器を鳴らす（陽性=実在の名／陰性=贋の名）。
#   ★当ての向き（★便に先に出した★）★= 減りは `refs/remotes/origin/` に偏り ★2 本では止まらぬ★。外れたら「外れた」と書く。
#   ★測れぬと先に申した物★= ㋐何時 消えたかの ★点★（file が無い以上 出ぬ・出せるのは範のみ）㋑★誰が消したか★（出ぬ）。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import collections, datetime, os, sys, time

GIT  = "/mnt/c/DentalBI/.git"
HOME = "/home/hakudoukai/multi-agent-shogun/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
O116 = D + "/o116_order_20260908_124938.txt"      # 帯 200 本が悉く測れた走の生出力
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o136_shrink_%s.txt" % (D, TS)

def packed_set(root):
    s = set()
    p = os.path.join(root, "packed-refs")
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            for ln in f:
                if ln.startswith(("#", "^")):
                    continue
                c = ln.split()
                if len(c) >= 2:
                    s.add(c[1])
    except OSError:
        pass
    return s

def probe(root, names, pk):
    """各名に就き ★帳★ と ★ref★ を 別々に当てる"""
    r = {}
    for n in names:
        try:
            os.stat(os.path.join(root, "logs", n)); log = True
        except OSError:
            log = False
        try:
            os.stat(os.path.join(root, n)); loose = True
        except OSError:
            loose = False
        r[n] = (log, loose, n in pk)
    return r

# ── ① 対照（数より先に鳴らす）──
hp = packed_set(HOME)
real = sorted(hp)[:20]
if not real:
    print("ABORT reason=control_has_no_packed_refs"); sys.exit(3)
fake = ["refs/heads/zzz-o136-nonexistent-%02d" % i for i in range(20)]
cr = probe(HOME, real, hp); cf = probe(HOME, fake, hp)
pos = sum(1 for n in real if cr[n][1] or cr[n][2])       # 実在の名 ⇒ ref 在り
neg = sum(1 for n in fake if not (cf[n][1] or cf[n][2])) # 贋の名   ⇒ ref 無し
print("対照 陽性(home の実在 %d 本 → ref 在り %d) ／ 陰性(贋の名 %d 本 → ref 無し %d)" % (
      len(real), pos, len(fake), neg))
if pos != len(real) or neg != len(fake):
    print("ABORT reason=control_did_not_stand"); sys.exit(3)
print("対照 2/2 立つ")

# ── ② 母（o112 の一覧 345 本・層は其の儘）──
rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)
assert len(rows) == 345, "母数 %d（345 を前提として居る）" % len(rows)
grp   = {c[1]: c[0] for c in rows}
names = [c[1] for c in rows]
lay   = collections.Counter(grp[n] for n in names)
print("★母★ o112 の一覧 %d 本（%s）" % (len(names), " ／ ".join("%s %d" % (k, v) for k, v in sorted(lay.items()))))

# ── ③ 今 当たる ──
pk = packed_set(GIT)
now = probe(GIT, names, pk)
gone_log = [n for n in names if not now[n][0]]
gone_ref = [n for n in names if not (now[n][1] or now[n][2])]
both     = [n for n in gone_log if n in set(gone_ref)]
print("★㋐ 幾つ減つた★ 帳(logs)が無い %d 本 ／ ref(loose|packed)が無い %d 本 ／ 両方無い %d 本（母 %d）" % (
      len(gone_log), len(gone_ref), len(both), len(names)))
print("   ※ 『帳が無い』と『ref が無い』は ★別語★ ―― 帳だけ消える事も ref だけ消える事も在り得る")

def by(lst, key):
    return " ／ ".join("%s %d" % (k, v) for k, v in sorted(collections.Counter(key(n) for n in lst).items())) or "（無し）"
print("★㋑ どの層から★ 帳が無い: %s" % by(gone_log, lambda n: grp[n]))
print("            ref が無い: %s" % by(gone_ref, lambda n: grp[n]))
def top(n):
    p = n.split("/")
    return "/".join(p[:3]) if n.startswith("refs/remotes/") else "/".join(p[:2])
print("★㋑' 何処から★ 帳が無い: %s" % by(gone_log, top))
print("            ref が無い: %s" % by(gone_ref, top))

# ── ④ ㋒ 何時より後か（★点は出ぬ・範で挟む★）──
def mt(p):
    try:
        return os.stat(p).st_mtime
    except OSError:
        return None
def j(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S") if t else "-"
left  = mt(O116)
right = datetime.datetime.now().timestamp()
pkm   = mt(os.path.join(GIT, "packed-refs"))
print("★㋒ 何時より後か（範）★ 左端 = o116 の生出力 mtime %s（帯 200 本が悉く測れた刻）" % j(left))
print("                        右端 = 本走 %s ／ 範の幅 %.2f 時間" % (j(right), (right-left)/3600.0 if left else 0))
print("   packed-refs の mtime = %s ―― %s" % (j(pkm),
      "範の中に在る（範を狭め得る）" if (left and pkm and left <= pkm <= right) else "★範の外 ∴ 範を狭められぬ★"))
print("   ★点は出ぬ★（消えた file に mtime は無い）／★誰が消したかも出ぬ★")

# ── ④' 走 2 で足した ★範を狭める二手★（家老へ申告済 msg_20260909_045644_8fb5dd12）──
print("── ★範を狭める二手（走 2 で足した）★ ──")
# 手 1: o116 の一覧で 消えた本が ★当時 packed に載つて居たか★ を讀む
o116rank = {}
try:
    with open(O116, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("#"):
                continue
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 6:
                o116rank[c[1]] = c[5]
except OSError as e:
    print("   手 1 ★讀めず★ %s" % e)
for n in gone_log:
    r = o116rank.get(n)
    print("   手 1 %s ―― o116(09-08 12:49) の packed 順 = %s ⇒ %s" % (
          n, r if r is not None else "★載らず★",
          "★当時 packed に在つた★" if (r is not None and r.isdigit() and int(r) < 10**8) else "★当時も packed に無し ∴ 此の手は効かぬ★"))
if pkm and all(o116rank.get(n, "").isdigit() for n in gone_log) and gone_log:
    print("   ⇒ ★右端を %s（packed-refs が ★最後に書かれた刻★）まで狭められる★" % j(pkm))
    print("     ★但し★ 21:04 の書きは ★最後の書き★ である ∴ 消えたのは『其の書きか ★其れ以前の書き★』＝★点ではなく なほ範★")
# 手 2: 帳(logs)の親 dir の mtime ―― file の消滅は親 dir の刻を動かす
seen = set()
for n in gone_log:
    d = os.path.dirname(os.path.join(GIT, "logs", n))
    if d in seen:
        continue
    seen.add(d)
    m = mt(d)
    print("   手 2 dir %s の mtime = %s %s" % (d.replace(GIT, "$GIT"), j(m),
          "（★範の中 ∴ 帳が消えた刻の ★上限★ を此処まで寄せられる★）" if (m and left and left <= m <= right)
          else "（★範の外 ∴ 寄せられぬ★）"))
print("   ★なほ言へぬ事★= ①点（何秒に消えたか）②誰が消したか ③一度に消えたか二度に分けてか")

# ── ④'' 走 3 で足した ★対照③＝手 2 の前提を検める★（申告 msg_20260909_050227_f1d558b9）──
#   前提=「dir の mtime は entry の ★出入り★ で動き、file の ★中身だけの書換★ では動かぬ」。
#   ★消す動詞 0 の儘★ 検める ―― 足す(陽性)と 中身書換(陰性)の二つで鳴らす。己の scratch 内のみ。
print("── ★対照③ 手 2 の前提（dir mtime は entry の出入りで動くか）★ ──")
cdir = os.path.join(D, "o136_ctl_dir")
os.makedirs(cdir, exist_ok=True)
#   ★走 4 の直し★= 走 3 は makedirs 直後と足した直後が ★同一 tick★ で等値に成り 陽性が立たなかつた。
#     ∴ ①各段の間に 1.1 秒措く ②★m0/m1/m2 を悉く刷る★（中間値を刷らなんだのが 走 3 の疵）。
m0 = os.stat(cdir).st_mtime_ns
time.sleep(1.1)
f1 = os.path.join(cdir, "ctl-%s.txt" % TS)
with open(f1, "w", encoding="utf-8") as fh:      # ★entry を 足す★
    fh.write("x")
m1 = os.stat(cdir).st_mtime_ns
time.sleep(1.1)
with open(f1, "a", encoding="utf-8") as fh:      # ★中身だけ 書換★
    fh.write("yy")
m2 = os.stat(cdir).st_mtime_ns
print("   m0=%d ／ m1=%d（差 %d ns）／ m2=%d（差 %d ns）" % (m0, m1, m1 - m0, m2, m2 - m1))
pos = m1 > m0
neg = (m2 == m1)
print("   陽性（entry を足す）: dir mtime %s ⇒ %s" % ("動いた" if pos else "★動かず★",
      "★立つ★" if pos else "★立たず★"))
print("   陰性（中身だけ書換）: dir mtime %s ⇒ %s" % ("動かず" if neg else "★動いた★",
      "★立つ★" if neg else "★立たず★"))
print("   ★此の対照の限界★= 鳴らしたのは %s（ext4）／測つた樹は %s（★drvfs＝別の fs★）"
      % (D, GIT))
print("     ∴ ★手 2 の刻は『此の fs では前提が立つ』止まり ―― 測つた樹で鳴らしては居らぬ★")
print("   ★今一つの限界★= 鳴らしたのは ★足す★ であり ★消す★ ではない（当席は消す動詞 0）"
      "―― 両方 entry の出入りではあるが ★同じ事象ではない★")
if not pos:
    print("ABORT reason=control3_positive_did_not_stand")
    sys.exit(3)

# ── ⑤ 当ての検め ──
origin_share = sum(1 for n in gone_log if n.startswith("refs/remotes/origin/"))
print("★当ての検め★ 当ては『remotes/origin に偏り 2 本では止まらぬ』であつた ⇒ 帳が無い %d 本中 origin %d 本 ＝ %s" % (
      len(gone_log), origin_share,
      "★当たり★" if (len(gone_log) > 2 and origin_share == len(gone_log)) else
      ("★半ば（偏りは当たり・本数は 2 本止まり）★" if origin_share == len(gone_log) else "★外れた★")))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o136 母 %d 本の今（組\t名\t帳\tloose\tpacked）as_of %s\n" % (len(names), TS))
    for n in names:
        a, b, c = now[n]
        f.write("\t".join([grp[n], n, "帳有" if a else "★帳無★",
                           "loose有" if b else "loose無", "packed有" if c else "packed無"]) + "\n")
print("一覧: %s" % OUT)

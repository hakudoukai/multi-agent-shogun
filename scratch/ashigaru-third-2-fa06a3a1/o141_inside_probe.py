#!/usr/bin/env python3
# o141: 順 12「★同居の内側★（prefix も階層も同じ 12 本）で 空と保つ を分けた物は何か」。
#   ★母★=`refs/heads/codex`（空 1・保つ 1）＋`refs/remotes/origin/ashigaru-third-1`（空 9・保つ 1）＝★12 本★。
#   ★使はぬ尺（先に外す）★=行数・中身の最古・中身の最新 ―― ★『空』の定めが「中身 0 行」である ∴ 循環する★。
#   ★使ふ尺 三つ★=㋐在り処(loose|packed) ㋑mtime の順 ㋒名の辞書順。
#   ★階層は族の内で一定★（codex は heads・a-third-1 は origin）∴ ★族の内では尺に成らぬ★ ―― 先に書いて置く。
#
#   ★門（走る前に書く・厳密な組合せ）★
#     完全分離＝「保つ」が丸ごと一つの側に収まり 其処に「空」が一本も混ざらぬ事。
#     偶然の確率 p を ★組合せで厳密に★ 出す（近似せぬ）:
#       ・類の尺（在り処）: p = （大きさ k の類の数）/ C(n,k)
#       ・順の尺（mtime・名）  : ★両側★ p = 2 / C(n,k)（上端 k 本 或は 下端 k 本）／★片側★ p = 1 / C(n,k)
#     ★p が 5% 以上なら ★棄てる★（分離が現に在つても 偶然と分けられぬ ∴ 数を出さぬ）★。
#
#   ★撃つても判らぬ事（走る前に書く）★
#     ㋐ §19 で「名の階層／在り処／中身の刻では出ぬ」と既に出た尺である。
#     ㋑ 母が 12 本（族別では 2 本と 10 本）∴ ★何を振つても分かれ得る★。
#     ㋒ 「空」側は中身 0 行 ∴ ★中身から引ける物は原理として無い★。
#     ㋓ 族を併せれば p は下がる（12 本・k=2）が ★併合は族の交絡を戻す★ ∴ ★主は族別・併合は副として刷るのみ★。
#   ★file を讀むだけ。git は一度も実行せぬ。.git も讀まぬ。書込は scratch のみ。★
import io, math, sys, collections, datetime

D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
GATE = 0.05

def pre(n):
    p = n.split("/")
    return "/".join(p[:-1]) if len(p) >= 2 else n

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k)) if 0 <= k <= n else 0

def load(path):
    rows = []
    with io.open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                c = ln.rstrip("\n").split("\t")
                if len(c) >= 8:
                    rows.append(c)
    return rows

def cat_sep(items, k):
    """categorical: (分離したか, p)"""
    g = collections.defaultdict(list)
    for nm, val, lab in items:
        g[val].append(lab)
    n = len(items)
    hit = any(len(v) == k and all(x == u"保つ" for x in v) for v in g.values())
    same = sum(1 for v in g.values() if len(v) == k)
    return hit, (float(same) / C(n, k) if C(n, k) else 1.0)

def ord_sep(items, k):
    """順: (分離したか, 両側 p, 片側 p)"""
    n = len(items)
    s = sorted(items, key=lambda t: t[1])
    top = [t[2] for t in s[n-k:]]
    bot = [t[2] for t in s[:k]]
    hit = all(x == u"保つ" for x in top) or all(x == u"保つ" for x in bot)
    c = C(n, k)
    return hit, (2.0 / c if c else 1.0), (1.0 / c if c else 1.0)

def judge(rows, fams, out=sys.stdout, label=u"実測"):
    got = {}
    for fam in fams:
        mem = [c for c in rows if pre(c[1]) == fam and c[0] in (u"空", u"保つ")]
        n = len(mem); k = sum(1 for c in mem if c[0] == u"保つ")
        out.write(u"── 族 %s ── %d 本（空 %d ／ 保つ %d）\n" % (fam, n, n - k, k))
        if n < 2 or k == 0 or k == n:
            out.write(u"  ★棄てる★=母が立たぬ\n"); got[fam] = u"棄てる"; continue
        tiers = set(c[2] for c in mem)
        out.write(u"  階層 %s ⇒ ★族の内で一定ゆゑ尺に成らぬ★\n" % (u"・".join(sorted(tiers))))
        lines = []
        h, p = cat_sep([(c[1], c[3], c[0]) for c in mem], k)
        lines.append((u"㋐在り処", h, p, p))
        for lab, key in ((u"㋑mtime の順", 7), (u"㋒名の辞書順", 1)):
            h, p2, p1 = ord_sep([(c[1], c[key], c[0]) for c in mem], k)
            lines.append((lab, h, p2, p1))
        worst = None
        for lab, h, p2, p1 in lines:
            out.write(u"  %-12s 分離 %s ／ 偶然 p 両側 %.4f（片側 %.4f）⇒ %s\n" % (
                lab, u"★在り★" if h else u"無し", p2, p1,
                u"★棄てる（p≧5%）★" if p2 >= GATE else (u"★言へる★" if h else u"言へぬ（分離せず）")))
            if h and p2 < GATE:
                worst = lab
        got[fam] = u"言へる（%s）" % worst if worst else (
            u"棄てる" if all(p2 >= GATE for _, _, p2, _ in lines) else u"言へぬ")
        out.write(u"  ★族の答★ %s\n" % got[fam])
    return got

def selftest():
    mk = lambda g, n, mt, at: [g, n, u"heads", at, u"-", u"-", u"0", mt]
    # 陽性: 12 本・保つ 2 本が mtime の上端（p 両側 = 2/66 = 3.03% < 5%）
    pos = [mk(u"空", u"refs/heads/z/e%02d" % i, u"2026-01-%02dT00:00:00" % (i+1), u"packed") for i in range(10)]
    pos += [mk(u"保つ", u"refs/heads/z/k%d" % i, u"2026-02-%02dT00:00:00" % (i+1), u"packed") for i in range(2)]
    # 陰性: 12 本・保つ 2 本が ★三尺の悉くで真中★（名も mtime も真中・在り処は両方に散る）
    #   ★一度誤つた（2026-09-09 走 0）★=保つを "k*"・空を "e*" と名づけた為 ★名の辞書順で上端に揃つて了ひ★
    #   陰性の筈が「言へる」と出た。疵は器に非ず ★己の対照★ ゆゑ 対照を直した（§41-4 と同じ形の二度目）。
    neg  = [mk(u"空", u"refs/heads/y/a%02d" % i, u"2026-01-%02dT00:00:00" % (i+1),
               u"loose" if i % 2 else u"packed") for i in range(5)]
    neg += [mk(u"空", u"refs/heads/y/z%02d" % i, u"2026-01-%02dT00:00:00" % (i+8),
               u"loose" if i % 2 else u"packed") for i in range(5)]
    neg += [mk(u"保つ", u"refs/heads/y/g%d" % i, u"2026-01-06T%02d:00:00" % (i+1),
               u"loose" if i else u"packed") for i in range(2)]
    # 棄てる: 2 本（p 両側 = 2/2 = 1.0）
    dis = [mk(u"空", u"refs/heads/x/a", u"2026-01-01T00:00:00", u"packed"),
           mk(u"保つ", u"refs/heads/x/b", u"2026-01-02T00:00:00", u"loose")]
    ok = True
    for lab, rows, fam, want in ((u"陽性(上端 2 本)", pos, u"refs/heads/z", u"言へる"),
                                 (u"陰性(真中)",     neg, u"refs/heads/y", u"言へぬ"),
                                 (u"棄てる(2 本)",   dis, u"refs/heads/x", u"棄てる")):
        buf = io.StringIO()
        g = judge(rows, [fam], buf)
        v = g[fam]
        good = v.startswith(want)
        sys.stdout.write(u"[%s] 望 %s ／ 出 %s ⇒ %s\n" % (lab, want, v, u"合" if good else u"★合はず★"))
        ok = ok and good
    return 0 if ok else 1

if "--selftest" in sys.argv:
    sys.exit(selftest())

rows = load(L112)
assert len(rows) == 345, u"母数 %d（345 を前提として居る）" % len(rows)
FAMS = [u"refs/heads/codex", u"refs/remotes/origin/ashigaru-third-1"]
sys.stdout.write(u"母数(引継) %d ／ 出所 %s ／ 門 p<%.0f%%\n" % (len(rows), L112, GATE*100))
got = judge(rows, FAMS)

# ── 副（併合・族の交絡を戻す ∴ 主に非ず）──
mem = [c for c in rows if pre(c[1]) in FAMS and c[0] in (u"空", u"保つ")]
n = len(mem); k = sum(1 for c in mem if c[0] == u"保つ")
sys.stdout.write(u"[副・併合 %d 本（空 %d／保つ %d）★族の交絡を戻す ∴ 主に非ず★]\n" % (n, n-k, k))
h, p = cat_sep([(c[1], c[3], c[0]) for c in mem], k)
sys.stdout.write(u"  ㋐在り処 分離 %s ／ p %.4f\n" % (u"★在り★" if h else u"無し", p))
for lab, key in ((u"㋑mtime の順", 7), (u"㋒名の辞書順", 1)):
    h, p2, p1 = ord_sep([(c[1], c[key], c[0]) for c in mem], k)
    sys.stdout.write(u"  %-12s 分離 %s ／ p 両側 %.4f（片側 %.4f）\n" % (lab, u"★在り★" if h else u"無し", p2, p1))

OUT = "%s/o141_inside_%s.txt" % (D, TS)
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(u"# o141 同居の内側 12 本（0 本でも落とす）。列: 族\t組\t名\t階層\t在り処\t行数\tmtime\n")
    for c in sorted(mem, key=lambda c: (pre(c[1]), c[7], c[1])):
        f.write(u"\t".join([pre(c[1]), c[0], c[1], c[2], c[3], c[6], c[7]]) + u"\n")
sys.stdout.write(u"名の一覧: %s (%d 行)\n" % (OUT, len(mem) + 1))
sys.stdout.write(u"★順 12 の答★ %s\n" % u" ／ ".join(u"%s=%s" % (f.split("/")[-1], got[f]) for f in FAMS))

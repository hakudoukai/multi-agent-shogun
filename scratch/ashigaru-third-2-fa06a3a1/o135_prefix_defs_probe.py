#!/usr/bin/env python3
# o135: 第八の目の ★打ち直し（order133）★ ―― 「prefix の境で切り替はるか」を ★定義を先に一つ決めて★ 測る。
#   ★走る前に一つ決めた主定義（同じ手番で ★便にも出した★・msg_20260909_043819_b0f43a8a）★
#     D2 = prefix は ★名から末尾一節を除いた所★、★但し 片方が他方の前置なら「変つた」と数へぬ★。
#          （因＝o117 の P=48 のうち ★25 対は『/ が増えただけ』★＝族は変つて居らぬのに「変つた」と数へて居た＝★定義の疵★）
#   ★尺（o117 と同じ・変へぬ）★= O < 2E なら ★棄てる★。E = B × P/199 ―― ★実測 O より先に刷る★。
#   ★当ての向き（今度は器でなく ★便★ に出した）★= P は 48→23 前後へ落ち E も落ちるが O は余り落ちぬ
#          ∴ ★比は 2.84 より ★上がる★★ と当てる。（外れたら外れたと書く）
#   ★不利な証（先に書く）★= ㋐prefix は生年と交絡（§24-4：真の順は名の順の近傍）∴ ★寄つても『席が決めた』の証に成らぬ★
#     ㋑B=19 は小さい ∴ 2 倍の閾は少数で超え得る ㋒定義を粗くすれば P→0 となり ★比は測れなくなる（0 ではない）★
#   ★母（悉くの数に添へる）★= 帯 200 本（空 112／保つ 88）・隣接 199 対・B は定義に依らず 19。
#   ★走 2 で直した疵（己の誤り・隠さず記す）★= 走 1 の器は母を「帯 200／隣接 199」と ★書き置いた文字で刷つて居た★。
#     実測は 198／197（「保つ」2 本が o116 の後に測れなくなつた）∴ ★母は毎走 実測して刷る★ へ改めた。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, os, sys

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT  = "%s/o135_prefix_defs_%s.txt" % (D, TS)

# ── 数へる核（悉くの定義で ★同じ核★ を使ふ）──
def tally(seq, lab, changed):
    """seq=真の順の名 / lab=名→札 / changed=(a,b)→prefix が変つたか"""
    pairs = len(seq) - 1
    B = sum(1 for i in range(pairs) if lab(seq[i+1]) != lab(seq[i]))
    P = sum(1 for i in range(pairs) if changed(seq[i], seq[i+1]))
    O = sum(1 for i in range(pairs)
            if lab(seq[i+1]) != lab(seq[i]) and changed(seq[i], seq[i+1]))
    E = B * P / float(pairs) if pairs else 0.0
    return pairs, B, P, E, O

def verdict(E, O):
    if E == 0:
        return "測れず(別値・P=0 ゆゑ E=0 ∴ 比を作れぬ)", None
    r = O / E
    return ("★棄てる★" if O < 2 * E else "★棄てぬ★"), r

# ── ① 対照（数より先に鳴らす・条 十四）──
def ctl_run():
    n = 200
    seq = ["x%03d" % i for i in range(n)]
    # 札＝10 本ごとに入替る（塊 20・B=19）
    lab = {s: ("空" if (i // 10) % 2 == 0 else "保つ") for i, s in enumerate(seq)}
    # 陽性＝prefix も 10 本ごとに変る（境が札の境と ★悉く重なる★）
    pos = {s: "p%02d" % (i // 10) for i, s in enumerate(seq)}
    # 陰性＝prefix は 7 本ごとに変る（10 と互ひに素 ∴ 札の境と ★揃はぬ★）
    neg = {s: "q%02d" % (i // 7) for i, s in enumerate(seq)}
    out = []
    for nm, mp, want in (("陽性(境が重なる)", pos, "★棄てぬ★"), ("陰性(境が揃はぬ)", neg, "★棄てる★")):
        pairs, B, P, E, O = tally(seq, lambda s: lab[s], lambda a, b: mp[a] != mp[b])
        v, r = verdict(E, O)
        print("対照 %-16s B=%-3d P=%-3d E=%.2f O=%-3d 比=%s 判=%s 望み=%s %s" % (
              nm, B, P, E, O, ("%.2f" % r) if r else "-", v, want,
              "立つ" if v == want else "★外れ★"))
        out.append(v == want)
    return all(out)

if not ctl_run():
    print("ABORT reason=control_did_not_stand")
    sys.exit(3)

# ── ② 帯（o112 の一覧のみを材料に・o116/o117 と同じ）──
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
mt = {}; lost = []
for nm in band:
    try:
        mt[nm] = os.stat(os.path.join(GIT, "logs", nm)).st_mtime_ns
    except OSError as e:
        lost.append((grp[nm], nm, "stat-%s" % getattr(e, "errno", "?")))
tgt   = [n for n in band if n in mt]
truth = sorted(tgt, key=lambda n: (mt[n], n))
PAIRS = len(truth) - 1
print("★母（★実測★・器に書き置いた数を使はぬ）★ 引継一覧 %d ／ 帯の名 %d ／ ★測れた %d 本（空 %d ／ 保つ %d）★ ／ 隣接対 %d" % (
      len(rows), len(band), len(tgt), sum(1 for n in tgt if grp[n] == "空"),
      sum(1 for n in tgt if grp[n] == "保つ"), PAIRS))
print("★母が動いた★ o116/o117 の帯は 200 本・隣接 199 対であつた ⇒ 今 %d 本・%d 対（差 %d 本）" % (
      len(tgt), PAIRS, len(band) - len(tgt)))
if lost:
    print("★測れなくなつた本（0 と書かず 別値として名指す）★ %d 本" % len(lost))
    for g, n, e in lost:
        print("   ・%s\t%s\t%s" % (g, n, e))

# ── ③ 定義 六つ ──
def seg(n, k):
    p = n.split("/")
    return "/".join(p[:k]) if len(p) >= k else n
def d_tail(n):                      # 末尾一節を除く
    return n.rsplit("/", 1)[0] if "/" in n else "(根)"
def d_area(n):                      # 器（remotes は上三節・他は上二節）
    return seg(n, 3) if n.startswith("refs/remotes/") else seg(n, 2)
def d_seat(n):                      # 席（heads は上三節・remotes は上四節）
    return seg(n, 4) if n.startswith("refs/remotes/") else seg(n, 3)

def ne(f):
    return lambda a, b: f(a) != f(b)
def ne_nopre(f):                    # ★主定義 D2★=片方が他方の前置なら「変つた」と数へぬ
    def g(a, b):
        x, y = f(a), f(b)
        if x == y:
            return False
        return not (x.startswith(y + "/") or y.startswith(x + "/"))
    return g

DEFS = [
    ("D2 ★主★ 末尾一節除去＋前置は同族", ne_nopre(d_tail), "★走る前に決めた★"),
    ("D1 末尾一節除去（o117 の元）",       ne(d_tail),       "打ち直しの比べ元"),
    ("D3 器（heads/remotes+遠隔名）",      ne(d_area),       "§24-3 の上三節"),
    ("D4 上二節（refs/heads・refs/remotes）", ne(lambda n: seg(n, 2)), "§24-3 の上二節"),
    ("D5 席（heads の第三節迄）",           ne(d_seat),       "席が決めたなら此処で切れる筈"),
    ("D6 第一節（refs のみ）",              ne(lambda n: seg(n, 1)), "★粗くする極★"),
]
print("── 定義別（母は悉く同じ：★帯 %d／隣接 %d★／B は定義に依らず）──" % (len(tgt), PAIRS))
res = []
for lab_, chg, note in DEFS:
    pairs, B, P, E, O = tally(truth, lambda s: grp[s], chg)
    v, r = verdict(E, O)
    res.append((lab_, B, P, E, O, r, v, note))
    print("  %-34s B=%-3d P=%-3d(%.1f%%) E=%.2f O=%-3d 比=%-6s %s  ← %s" % (
          lab_, B, P, 100.0*P/pairs, E, O, ("%.2f" % r) if r else "測れず", v, note))

r2 = [x for x in res if x[0].startswith("D2")][0]
r1 = [x for x in res if x[0].startswith("D1")][0]
print("★主定義 D2 の答★ B=%d P=%d E=%.2f O=%d 比=%.2f ⇒ %s（★母＝帯 %d・隣接 %d★）" % (
      r2[1], r2[2], r2[3], r2[4], r2[5], r2[6], len(tgt), PAIRS))
print("★当ての検め（★同じ母の中で★ 比べる）★ D1 比 %.2f → D2 比 %.2f ＝ %s（当ては『上がる』であつた）" % (
      r1[5], r2[5], "★上がつた（当たり）★" if r2[5] > r1[5] else "★上がらなんだ（外れ）★"))
print("★借りた 2.84 とは足し比べるな★ o117 の 2.84 は 帯 200・隣接 199 の数、今の D1 は 帯 %d・隣接 %d で %.2f ＝ ★母が違ふ★" % (
      len(tgt), PAIRS, r1[5]))
print("★2.84 が定義でどう動くか★ " + " ／ ".join(
      "%s=%s" % (x[0].split()[0], ("%.2f" % x[5]) if x[5] else "測れず") for x in res))

# ── ④ D1 と D2 の差の中身（何を「変つた」と数へなくしたか）──
pairs = len(truth) - 1
only_d1 = []
for i in range(pairs):
    a, b = truth[i], truth[i+1]
    if ne(d_tail)(a, b) and not ne_nopre(d_tail)(a, b):
        only_d1.append((i, a, b, grp[a] != grp[b]))
print("★D1 で『変つた』と数へ D2 で数へぬ対★ = %d（内 札も入替る対 %d）" % (
      len(only_d1), sum(1 for x in only_d1 if x[3])))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o135 定義別（母＝帯 %d 本・隣接 %d 対）as_of %s\n" % (len(tgt), pairs, TS))
    f.write("# 定義\tB\tP\tE\tO\t比\t判\t註\n")
    for x in res:
        f.write("\t".join([x[0], str(x[1]), str(x[2]), "%.2f" % x[3], str(x[4]),
                           ("%.2f" % x[5]) if x[5] else "測れず", x[6], x[7]]) + "\n")
    f.write("# D1 で数へ D2 で数へぬ対（位置\t左\t右\t札も入替るか）\n")
    for i, a, b, sw in only_d1:
        f.write("%d\t%s\t%s\t%s\n" % (i, a, b, "入替る" if sw else "入替らぬ"))
    f.write("# 測れなくなつた本 %d（組\t名\t理由）― o116 では 200 本悉く測れて居た\n" % len(lost))
    for g, n, e in lost:
        f.write("%s\t%s\t%s\n" % (g, n, e))
print("一覧: %s" % OUT)

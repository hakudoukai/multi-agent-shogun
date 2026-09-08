#!/usr/bin/env python3
# o139: 順 6「★prefix の境★ が ★掃く/掃かぬ の境★ と ★重なるか★」を ★生年で層別してから★ 見る。
#   ★出るのは「言へる/言へぬ」のみ★（「prefix は分け目である」とは出ぬ）。
#
#   ★宣言する尺（走る前に書く）★
#     主尺 prefix ＝ 名から末尾一節を除いた所（★o117 と同じ定義を其の儘写す★・新たに作らぬ）。
#     副尺 族(fam) ＝ 階層(refs/heads・refs/remotes/origin 等)を外した名の族。★是も走る前に宣言する★。
#     ㋐ 帯200 のうち ★同じ prefix に 空 と 保つ が同居する prefix★ が ★1 つ以上★ 在れば
#        ⇒ ★「prefix の境は 掃く/掃かぬ の境に重ならぬ」と ★言へる★★（生年に依らず言へる)。
#     ㋑ 同居 0 なら ⇒ ★言へぬ★（重なつて見えても ★生年で層別できぬ★ ゆゑ 生年の仕業と分けられぬ）。
#
#   ★外れる形（走る前に送る）★=帯200 の prefix が悉く ★本数 1★ なら 同居は原理として 0
#     ∴ 尺が立たぬ ⇒ ★棄てる★（数を出さぬ）。prefix ごとの本数分布を ★実測の前に刷る★。
#
#   ★撃つても判らぬ事（走る前に送つた三つ＋走る前に足す一つ）★
#     ㋐ 227 名が片側だけ ∴ 対に成らぬ。
#     ㋑ 生年(誕生の印)は remotes/* に ★原理として付かぬ★ ∴ 解けるのは heads の側だけ。
#     ㋒ 出るのは「言へる/言へぬ」であつて「prefix は分け目である」ではない。
#     ㋓ ★空 112 は reflog 0 行 ∴ 生年 0 本★ ―― 層別は ★掃かれた側で立たぬ★（下で実測して刷る）。
#
#   ★file を讀むだけ。git は一度も実行せぬ。.git も讀まぬ（前弾の落した帳のみを材料とする）。書込は scratch のみ。★
import collections, datetime, io, sys

D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def pre(n):                      # ★o117 と同じ定義★
    p = n.split("/")
    return "/".join(p[:-1]) if len(p) >= 2 else n

def fam(n):                      # 副尺: 階層を外した族
    p = n.split("/")
    if len(p) >= 3 and p[0] == "refs":
        q = p[2:] if p[1] != "remotes" else p[3:]
        return q[0] if q else "(無)"
    return n

def load(path):
    rows = []
    with io.open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                c = ln.rstrip("\n").split("\t")
                if len(c) >= 5:
                    rows.append(c)   # 組/名/階層/在り処/中身の最古/…
    return rows

def judge(rows, key, out=sys.stdout):
    grp  = dict((c[1], c[0]) for c in rows)
    born = dict((c[1], c[4]) for c in rows)
    band = [c[1] for c in rows if c[0] in (u"空", u"保つ")]
    d = collections.defaultdict(lambda: [0, 0])
    for n in band:
        d[key(n)][0 if grp[n] == u"空" else 1] += 1
    sizes = collections.Counter(a + b for a, b in d.values())
    out.write(u"帯 %d 本 ／ %s の数 %d ／ 本数分布(本数:個数) %s\n" % (
        len(band), key.__name__, len(d), sorted(sizes.items())))
    if all(a + b == 1 for a, b in d.values()):
        out.write(u"★棄てる★=悉く本数 1 ゆゑ同居は原理として 0（尺が立たぬ）\n")
        return u"棄てる", d
    mixed = sorted(k for k, (a, b) in d.items() if a and b)
    out.write(u"★同居(空と保つが同じ %s に居る)★ %d 個\n" % (key.__name__, len(mixed)))
    # 生年の在り処（層別が立つ側/立たぬ側）
    has = sum(1 for n in band if born.get(n, u"-") != u"-")
    e_has = sum(1 for n in band if grp[n] == u"空"  and born.get(n, u"-") != u"-")
    k_has = sum(1 for n in band if grp[n] == u"保つ" and born.get(n, u"-") != u"-")
    out.write(u"生年の在る本数 帯 %d／空 %d／保つ %d ―― ★空側 %d 本ゆゑ層別は掃かれた側で立たぬ★\n" % (
        has, e_has, k_has, e_has))
    verdict = u"言へる（重ならぬ）" if mixed else u"言へぬ"
    out.write(u"★判定★ %s\n" % verdict)
    return verdict, d

def selftest():
    mk = lambda g, n, b: [g, n, u"heads", u"packed", b, u"-", u"0", u"-"]
    # ★三つ置く★（陰性を最初 本数 1 で作つた所 ★棄てる★ が鳴つた ＝ 外れる形の門が現に働く証）
    pos = [mk(u"空", u"refs/heads/x/a", u"-"), mk(u"保つ", u"refs/heads/x/b", u"2026-01-01T00:00:00")]
    neg = [mk(u"空", u"refs/heads/x/a", u"-"), mk(u"空", u"refs/heads/x/b", u"-"),
           mk(u"保つ", u"refs/heads/y/c", u"2026-01-01T00:00:00"),
           mk(u"保つ", u"refs/heads/y/d", u"2026-01-01T00:00:00")]
    dis = [mk(u"空", u"refs/heads/x/a", u"-"), mk(u"保つ", u"refs/heads/y/b", u"2026-01-01T00:00:00")]
    ok = True
    for lab, rows, want in ((u"陽性(同居 1)", pos, u"言へる（重ならぬ）"),
                            (u"陰性(純・本数 2)", neg, u"言へぬ"),
                            (u"棄てる(悉く本数 1)", dis, u"棄てる")):
        buf = io.StringIO()
        got, _ = judge(rows, pre, buf)
        sys.stdout.write(u"[%s] 望 %s ／ 出 %s ⇒ %s\n" % (lab, want, got, u"合" if got == want else u"★合はず★"))
        ok = ok and (got == want)
    return 0 if ok else 1

if "--selftest" in sys.argv:
    sys.exit(selftest())

rows = load(L112)
assert len(rows) == 345, u"母数 %d（345 を前提として居る）" % len(rows)
sys.stdout.write(u"母数(引継) %d ／ 出所 %s\n" % (len(rows), L112))
res = {}
for key in (pre, fam):
    sys.stdout.write(u"── 尺 %s ──\n" % key.__name__)
    res[key.__name__], d = judge(rows, key)
    mixed = sorted(k for k, (a, b) in d.items() if a and b)
    for k in mixed[:12]:
        a, b = d[k]
        sys.stdout.write(u"   同居 %s ＝ 空 %d ／ 保つ %d\n" % (k, a, b))
    if len(mixed) > 12:
        sys.stdout.write(u"   …他 %d 個（名は下の一覧に落とす）\n" % (len(mixed) - 12))
    p = u"%s/o139_%s_%s.txt" % (D, key.__name__, TS)
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(u"# o139 %s ごとの 空/保つ（帯200）。0 本でも落とす。\n# 列: %s\t空\t保つ\t同居?\n" % (key.__name__, key.__name__))
        for k in sorted(d):
            a, b = d[k]
            f.write(u"%s\t%d\t%d\t%s\n" % (k, a, b, u"同居" if a and b else u"-"))
    sys.stdout.write(u"   一覧: %s (%d 行)\n" % (p, len(d) + 2))
sys.stdout.write(u"★順 6 の答★ 主尺 %s ／ 副尺 %s\n" % (res["pre"], res["fam"]))

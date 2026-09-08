#!/usr/bin/env python3
# o137: 順 11 ＝ ★母の 増え方★（順 10 の ★裏側★）。
#   ★走る前に開示した食ひ違ひ★= o112 の母 345 は `.git/logs/refs` 樹＝★帳★の集合であり ★全 ref ではない★。
#     ∴「母 345 に無く 今の樹に在る ★ref★」は ★母が違ふ★ ゆゑ 直には出せぬ。
#   ★∴ 三つを別語で刷る★:
#     ① ★帳★ の増減 ―― 母 = o112 の 345（帳）／今 = 今の `logs/refs` 樹（★同一母★）
#     ② ★ref★ の増減 ―― 母 = o103 の 346（`for-each-ref` の名簿・★刻 10:20:05★）／今 = loose ∪ packed
#        ★刻が違ふ（o112 は 11:59:33）∴ ①と②の数を足し引きするな★
#     ③ ★門★ ―― 母 345（帳）と 母 346（ref）の ★重なり★。★之が食ひ違へば ①②を混ぜて語らぬ★
#   ★出す物は 三つ止まり★= ㋐幾つ増えた ㋑どの前置きか ㋒何時より後か（範）。
#   ★撃つ前に申す『出ぬ物』★= 誰が足したかは出ぬ／新しい物に帳が無ければ 刻の下限も置けぬ／★点は出ぬ（範のみ）★。
#   ★列挙は o116_order_probe.py の readdir 走査＋packed-refs parse の ★写し★ である（二重実装の開示）。
#   ★走 1・讀取のみ・git 実行 0・書込は scratch のみ・消す動詞 0。★
import collections, datetime, os, sys, time

GIT  = "/mnt/c/DentalBI/.git"
HOME = "/home/hakudoukai/multi-agent-shogun/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"          # 母①＝帳 345（11:59:33）
L103 = D + "/o103_refs_20260908_102005.txt"           # 母②＝ref 346（10:20:05）
O116 = D + "/o116_order_20260908_124938.txt"          # 範の左端に使つた生出力
JST  = datetime.timezone(datetime.timedelta(hours=9))
TS   = datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S")

def j(t): return datetime.datetime.fromtimestamp(t, JST).strftime("%Y-%m-%d %H:%M:%S")
def mt(p):
    try: return os.stat(p).st_mtime
    except OSError: return None

def logs_set(root):
    """今の 帳（logs/refs 樹の file）の名の集合 ―― o112 の母の作り方と ★同じ形★"""
    out = set(); r = os.path.join(root, "logs", "refs")
    for dp, dn, fn in os.walk(r):
        for f in fn:
            p = os.path.join(dp, f)
            out.add("refs/" + os.path.relpath(p, r).replace(os.sep, "/"))
    return out

def refs_set(root):
    """今の ref ―― loose(refs/** の file) ∪ packed(packed-refs の行)。o116 の parse の ★写し★"""
    loose = set(); r = os.path.join(root, "refs")
    for dp, dn, fn in os.walk(r):
        for f in fn:
            p = os.path.join(dp, f)
            loose.add("refs/" + os.path.relpath(p, r).replace(os.sep, "/"))
    packed = set()
    pf = os.path.join(root, "packed-refs")
    try:
        with open(pf, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.rstrip("\n")
                if not ln or ln[0] in "#^": continue
                sp = ln.split(" ", 1)
                if len(sp) == 2: packed.add(sp[1].strip())
    except OSError:
        pass
    return loose, packed

def pre(nm):
    """前置き ―― refs/remotes/origin/... -> refs/remotes/origin ／ refs/heads/... -> refs/heads"""
    p = nm.split("/")
    if len(p) >= 3 and p[1] == "remotes": return "/".join(p[:3])
    return "/".join(p[:2])

print("=== o137 順 11 ＝ 母の ★増え方★（順 10 の裏側）／as_of %s JST ===" % j(time.time()))
print("★走る前に申した『出ぬ物』★: 誰が足したかは出ぬ ／ 帳の無い物は刻の下限も置けぬ ／ ★点は出ぬ（範のみ）★")

# ── 母① 帳 345（o112）──
m112 = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if ln.startswith("#"): continue
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 4: m112.append(c)
grp   = {c[1]: c[0] for c in m112}
MOM_L = set(c[1] for c in m112)
print("母① ★帳★ = o112 %d 本（刻 11:59:33・層 空/保つ/別刻）" % len(MOM_L))
assert len(MOM_L) == 345, "母① %d（345 を前提として居る）" % len(MOM_L)

# ── 母② ref 346（o103）──
MOM_R = set()
with open(L103, encoding="utf-8") as f:
    for ln in f:
        if ln.startswith("#") or not ln.strip(): continue
        MOM_R.add(ln.split("\t")[0])
print("母② ★ref★ = o103 %d 本（刻 10:20:05・`for-each-ref` の名簿）" % len(MOM_R))

# ── ③ 門 ＝ 母① と 母② の重なり（★先に検める★）──
inter = MOM_L & MOM_R
print("\n★③ 門（先に検める）★ 母①∩母② = %d ／ 母①のみ %d ／ 母②のみ %d"
      % (len(inter), len(MOM_L - MOM_R), len(MOM_R - MOM_L)))
same = (MOM_L == MOM_R)
print("   母① と 母② は ★同一集合か★ = %s" % ("★同一★" if same else "★違ふ★"))
if not same:
    print("   ∴ ★『母 345 と当時の全 ref 数が同じか』は ★立たぬ★ ―― 走る前に申した通り。★")
    print("   ∴ ★① 帳 と ② ref を ★別語★ で出し 足し引きせぬ★（混ぜれば 母の違ひが数に化ける）。")
    for lab, st in (("母①のみ（帳は在るが 当時 ref 名簿に無い）", MOM_L - MOM_R),
                    ("母②のみ（ref 名簿に在るが 帳が無い）",      MOM_R - MOM_L)):
        c = collections.Counter(pre(n) for n in st)
        print("   %s %d 本 ： %s" % (lab, len(st),
              " / ".join("%s=%d" % kv for kv in sorted(c.items(), key=lambda x: -x[1])) or "―"))

# ── 対照（★立たねば 数を出さぬ★・走 3 の教訓で ★中間値を悉く刷る★）──
print("\n★対照（home 樹・立たねば 数を出さぬ）★")
h_now = logs_set(HOME)
print("   home の 今の帳 = %d 本" % len(h_now))
if len(h_now) < 40:
    print("ABORT reason=home_logs_too_small_for_control"); sys.exit(4)
X   = sorted(h_now)[:20]
posm = h_now - set(X)                      # 陽性：母から 20 本 抜く ⇒ 増分が 20 と出る筈
pos_add = len(h_now - posm); pos_del = len(posm - h_now)
FAKE = set("refs/heads/zzz-fake-%s-%02d" % (TS, i) for i in range(20))
negm = h_now | FAKE                        # 陰性：母に贋 20 を足す ⇒ 増分 0・減分 20 の筈
neg_add = len(h_now - negm); neg_del = len(negm - h_now)
print("   陽性（母から実在 20 本 抜く）: 増分 %d（20 を期す）／減分 %d（0 を期す）" % (pos_add, pos_del))
print("   陰性（母に贋 20 本 足す）    : 増分 %d（0 を期す）／減分 %d（20 を期す）" % (neg_add, neg_del))
ok = (pos_add == 20 and pos_del == 0 and neg_add == 0 and neg_del == 20)
print("   対照 %s" % ("★2/2 立つ★" if ok else "★立たず★"))
if not ok:
    print("ABORT reason=control_did_not_stand"); sys.exit(3)

# ── ① 帳 の増減（★同一母★）──
now_L = logs_set(GIT)
addL  = now_L - MOM_L; delL = MOM_L - now_L
print("\n★① 帳（logs/refs）の増減 ―― 母 345（o112 11:59:33）と 今★")
print("   今の帳 = %d 本 ／ ★増えた %d★ ／ ★減つた %d★" % (len(now_L), len(addL), len(delL)))
for lab, st in (("増えた", addL), ("減つた", delL)):
    c = collections.Counter(pre(n) for n in st)
    print("   %s の前置き： %s" % (lab, " / ".join("%s=%d" % kv for kv in sorted(c.items(), key=lambda x: -x[1])) or "―"))
for n in sorted(addL)[:20]:
    p = os.path.join(GIT, "logs", n); m = mt(p)
    print("     ＋帳 %s ／ mtime %s" % (n, j(m) if m else "―"))

# ── ② ref の増減（母は o103・★刻違ひ★）──
loose, packed = refs_set(GIT)
now_R = loose | packed
addR  = now_R - MOM_R; delR = MOM_R - now_R
print("\n★② ref（loose ∪ packed）の増減 ―― 母 346（o103 ★10:20:05★・★母①と刻が違ふ★）と 今★")
print("   今の ref = %d 本（loose %d ／ packed %d）／ ★増えた %d★ ／ ★減つた %d★"
      % (len(now_R), len(loose), len(packed), len(addR), len(delR)))
for lab, st in (("増えた", addR), ("減つた", delR)):
    c = collections.Counter(pre(n) for n in st)
    print("   %s の前置き： %s" % (lab, " / ".join("%s=%d" % kv for kv in sorted(c.items(), key=lambda x: -x[1])) or "―"))
for n in sorted(addR)[:20]:
    print("     ＋ref %s ／ 在り処 %s" % (n, "両方" if (n in loose and n in packed) else ("loose" if n in loose else "packed")))

# ── ㋒ 範（★点は出ぬ★）──
lo = mt(L112); hi = time.time()
pkm = mt(os.path.join(GIT, "packed-refs"))
print("\n★㋒ 範（★点ではなく 範★）★")
print("   左端 = 母① の生出力 mtime %s ／ 右端 = 本走の刻 %s ／ 幅 %.2f 時間" % (j(lo), j(hi), (hi - lo) / 3600.0))
print("   狭める手 = `packed-refs` の mtime %s ―― ★之は『最後の書き』ゆゑ 其れ以前に入つた公算あり＝★点に非ず★★" % j(pkm))
print("\n★此の数が言はぬ事★: 誰が足したか ／ 何時 足したかの ★点★ ／ 帳と ref を足した『総数の増減』（★母が違ふ ∴ 足すな★）")

# ══════════════════════════════════════════════════════════════════
# ★走 2（家老の許し `msg_20260909_052801_5bc75fc0`）＝増分の ★帳 mtime の幅と名★★
#   ★増側は帳が在る ∴ 一本づつに ★刻の下限★ が置ける（減側と非対称）。
#   ★但し mtime は「最後の書き」∴ 各本は「★其の刻 ★以前★ に生れた★」としか言へぬ。
#   ★己の母を検める一手★= 増分のうち ★母① の刻(11:59:33)より ★前★ の mtime を持つ物★ を数へる。
#     0 なら 母の取り方と整合／★>0 なら 母 345 の取り方に ★抜け★ が在つた事に成る（＝己の疵）。
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("★走 2 ＝ 増分の帳 mtime の幅と名（増側は帳在り ∴ 刻の下限が置ける）★")

# ── 対照（走 2 用・★中間値を悉く刷る★）──
h_logs = os.path.join(HOME, "logs")
h_real = sorted(h_now)[:5]
c_ok = 0; c_ng = 0
for n in h_real:
    if mt(os.path.join(h_logs, n)) is not None: c_ok += 1
for i in range(5):
    if mt(os.path.join(h_logs, "refs/heads/zzz-fake-%s-%02d" % (TS, i))) is None: c_ng += 1
print("   対照 陽性（home の実在 5 本 → mtime 讀めた %d／5 を期す）／陰性（贋 5 本 → mtime 讀めず %d／5 を期す）"
      % (c_ok, c_ng))
if not (c_ok == 5 and c_ng == 5):
    print("ABORT reason=run2_control_did_not_stand"); sys.exit(5)
print("   対照 ★2/2 立つ★")

# ── 増分 102 本の mtime ──
rows = []
for n in sorted(addL):
    m = mt(os.path.join(GIT, "logs", n))
    rows.append((n, m))
have = [(n, m) for n, m in rows if m is not None]
none = [n for n, m in rows if m is None]
print("\n   増分 %d 本 ／ mtime 讀めた %d ／ 讀めぬ %d" % (len(rows), len(have), len(none)))
if have:
    ms = sorted(m for _, m in have)
    print("   ★幅★ 最古 %s ／ 中央 %s ／ 最新 %s ／ 幅 %.2f 時間"
          % (j(ms[0]), j(ms[len(ms)//2]), j(ms[-1]), (ms[-1] - ms[0]) / 3600.0))
    # 前置き別
    by = collections.defaultdict(list)
    for n, m in have: by[pre(n)].append(m)
    for k in sorted(by, key=lambda x: -len(by[x])):
        v = sorted(by[k])
        print("     %-26s %3d 本 ／ 最古 %s ／ 最新 %s" % (k, len(v), j(v[0]), j(v[-1])))

# ── ★己の母を検める★ ＝ 母① の刻より前の mtime を持つ増分 ──
MOM_T = mt(L112)
early = [(n, m) for n, m in have if m < MOM_T]
print("\n   ★母を検める★ 母① の生出力 mtime = %s" % j(MOM_T))
print("   増分のうち ★其れより前★ の mtime を持つ物 = ★%d 本★" % len(early))
if early:
    print("   ∴ ★母 345 の取り方に ★抜け★ が在つた（＝己の疵）★ ―― 下に名を出す。")
    for n, m in sorted(early, key=lambda x: x[1])[:20]:
        print("     ・%s ／ mtime %s" % (n, j(m)))
else:
    print("   ∴ ★母の取り方と 整合★（増分は悉く 母の刻より後の書きを持つ）―― ★但し『生れた刻が後』の証ではない★（mtime は最後の書き）。")

# ── 減つた 2 本（非対称の実測を 同じ走で並べる）──
print("\n   ★減つた側（非対称）★ %d 本 ―― file が無い ∴ mtime 0 本 讀めた（★刻の下限も置けぬ★）" % len(delL))
for n in sorted(delL):
    print("     ・%s ／ mtime %s" % (n, "―（file 無し）"))

# ── 名の一覧を落とす（前科の手当＝o116 と同じ作法）──
OUT = "%s/o137_growth_%s.txt" % (D, TS)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o137 走 2 ／ 増分の名と刻 ／ as_of %s JST\n" % j(time.time()))
    f.write("# 1 行 = <種>\t<名>\t<前置き>\t<mtime または ->\n")
    f.write("# ★mtime は『最後の書き』であり 誕生の刻ではない★。種 = 帳増/帳減/ref増/ref減。\n")
    for n, m in rows:
        f.write("\t".join(["帳増", n, pre(n), j(m) if m else "-"]) + "\n")
    for n in sorted(delL):
        f.write("\t".join(["帳減", n, pre(n), "-"]) + "\n")
    for n in sorted(addR):
        f.write("\t".join(["ref増", n, pre(n), "-"]) + "\n")
    for n in sorted(delR):
        f.write("\t".join(["ref減", n, pre(n), "-"]) + "\n")
tot = len(rows) + len(delL) + len(addR) + len(delR)
print("\n   名の一覧 = %s（%d 行＋註 3 行）" % (OUT, tot))
print("★走 2 が言はぬ事★: 誕生の刻（mtime は最後の書き）／誰が足したか／ref 側の刻（★ref に mtime を当てて居らぬ＝packed は行ゆゑ file mtime を持たぬ★）")

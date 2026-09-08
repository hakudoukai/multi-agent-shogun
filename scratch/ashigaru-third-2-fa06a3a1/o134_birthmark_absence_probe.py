#!/usr/bin/env python3
# o134: 第四の弾「heads の ★印無し★ の本は 何時出来たか・何故 印が無いか」。
#   ★紙の頭に置く定め（此の器の頭註と一字一句同じ）★
#     材   = $GIT/logs/<refname> （reflog の帳）。無ければ「帳が無い」＝印を論じ得ぬ ★別値★。
#     定めA（o113 が用ゐた語彙照合・当弾も之を「印」の定めとする）
#            = 帳の ★最古 entry の action★ が
#              BORN=("branch: Created from","checkout: moving from","clone:") の何れかで ★始まる★ ⇒ ★印有り★
#              讀めた別 action（空 message を含む） ⇒ ★印無し★
#              帳が開けぬ/空/行が解せぬ ⇒ ★讀めず★
#     定めB（当弾で足す・因を分ける物差し）
#            = 最古 entry の ★old_sha が 40 個の 0★ ⇒ 其の ref は此の帳の中で ★生まれた★（創生の記録 有り）
#              old_sha が ★非零★ ⇒ 帳の頭より前に其の ref は ★既に在つた★（創生の記録 無し）
#   ★三択語の割付★
#     器が付けぬ      = 創生の記録 有り(old0) ＋ action が BORN 語でない（器が別の語を書いた/何も書かなんだ）
#     付けた後に消えた = 創生の記録 無し(old≠0)（＝最古 entry より前が現存せぬ）
#     元より対象外    = 帳が無い（印を書く器が一度も回つて居らぬ）
#   ★生年★= 創生の記録 有り の本のみ「最古 entry の刻」を生年とする。
#            創生の記録 無し の本は ★生年 別値（上限のみ：其の刻より前に在つた）★ ―― ★0 と書かぬ★。
#   ★対照（条 十四）★= 合成の帳 5 本を同じ走で鳴らす（陽性 2/陰性 3）。立たねば数を出さず exit 3。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import datetime, os, re, sys

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"
CTL  = D + "/o134_control"
ZERO = "0" * 40
BORN = ("branch: Created from", "checkout: moving from", "clone:")
LINE = re.compile(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$")

def jst(ep):
    return datetime.datetime.utcfromtimestamp(int(ep) + 9 * 3600).strftime("%Y-%m-%dT%H:%M:%S")

def first_entry(path):
    """(old,new,epoch,action) か ('讀めず', 理由)"""
    try:
        st = os.stat(path)
    except OSError as e:
        return None, "stat-%s" % (e.errno,)
    if st.st_size == 0:
        return None, "zero-byte"
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError as e:
        return None, "open-%s" % (e.errno,)
    with fh:
        for ln in fh:
            m = LINE.match(ln.rstrip("\n"))
            if m:
                return (m.group(1), m.group(2), m.group(3), m.group(5)), None
    return None, "no-parsable-line"

def markA(act):
    if act is None:
        return "讀めず"
    return "印有り" if act.startswith(BORN) else "印無し"

def why(ent, has_log):
    if not has_log:
        return "元より対象外"
    if ent is None:
        return "-（讀めず）"
    return "器が付けぬ" if ent[0] == ZERO else "付けた後に消えた"

# ── ① 対照（走る前に鳴らす）──
os.makedirs(CTL, exist_ok=True)
ctl = [
    ("pos_born_branch", "%s %s x <x@y> 1780000000 +0900\tbranch: Created from HEAD\n" % (ZERO, "a"*40),
     "印有り", "器が付けぬ"),                     # 陽性①：印有り ゆゑ 三択語は使はぬ（下で見ぬ）
    ("pos_born_clone",  "%s %s x <x@y> 1780000001 +0900\tclone: from https://e/x\n" % (ZERO, "b"*40),
     "印有り", "器が付けぬ"),                     # 陽性②
    ("neg_empty_msg",   "%s %s x <x@y> 1780000002 +0900\n" % (ZERO, "c"*40),
     "印無し", "器が付けぬ"),                     # 陰性①：創生は在るが語が無い
    ("neg_trimmed",     "%s %s x <x@y> 1780000003 +0900\tcommit: z\n" % ("d"*40, "e"*40),
     "印無し", "付けた後に消えた"),               # 陰性②：帳の頭が削られて居る
    ("neg_zero_byte",   "",
     "讀めず", "-（讀めず）"),                    # 陰性③
]
bad = []
for nm, body, want_mark, want_why in ctl:
    p = os.path.join(CTL, nm)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    ent, rsn = first_entry(p)
    got_m = markA(ent[3] if ent else None)
    got_w = why(ent, True)
    ok = (got_m == want_mark) and (got_w == want_why)
    print("対照 %-16s 印=%-5s 因=%-12s 望み(%s/%s) %s" % (nm, got_m, got_w, want_mark, want_why,
          "立つ" if ok else "★外れ★"))
    if not ok:
        bad.append(nm)
if bad:
    print("ABORT reason=control_did_not_stand bad=%s" % ",".join(bad))
    sys.exit(3)

# ── ② 母数を ★己で数へる★（借りた 15 を前提とせぬ）──
#   母数甲 = $GIT/logs/refs/heads/ 以下に帳の在る全 refname（readdir・sort せぬ）
heads_log = []
def rec(d, rel):
    try:
        ents = list(os.scandir(d))
    except OSError:
        return
    for e in ents:
        r = rel + "/" + e.name
        if e.is_dir(follow_symlinks=False):
            rec(e.path, r)
        else:
            heads_log.append(r)
rec(os.path.join(GIT, "logs", "refs", "heads"), "refs/heads")
#   母数乙 = 今 生きて居る refs/heads（loose + packed-refs）
live = set()
def rec2(d, rel):
    try:
        ents = list(os.scandir(d))
    except OSError:
        return
    for e in ents:
        r = rel + "/" + e.name
        if e.is_dir(follow_symlinks=False):
            rec2(e.path, r)
        else:
            live.add(r)
rec2(os.path.join(GIT, "refs", "heads"), "refs/heads")
n_packed = 0
try:
    with open(os.path.join(GIT, "packed-refs"), encoding="utf-8", errors="replace") as f:
        for ln in f:
            if ln.startswith(("#", "^")):
                continue
            p = ln.split()
            if len(p) >= 2 and p[1].startswith("refs/heads/"):
                live.add(p[1]); n_packed += 1
except OSError as e:
    print("packed-refs 讀めず errno=%s" % e.errno)
#   母数丙 = 前弾 o112 の一覧のうち refs/heads（＝15 が出た母）
l112 = []
try:
    with open(L112, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                c = ln.rstrip("\n").split("\t")
                if len(c) >= 4 and c[1].startswith("refs/heads/"):
                    l112.append(c[1])
except OSError as e:
    print("o112 一覧 讀めず errno=%s" % e.errno)
print("母数甲 帳の在る heads %d ／ 母数乙 今 生きて居る heads %d (packed 行 %d) ／ 母数丙 o112 の heads %d"
      % (len(heads_log), len(live), n_packed, len(l112)))
print("甲に在り乙に無い(＝帳のみ残る) %d ／ 乙に在り甲に無い(＝帳が無い＝元より対象外) %d"
      % (len(set(heads_log) - live), len(live - set(heads_log))))

# ── ③ 分類（甲∪乙 を通す。帳の無い本も「元より対象外」として数へる）──
allnames = sorted(set(heads_log) | live)
rows = []
for nm in allnames:
    p = os.path.join(GIT, "logs", nm)
    has_log = os.path.exists(p)
    ent, rsn = first_entry(p) if has_log else (None, "no-log")
    mk = markA(ent[3] if ent else None) if has_log else "帳が無い"
    w  = why(ent, has_log)
    if ent and ent[0] == ZERO:
        born, born_kind = jst(ent[2]), "測れた"
    elif ent:
        born, born_kind = jst(ent[2]), "別値(上限のみ)"
    else:
        born, born_kind = "-", "別値(讀めず)"
    rows.append((nm, mk, w, born, born_kind,
                 (ent[3] if ent else (rsn or "-")) or "(空 message)",
                 str(len(list(open(os.path.join(GIT, "logs", nm), encoding="utf-8", errors="replace"))) ) if has_log else "-"))

def tally(sub):
    d = {}
    for r in sub:
        d[r[1]] = d.get(r[1], 0) + 1
    return d
print("★甲∪乙 %d 本の印★ %s" % (len(rows), tally(rows)))
in112 = [r for r in rows if r[0] in set(l112)]
print("★母数丙(o112 の heads %d 本)に限つた印★ %s" % (len(in112), tally(in112)))
n15 = [r for r in in112 if r[1] == "印無し"]
print("★己の定めで出た『母数丙 かつ 印無し』= %d 本（借りた数 15 と %s）★"
      % (len(n15), "一致" if len(n15) == 15 else "★食ひ違ふ★"))
n15_all = [r for r in rows if r[1] == "印無し"]
print("（参考）母数甲∪乙 で 印無し = %d 本 ―― 母が違へば数も違ふ" % len(n15_all))

# ── ④ 的の 15 本を細かく ──
print("── 母数丙 かつ 印無し の各本（名 / 生年 / 生年の質 / 三択語 / entries / action 逐語）──")
for r in sorted(n15, key=lambda x: x[3]):
    print("  %-58s %s %-12s %-14s n=%-5s %s" % (r[0][:58], r[3], r[4], r[2], r[6], r[5][:60]))
w3 = {}
b2 = {}
for r in n15:
    w3[r[2]] = w3.get(r[2], 0) + 1
    b2[r[4]] = b2.get(r[4], 0) + 1
print("★三択語の数★ %s" % w3)
print("★生年の質★ %s ―― ★測れぬ本を 0 と書かぬ★" % b2)

# ── ⑤ 一覧を落とす ──
TS  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = "%s/o134_birthmark_absence_%s.txt" % (D, TS)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# o134 名\t印(定めA)\t三択語(定めB)\t生年\t生年の質\tentries\taction逐語\n")
    for r in sorted(rows):
        f.write("\t".join([r[0], r[1], r[2], r[3], r[4], r[6], r[5].replace("\t", " ")]) + "\n")
print("一覧: %s (%d 行)" % (OUT, len(rows) + 1))

#!/usr/bin/env python3
# o113: 交絡(「古いを切つた」対「新しく生れただけ」)を解く。
#   道(a) logs/HEAD の帳 …… 家老の受入に従ひ 先づ命ぜられた道を打つ。
#   道(b) 各 ref の reflog の ★最古 entry の action★ …… 「branch: Created from」等 ＝ ★誕生の印★。
#         誕生の印が在れば ★其の枝は切られて居らぬ★(生れた刻が其処)。
#   ★何れも file を讀むだけ。git は一度も実行せぬ。★
import os, re, sys, datetime, collections

GIT   = "/mnt/c/DentalBI/.git"
LIST  = "scratch/ashigaru-third-2-fa06a3a1/o112_split_20260908_115933.txt"
OUT   = "scratch/ashigaru-third-2-fa06a3a1/o113_birthmark_%s.txt"  # 走 2 = 組の名の疵を直した版
LINE  = re.compile(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$")
BORN  = ("branch: Created from", "checkout: moving from", "clone:")

def iso(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%S")

def first_entry(path):
    # 最古 entry の (刻, action) を返す。読めぬ理由は★名で★残す。
    try:
        st = os.stat(path)
    except OSError as e:
        return None, None, "stat-%s" % e.errno
    if st.st_size == 0:
        return None, None, "zero-byte"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for ln in f:
                m = LINE.match(ln.rstrip("\n"))
                if m:
                    return int(m.group(3)), m.group(5), None
    except OSError as e:
        return None, None, "open-%s" % e.errno
    return None, None, "no-parsable-line"

# ── 組分けを o112 の一覧から引き継ぐ（新たに数へ直さぬ＝母数を揃へる）──
groups = {}
with open(LIST, encoding="utf-8") as f:
    for ln in f:
        if ln.startswith("#"):
            continue
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 2:
            groups[c[1]] = c[0]
cnt = collections.Counter(groups.values())
print("母数(o112 より引継) 計 %d ―― %s" % (len(groups), dict(cnt)))

# ── 道(a) logs/HEAD の帳 ──
head = os.path.join(GIT, "logs", "HEAD")
n_head = 0; acts = collections.Counter(); names = set(); ts_min = None; ts_max = None
mv = re.compile(r"^checkout: moving from (\S+) to (\S+)")
mg = re.compile(r"^(?:merge|pull[^:]*) (\S+)")
with open(head, encoding="utf-8", errors="replace") as f:
    for ln in f:
        m = LINE.match(ln.rstrip("\n"))
        if not m:
            continue
        n_head += 1
        t = int(m.group(3)); a = m.group(5)
        ts_min = t if ts_min is None else min(ts_min, t)
        ts_max = t if ts_max is None else max(ts_max, t)
        acts[a.split(":")[0]] += 1
        g = mv.match(a)
        if g:
            names.update(g.groups())
        g = mg.match(a)
        if g:
            names.add(g.group(1))
print("道(a) HEAD entry %d 行・刻 %s 〜 %s" % (n_head, iso(ts_min), iso(ts_max)))
print("道(a) action 上位: %s" % acts.most_common(6))
print("道(a) ★枝の名が拾へた entry から得た名 = %d 個★ …… %s" % (len(names), sorted(names)[:8]))

# ── 道(b) 誕生の印 ──
T2 = None
rows = []
for nm, grp in sorted(groups.items()):
    t, act, why = first_entry(os.path.join(GIT, "logs", nm))
    rows.append((grp, nm, t, act, why))
keep = [r for r in rows if r[0] == "保つ"]
late = [r for r in rows if r[0] == "別刻"]
zero = [r for r in rows if r[0] == "空"]
kt = [r[2] for r in keep if r[2] is not None]
T2 = min(kt) if kt else None
print("道(b) 保つ %d(讀めた %d) / 別刻 %d / 空 %d" % (len(keep), len(kt), len(late), len(zero)))
print("道(b) T2(保つ の最古 entry) = %s" % (iso(T2) if T2 else "-"))

def mark(act):
    if act is None:
        return "讀めず"
    for b in BORN:
        if act.startswith(b):
            return "誕生の印"
    return "印無し"

for label, grp in (("保つ88", keep), ("別刻145", late)):
    c = collections.Counter(mark(r[3]) for r in grp)
    print("道(b) %s の最古 entry: %s" % (label, dict(c)))
    born = [r for r in grp if mark(r[3]) == "誕生の印"]
    if born and T2:
        aft = [r for r in born if r[2] >= T2]
        print("      ―― 誕生の印 %d 本のうち ★T2 以降に生れた = %d 本★(∴ 切られたのでなく ★新しく生れた★)" % (len(born), len(aft)))
    nb = [r for r in grp if mark(r[3]) == "印無し"]
    ca = collections.Counter((r[3] or "").split(":")[0] for r in nb)
    print("      ―― 印無し %d 本の action 上位: %s" % (len(nb), ca.most_common(5)))

# 名の一覧を落とす（0 本でも落とす＝五条の親類）
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
path = OUT % stamp
with open(path, "w", encoding="utf-8") as f:
    f.write("# o113 誕生の印。列: 組 / 名 / 最古 entry の刻 / 印 / action / 讀めぬ理由\n")
    for grp, nm, t, act, why in rows:
        f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (grp, nm, iso(t) if t else "-", mark(act), (act or "-")[:80], why or "-"))
print("名の一覧: %s (%d 行)" % (path, len(rows) + 1))

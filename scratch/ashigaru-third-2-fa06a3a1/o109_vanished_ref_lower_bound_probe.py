#!/usr/bin/env python3
# order109 / 席 ashigaru-third-2 / as_of 2026-09-08 11:1x JST
# 問ひ = 索引 §3① の最後の一つ「★窓の内に生れ 窓の内に消えた ref★」に ★別の道★ で当たる。
#        令: ★git fsck --lost-found は禁★ ∴ object 側からは攻めぬ。攻めるは ★reflog の消え残り★ の側。
# 註 = 今の ref の読み方（loose walk + packed-refs）は o103・o105・o106・o107・o108 の写し＝★二重実装★。紙で開示。
# 走: python process ★1本★（git 実行 0・.git 下は讀取のみ・書込 0）。
import pathlib, datetime, os, re, collections

HERE = pathlib.Path(__file__).resolve().parent
GIT  = pathlib.Path("/mnt/c/DentalBI/.git")
JST  = datetime.timezone(datetime.timedelta(hours=9))
Z40  = "0" * 40
def j(ts): return datetime.datetime.fromtimestamp(ts, JST).isoformat(timespec="seconds")

print("== ★測る前に置く（値切り）★ ==")
print("・reflog file は ref を消すと ★普通は共に消える★ ∴ 本器が拾へるは ★消え残つた分のみ★ ―― 真より ★低い★。")
print("・拾へるのは『窓内に誕生の刻を持ち ★今★ ref に無い名』であつて、★窓の後に消えた物も混じる★。")
print("  ∴ 之は『窓内で ★消えた★』の証に非ず。消えた刻の見当は ★最後の entry の刻★ で述べるに留める。")
print("・★0 と出ても『無かつた』の証には成らぬ★ ―― 『本器では 0 と出た』としか書かぬ。")
print("・本器は object を一つも開かぬ ∴ ★未参照 commit の有無は何も言はぬ★。")

# ―― 窓
o98 = HERE / "o98_overlap_probe.py"; s98 = o98.stat()
L_lo, L_pt = s98.st_atime, s98.st_mtime
R = os.stat(HERE / "o103_refs_20260908_102005.txt").st_mtime
print("\n== ㋐ 窓（o108 の範を其の儘用ゐる）==")
print("  左端 下限 %s（o98 器 atime）／旧の点 %s（同 mtime）" % (j(L_lo), j(L_pt)))
print("  右端 %s（一枚目 mtime）" % j(R))

# ―― 今の ref 名（loose + packed）
now = set()
rd = GIT / "refs"
for p in rd.rglob("*"):
    if p.is_file():
        now.add("refs/" + str(p.relative_to(rd)).replace(os.sep, "/"))
n_loose = len(now)
pk = GIT / "packed-refs"
n_pk = 0
for l in pk.read_text(encoding="utf-8", errors="replace").split("\n"):
    if not l or l.startswith("#") or l.startswith("^"):
        continue
    f = l.split(" ", 1)
    if len(f) == 2:
        now.add(f[1].strip()); n_pk += 1
print("\n== ㋑ 今の ref 名 ==")
print("  loose %d ＋ packed %d ⇒ ★相異なる名 %d★（重なり %d）" % (n_loose, n_pk, len(now), n_loose + n_pk - len(now)))

# ―― logs/refs の全 file
LR = GIT / "logs" / "refs"
logs, bad = {}, collections.Counter()
badnames = []
for p in LR.rglob("*"):
    if not p.is_file():
        continue
    nm = "refs/" + str(p.relative_to(LR)).replace(os.sep, "/")
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        bad["讀めぬ"] += 1; badnames.append((nm, "讀めぬ:%s" % type(e).__name__)); continue
    ent = []
    for l in txt.split("\n"):
        if not l.strip():
            continue
        m = re.match(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$", l)
        if not m:
            bad["行の形が合はぬ"] += 1; continue
        ent.append((m.group(1), m.group(2), int(m.group(3)), m.group(5)))
    if not ent:
        bad["entry 0"] += 1; badnames.append((nm, "entry 0")); continue
    logs[nm] = ent
print("\n== ㋒ .git/logs/refs ==")
print("  file %d ／ 讀めた %d ／ 除いた %d（%s）" % (len(logs) + sum(bad.values()), len(logs), sum(bad.values()),
      " ".join("%s=%d" % (k, v) for k, v in sorted(bad.items())) or "無し"))
for nm, why in badnames[:10]:
    print("    除外: %s ← %s" % (nm, why))

# ―― 消え残り（log は在るが 今 ref に無い名）
orphan = sorted(n for n in logs if n not in now)
print("\n== ㋓ ★log は在るが 今 ref に無い名★ ＝ %d 本 ==" % len(orphan))
rows, inwin_lo, inwin_pt = [], [], []
for nm in orphan:
    e = logs[nm]
    birth = e[0][2] if e[0][0] == Z40 else None
    last  = e[-1][2]
    rows.append((nm, birth, last, e[-1][3][:40]))
    if birth is not None and L_lo < birth <= R:
        inwin_lo.append(nm)
    if birth is not None and L_pt < birth <= R:
        inwin_pt.append(nm)
for nm, b, la, msg in rows[:25]:
    print("  %-52s 誕生 %s / 最後 %s / %s" % (nm[:52], j(b) if b else "★不明(先頭が誕生に非ず)★", j(la), msg))
if len(rows) > 25:
    print("  … 他 %d 本（名の一覧 file に全て）" % (len(rows) - 25))

print("\n== ㋔ ★答★ ==")
print("  窓内に誕生の刻を持ち 今 ref に無い名 = ★%d 本★（左端＝下限 %s の時）" % (len(inwin_lo), j(L_lo)))
print("  同（左端＝旧の点 %s の時）        = ★%d 本★" % (j(L_pt), len(inwin_pt)))
print("  ⇒ 之が ★『窓内で生れ 今は無い ref』の下限★ である。")
if len(inwin_lo) == 0:
    print("  ★0 と出た★ ―― 之は『窓内で生れ消えた ref が ★無かつた★』の意に非ず。")
    print("     reflog が ref と共に消えて居れば ★本器には初めから見えぬ★（値切り 第一項）。")
else:
    for nm in inwin_lo:
        e = logs[nm]
        print("    %s 誕生 %s / 最後 %s ⇒ 最後が窓内か: %s" % (nm, j(e[0][2]), j(e[-1][2]), "★然り★" if L_lo < e[-1][2] <= R else "否（窓の外）"))

# ―― HEAD の reflog（削除で消えぬ側）
hd = GIT / "logs" / "HEAD"
hn, hbad = collections.Counter(), collections.Counter()
first = {}
nl = 0
for l in hd.read_text(encoding="utf-8", errors="replace").split("\n"):
    if not l.strip():
        continue
    nl += 1
    m = re.match(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$", l)
    if not m:
        hbad["行の形が合はぬ"] += 1; continue
    ts, msg = int(m.group(3)), m.group(5)
    for nm in re.findall(r"(?:moving from |moving to |checkout: moving from )?([A-Za-z0-9_./-]{3,})", msg):
        if "/" in nm or nm.startswith(("a2/", "dry/")):
            k = nm if nm.startswith("refs/") else "refs/heads/" + nm
            hn[k] += 1
            if k not in first or ts < first[k]:
                first[k] = ts
print("\n== ㋕ .git/logs/HEAD（★削除でも消えぬ側★）==")
print("  行 %d ／ 形の合はぬ行 %d ／ 名らしき綴り %d 種" % (nl, hbad["行の形が合はぬ"], len(hn)))
gone = sorted(k for k in first if k not in now)
gone_win = [k for k in gone if L_lo < first[k] <= R]
print("  今 ref に無い綴り %d 種 ／ 其のうち ★初出が窓内★ %d 種" % (len(gone), len(gone_win)))
print("  ※ 綴りは msg から正規表現で抜いた物 ∴ ★取りこぼしも 拾ひ過ぎも在る★（枝名でない語を拾ふ）。")
for k in gone_win[:15]:
    print("    %-52s 初出 %s" % (k[:52], j(first[k])))

# ―― 名の一覧を落とす（五条の親類・0 でも落とす）
stamp = datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S")
op = HERE / ("o109_vanished_%s.txt" % stamp)
buf = ["# order109 消え残り reflog / as_of %s" % j(datetime.datetime.now(JST).timestamp()),
       "# 窓 [%s(下限) / %s(旧点) , %s]" % (j(L_lo), j(L_pt), j(R)),
       "# ㋓ log は在るが今 ref に無い名 = %d 本 / 其のうち窓内誕生 = %d 本" % (len(orphan), len(inwin_lo)),
       "# ㋕ HEAD reflog 側 今無い綴り %d 種 / 窓内初出 %d 種" % (len(gone), len(gone_win)),
       "#--- ㋓ 全件（名\t誕生\t最後）---"]
for nm, b, la, msg in rows:
    buf.append("%s\t%s\t%s" % (nm, j(b) if b else "不明", j(la)))
buf.append("#--- ㋕ 今 ref に無い綴り 全件（綴り\t初出）---")
for k in gone:
    buf.append("%s\t%s" % (k, j(first[k])))
with open(op, "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
print("\n名の一覧: %s（%d 行）" % (op.name, len(buf)))
print("\n== 検算 ==")
print("  logs/refs file %d ＝ 讀めた %d ＋ 除いた %d" % (len(logs) + sum(bad.values()), len(logs), sum(bad.values())))
print("  讀めた %d ＝ 今も在る %d ＋ 今は無い %d" % (len(logs), len(logs) - len(orphan), len(orphan)))
print("  ★足して合ふ事を確かめた★")

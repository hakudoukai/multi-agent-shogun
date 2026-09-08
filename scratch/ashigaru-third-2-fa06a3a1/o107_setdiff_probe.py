#!/usr/bin/env python3
# order107 / 席 ashigaru-third-2 / as_of 2026-09-08 11:0x JST
# 問ひ = 「334→346 の ★増えた 12 本★」と「窓の内に生れた 12 本（o104/o105）」は ★同集合か★。
# 手 = 一枚目 346 本の各 ref を ★窓で生れたか否か★ で分ける。
#      刻の器 三種（優先順）: ①reflog の初出刻 ②loose file の mtime ③packed-refs に載る（= 畳んだ刻 08:44:30 に在つた = 窓より前）
# 註 = 分類の規則（讀めた/空/tab 無し/file 無し）と loose/packed の当て方は ★o105・o106 の写し＝二重実装★。紙で開示する。
# 走: python process ★1本★（git 実行 0 ―― .git 下を file として讀むのみ・書込 0）。
import pathlib, datetime, os, hashlib

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path("/mnt/c/DentalBI")
GIT  = REPO / ".git"
LOGS = GIT / "logs"
JST  = datetime.timezone(datetime.timedelta(hours=9))
def j(ts): return datetime.datetime.fromtimestamp(ts, JST).isoformat(timespec="seconds")

ONE = HERE / "o103_refs_20260908_102005.txt"          # 一枚目（346 本）
L = os.stat(HERE / "o98_overlap_probe.py").st_mtime   # 窓 左端（代用）
R = os.stat(ONE).st_mtime                             # 窓 右端 ＝ ★一枚目の mtime★（本弾は 10:05:38 でなく 10:20:05）

print("== 窓（本弾は右端を ★一枚目の刻★ に取る ―― 比べる相手が 334→346 ゆゑ）==")
print("左端 %s（代用・o98 の器 mtime）/ 右端 %s（一枚目 mtime）" % (j(L), j(R)))

print("\n== ★測る前に置く（値切り）★ ==")
print("・窓の内に生れて ★窓の内に消えた★ ref は 名が残らぬ ∴ 本器には掛からぬ。")
print("・同じく ★窓の左端に在つて 一枚目より前に消えた★ ref も 名が残らぬ（＝下の D）。")
print("・∴ ★復元率 100 でなければ 同集合の証にはならぬ★ ―― 数が合うても『合うた』としか書かぬ。")
print("・左端は今も ★代用★（o98 が生出力を残さなんだ）。")

names = [l.split("\t")[0] for l in ONE.read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]
print("\n== 一枚目 ==")
print("ref %d 本 / file %s" % (len(names), ONE.name))

# packed-refs（畳んだ刻と 載る ref）
pr = GIT / "packed-refs"
pm = pr.stat().st_mtime
packed = set()
for line in pr.read_text(errors="replace").split("\n"):
    if not line or line.startswith("#") or line.startswith("^"):
        continue
    part = line.split(" ", 1)
    if len(part) == 2:
        packed.add(part[1].strip())
print("packed-refs mtime %s / 載る ref %d 本" % (j(pm), len(packed)))
assert pm < L, "畳んだ刻が窓の左端より後 ―― 本器は何も決めぬ"

born, pre, unknown = [], [], []
by = {"reflog": 0, "loose": 0, "packed": 0}
for n in names:
    t = None; how = None
    p = LOGS / n
    if p.is_file() and p.stat().st_size > 0:
        head = p.read_text(errors="replace").split("\n")[0]
        if "\t" in head:
            pre_f = head.split("\t")[0].split()
            try:
                t, how = int(pre_f[-2]), "reflog"
            except Exception:
                t, how = None, None
    if t is None:
        q = GIT / n
        if q.is_file():
            t, how = q.stat().st_mtime, "loose"
    if t is None and n in packed:
        pre.append((n, "packed")); by["packed"] += 1; continue
    if t is None:
        unknown.append(n); continue
    by[how] += 1
    (born if L < t <= R else pre).append((n, how))

print("\n== 分け（一枚目 346 本）==")
print("窓の内に生れた   : %d 本" % len(born))
print("窓より前から在つた: %d 本" % len(pre))
print("★何れの器でも決まらぬ★: %d 本" % len(unknown))
print("合計 %d ＝ 一枚目 %d（★足して合ふ事を確かめた★）" % (len(born) + len(pre) + len(unknown), len(names)))
print("刻の出所: reflog %d / loose %d / packed(前と決まる) %d" % (by["reflog"], by["loose"], by["packed"]))

print("\n== 窓の内に生れた ref の名 ==")
for n, how in sorted(born):
    print("  %-72s %s" % (n, how))

# 本弾の 12（o105 が出した名）と引く ―― o105 は名を file に残さなんだゆゑ 二枚目から同じ規則で作り直す
NEW = HERE / "o103_refs_20260908_102945.txt"
R2 = os.stat(HERE / "o102_run1_raw.txt").st_mtime
prev = set()
for l in NEW.read_text(encoding="utf-8").split("\n"):
    if not l or l.startswith("#"):
        continue
    n = l.split("\t")[0]
    t = None
    p = LOGS / n
    if p.is_file() and p.stat().st_size > 0:
        head = p.read_text(errors="replace").split("\n")[0]
        if "\t" in head:
            f = head.split("\t")[0].split()
            try:
                t = int(f[-2])
            except Exception:
                t = None
    if t is None:
        q = GIT / n
        if q.is_file():
            t = q.stat().st_mtime
    if t is not None and L < t <= R2:
        prev.add(n)

A = set(n for n, _ in born); B = prev
print("\n== 引き（本弾＝前弾の 12 と）==")
print("本弾(右端 %s) %d 本 / 前弾(右端 %s) %d 本" % (j(R), len(A), j(R2), len(B)))
print("両方に在る %d / 本弾のみ %d / 前弾のみ %d" % (len(A & B), len(A - B), len(B - A)))
for n in sorted(A - B): print("  ＋本弾のみ %s" % n)
for n in sorted(B - A): print("  ＋前弾のみ %s" % n)

print("\n== 334 との突き合はせ ==")
S = len(names) - len(born)
print("窓の左端に在つて 一枚目迄 生き残つた ref S = 346 - %d = %d" % (len(born), S))
print("o98 が数へた 334 との差 D = 334 - S = %d  … ★窓の左端に在つて 一枚目より前に消えた ref の数★" % (334 - S))
print("（D は数のみ ―― ★名は残らぬ★。D が 0 でなければ『増えた 12 本＝生れた %d 本』とは言へぬ）" % len(born))

out = HERE / ("o107_born_%s.txt" % datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S"))
body = "".join("%s\t%s\n" % (n, how) for n, how in sorted(born))
out.write_text("# 窓 %s 〜 %s に生れた ref / %d 本\n# 器 o107_setdiff_probe.py\n" % (j(L), j(R), len(born)) + body, encoding="utf-8")
print("\n名の一覧: %s / %d 行 / %s" % (out.name, len(body.split("\n")) + 1, hashlib.sha256(out.read_bytes()).hexdigest()[:16]))
print("決まらぬ %d 本（在れば名を下に）" % len(unknown))
for n in sorted(unknown): print("  ? %s" % n)

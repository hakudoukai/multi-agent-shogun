#!/usr/bin/env python3
# order105 / 席 ashigaru-third-2 / as_of 2026-09-08 10:4x JST
# 為す = o104 の疵の cure 三つ:
#  (1) ★黙りを止める★ ―― 讀めなんだ reflog を「数」だけでなく ★理由別に分けて 名も刷る★
#      （空 0byte / 一行目に tab 無し / 其の他の例外）。o104 は except: continue で 112 本を黙つて落とした。
#  (2) ★窓の右端を切り直す★ ―― o102 の「便の刻(10:03 頃)」を止め、生出力 o102_run1_raw.txt の ★mtime★ を使ふ。
#      左端は o98 の器 mtime のまま（o98 は生出力を残さなんだ ―― ★之も己の疵★）。
#  (3) ★刻を持たぬ ref を当て直す★ ―― reflog が空/無い ref は .git/refs 下の ★loose file の mtime★ で当てる。
#      ★mtime は「書かれた刻」であり「生れた刻」ではない（上書きで動く）★ ―― ★代用である事を先に書く★。
#      packed-refs に畳まれた ref は loose file を持たぬ ∴ ★何れの器でも刻を持たぬ★ = 判定不能として数へる。
# 問ひ = 之で ★12 本★ は動くか。
# 走: python process ★1本★（内で git 讀取のみ）。
import subprocess, pathlib, datetime, os

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path("/mnt/c/DentalBI")
LOGS = REPO / ".git" / "logs"
JST  = datetime.timezone(datetime.timedelta(hours=9))
def j(ts): return datetime.datetime.fromtimestamp(ts, JST).isoformat(timespec="seconds")

L = os.stat(HERE / "o98_overlap_probe.py").st_mtime          # 窓の左端（代用・o98 は生出力無し）
R = os.stat(HERE / "o102_run1_raw.txt").st_mtime             # 窓の右端（★生出力の mtime＝走了の刻に最も近い★）
print("== 窓 ==")
print("左端 = %s ★代用（o98 の器 mtime ―― o98 は生出力を残さなんだ＝己の疵）★" % j(L))
print("右端 = %s ★o102 の生出力 mtime（前回は便の刻 10:03 頃を使つた ―― 今回 切り直した）★" % j(R))
print("差 = %.1f 分（前回の窓は およそ 44 分・今回 %.1f 分）" % ((R-L)/60.0, (R-L)/60.0))

# ―― 現 ref（二枚目を正とする。本弾では新たに落とさぬ＝走を増やさぬ為）
NEW = HERE / "o103_refs_20260908_102945.txt"
cur = [l.split("\t")[0] for l in NEW.read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]
print("\n== 現 ref = %d 本（二枚目 %s を正とする） ==" % (len(cur), NEW.name))

# ―― (1) reflog を讀む・★落とした物を理由別に★
first, empty, notab, other, absent = {}, [], [], [], []
for name in cur:
    p = LOGS / name
    if not p.is_file():
        absent.append(name); continue
    try:
        raw = p.read_text(errors="replace")
    except Exception as e:
        other.append((name, "read:%s" % type(e).__name__)); continue
    if p.stat().st_size == 0 or not raw.strip():
        empty.append(name); continue
    head = raw.split("\n")[0]
    if "\t" not in head:
        notab.append(name); continue
    try:
        pre = head.split("\t")[0].split()
        first[name] = int(pre[-2])
    except Exception as e:
        other.append((name, "parse:%s" % type(e).__name__))
print("== (1) reflog の内訳（★落とした物も名で刷る★） ==")
print("初出刻を讀めた = ★%d★ / 空(0byte) = ★%d★ / 一行目に tab 無し = ★%d★ / file 其の物が無い = ★%d★ / 其の他の例外 = ★%d★"
      % (len(first), len(empty), len(notab), len(absent), len(other)))
print("  合計 %d ＝ 現 ref %d（★足して合ふ事を確かめた★）" % (len(first)+len(empty)+len(notab)+len(absent)+len(other), len(cur)))
for lab, arr in (("空(0byte)", empty), ("tab 無し", notab), ("file 無し", absent)):
    print("  -- %s の名（先頭 8）: %s%s" % (lab, ", ".join(arr[:8]) if arr else "★0 件★", " …他 %d" % (len(arr)-8) if len(arr) > 8 else ""))
if other:
    print("  -- 其の他: %s" % other)

# ―― (2) 窓で切る（reflog 由来）
in_log = sorted([(n, t) for n, t in first.items() if L < t <= R], key=lambda x: x[1])
print("\n== (2) reflog の初出刻で 窓に入る ref = ★%d 本★ ==" % len(in_log))
for n, t in in_log:
    print("   %s  (%s)" % (n, j(t)))

# ―― (3) 刻を持たぬ ref を loose file の mtime で当て直す
undated = empty + notab + absent + [n for n, _ in other]
in_loose, dated_loose, no_file = [], 0, []
for n in undated:
    p = REPO / ".git" / n
    if p.is_file():
        dated_loose += 1
        m = p.stat().st_mtime
        if L < m <= R:
            in_loose.append((n, m))
    else:
        no_file.append(n)
in_loose.sort(key=lambda x: x[1])
print("\n== (3) 刻を持たぬ %d 本を loose file の mtime で当て直す ==" % len(undated))
print("loose file が在り刻を当てられた = ★%d★ / packed 等で loose file が無く ★何れの器でも刻を持たぬ★ = ★%d★" % (dated_loose, len(no_file)))
print("うち 窓に入る = ★%d 本★%s" % (len(in_loose), "（0 件）" if not in_loose else ""))
for n, m in in_loose:
    print("   %s  (loose mtime %s)" % (n, j(m)))
print("★註★ mtime は ★書かれた刻★ ―― 上書きでも動く ∴ 『生れた刻』の ★代用★ である。")

print("\n== 答 ==")
print("前回（o104）= ★12 本★（窓の右端＝便の刻・reflog のみ・空 log は黙つて落ちた）")
print("今回（o105）= reflog 由来 ★%d 本★ ＋ loose mtime 由来 ★%d 本★ ＝ ★%d 本★" % (len(in_log), len(in_loose), len(in_log)+len(in_loose)))
print("★何れの器でも刻を持たぬ ref が %d 本 在る ∴ 本数は なほ ★下振れ★ である。★" % len(no_file))

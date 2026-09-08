#!/usr/bin/env python3
# order104 / 席 ashigaru-third-2 / as_of 2026-09-08 10:3x JST
# 為す 三つ:
#  (A) 二枚目の ref 名 file を落とす ―― ★o103 の器を再走させる★（写さぬ＝二重実装 0）。
#  (B) 紙 §10-2 の三つ（comm -13 / comm -23 / join+awk）を ★逐語で実走★ し、名を引けるかを確かめる。
#      ★0 件なら 0 件と書く（空欄にせぬ）。★
#  (C) 「334→346 の 12 本の名」が ①原理として復せぬ / ②残さなんだ(復せる) / ③未だ測らぬ の何れかを ★測る★。
#      測り方 = 各 ref の reflog の ★初出の刻★ を讀み、o98 の刻より後に生れた ref を名で拾ふ。
#      o98 の刻 = 器 o98_overlap_probe.py の mtime（★代用★・o98 は刻を残さなんだゆゑ）。
# 走: python process ★1本★。内で git(讀取)・bash(comm/join) を呼ぶが器は 1 本 ―― o101/o102 と同じ数へ方。
import subprocess, pathlib, hashlib, datetime, os

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path("/mnt/c/DentalBI")
OLD  = HERE / "o103_refs_20260908_102005.txt"
ZERO = "0" * 40

def sh(cmd):
    return subprocess.run(["/bin/bash", "-c", cmd], capture_output=True, text=True)

print("== (A) 二枚目を落とす（o103 の器を再走） ==")
r = subprocess.run(["/usr/bin/python3", str(HERE / "o103_ref_names_dump.py")], capture_output=True, text=True)
print(r.stdout.strip())
new_name = [l.split("= ")[1] for l in r.stdout.split("\n") if l.startswith("落とした file 名")][0]
NEW = HERE / new_name
print("一枚目 = %s / 二枚目 = %s" % (OLD.name, NEW.name))
print("間隔 = %.1f 分" % ((NEW.stat().st_mtime - OLD.stat().st_mtime) / 60.0))

print()
print("== (B) 紙 §10-2 の三つを逐語で実走 ==")
o, n = str(OLD), str(NEW)
cmds = [
 ("㋑ 増えた ref の名", "comm -13 <(grep -v '^#' %s | cut -f1 | sort) <(grep -v '^#' %s | cut -f1 | sort)" % (o, n)),
 ("㋺ 消えた ref の名", "comm -23 <(grep -v '^#' %s | cut -f1 | sort) <(grep -v '^#' %s | cut -f1 | sort)" % (o, n)),
 ("㋩ 名は同じで先が動いた ref",
  "join -t$'\\t' <(grep -v '^#' %s | sort) <(grep -v '^#' %s | sort)"
  " | awk -F'\\t' '$2!=$3 {print $1\"  \"substr($2,1,9)\" -> \"substr($3,1,9)}'" % (o, n)),
]
for label, c in cmds:
    res = sh(c)
    lines = [x for x in res.stdout.split("\n") if x.strip()]
    print("-- %s : rc=%d / ★%d 件★%s" % (label, res.returncode, len(lines), "（0 件）" if not lines else ""))
    for x in lines[:20]:
        print("   %s" % x)
    if len(lines) > 20:
        print("   …他 %d 件" % (len(lines) - 20))
    if res.stderr.strip():
        print("   stderr: %s" % res.stderr.strip()[:200])

print()
print("== (C) 12 本の名は ①/②/③ の何れか ―― reflog の初出刻で測る ==")
T98 = os.stat(HERE / "o98_overlap_probe.py").st_mtime
print("o98 の刻（代用＝器の mtime）= %s" % datetime.datetime.fromtimestamp(T98, datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds"))
LOGS = REPO / ".git" / "logs"
first = {}
for p in LOGS.rglob("*"):
    if not p.is_file():
        continue
    rel = p.relative_to(LOGS).as_posix()
    if rel == "HEAD":
        continue
    try:
        head_line = p.read_text(errors="replace").split("\n")[0]
    except Exception:
        continue
    try:
        pre = head_line.split("\t")[0].split()
        first["refs/" + rel if not rel.startswith("refs/") else rel] = (int(pre[-2]), pre[0])
    except Exception:
        continue
cur = [l.split("\t")[0] for l in NEW.read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]
born_after, before, no_log = [], [], []
for name in cur:
    key = name if name.startswith("refs/") else name
    if key in first:
        (ts, old0) = first[key]
        (born_after if ts > T98 else before).append((name, ts))
    else:
        no_log.append(name)
print("現 ref = %d 本 / reflog 初出を讀めた = %d / reflog 無し = ★%d★" % (len(cur), len(cur) - len(no_log), len(no_log)))
print("o98 の刻より ★後に生れた★ ref = ★%d 本★%s" % (len(born_after), "（0 件）" if not born_after else ""))
for name, ts in sorted(born_after, key=lambda x: x[1]):
    print("   %s  (初出 %s)" % (name, datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")))
print("o98 の刻より前から在つた ref = %d 本" % len(before))
print("★註★ 本測は ★今 在る ref★ しか見ぬ ―― o98 以後に生れて ★既に消えた★ ref は reflog ごと失せ、名を挙げられぬ（下振れ）。")
print("★註★ reflog 無き %d 本は 初出刻を持たぬゆゑ ★何れとも決まらぬ★（判定不能）。" % len(no_log))

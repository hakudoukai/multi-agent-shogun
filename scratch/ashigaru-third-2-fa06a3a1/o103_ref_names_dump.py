#!/usr/bin/env python3
# order103 / 席 ashigaru-third-2 / as_of 2026-09-08 10:1x JST
# 為す: 局所 ref の ★名★ を証拠 file に落とす（o98・o102 が ★数だけ残して名を残さなんだ★ 疵の埋め＝§9-5）。
# 形: 1 行 = "<refname>\t<sha40>"。★refname 昇順★（diff が安定する為）。頭に # で刻と本数を書く。
# 走: python process ★1本★。git は for-each-ref の讀取のみ（書込動詞 0）。
import subprocess, datetime, pathlib, hashlib

REPO = "/mnt/c/DentalBI"
OUT  = pathlib.Path(__file__).resolve().parent

def git(*a):
    return subprocess.run(["/usr/bin/git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout

now  = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
rows = []
for l in git("for-each-ref", "--format=%(objectname) %(refname)").split("\n"):
    if l:
        sha, name = l.split(" ", 1)
        rows.append((name, sha))
rows.sort(key=lambda x: x[0])

stamp = now.strftime("%Y%m%d_%H%M%S")
path  = OUT / ("o103_refs_%s.txt" % stamp)
body  = "".join("%s\t%s\n" % (n, s) for n, s in rows)
head  = ("# 局所 ref の名 ―― 刻の写し / as_of %s / 本数 %d\n"
         "# 1 行 = <refname>\\t<sha40>・refname 昇順。★取つた後に増えた分は入らぬ★。\n"
         "# 引き方は 紙 after_delete_5668_gap_1483_readonly_v1.md §10 に在り。\n") % (now.isoformat(timespec="seconds"), len(rows))
path.write_text(head + body, encoding="utf-8")

d = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
print("落とした file 名 = %s" % path.name)
print("本数 = ★%d 本★ / 行数 = %d（頭の註 3 行を含む） / sha256:16 = %s" % (len(rows), head.count("\n") + len(rows), d))
pre = {}
for n, _ in rows:
    k = "/".join(n.split("/")[:3]) if n.startswith("refs/remotes/") else "/".join(n.split("/")[:2])
    pre[k] = pre.get(k, 0) + 1
print("前置き別: " + ", ".join("%s=%d" % kv for kv in sorted(pre.items(), key=lambda x: -x[1])))
print("★本器は名を落とすのみ ―― 増減の判定は為して居らぬ（比べる相手が無い＝之が一枚目ゆゑ）。★")

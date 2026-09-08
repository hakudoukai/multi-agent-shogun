#!/usr/bin/env python3
# order96 / 席 ashigaru-third-2 / as_of 2026-09-08 09:0x JST
# 問: o85 §1 の index 基準 4,113 は、tree 基準でも出るか。
#   08faa1939(§6 の最後の commit・A=13,991 と同じ時点)の tree に同じ判定を当てて N を出す。
#   4,113 なら 10 は ★commit の差★ / 4,103 なら 10 は ★index 特有★ と二分する。
# 借り: order48_n_by_commit.py の L1-40（git / consts / g2re）を exec で再利用。★元器は不書換★。
# 写し: 判定 3 段は同器 count() L47-56 の逐語（keep を集合で返す形にのみ変へた）＝二重実装ゆゑ開示。
# 走: python process ★1本★。git は ls-tree / show / rev-parse の讀取のみ（書込動詞 0）。
import pathlib, fnmatch, hashlib

SRCF = pathlib.Path("/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/order48_n_by_commit.py")
borrowed = "\n".join(SRCF.read_text(encoding="utf-8").split("\n")[0:40])
ns = {}
exec(compile(borrowed, str(SRCF), "exec"), ns)
git, consts, g2re = ns["git"], ns["consts"], ns["g2re"]

def keep_set(paths, c):
    inc = [g2re(p) for p in c.get("INCLUDE_PATTERNS", [])]
    exc = list(c.get("EXCLUDE_PATTERNS", []))
    exd = set(c.get("EXCLUDE_DIRS", set()) or set())
    out = set()
    for rel in paths:
        if exd and any(part in exd for part in rel.split("/")):
            continue
        if not any(r.match(rel) for r in inc):
            continue
        if any(fnmatch.fnmatch(rel, p) for p in exc):
            continue
        out.add(rel)
    return out

C = consts("origin/main")   # o95b で「定数は全 commit 逐語同一」と確かめ済
A = "08faa1939"             # o85 §1/§6 の時点
B = "56b63eb13"             # 今の HEAD（§13-1 で 4,103 と測つた）

res = {}
for c in (A, B):
    tree = [l for l in git("ls-tree", "-r", "--name-only", c).split("\n") if l]
    k = keep_set(tree, C)
    res[c] = (len(tree), k)
    print("commit %s : tree 全 path=%d / INCLUDE 通過 N=%d" % (c, len(tree), len(k)))

ka, kb = res[A][1], res[B][1]
only_a = sorted(ka - kb)
only_b = sorted(kb - ka)
print("★%s のみ★ 本数=%d" % (A, len(only_a)))
for p in only_a:
    print("   A> " + p)
print("★%s のみ★ 本数=%d" % (B, len(only_b)))
for p in only_b:
    print("   B> " + p)
print("差の絶対値 |A|-|B| = %d" % (len(ka) - len(kb)))

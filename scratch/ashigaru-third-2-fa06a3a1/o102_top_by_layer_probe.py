#!/usr/bin/env python3
# order102 / 席 ashigaru-third-2 / as_of 2026-09-08 10:0x JST
# 問: 紙 §6 で出した ㋑∪㋺（＝1,589・334 ref 期）の ★先頭階層別★ を、
#     §7-4 の SELECT③ と ★同じ形（top / rows・rows 降順）★ で出す。
# ★出る値は「今の ref 数での値」である。1,589 は 09-08 09:2x（334 ref）の数 ―― ★同じ物差しではない★。★
# 借り: order48_n_by_commit.py の L1-40（git / consts / g2re）を exec で再利用。★元器は不書換★。
# 写し: keep()/tree()/判定 3 段は o98_overlap_probe.py の逐語＝二重実装ゆゑ開示。
# 走: python process ★1本★。git は for-each-ref / rev-parse / ls-tree / log / show の讀取のみ（書込動詞 0）。
import pathlib, fnmatch, collections

SRCF = pathlib.Path("/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/order48_n_by_commit.py")
ns = {}
exec(compile("\n".join(SRCF.read_text(encoding="utf-8").split("\n")[0:40]), str(SRCF), "exec"), ns)
git, consts, g2re = ns["git"], ns["consts"], ns["g2re"]

C = consts("origin/main")
INC = [g2re(p) for p in C.get("INCLUDE_PATTERNS", [])]
EXC = list(C.get("EXCLUDE_PATTERNS", []))
EXD = set(C.get("EXCLUDE_DIRS", set()) or set())

def keep(paths):
    out = set()
    for rel in paths:
        if not rel: continue
        if EXD and any(part in EXD for part in rel.split("/")): continue
        if not any(r.match(rel) for r in INC): continue
        if any(fnmatch.fnmatch(rel, p) for p in EXC): continue
        out.add(rel)
    return out

def tree(c):
    return [l for l in git("ls-tree", "-r", "--name-only", c).split("\n") if l]

refs = [l.split(" ", 1)[1] for l in git("for-each-ref", "--format=%(objectname) %(refname)").split("\n") if l]
N = len(refs)
print("=" * 78)
print("★本器の値は【今の ref 数での値】である。★ 局所 ref = ★%d 本★（o98 の時は 334 本・§3 の時は 226 本）" % N)
print("=" * 78)

M = keep(tree("origin/main"))
H = keep(tree("HEAD"))
U = set()
miss = 0
for r in refs:
    try:
        U |= keep(tree(r))
    except Exception:
        miss += 1
I1 = U - M
dele = set(l for l in git("log", "--all", "--diff-filter=D", "--pretty=format:", "--name-only").split("\n") if l)
I2 = keep(dele) - H
both, uni = I1 & I2, I1 | I2
print("\n[1] M=%d H=%d U=%d（讀めなんだ ref %d）" % (len(M), len(H), len(U), miss))
print("[2] ㋑=%d ㋺=%d ㋑∩㋺=%d ★㋑∪㋺=%d★" % (len(I1), len(I2), len(both), len(uni)))

def table(name, s):
    c = collections.Counter(p.split("/")[0] for p in s)
    print("\n―― %s（計 %d）―― SELECT③ と同じ形 ――" % (name, len(s)))
    print("%-28s | %6s | %-19s | %-19s" % ("top", "rows", "oldest", "newest"))
    print("-" * 28 + "-+-" + "-" * 6 + "-+-" + "-" * 19 + "-+-" + "-" * 19)
    for k, v in sorted(c.items(), key=lambda x: (-x[1], x[0])):
        print("%-28s | %6d | %-19s | %-19s" % (k, v, "(git に無し)", "(git に無し)"))
    print("%-28s | %6d |" % ("★合計★", sum(c.values())))
    return c

cu  = table("★㋑∪㋺（本弾の答）★", uni)
ci  = table("㋑ 他枝のみ", I1)
cr  = table("㋺ 履歴 D で消え現 tree に無い", I2)
cb  = table("㋑∩㋺ 重なり", both)

print("\n[3] ★八条目 ―― 物差しが動いた分を分ける★")
print("    o98（09-08 09:2x・334 ref）: ㋑=1,422 ㋺=361 ∩=194 ∪=1,589")
print("    本弾（%s ref）           : ㋑=%d ㋺=%d ∩=%d ∪=%d" % (N, len(I1), len(I2), len(both), len(uni)))
print("    差                        : ㋑=%+d ㋺=%+d ∩=%+d ∪=%+d"
      % (len(I1) - 1422, len(I2) - 361, len(both) - 194, len(uni) - 1589))
print("    ★o98 の ∩ 階層別: .claude=153 / frontend=32 / backend=8 / tests=1★")
print("    本弾の ∩ 階層別: " + ", ".join("%s=%d" % kv for kv in sorted(cb.items(), key=lambda x: -x[1])))
print("    ★開示: o98 は ref 名の一覧を残さぬ ∴『どの ref が増えたか』は名指せぬ（五条の教への繰り返し）★")
print("\n[4] SELECT③ と突き合はせる者へ: `oldest`/`newest` は ★git からは出ぬ★（v3 の `updated_at` は DB 側の列）。")
print("    ★本表の rows は path 1 本の数。SELECT③ の rows は行 1 行の数 ―― ★元素が違ふ（四条③）★ ∴ 引き算はするな。★")
print("    突き合はせて可なるは ★層の形（どの top が厚いか）★ のみ。")

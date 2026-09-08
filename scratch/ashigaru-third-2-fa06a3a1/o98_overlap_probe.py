#!/usr/bin/env python3
# order98 (E) / 席 ashigaru-third-2 / as_of 2026-09-08 09:2x JST
# 問: after_delete_5668_gap_1483_readonly_v1.md §3 の ㋑(他枝のみ 1,442) と ㋺(履歴 D で消えた 357) の
#     ★重なり★ は何本か。§3 は「㋑ と重なる分が在る」と書いたのみで ★数へて居らぬ★。
# ★開示★: order50 の器は手元に残つて居らぬ ―― ★索引 §3 の ②「失せた(五条違背)」の二例目★。
#          ゆゑに本器は ★書き直し★ である。§3 の数が再現するか否かも併せて見る。
# 借り: order48_n_by_commit.py の L1-40（git / consts / g2re）を exec で再利用。★元器は不書換★。
# 写し: 判定 3 段は同器 count() L47-56 の逐語（集合で返す形にのみ変へた）＝二重実装ゆゑ開示。
# 走: python process ★1本★。git は for-each-ref / ls-tree / log / rev-parse の讀取のみ（書込動詞 0）。
import pathlib, fnmatch

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

# ―― 主 tip と 現 HEAD
main_tip = git("rev-parse", "origin/main").strip()
head     = git("rev-parse", "HEAD").strip()
print("origin/main=%s  HEAD=%s  同一=%s" % (main_tip[:9], head[:9], main_tip == head))
M = keep(tree("origin/main"))
H = keep(tree("HEAD"))
print("main tip の INCLUDE 通過 M=%d / HEAD の INCLUDE 通過 H=%d" % (len(M), len(H)))

# ―― 局所 ref を合併（§3 の「226 ref」を数へ直す）
refs = [l.split(" ", 1)[1] for l in git("for-each-ref", "--format=%(objectname) %(refname)").split("\n") if l]
print("局所 ref 本数=%d" % len(refs))
U = set()
for r in refs:
    try:
        U |= keep(tree(r))
    except Exception:
        pass
print("226ref 合併の INCLUDE 集合 U=%d   （§3 の記載 5,627）" % len(U))

# ―― ㋑ = U − main tip
I1 = U - M
print("★㋑ 他枝のみ★ = %d   （§3 の記載 1,442）" % len(I1))

# ―― ㋺ = 履歴上 D で消え、現 tree に無い INCLUDE path
dele = set(l for l in git("log", "--all", "--diff-filter=D", "--pretty=format:", "--name-only").split("\n") if l)
I2 = keep(dele) - H
print("★㋺ 履歴 D で消え 現 tree に無い★ = %d   （§3 の記載 357）" % len(I2))

# ―― ★重なり★
both = I1 & I2
print("★★㋑ ∩ ㋺ = %d★★" % len(both))
print("㋑ のみ = %d / ㋺ のみ = %d / 和(重複を除く) = %d" % (len(I1 - I2), len(I2 - I1), len(I1 | I2)))
tops = {}
for p in sorted(both):
    k = p.split("/")[0]
    tops[k] = tops.get(k, 0) + 1
print("重なりの先頭階層別: " + ", ".join("%s=%d" % kv for kv in sorted(tops.items(), key=lambda x: -x[1])))

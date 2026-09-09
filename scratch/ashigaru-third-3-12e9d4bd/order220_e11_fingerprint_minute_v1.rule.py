# -*- coding: utf-8 -*-
u"""E11: gap_fill2 の集合指紋を ★分〜時の桁★ で当て直す。
讀取のみ・的の樹の code を一行も exec せぬ・書込は生 raw のみ・DB 0・走行(製品) 0。
★器を一字も変へぬ★ 為、走査の本体は o194 の source から ★逐語で切り出して exec★ する。
"""
import io, os, sys, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "order194_gap_fill2_v1.rule.py")

PREV_UNREAD = "98ea6880df4aca4454c194c2e207b8c8f56386715b826ddb71497c287bf5496f"
PREV_READ = "87d7df477eb766f8bdcd11fac49ab3cc67a95c27b035f3ee57fb58a15abb0435"
PREV_N_UNREAD = 1340
PREV_N_READ = 15632
PREV_WALKED = 16972
PREV_AS_OF = "2026-09-08T21:39:59+0900"

src = io.open(SRC, encoding="utf-8").read()
lines = src.split(chr(10))
seg = chr(10).join(lines[4:21])
assert seg.startswith("import os, io, hashlib"), "SEG_HEAD_MISS"
assert seg.rstrip().endswith("return walked, ok, bad"), "SEG_TAIL_MISS"
seg_sha = hashlib.sha256(seg.encode("utf-8")).hexdigest()

ns = {"__name__": "__o220_walker__"}
exec(compile(seg, SRC, "exec"), ns)
TREE = ns["TREE"]
assert TREE == "/home/hakudoukai/a3/wt-bundle-fix4", "TREE_MISMATCH"

out = []
def w(x):
    out.append(x)

w(u"## §A 切り出した走査本体（★o194 の source から逐語★）")
w(u"src_path=" + os.path.relpath(SRC, HERE))
w(u"src_lines_split=" + str(len(lines)))
w(u"seg_lines=5..21 (1 始まり)  seg_split=" + str(len(seg.split(chr(10)))))
w(u"seg_sha256=" + seg_sha)
w(u"seg_head=" + repr(seg.split(chr(10))[0]))
w(u"seg_tail=" + repr(seg.rstrip().split(chr(10))[-1]))
w(u"TREE=" + TREE)
w(u"SKIPD_n=" + str(len(ns["SKIPD"])))
w(u"")

w(u"## §B 走査（同じ走の中で二度・o194 と同じ形）")
w1, ok1, bad1 = ns["pass_once"]()
w2, ok2, bad2 = ns["pass_once"]()
w(u"walked: 1st=" + str(w1) + u" 2nd=" + str(w2) + u"  同じ=" + str(w1 == w2))
w(u"readable: 1st=" + str(len(ok1)) + u" 2nd=" + str(len(ok2)))
w(u"unreadable: 1st=" + str(len(bad1)) + u" 2nd=" + str(len(bad2)))
a_only = sorted(ok1 - ok2); b_only = sorted(ok2 - ok1)
w(u"秒の桁の揺れ: 1st_only=" + str(len(a_only)) + u" 2nd_only=" + str(len(b_only)))
w(u"")

w(u"## §C 指紋（o194 §三 と同じ算き方）")
h = hashlib.sha256(); h.update(chr(10).join(sorted(bad1)).encode("utf-8"))
cur_unread = h.hexdigest()
h2 = hashlib.sha256(); h2.update(chr(10).join(sorted(ok1)).encode("utf-8"))
cur_read = h2.hexdigest()
w(u"unreadable_set_sha256=" + cur_unread + u"  n=" + str(len(bad1)))
w(u"readable_set_sha256=" + cur_read + u"  n=" + str(len(ok1)))
w(u"")

w(u"## §D 前の刻との突合（★分〜時の桁★）")
try:
    t0 = datetime.datetime.strptime(PREV_AS_OF, "%Y-%m-%dT%H:%M:%S%z")
    t1 = datetime.datetime.now(t0.tzinfo)
    gap = t1 - t0
    gap_s = int(gap.total_seconds())
    w(u"prev_as_of=" + PREV_AS_OF)
    w(u"now=" + t1.strftime("%Y-%m-%dT%H:%M:%S%z"))
    w(u"gap_seconds=" + str(gap_s) + u"  gap_minutes=" + str(gap_s // 60) + u"  gap_hours=" + str(gap_s // 3600))
    w(u"gap は 分の桁を越えたか=" + str(gap_s >= 60) + u"  時の桁を越えたか=" + str(gap_s >= 3600))
except Exception as e:
    w(u"gap 測定不能: " + type(e).__name__)
w(u"unreadable 指紋 同じ=" + str(cur_unread == PREV_UNREAD))
w(u"readable   指紋 同じ=" + str(cur_read == PREV_READ))
w(u"unreadable n: prev=" + str(PREV_N_UNREAD) + u" now=" + str(len(bad1)) + u" 差=" + str(len(bad1) - PREV_N_UNREAD))
w(u"readable   n: prev=" + str(PREV_N_READ) + u" now=" + str(len(ok1)) + u" 差=" + str(len(ok1) - PREV_N_READ))
w(u"walked     n: prev=" + str(PREV_WALKED) + u" now=" + str(w1) + u" 差=" + str(w1 - PREV_WALKED))
both_same = (cur_unread == PREV_UNREAD) and (cur_read == PREV_READ)
w(u"★二つ共に同じ=" + str(both_same) + u"★")
w(u"")

w(u"## §E 負の対照（差が出得る口が現に在る事）")
w(u"本器は 指紋が食ひ違へば 下の §F へ 出入りの数を刷る口を持つ。")
probe = hashlib.sha256(u"".encode("utf-8")).hexdigest()
w(u"空集合の指紋=" + probe + u"  (前の二つと同じ=" + str(probe in (PREV_UNREAD, PREV_READ)) + u")")
w(u"∴ 突合は ★何を入れても True を返す形ではない★。")
w(u"")

w(u"## §F 差の中身（名は刷らぬ・数と拡張子の別のみ）")
if both_same:
    w(u"差 現に無し ∴ 刷る物 無し。")
else:
    for label, cur, prev_note in ((u"unreadable", bad1, u""), (u"readable", ok1, u"")):
        pass
    w(u"※ 前の刻の ★名の列★ は残して居らぬ（o194 で名を紙へ写さぬと定めた）")
    w(u"  ∴ ★どの名が出入りしたか★ は 本弾では 測定不能。数と拡張子の別のみ書く。")
    ext = {}
    for rel in bad1:
        e = (os.path.splitext(rel)[1] or u"(拡張子なし)").lower()
        ext[e] = ext.get(e, 0) + 1
    w(u"今の unreadable 拡張子 種類数=" + str(len(ext)))
    for e, n in sorted(ext.items(), key=lambda x: (-x[1], x[0]))[:25]:
        w(u"  " + e + u"  " + str(n))
w(u"")

w(u"## §G 母数と測れなかつた数")
w(u"母数(walked)=" + str(w1))
w(u"讀めた=" + str(len(ok1)) + u"  讀めなんだ=" + str(len(bad1)) + u"  和=" + str(len(ok1) + len(bad1)) + u"  母と一致=" + str(len(ok1) + len(bad1) == w1))
w(u"降らなんだ dir(5 種)の中の枚数は ★数へて居らぬ★ ∴ 測定不能。")

txt = chr(10).join(out) + chr(10)
raw = os.path.join(HERE, "order220_e11_fingerprint.raw.txt")
io.open(raw, "w", encoding="utf-8").write(txt)
sys.stdout.write(txt)

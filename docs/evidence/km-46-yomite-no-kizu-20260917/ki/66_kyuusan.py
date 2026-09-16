#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""66_kyuusan.py -- ㋓ 第45弾の ★実体無 3本★ を ★実の名★ で追ふ器。

臺帳の行から 実の名を取り(★讀手に頼らず 己で括りを解いて★)、
  ⑴ disk に在るか ⑵ 録された sha と合ふか
  ⑶ BEFORE は何を讀まうとしたか ⑷ AFTER は何を讀んだか
を並べる。★「直つた」は 数ではなく 名で言へ。★
"""
import io, os, re, sys, hashlib, importlib.util

ROOT = os.path.abspath(sys.argv[1])
B = os.path.abspath(sys.argv[2])
MAN = os.path.join(ROOT, sys.argv[3])

def yomu(p, na):
    sp = importlib.util.spec_from_file_location(na, p)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
mae = yomu(os.path.join(B, "patch", "verify_BEFORE.py"), "km46_mae66")
ato = yomu(os.path.join(B, "patch", "verify_AFTER.py"), "km46_ato66")

o = []
n = 0
for l in io.open(MAN, encoding="utf-8").read().split(u"\n"):
    if not l.strip() or u"sha256=" not in l:
        continue
    # ★実の名★ = 括りの内側を 最右の sha256=<64hex> まで取る(讀手を使はぬ・己の目で)
    m = re.match(r'^path="(.+)"\s+sha256=([0-9a-f]{64})\s+bytes=(\d+)\s+lines=(\d+)\s*$', l)
    if not m:
        continue
    na, sen, by, gy = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    if u" sha256=" not in na:        # ★疵の形(名の中に sha256= を持つ)だけ追ふ★
        continue
    n += 1
    ap = os.path.join(ROOT, na)
    aru = os.path.isfile(ap)
    ima = hashlib.sha256(open(ap, "rb").read()).hexdigest() if aru else None
    cb, ca = mae.paths_of(l), ato.paths_of(l)
    def toku(c):
        for p in c:
            if os.path.isfile(os.path.join(ROOT, p)):
                return p
        return None
    tb, ta = toku(cb), toku(ca)
    o.append(u"■ 第%d本 ★実の名★" % n)
    o.append(u"    %s" % na)
    o.append(u"    disk に在るか = %s / 録 sha=%s… / 今の sha=%s…"
             % (u"★在る★" if aru else u"無い", sen[:16], (ima or u"-")[:16]))
    o.append(u"    録と今が合ふか = %s   bytes=%d lines=%d" % (u"★合ふ★" if ima == sen else u"合はぬ", by, gy))
    o.append(u"    BEFORE 候補 %d本 → 解けた物 = %s" % (len(cb), tb if tb else u"★無し(=実体無と鳴る)★"))
    o.append(u"      第一候補 %s" % repr(cb[0] if cb else None))
    o.append(u"    AFTER  候補 %d本 → 解けた物 = %s" % (len(ca), u"★狙つた物★" if ta == na else (ta or u"無し")))
    o.append(u"      第一候補 %s" % repr(ca[0] if ca else None))
    o.append(u"")
o.insert(0, u"= 臺帳 %s" % os.path.relpath(MAN, ROOT))
o.insert(1, u"= ★名の中に sha256= を持つ行★ = %d 本" % n)
o.insert(2, u"")
t = u"\n".join(o)
io.open(os.path.join(B, "an", "kyuusan.txt"), "w", encoding="utf-8", newline="").write(t + u"\n")
sys.stdout.write(t + u"\n")

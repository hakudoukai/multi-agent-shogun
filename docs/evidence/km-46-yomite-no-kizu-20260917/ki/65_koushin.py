#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""65_koushin.py -- ★恒真でない證★ を 現物の臺帳 全本で立てる器。

㋒⑴ が課すのは「★既に讀める行の出目を一つも変へぬ★」。
之を 恒真(何時も真)でなく ★落ち得る形★ で測る為、対照を二つ置く:

  ★陰性対照★ = 現物の臺帳 全 N 本の全行 ―― ★一つでも候補列が変れば 露れる★
  ★陽性対照★ = 62 で建てた 破れる形 ―― ★変らねば 器が何も直して居らぬ事になる★

段を二つに分ける:
  ①行の段(disk を触らぬ): BEFORE.paths_of と AFTER.paths_of の候補列を比べる。
      ★完全一致なら 出目は disk を見ずとも不変と断ぜられる★(main は候補列しか使はぬ故)
  ②候補列が違つた臺帳のみ: ★現物の器★ を両方走らせ 出目を比べる(時限付き=FIFO の止を捕へる)
"""
import io, os, sys, subprocess, importlib.util

ROOT = os.path.abspath(sys.argv[1])
B = os.path.abspath(sys.argv[2])
ICHI = os.path.join(B, "raw", "daichou_ichiran.txt")
AN = os.path.join(B, "an")
VB = os.path.join(B, "patch", "verify_BEFORE.py")
VA = os.path.join(B, "patch", "verify_AFTER.py")

def yomu(path, na):
    sp = importlib.util.spec_from_file_location(na, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m
mae, ato = yomu(VB, "km46_mae65"), yomu(VA, "km46_ato65")

hon = [l for l in io.open(ICHI, encoding="utf-8").read().split(u"\n") if l.strip()]
# ★己の束は陰性対照から除かぬ——除けば母數が痩せる★
gyou_kei = kata_onaji = kata_chigau = 0
yomenu_hon = []
chigau_hon = {}
for p in hon:
    ap = os.path.join(ROOT, p)
    try:
        t = io.open(ap, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        yomenu_hon.append((p, type(e).__name__))
        continue
    for l in t.split(u"\n"):
        if not l.strip():
            continue
        gyou_kei += 1
        cb, ca = mae.paths_of(l), ato.paths_of(l)
        if cb == ca:
            kata_onaji += 1
        else:
            kata_chigau += 1
            chigau_hon.setdefault(p, []).append((l, cb, ca))

o = []
o.append(u"= ①行の段(disk を触らぬ) =")
o.append(u"  臺帳 %d 本 / 讀めぬ臺帳 %d 本 / 行 計 %d" % (len(hon), len(yomenu_hon), gyou_kei))
o.append(u"  候補列 ★同じ★ %d 行  ―― 出目は disk を見ずとも ★不変★ と断ぜられる" % kata_onaji)
o.append(u"  候補列 ★違ふ★ %d 行  ―― 之だけ ②へ送る" % kata_chigau)
for p, w in yomenu_hon[:10]:
    o.append(u"    讀めぬ: %s (%s)" % (p, w))
o.append(u"")
o.append(u"= ②候補列が違つた臺帳に 現物の器を当てる(時限 180 秒) =")
o.append(u"  該当 臺帳 %d 本" % len(chigau_hon))
kawatta = []
for p in sorted(chigau_hon):
    r = []
    for v in (VB, VA):
        try:
            x = subprocess.run([sys.executable, "-B", v, os.path.join(ROOT, p), ROOT + os.sep],
                               cwd=ROOT, capture_output=True, text=True, timeout=180)
            at = u"?"
            for l in x.stdout.split(u"\n"):
                if l.strip().startswith(u"一致"):
                    at = l.strip().replace(u"★", u"")
            r.append((x.returncode, at))
        except subprocess.TimeoutExpired:
            r.append((u"止", u"★時限を超えた(FIFO 等)★"))
    onaji = (r[0] == r[1])
    if not onaji:
        kawatta.append(p)
    o.append(u"  %s %s" % (u"不変" if onaji else u"★変つた★", p))
    o.append(u"      BEFORE rc=%s %s" % r[0])
    o.append(u"      AFTER  rc=%s %s" % r[1])
    for l, cb, ca in chigau_hon[p][:3]:
        o.append(u"      行: %s" % l[:110])
        o.append(u"        BEFORE候補 %s" % repr(cb)[:150])
        o.append(u"        AFTER 候補 %s" % repr(ca)[:150])
o.append(u"")
o.append(u"= 締 =")
o.append(u"  ★陰性対照★ 現物 %d 本 %d 行 の内、出目が変つた臺帳 = %d 本" % (len(hon), gyou_kei, len(kawatta)))
for p in kawatta:
    o.append(u"    変つた: %s" % p)
t = u"\n".join(o)
io.open(os.path.join(AN, u"koushin.txt"), "w", encoding="utf-8", newline="").write(t + u"\n")
sys.stdout.write(t + u"\n")

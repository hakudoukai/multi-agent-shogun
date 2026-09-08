# -*- coding: utf-8 -*-
u"""order199 ―― ★E3+E4 を一弾で★ (走 0・己の讀取器・製品走 0)

  ★令の逐語★ = 「★承認(order199)＝E3+E4 を一弾で(走 0・己の讀取器)★=根の規 3 本を走らせ
    紙の数と突合し ★同じ走りで A3=−7(o185) 対 −9(o182/183) の食ひ違ひを落とせ★。
    ★落ちねば『落ちず』と書き ★何方が正か判らぬ★ を其の語で★。製品走 0・DB 0・HEAD 不動・
    型で出し 枝名＋tip を一行で。」

  ㋐ ★根の規 3 本★ (紙 o191:145 が sha16 で名指した物) ――
     order183_frame_precision_v1.rule.py  67b4d870d1d33e1d
     order181_vocab_window_both_v1.rule.py 5f2d02e3118146e8
     order182_asym_and_two_bands_v1.rule.py 95fb3a5571769e66
     ★併せて o180 も当てる★ ―― o185 が −7 の ★源の紙★ と名指したのが order180 であり、
     其の ★規★ が現に在るゆゑ (E4 を規で判ずるには 源の規が要る)
  ㋑ ★先に字にした検め★ ―― 四本は `open(` を ★一つも持たぬ★ (己が /usr/bin/grep で当てた・
     陽性対照 import/def/print は現に出た) ∴ file を讀まず ★importlib で 己の dir の規を鎖で讀む★。
     ∴ 「規を走らせて紙と突合」は ★規の中の数★ と ★紙の数★ の突合である (條 o176 ―― 数が出る事と
     其の数が意味を持つ事は別)。★之を先に字にする★。
  ㋒ ★三つを別々に測る★ (床(30) 何を一つと数へたか)
     ㋒1 ★規の今日の sha16★ 対 ★紙が記した sha16★      (＝規が改まつて居らぬか)
     ㋒2 ★規の註が書いた sha16★ 対 ★今日の sha16★      (＝規が己の中で記した数が合ふか)
     ㋒3 ★規の出す数★ 対 ★紙の数★                      (＝写しが正しいか)
  ㋓ ★E4★ = A3 の得失を ★規の出力から★ 取り −7 / −9 の何方と合ふかを見る
     ★落ちねば「落ちず」と書き「何方が正か判らぬ」を其の語で★ (令の逐語)
  ㋔ ★見込み★ = 規は −7 を出す (o185 が源の紙 L171/L181 で 得17/失24 を讀んで居るゆゑ)。
     ★但し 己は 三度続けて 少なく外して居る★ (條 o179-a) ∴ ★外れも書く★
  ㋕ ★走らせるのは己の dir の讀取器のみ★・製品走 0・DB 0・network 0・書込 0・git 0
"""
import os, io, re, glob, hashlib, importlib.util as IU

HERE = os.path.dirname(os.path.abspath(__file__))

ROOTS = [("order183_frame_precision_v1.rule.py",  "67b4d870d1d33e1d"),
         ("order181_vocab_window_both_v1.rule.py", "5f2d02e3118146e8"),
         ("order182_asym_and_two_bands_v1.rule.py", "95fb3a5571769e66"),
         ("order180_window_widen_v1.rule.py",       None)]   # 註のみ (紙は sha を記さず)

def sha16(fn):
    return hashlib.sha256(io.open(os.path.join(HERE, fn), "rb").read()).hexdigest()[:16]

def wcs(fn):
    s = io.open(os.path.join(HERE, fn), encoding="utf-8").read()
    return s.count(chr(10)), len(s.split(chr(10))), len(s.encode("utf-8"))

def stage0():
    p = os.path.abspath(__file__)
    s = io.open(p, encoding="utf-8").read()
    print("== order199 第零段 ―― ★定めを 先に 字にした★ (数を一つも出す前) ==")
    print("  規 = %s" % os.path.basename(p))
    print("  sha16=%s wc=%d split=%d bytes=%d"
          % (hashlib.sha256(s.encode("utf-8")).hexdigest()[:16],
             s.count(chr(10)), len(s.split(chr(10))), len(s.encode("utf-8"))))

def stage1():
    print("\n== order199 第一段 ―― ㋒1 ★規の今日の sha16★ 対 ★紙が記した sha16★ ==")
    for fn, want in ROOTS:
        h = sha16(fn); w, sp, b = wcs(fn)
        if want is None:
            print("  %-42s 今日=%s wc=%d split=%d bytes=%d ★紙は sha を記さず★" % (fn, h, w, sp, b))
        else:
            print("  %-42s 今日=%s 紙=%s ★%s★ wc=%d split=%d bytes=%d"
                  % (fn, h, want, u"一致" if h == want else u"合はぬ", w, sp, b))

def stage2():
    print("\n== order199 第二段 ―― ㋒2 ★規の註が書いた sha16★ 対 ★今日の sha16★ ==")
    RE = re.compile(r'_load\("([^"]+)",\s*"([^"]+)"\)(.*)')
    RS = re.compile(r"([0-9a-f]{16})")
    tot = ok = ng = nosha = 0
    for fn, _w in ROOTS:
        src = io.open(os.path.join(HERE, fn), encoding="utf-8").read()
        print("  -- %s が鎖で讀む規 --" % fn)
        for ln in src.split(chr(10)):
            m = RE.search(ln)
            if not m: continue
            tgt = m.group(2); tail = m.group(3)
            tot += 1
            try: h = sha16(tgt)
            except Exception: print("     %-44s ★讀めぬ★" % tgt); continue
            ms = RS.search(tail)
            if not ms:
                nosha += 1
                print("     %-44s 今日=%s ★註に sha 無し★" % (tgt, h))
            elif ms.group(1) == h:
                ok += 1
                print("     %-44s 今日=%s 註=%s ★一致★" % (tgt, h, ms.group(1)))
            else:
                ng += 1
                print("     %-44s 今日=%s 註=%s ★合はぬ★" % (tgt, h, ms.group(1)))
    print("  ⇒ 鎖の辺 = ★%d★ / 一致 = ★%d★ / 合はぬ = ★%d★ / 註に sha 無し = ★%d★"
          % (tot, ok, ng, nosha))

def _load(nick, fn):
    sp = IU.spec_from_file_location(nick, os.path.join(HERE, fn))
    m = IU.module_from_spec(sp); sp.loader.exec_module(m); return m

def stage3():
    print("\n== order199 第三段 ―― ㋓ ★A3 の得失を 規の中から★ 取る (E4) ==")
    o0 = _load("o0_199", "order180_window_widen_v1.rule.py")
    names = [n for n in dir(o0) if not n.startswith("_")]
    print("  order180 の規が持つ名 = ★%d★ (先頭 20): %s" % (len(names), ", ".join(sorted(names)[:20])))
    for n in sorted(names):
        v = getattr(o0, n)
        if isinstance(v, dict) and len(v) <= 12:
            keys = list(v.keys())
            if any(isinstance(k, type(u"")) and (u"得" in k or u"失" in k) for k in keys):
                print("  ★%s★ = %d 項" % (n, len(v)))
                tot = 0
                for k in keys:
                    print("     %-58s : %s" % (k[:58], v[k]))
                    if isinstance(v[k], int): tot += v[k]
                print("     (和 = %d)" % tot)

def stage4():
    print("\n== order199 第四段 ―― ㋒3 ★規の出す数★ 対 ★紙の数★ (A3 の得/失/差引) ==")
    o0 = _load("o0b_199", "order180_window_widen_v1.rule.py")
    got = {}
    for n in sorted(dir(o0)):
        if n.startswith("_"): continue
        v = getattr(o0, n)
        if not isinstance(v, dict): continue
        for k in v:
            if not isinstance(k, type(u"")): continue
            if k.startswith(u"得") and isinstance(v[k], int): got.setdefault("得", []).append((n, k, v[k]))
            if k.startswith(u"失") and isinstance(v[k], int): got.setdefault("失", []).append((n, k, v[k]))
    for side in (u"得", u"失"):
        rows = got.get(side, [])
        s = sum(x[2] for x in rows)
        print("  ★%s★ = %d 項 / 和 = ★%d★" % (side, len(rows), s))
        for (n, k, val) in rows:
            print("     [%s] %-52s : %d" % (n, k[:52], val))
    e = sum(x[2] for x in got.get(u"得", []))
    l = sum(x[2] for x in got.get(u"失", []))
    print("  ⇒ ★規から出た A3 の 得=%d / 失=%d / 差引=%+d★" % (e, l, e - l))
    print("  ⇒ o185 の紙 (源 order180 の L171/L181 を讀んだ) = 得 17 / 失 24 / 差引 ★−7★")
    print("  ⇒ o182/o183 の紙が併記した = ★−9★")
    if e - l == -7:
        print("  ⇒ ★規は −7 を出した★ ∴ ★−7 が 規と合ふ★ / ★−9 は 規と合はぬ★ ―― ★E4 は落ちた★")
    elif e - l == -9:
        print("  ⇒ ★規は −9 を出した★ ∴ ★−9 が 規と合ふ★ / ★−7 は 規と合はぬ★ ―― ★E4 は落ちた(向きは逆)★")
    else:
        print("  ⇒ ★規は %+d を出した★ ―― ★−7 とも −9 とも 合はぬ★" % (e - l))
        print("  ⇒ ★E4 は 落ちず★ ―― ★何方が正か判らぬ★ (令の逐語)")

def stage5():
    print("\n== order199 第五段 ―― ★紙の数を 機械で拾ふ★ (突合の相手) ==")
    for nm, pat in ((u"o185 の A3 行", u"| A3 | 17 | 16 + 1 | 24 | 8 + 16 |"),
                    (u"o185 の食ひ違ひ表", u"| A3 | −7 | −7 | −9 |"),
                    (u"o183 の四度の損", u"A3 = ★-9★")):
        n = 0; where = []
        for fp in sorted(glob.glob(os.path.join(HERE, "*.md"))):
            t = io.open(fp, encoding="utf-8").read()
            c = t.count(pat)
            if c: n += c; where.append((os.path.basename(fp), c))
        print("  %-18s : 度数=★%d★ %s" % (nm, n, where[:3]))

def stage6():
    """★第六段 ―― 第四段の打ち直し★ (家老 條 百九十七)

      ★第四段は 誤つた辺を拾つた★ ―― `MIKOMI180_*` は ★見込みの帳★ (名が MIKOMI) であり
      A3 の得失の ★実測★ ではない。「得/失」で始まる鍵を機械で和して +38 を出したのは
      條 o176 (数が出る事と 其の数が意味を持つ事は別) の ★己の現行犯★。
      ★第四段は 消さぬ★ (raw に残る) ―― 此処で ★併記で 打ち直す★。

      ★実測の在処★ = o180 の main() の print (L274 / L280) ―― len() から ★計算★ して出る。
        L274: "   得 合計 = %d 件" % (len(gain_g1) + len(gain_new))
        L280: "   失 合計(真を刈る + 新たな偽陽性) = %d 件" % (len(lost)-len(lost_ok)+len(fp_new))
      ∴ __main__ guard が在るゆゑ exec_module では走らぬ ⇒ ★subprocess で 規其の物を走らせる★。

      ★−9 の在処★ = o182 L246 / o183 L309 ―― 逐語:
        o182:246  "    四度の差引: A2 = -6 / A3 = -9 / A4 = -7 / ★A5 = %+d★ …" % d5
        o183:309  "  ★受入③ 五度目の差引★ : A2 = -6 / A3 = -9 / A4 = -7 / A5 = -15 / ★A6 = %+d★"
      ⇒ ★A3 = -9 は format 子を持たぬ literal★ (%+d は d5 / d6 にのみ掛かる)
      ⇒ ∴ ★−9 は 規が計算した数に非ず 規に ★写された★ 数★ である。之を機械で確かめる。

      ★見込みを 先に 字にする★ (條 o179-a ―― 己は三度続けて ★少なく★ 外して居る)
        見込み = o180 は 得 17 / 失 24 / 差引 −7 を出す (紙 order180 の L171/L181 と同じ)
        ∴ ★−7 が実測・−9 は写しの誤り★ と見る。★外れたら 向きを数へて 四度目として書く★。
    """
    import subprocess, sys, re as _re
    print("\n== order199 第六段 ―― ★第四段の打ち直し★ + E4 の決着 ==")
    print("  ★第四段の +38 は 見込みの帳(MIKOMI180_*)を和した数 ∴ ★E4 の材に非ず★ (消さず併記)★")
    print("  ★見込み(先に字にした)★ = o180 は 得 17 / 失 24 / 差引 −7 を出す")

    print("\n  -- ㋐ 四本を ★一字も変へず★ 走らせる (條 o174) --")
    outs = {}
    for fn in ["order180_window_widen_v1.rule.py",
               "order181_vocab_window_both_v1.rule.py",
               "order182_asym_and_two_bands_v1.rule.py",
               "order183_frame_precision_v1.rule.py"]:
        pr = subprocess.Popen([sys.executable, fn], cwd=HERE,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        b = pr.communicate()[0].decode("utf-8", "replace")
        outs[fn] = (b, pr.returncode)
        print("     %-42s rc=%d 出力 wc=%d split=%d bytes=%d"
              % (fn, pr.returncode, b.count(chr(10)), len(b.split(chr(10))), len(b.encode("utf-8"))))

    print("\n  -- ㋑ o180 の出力から ★得/失 合計★ を拾ふ (計算値) --")
    o180 = outs["order180_window_widen_v1.rule.py"][0]
    mg = _re.search(u"得 合計 = ([0-9]+) 件", o180)
    ml = _re.search(u"失 合計\\(真を刈る \\+ 新たな偽陽性\\) = ([0-9]+) 件", o180)
    if mg: print("     得 合計 = ★%s★  (逐語: %s)" % (mg.group(1), mg.group(0)))
    else:  print("     ★得 合計 の行 現に無し★")
    if ml: print("     失 合計 = ★%s★  (逐語: %s)" % (ml.group(1), ml.group(0)))
    else:  print("     ★失 合計 の行 現に無し★")

    print("\n  -- ㋒ −9 の literal 性を 機械で確かめる --")
    for fn, ln in [("order182_asym_and_two_bands_v1.rule.py", 246),
                   ("order183_frame_precision_v1.rule.py", 309)]:
        t = io.open(os.path.join(HERE, fn), encoding="utf-8").read().split(chr(10))[ln-1]
        has = u"A3 = -9" in t
        pre = t.split(u"A3 = -9")[0] if has else u""
        print("     %s:%d  ★A3 = -9 在り = %s★ / 其の左に format 子 %% = ★%d 個★"
              % (fn, ln, u"現に在る" if has else u"現に無い", pre.count(u"%")))
        print("        逐語: %s" % t.strip()[:110])

    print("\n  -- ㋓ ★E4 の判じ★ --")
    if mg and ml:
        G = int(mg.group(1)); L = int(ml.group(1)); D = G - L
        print("     ★規(o180)が 計算して 出した A3 = 得 %d / 失 %d / 差引 %+d★" % (G, L, D))
        print("     o185 の紙 = 得 17 / 失 24 / 差引 ★−7★  (源の紙 L171/L181 を ★讀んで★ 得た)")
        print("     o182:246 / o183:309 = ★−9★  (★literal の写し★ ―― 計算に非ず)")
        if D == -7:
            print("     ⇒ ★E4 は 落ちた★ ―― ★規の計算値は −7★ ∴ ★−7 が正★ / ★−9 は 写しの誤り★")
            print("     ⇒ ★見込みは 当たつた★ (四度目にして 外れ ★ず★)")
        elif D == -9:
            print("     ⇒ ★E4 は 落ちた★ ―― ★規の計算値は −9★ ∴ ★−9 が正★ / ★−7 が 誤り★")
            print("     ⇒ ★見込みは 外れた★ ―― 四度目 (向き = ★己に甘く★)")
        else:
            print("     ⇒ ★E4 は 落ちず★ ―― 規は %+d を出し ★−7 とも −9 とも 合はぬ★" % D)
            print("     ⇒ ★何方が正か判らぬ★ (令の逐語)")
    else:
        print("     ⇒ ★E4 は 落ちず★ ―― ★得/失 合計 の行が 拾へなんだ★")
        print("     ⇒ ★何方が正か判らぬ★ (令の逐語)")

    print("\n  -- ㋔ ★E3 ―― 規の出す数 対 紙の数★ (o181/o182/o183 の受入③ 行) --")
    for fn, pat in [("order181_vocab_window_both_v1.rule.py", u"差引 = ([+-][0-9]+)"),
                    ("order182_asym_and_two_bands_v1.rule.py", u"A5 = ([+-][0-9]+)"),
                    ("order183_frame_precision_v1.rule.py", u"A6 = ([+-][0-9]+)")]:
        b = outs[fn][0]
        ms = _re.findall(pat, b)
        print("     %-42s 拾へた数 = ★%s★" % (fn, ms if ms else u"現に無い"))

if __name__ == "__main__":
    stage0(); stage1(); stage2(); stage3(); stage4(); stage5(); stage6()

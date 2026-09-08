# -*- coding: utf-8 -*-
u"""order198 ―― ★o186 の「52 は上限」を 値へ落とす★ (E2・走 0・讀取のみ)

  ★令の逐語★ = 「偽陽性を刈つた後の ★『源を欠く写し』の真の数★ = o186 の『52 は上限』を
                 ★値★ へ落とせ。★上限と値を併記(52 を消すな)・刈つた偽陽性の形と数も
                 同じ紙に・零なら零と書け★」

  ㋐ ★52 の定め (o186 逐語)★
     「写した得失の数」 = 同じ行に ㋐器の名 A2〜A7 ㋑負号付きの数 の ★両方★ を持つ行 (71 行)
     「源が添へて在る」 = ★同じ行★ に 16 桁 hex か *.md の名 が在る          (19 行)
     ★52 = 71 − 19★ ―― ★源を同じ行に欠く★ 行 ∴ 「源を欠く写し」の ★上限★ (値ではない)

  ㋑ ★己が先に見付けた事★ = o189 の㋒「数へ直す物 = 71/19/17/54/26/28」に ★52 は 現に無い★
     ∴ o189 は ★o187 の 54 (=71−17) だけ を打ち直し ★o186 の 52 を 落として居た★
     而して o189 の器は s186 を ★現に持つて居る★ ∴ 新たに測るに非ず ―― ★引き算を 明示に取る★

  ㋒ ★旧器・新器は o189 から 一字も変へず写す★ (條 o174「器を一字も変へずに二度測れ」)
     写した事を明かに書く (床⑸) ―― ★写した★ 源 = order189_falsepos_cure_v1.rule.py L29-L52

  ㋓ ★三欄で出す★ (作法 八条目 ―― 物差しを動かした分と 紙が増えた分を 分ける)
     欄1 ★公表値★ = 旧器 × 紙 255 本 (o186 の刻・★己は再現し得ぬ★ ∴ 紙から写す・確かめて居らぬ)
     欄2         = 旧器 × ★今日の紙★  (紙が増えた分だけが動く)
     欄3 ★新器★  = 新器 × ★今日の紙★  (器を動かした分も入る)

  ㋔ ★52 の中の刈り★ = ★o189 に無い所★ ―― o189 の刈りは 71 行全体に対する物
     本弾は ★源を欠く行 に限つて★ 刈りを取り 形1/形2 に割る
       形1 ★負号の徴で落ちた★ = 旧器が語中 hyphen を負号と見た行
       形2 ★器名の境界で落ちた★ = 旧器が A3 等を境界無しに拾つた行
     ★両方で落ちた行★ が在り得る ∴ 形1/形2 を ★排他にせず★ 重なりを別値で書く (床(30))

  ㋕ ★真の巻添への上限★ = 刈つた行の内 直前字が 英数字でも NEG_OK でもない物 (o189 第七段の形)
  ㋖ ★零なら零と書く★ (令の逐語)
  ㋗ ★一つと数へた物 = 己の紙の一行★ (床(30))・行数は wc/split 併記 (床(32))
  ㋘ ★見込み★ = 値は ★31 前後★ と見る (o189 §四 の「源無し 31」に近い) ―― 外れも書く
  ㋙ ★git を打たぬ・/mnt/c に触れぬ・他席は讀取のみ・走 0★
"""
import os, io, re, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))

# ── 旧器 (order189 L29-L30 から ★一字も変へず写した★) ──
OLD_KEN = re.compile(r"A[2-7]")
OLD_NEG = re.compile(u"[\u2212-][0-9]+")
# ── 新器 (order189 L32-L35 から ★一字も変へず写した★) ──
NEW_KEN = re.compile(r"(?:^|[^A-Za-z0-9_])(A[2-7])(?:[^A-Za-z0-9_]|$)")
NEG_OK  = set(u" \t(=:\u2605\u300c\u3001")
RE_SHA  = re.compile(r"[0-9a-f]{16}")
RE_MD   = re.compile(r"[A-Za-z0-9_]+\.md")

def new_neg(ln):
    out = []
    for m in re.finditer(u"([\u2212-])([0-9]+)", ln):
        c = m.group(1); i = m.start()
        if c == u"\u2212": out.append(m.group(2)); continue
        if i == 0 or ln[i-1] in NEG_OK: out.append(m.group(2))
    return set(out)

def _sha16(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()[:16]

def _corpus():
    papers = sorted(glob.glob(os.path.join(HERE, "*.md")))
    rules  = sorted(glob.glob(os.path.join(HERE, "*.rule.py")))
    sha2name = {}
    for fp in papers + rules: sha2name[_sha16(fp)] = os.path.basename(fp)
    txt = {}
    for fp in papers:
        b = os.path.basename(fp)
        txt[b] = io.open(fp, encoding="utf-8").read()
    return papers, rules, txt, sha2name

def _rows(txt, new):
    """(紙, 行, 源186在り) ―― 源186 = ★同じ行★ に 16桁hex か *.md (o186 の定め)"""
    out = []
    for b in sorted(txt):
        for ln in txt[b].split(chr(10)):
            if new:
                ks = NEW_KEN.findall(ln); ns = new_neg(ln)
                if not (ks and ns): continue
            else:
                if not (OLD_KEN.search(ln) and OLD_NEG.search(ln)): continue
            s186 = bool(RE_SHA.search(ln) or RE_MD.search(ln))
            out.append((b, ln, s186))
    return out

def stage0():
    p = os.path.abspath(__file__)
    s = io.open(p, encoding="utf-8").read()
    print("== order198 第零段 ―― ★定めを 先に 字にした★ (数を一つも出す前) ==")
    print("  規 = %s" % os.path.basename(p))
    print("  sha16=%s wc=%d split=%d bytes=%d"
          % (_sha16(p), s.count(chr(10)), len(s.split(chr(10))), len(s.encode("utf-8"))))
    print("  ★旧器/新器は order189_falsepos_cure_v1.rule.py L29-L52 から 写した★ (床⑸)")
    src = os.path.join(HERE, "order189_falsepos_cure_v1.rule.py")
    print("  写した源 sha16=%s (己で当たつた)" % _sha16(src))

def stage1():
    print("\n== order198 第一段 ―― ★三欄★ (作法 八条目・條 o174 同じ走り) ==")
    papers, rules, txt, sha2name = _corpus()
    print("  今日の紙 = ★%d 本★ / 規 = ★%d 本★ (o186 の刻 ★255 本★ ―― ★己は再現し得ぬ★)"
          % (len(papers), len(rules)))
    res = {}
    for new in (False, True):
        r = _rows(txt, new)
        res[new] = r
        n = len(r); y = sum(1 for x in r if x[2]); no = n - y
        tag = u"★新器★" if new else u"旧器  "
        print("  %s × 今日の紙 : 母集団=★%d★ / 源在り(186 の定め)=★%d★ / ★源を欠く=%d★"
              % (tag, n, y, no))
    print("  欄1 ★公表値★ 旧器 × 紙 255 : 母集団=★71★ / 源在り=★19★ / ★源を欠く=52 (上限)★")
    print("      ⇒ ★紙から写した数である・己は当時の紙 255 本の集合を保つて居らぬ★ (確かめて居らぬ)")
    return res, txt

def stage2(res):
    print("\n== order198 第二段 ―― ★52 の中の刈り★ (o189 に ★無い★ 所) ==")
    old = res[False]; new = res[True]
    keyn = set((b, ln) for (b, ln, s) in new)
    old_no = [(b, ln) for (b, ln, s) in old if not s]      # 旧器で 源を欠く行
    new_no = [(b, ln) for (b, ln, s) in new if not s]      # 新器で 源を欠く行
    dropped = [(b, ln) for (b, ln) in old_no if (b, ln) not in keyn]
    print("  旧器×今日の紙 で ★源を欠く★ = ★%d 行★" % len(old_no))
    print("  其の内 ★新器で 刈られた★     = ★%d 行★" % len(dropped))
    print("  ⇒ ★新器×今日の紙 で 源を欠く = %d 行★ ―― ★之が 52 の 値★" % len(new_no))
    f1 = f2 = both = neither = 0
    for (b, ln) in dropped:
        ken_die = bool(OLD_KEN.search(ln)) and not bool(NEW_KEN.findall(ln))
        neg_die = bool(OLD_NEG.search(ln)) and not bool(new_neg(ln))
        if ken_die and neg_die: both += 1
        elif neg_die: f1 += 1
        elif ken_die: f2 += 1
        else: neither += 1
    print("  -- ★刈つた偽陽性の 形と数★ (令の逐語・★重なりを別値★ 床(30)) --")
    print("    形1 ★負号の徴のみで落ちた★   = ★%d 行★" % f1)
    print("    形2 ★器名の境界のみで落ちた★ = ★%d 行★" % f2)
    print("    ★両方で落ちた★               = ★%d 行★" % both)
    print("    ★何れでもない (説明が付かぬ)★ = ★%d 行★" % neither)
    print("    (形1+形2+両方+説明付かぬ = %d ‖ 刈つた行 = %d ★一致せねば疵★)"
          % (f1 + f2 + both + neither, len(dropped)))
    if not dropped:
        print("    ★零★ ―― ★一行も刈られなかつた★")
    return old_no, new_no, dropped

def stage3(dropped):
    print("\n== order198 第三段 ―― ★真の巻添への上限★ (家老 140・o189 第七段の形) ==")
    amb = []
    for (b, ln) in dropped:
        if u"\u2212" in ln:
            amb.append((b, ln, u"U+2212")); continue
        for m in re.finditer(u"-([0-9]+)", ln):
            i = m.start()
            if i == 0: continue
            c = ln[i-1]
            if c in NEG_OK: continue
            if re.match(r"[A-Za-z0-9_]", c): continue
            amb.append((b, ln, c)); break
    print("  刈つた ★%d 行★ の内 ★曖昧 (真の負号かも知れぬ) = %d 行★ ∴ ★上限=%d / 下限=0★"
          % (len(dropped), len(amb), len(amb)))
    for (b, ln, c) in amb[:8]:
        print("    直前字[%s] %-34s | %s" % (c, b[:34], ln.strip()[:46]))
    if not amb:
        print("    ★零★ ―― ★真の負号を持つ行は 一行も刈られて居らぬ★ ∴ ★上限も下限も 零★")
    return len(amb)

def stage4(new_no):
    print("\n== order198 第四段 ―― ★値の中身★ (生き残つた「源を欠く」行を 人が讀む材) ==")
    per = {}
    for (b, ln) in new_no: per[b] = per.get(b, 0) + 1
    print("  紙ごと (多き順・上位 8):")
    for b in sorted(per, key=lambda z: (-per[z], z))[:8]:
        print("    %-48s %d 行" % (b[:48], per[b]))
    print("  -- 逐語 (先頭 10 本・各 54 字) --")
    for (b, ln) in new_no[:10]:
        print("    %-34s | %s" % (b[:34], ln.strip()[:54]))
    ken = {}
    for (b, ln) in new_no:
        for k in NEW_KEN.findall(ln): ken[k] = ken.get(k, 0) + 1
    print("  -- 器の名ごと (★A3 は 席の名との別が 機械で付かぬ★ o189 直3) --")
    for k in sorted(ken): print("    %s : %d 行" % (k, ken[k]))

def stage5(old_no, new_no):
    print("\n== order198 第五段 ―― ★52 を消さぬ★ 併記表 (令の逐語) ==")
    print("  | 欄 | 器 | 紙 | 母集団 | 源在り | ★源を欠く★ |")
    print("  | 1 ★公表★ | 旧 | 255 (写し) | 71 | 19 | ★52 = 上限★ |")
    print("  | 2 | 旧 | 今日 | %d | %d | ★%d★ |"
          % (len(old_no) + 0, 0, len(old_no)))
    print("  | 3 ★新★ | 新 | 今日 | %d | %d | ★%d = 値★ |"
          % (len(new_no) + 0, 0, len(new_no)))
    print("  ★註★ 欄2/欄3 の「母集団」「源在り」は 第一段の数を見よ (本表は 源を欠く 行の数のみ)")

def stage6():
    """★実証★ ―― o189 の紙は 31/0/31 と書いた・己は今日 57/22/35 を得た。
       候補 = ★紙が増えた分★ (o189 の as_of 15:52:28 より後に生まれた紙)。
       ★消去で残つた物は候補★ (己の條 百七十一・改) ∴ ★mtime で o189 の刻へ戻して 実証する★"""
    import time
    print("\n== order198 第六段 ―― ★o189 の 31 と 己の 35 の食ひ違ひ を 実証で解く★ ==")
    CUT = time.mktime(time.strptime("2026-09-08 15:52:28", "%Y-%m-%d %H:%M:%S"))
    papers = sorted(glob.glob(os.path.join(HERE, "*.md")))
    old_set = [fp for fp in papers if os.path.getmtime(fp) <= CUT]
    print("  o189 の as_of = 2026-09-08T15:52:28 ―― 其の刻までの紙 = ★%d 本★ (o189 の紙は ★258 本★ と書く)"
          % len(old_set))
    print("  ★差 = %d 本★ (mtime は 書いた刻・後に touch されて居らぬ事は ★測定不能★)"
          % (258 - len(old_set)))
    txt = {}
    for fp in old_set:
        txt[os.path.basename(fp)] = io.open(fp, encoding="utf-8").read()
    r = _rows(txt, True)
    n = len(r); y = sum(1 for x in r if x[2])
    print("  ★新器 × 其の刻の紙★ : 母集団=★%d★ / 源在り(186)=★%d★ / ★源を欠く=%d★" % (n, y, n - y))
    print("  ⇒ o189 の紙の数 (31 / 0 / 31) と ★合ふか★ : 母集団 %s / 源在り %s / 源を欠く %s"
          % (u"合ふ" if n == 31 else u"合はぬ(%d)" % n,
             u"合ふ" if y == 0 else u"合はぬ(%d)" % y,
             u"合ふ" if n - y == 31 else u"合はぬ(%d)" % (n - y)))
    newer = [os.path.basename(fp) for fp in papers if os.path.getmtime(fp) > CUT]
    print("  ★其の刻より後に生まれた紙★ = ★%d 本★ (先頭 8):" % len(newer))
    for b in sorted(newer)[:8]: print("    %s" % b)
    t2 = {}
    for fp in papers:
        b = os.path.basename(fp)
        if b in newer: t2[b] = io.open(fp, encoding="utf-8").read()
    r2 = _rows(t2, True)
    n2 = len(r2); y2 = sum(1 for x in r2 if x[2])
    print("  ★後の紙 だけ★ : 母集団=★%d★ / 源在り(186)=★%d★ / 源を欠く=★%d★" % (n2, y2, n2 - y2))

if __name__ == "__main__":
    stage0()
    res, txt = stage1()
    old_no, new_no, dropped = stage2(res)
    stage3(dropped)
    stage4(new_no)
    stage5(old_no, new_no)
    stage6()

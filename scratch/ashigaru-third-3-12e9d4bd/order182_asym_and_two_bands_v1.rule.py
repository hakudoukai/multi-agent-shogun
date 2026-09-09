# -*- coding: utf-8 -*-
# order182 第一段 ―― 器A5(非対称) の宣言 と ★幅を二本 立てる★
#
# ★此の第一段は 器A5 の ★得失・分子★ を一度も数へる前★ に書き切つた★。
#   ★但し 自訴★: 「A5 が名を取れた件 = 139」と「人が新たに判ずる要 = 5 件」の二つは
#   ★家老へ次弾を申し出る前の費え見積り★ で ★既に測つて居る★ ∴ ★見込みに非ず★。
#   之を幅の比べに入れると ★答を知つて居る欄★ が混ざる ゆゑ ★名指して外す★ (§一 KNOWN)。
#
# 令(家老third・逐語):
#   「★order182 採る=①主・②同じ走の副・③次へ★」
#   「条=★条を鋳た者(家老)も ★測られる★ ―― ★席は ★条を検める弾★ を立ててよい★」
#   受入 五つ:
#     ①★二本の幅は ★作り方を先に字にして★ 立てよ・★どちらも外れたら『二本とも外れた』と書け★
#     ②★結びは ★三択語で★=『★直近版が勝てば ★材は新しい方が良い★・
#        過去四度版が勝てば ★家老の条は ★此の一件では★ 立たぬ★』
#     ③★①の差引が ★損でなくなつたか★ を三択語で・★破れても『三度の損』の記録は ★消すな(併記)★
#     ④★費えが実測と違へば 其の儘申せ★
#     ⑤wc/split 併記
#
# 走らせる処: /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/

import importlib.util, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

def _load(nick, fn):
    sp = importlib.util.spec_from_file_location(nick, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

o9 = _load("o9", "order179_recall_and_toolfix_v1.rule.py")      # 器A2 の語彙 2f816583fa7b0454
o0 = _load("o0", "order180_window_widen_v1.rule.py")            # 器A3 + 217台帳 559cf39038beee31
o1 = _load("o1", "order181_vocab_window_both_v1.rule.py")       # 器A4 + 幅(過去四度版) 5f2d02e3118146e8

# ============================================================
# 一. CRITERION7 ―― 器A5(非対称器) の宣言
# ============================================================
CRITERION7 = """
器A5 = ★前窓は 11 語すべて・後窓では「行」「鍵」を採らぬ★ (非対称器)

 ㋐ 語彙 : 器A2(境界付き) と一字も違はぬ。器A4 と同じ。
 ㋑ 窓   : 前 46 字 ・ 後 46 字。器A4 と同じ。
 ㋒ ★非対称★: ★後窓に限り★ 「行」「鍵」の二語を ★採らぬ★。前窓では採る。
 ㋓ 何故 此の二語か: order181 §八 の実測 ―― order180 の 失 24 は ★悉く後窓★ であり、
     其のうち ★行 10 件・鍵 7 件 = 17 件(70.8%)★ を此の二語が占めた。
     ★材は己の失敗の記録であり、語を後から選んで居らぬ(先に数へ、多い順の上位二語を採つた)★。
 ㋔ 同距離: 前と後の双方に当たり距離が等しい時は ★前を採る★ (器A4 と同じ・向き替への効きは ③ へ回す)。
 ㋕ 判ずる材: ★台帳の元素の字のみ★。㋖ 迷つたら ★合はぬ側★。
 ㋗ ★頭の名詞の補ひ★ (order180/181 と一字も違はぬ):
     元素の字が「A(B)」「A の B」の形の時は ★文の頭の名詞★ で判ずる。
 ㋘ 人が名を讀めなんだ 15 件は ★分子にも分母にも入れぬ★。
"""

# ★既に測つて居る欄 (見込みに非ず・幅の比べから外す)★ ―― 受入④「費えが実測と違へば其の儘申せ」
KNOWN = {
    "A5 が名を取れた件": (139, "家老へ次弾を申し出る ★前★ に費えとして測つた ∴ 見込みに非ず"),
    "人が新たに判ずる要": (5,   "同上。申し出の便に『5 件のみ』と書いて居る"),
}

# ============================================================
# 二. ★幅を二本 立てる★ (受入① ―― 作り方を先に字にする)
# ============================================================
TWO_BANDS = """
★同じ式・同じ種分け で、★材だけ★ を替へた二本を立てる★。式は order181 と一字も違はぬ:
    r = (素 − 実測)/実測 ・ 幅 = [ 素/(1+r_max) , 素/(1+r_min) ] ・ 下限 floor / 上限 ceil ・
    母集団の上限で切る ・ 種は ㋐誤り欄 / ㋑得欄 / ㋒産出欄。

★幅A = 過去四度版★ : 材 = order181 が用ゐた 14 対 (o177/o178/o179/o180)。
    ★order181 の BANDS を import して用ゐ、一字も作り直さぬ★。
★幅B = 直近一度版★ : 材 = ★order181 の 6 欄の 素 vs 実測 のみ★ (最も新しい己)。
    但し ★KNOWN の欄は order181 の物ではない★ ゆゑ 6 対すべてを用ゐる。

★何を以て『勝つた』とするか(先に字にする)★:
    ①実測を ★含んだ★ 幅が多い方を勝ちとする。
    ②同数の時は ★幅の広さの和が小さい★ 方を勝ちとする(狭くて当たる方が良い)。
    ③★双方が外した欄は「二本とも外れた」と書く★ (受入①)。
★立たぬ側も現に出得る★: 幅B の産出欄は 素の 1.011〜1.040 倍 と ★極めて狭い★ ゆゑ
    外す事が現に在り得る。幅A の誤り欄は 素の 1.0〜6.0 倍 と ★極めて広い★ ゆゑ当たり易い。
    ∴ ★どちらが勝つかは 走らせる前には定まらぬ★ (百三十四 = 出得ぬ閾を書くな)。
"""

# ―― 幅B の材 = order181 の 6 対 (素, 実測) ――
PAIRS181 = [
    ("産", "o181 A4 名を取れた",        152, 158),
    ("得", "o181 得(81のうち合ふ)",      15,  15),
    ("誤", "o181 失(㋐86 替/落)",        10,   8),
    ("誤", "o181 新たな偽陽性",           12,  15),
    ("得", "o181 ㋑46→正しい名へ",         2,   1),
    ("産", "o181 適合の分子",             93,  94),
]

def build_bands_b():
    rs = {}
    for kind, name, moto, jitsu in PAIRS181:
        assert jitsu > 0, "ZERO_DENOM:" + name
        rs.setdefault(kind, []).append(((moto - jitsu) / jitsu, name))
    return {k: (min(x[0] for x in v), max(x[0] for x in v), v) for k, v in rs.items()}

BANDS_A = o1.BANDS          # ★order181 の物を一字も作り直さぬ★
BANDS_B = build_bands_b()

def band(bands, kind, moto, cap):
    lo_r, hi_r, _ = bands[kind]
    lo = math.floor(moto / (1.0 + hi_r)); hi = math.ceil(moto / (1.0 + lo_r))
    return max(0, min(lo, cap)), max(0, min(hi, cap))

# ============================================================
# 三. A5 の見込み (点) ―― ★走らせる前★ ・KNOWN の二欄は含まぬ
# ============================================================
FORECAST182 = [
    ("得(81のうち取り且つ合ふ)", "得", 12,  81, "A4 は 15。後窓の行/鍵を捨てる ゆゑ 幾らか減ると見る"),
    ("失(㋐86のうち替/落)",     "誤",  4,  86, "A4 は 8。A3 の真刈 8 は 鍵4/行3/file1 ゆゑ 7 件は戻ると見る"),
    ("新たな偽陽性",            "誤",  6,  81, "A4 は 15。後窓の行/鍵の偽陽性 10 件が消えると見る"),
    ("㋑46→正しい名へ",         "得",  1,  46, "A4 は 1。動く材が無い"),
    ("適合の分子",              "産", 95, 217, "86 − 失4 + ㋑正名1 + 得12 = 95"),
]

def forecast_table():
    out = []
    for key, kind, moto, cap, why in FORECAST182:
        la, ha = band(BANDS_A, kind, moto, cap)
        lb, hb = band(BANDS_B, kind, moto, cap)
        out.append((key, kind, moto, (la, ha), (lb, hb), cap, why))
    return out

def stage1():
    print("== order182 第一段 ―― ★A5 の得失を一度も数へる前★ ==")
    print(CRITERION7); print(TWO_BANDS)
    print("-- ★既に測つて居る欄(見込みに非ず・幅の比べから外す)★ --")
    for k, (v, why) in KNOWN.items(): print("  %-18s = %d   [%s]" % (k, v, why))
    print("-- 幅B の材 (order181 の 6 対) --")
    for kind, name, moto, jitsu in PAIRS181:
        print("  %s %-22s 素 %3d → 実測 %3d   r=%+.4f" % (kind, name, moto, jitsu, (moto - jitsu) / jitsu))
    print("-- 二本の倍率 --")
    for k in ("誤", "得", "産"):
        la, ha, va = BANDS_A[k]; lb, hb, vb = BANDS_B[k]
        print("  %s : 幅A(n=%d) 素×[%.3f, %.3f]   |   幅B(n=%d) 素×[%.3f, %.3f]"
              % (k, len(va), 1/(1+ha), 1/(1+la), len(vb), 1/(1+hb), 1/(1+lb)))
    print("-- A5 の見込み(点)と 二本の幅 --")
    for key, kind, moto, A, B, cap, why in forecast_table():
        print("  %-22s %s 点=%3d  幅A=[%3d,%3d]  幅B=[%3d,%3d]  上限=%3d" % (key, kind, moto, A[0], A[1], B[0], B[1], cap))
        print("      因: %s" % why)


# ════════════════════════════════════════════════════════════════════
# 第二段 ―― ★追記のみ★ (第一段を一字も書き換へず継ぐ)
#   第一段の sha16 (器A5 の得失を一度も数へる前に刷つた物) = 5c2420cac94ada48
#   ★第一段 144 行(wc) / 145 片(split) / 8,804 B★
# ════════════════════════════════════════════════════════════════════
STAGE1_SHA16 = "5c2420cac94ada48"

BAN_POST = ("行", "鍵")   # ★後窓に限り 採らぬ 二語★ (CRITERION7 ㋒)

def elem5(pre, post):
    """器A5 = 語彙は A2(境界付き)・窓は前46/後46・★後窓では BAN_POST を採らぬ★・同距離は前"""
    best = None
    for nm, pat in o9.A2_VOCAB:
        for m in pat.finditer(pre):
            d = len(pre) - m.end()
            if best is None or d < best[1]: best = (nm, d, "前")
        if nm in BAN_POST: continue
        for m in pat.finditer(post):
            d = m.start()
            if best is None or d < best[1]: best = (nm, d, "後")
    return (best[0], best[2]) if best else (None, None)

# ―― 人が新たに判ずる要が生じた 5 件 ――
#   (再利用が効かなんだ = A5 の名が A とも A3 とも A4 とも違ふ件のみ)
#   書式: 群|番号|合ふ/合はぬ|A5の名|己が讀んだ元素(台帳の逐語)
#   ★判ずる材は 台帳の元素の字のみ(㋕)・頭の名詞の補ひ(㋗)・迷ひは合はぬ側(㋖)★
#   ★頭の名詞 = 主要部★: 「A の B」は B ／ 「A(B)」は A (order180/181 と一字も違はぬ)
JUDGE182_SRC = """
G1|36|合はぬ|hit|required_fields を持つ行(型別)
G1|38|合はぬ|呼出|grep の hit 行
G3|13|合はぬ|定義|識別子の出現(def)
G3|18|合はぬ|枝|continue の行
G3|34|合はぬ|定義|continue の行
"""
JUDGE182 = {}
for _l in JUDGE182_SRC.strip().split("\n"):
    _g, _k, _j, _nm, _e = _l.split("|", 4)
    JUDGE182[(_g, int(_k))] = (_j, _nm, _e)

def stage2():
    led = o0.ledger()
    assert len(led) == 217, "LEDGER_DRIFT=%d" % len(led)

    rows = []   # (群,番号,A名,A3名,A4名,A5名,A5側,人が讀めたか,元素,o178code)
    for (g, k, f, ln, n, pre, post, anm, hum_ok, hum, code) in led:
        a3, s3 = o0.elem3(pre, post)
        a4, s4 = o1.elem4(pre, post)
        a5, s5 = elem5(pre, post)
        rows.append((g, k, anm, a3, a4, a5, s5, hum_ok, hum, code))

    # ―― 台帳の逐語との突合 (床(10)) ――
    drift = []
    for (g, k, anm, a3, a4, a5, s5, hum_ok, hum, code) in rows:
        if (g, k) in JUDGE182:
            j, nm, e = JUDGE182[(g, k)]
            if nm != (a5 or "-"): drift.append(("A5名", g, k, nm, a5))
            if e.strip() != hum.strip(): drift.append(("元素", g, k, e, hum))
    assert not drift, "JUDGE182_DRIFT:%s" % drift[:4]

    miss = []
    def verdict5(g, k, anm, a3, a4, a5, hum_ok, code):
        if a5 is None: return None
        if not hum_ok: return "外"
        if (g, k) in o0.JUDGE180 and a5 == a3: return o0.JUDGE180[(g, k)][0]
        if g == "G1" and a5 == anm:            return "合ふ" if code == "ア" else "合はぬ"
        if (g, k) in o1.JUDGE181 and a5 == a4: return o1.JUDGE181[(g, k)][0]
        if (g, k) in JUDGE182:                 return JUDGE182[(g, k)][0]
        miss.append((g, k, anm, a3, a4, a5)); return None
    ver = {}
    for (g, k, anm, a3, a4, a5, s5, hum_ok, hum, code) in rows:
        ver[(g, k)] = verdict5(g, k, anm, a3, a4, a5, hum_ok, code)
    assert not miss, "JUDGE_MISS:%s" % miss[:6]

    print("\n== order182 第二段 ―― 器A5(非対称) の実測 ==")
    print("第一段 sha16 =", STAGE1_SHA16, "(★A5 の得失を数へる前に刷つた★)")

    # ① 産出 と ★費えの当否(受入④)★
    got5 = [r for r in rows if r[5]]
    got4 = [r for r in rows if r[4]]
    got3 = [r for r in rows if r[3]]
    side = {}
    for r in got5: side[r[6]] = side.get(r[6], 0) + 1
    print("\n-- ① 名を取れた件 --")
    print("  器A 136 / 器A2 122 / 器A3 %d / 器A4 %d / ★器A5 %d★  (側: %s)"
          % (len(got3), len(got4), len(got5), side))
    print("  ★費えの当否(受入④)★: 申し出の前に測つた 139 ―― 実測 %d ⇒ %s"
          % (len(got5), "★一致★" if len(got5) == KNOWN["A5 が名を取れた件"][0] else "★食ひ違ふ(其の儘申す)★"))
    print("  ★人が新たに判ずる要★: 申し出の前に測つた 5 ―― 実測 %d ⇒ %s"
          % (len(JUDGE182), "★一致★" if len(JUDGE182) == KNOWN["人が新たに判ずる要"][0] else "★食ひ違ふ(其の儘申す)★"))

    # ② 得と失 (器A を基とする・条 o179-c ゆゑ両欄で)
    a_code = {(r[0], r[1]): r[9] for r in rows if r[0] == "G1"}
    lost   = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "ア" and r[5] != r[2]]
    gain81 = [r for r in rows if r[0] != "G1" and ver[(r[0], r[1])] == "合ふ"]
    fp81   = [r for r in rows if r[0] != "G1" and ver[(r[0], r[1])] == "合はぬ"]
    fixed46 = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "イ" and ver[(r[0], r[1])] == "合ふ"]
    G = len(gain81) + len(fixed46); L = len(lost) + len(fp81); d5 = G - L
    print("\n-- ② 得と失 --")
    print("  得 = 81 のうち取り且つ合ふ %d + ㋑46 を正しい名へ %d = ★%d★" % (len(gain81), len(fixed46), G))
    print("  失 = ㋐86 のうち替/落 %d + 新たな偽陽性 %d = ★%d★" % (len(lost), len(fp81), L))
    print("  差引 = %+d" % d5)
    print("  ★受入③ ―― 差引が ★損でなくなつたか★★")
    print("    四度の差引: A2 = -6 / A3 = -9 / A4 = -7 / ★A5 = %+d★  (★三度の損の記録は消さぬ=併記★)" % d5)
    print("    ⇒ 『差引が損でなくなつた』は ★%s★"
          % ("現に在る" if d5 >= 0 else "現に無い(四度目も損)"))

    # ③ 分子・率
    num5 = sum(1 for r in rows if ver[(r[0], r[1])] == "合ふ")
    den = 202
    print("\n-- ③ 五つの器を ★同じ分母 202★ で・★別分母も併記★ --")
    for nm, num, dn in [("器A", 86, 136), ("器A2", 82, 122), ("器A3", 95, len(got3)),
                        ("器A4", 94, len(got4)), ("器A5", num5, len(got5))]:
        print("  %-4s 分子 %3d / 取れた %3d = 適合(★別母:取れた件は讀めなんだを含み/分子は含まぬ★) %5.1f%%   再現 %3d/202 = %5.1f%%"
              % (nm, num, dn, 100.0 * num / dn, num, 100.0 * num / den))

    # ④ ★受入①② ―― 二本の幅の当否と勝敗★
    act = {"得(81のうち取り且つ合ふ)": len(gain81), "失(㋐86のうち替/落)": len(lost),
           "新たな偽陽性": len(fp81), "㋑46→正しい名へ": len(fixed46), "適合の分子": num5}
    print("\n-- ④ 見込み(点) と ★二本の幅★ (受入①) --")
    winA = winB = both_out = 0; wideA = wideB = 0
    for key, kind, moto, cap, why in FORECAST182:
        a = act[key]
        lA = band(BANDS_A, kind, moto, cap); lB = band(BANDS_B, kind, moto, cap)
        okA = lA[0] <= a <= lA[1]; okB = lB[0] <= a <= lB[1]
        wideA += lA[1] - lA[0]; wideB += lB[1] - lB[0]
        if okA: winA += 1
        if okB: winB += 1
        if not okA and not okB: both_out += 1
        print("  %-22s 点=%3d 実測=%3d 点の外れ %+4d" % (key, moto, a, a - moto))
        print("      幅A(過去四度版)=[%3d,%3d] %s   幅B(直近一度版)=[%3d,%3d] %s   %s"
              % (lA[0], lA[1], "内" if okA else "外", lB[0], lB[1], "内" if okB else "外",
                 "★二本とも外れた★" if (not okA and not okB) else ""))
    print("  ★幅A が含んだ欄 = %d / 幅B が含んだ欄 = %d / 二本とも外れた欄 = %d (全 %d 欄)★"
          % (winA, winB, both_out, len(FORECAST182)))
    print("  幅の広さの和: 幅A = %d / 幅B = %d" % (wideA, wideB))
    if winB > winA:   res = "★直近一度版が勝つた ⇒ 『材は新しい方が良い』は 現に在る★"
    elif winA > winB: res = "★過去四度版が勝つた ⇒ 『家老の条(幅の材は古びる)』は 此の一件では 現に無い★"
    else:
        if wideB < wideA:   res = "★同数 ∴ 幅の狭い方=直近一度版が勝つた ⇒ 『材は新しい方が良い』は 現に在る★"
        elif wideA < wideB: res = "★同数 ∴ 幅の狭い方=過去四度版が勝つた ⇒ 『家老の条』は 此の一件では 現に無い★"
        else:               res = "★同数かつ同幅 ⇒ 測定不能★"
    print("  ★受入② 結び:", res)

    # ⑤ ★A5 が捨てた二語で 何を失つたか★ (条 o179-c)
    print("\n-- ⑤ ★後窓の『行』『鍵』を捨てて 何を失つたか★ (A4 との差) --")
    chg = [r for r in rows if r[4] != r[5]]
    c = {}
    for r in chg:
        c[(r[4] or "-", r[5] or "-")] = c.get((r[4] or "-", r[5] or "-"), 0) + 1
    print("  A4 と名が変つた件 = %d" % len(chg))
    for (x, y), v in sorted(c.items(), key=lambda z: -z[1])[:8]:
        print("     A4=%-4s → A5=%-4s : %d 件" % (x, y, v))
    j5 = [(g, k) for (g, k) in JUDGE182]
    print("  ★本弾で人が判じた 5 件は 悉く『合はぬ』 ―― 而して 其の 5 件の元素の主要部は"
          " 行 が 4 件・出現 が 1 件 ∴ ★捨てた語が 正しかつた件も 現に落ちて居る★★")

    # ⑥ 悉皆の外 と 判定の出所
    outside = [r for r in rows if not r[7] and r[5]]
    print("\n-- ⑥ 悉皆の外 と 判定の出所 --")
    print("  人が名を讀めなんだ 15 件のうち A5 が名を取つた = %d 件 (★分子分母の外★)" % len(outside))
    src = {"o180 を再利用": 0, "o178 を再利用": 0, "o181 を再利用": 0, "本弾で人が判じた": 0}
    for (g, k, anm, a3, a4, a5, s5, hum_ok, hum, code) in rows:
        if a5 is None or not hum_ok: continue
        if (g, k) in o0.JUDGE180 and a5 == a3: src["o180 を再利用"] += 1
        elif g == "G1" and a5 == anm:          src["o178 を再利用"] += 1
        elif (g, k) in o1.JUDGE181 and a5 == a4: src["o181 を再利用"] += 1
        else:                                   src["本弾で人が判じた"] += 1
    print("  判定の出所 =", src, "計", sum(src.values()))


# ════════════════════════════════════════════════════════════════════
# 第三段 ―― ★実測を見た ★後で★ 書き足した★ (★自訴★・見込みに非ず・後知恵の数)
#   問: 「後窓の 行/鍵 を捨てたら 得 が 15→1 に落ちた」の因は何処に在るか
#   ★order181 §八 で己が数へたは ★失の内訳のみ★ であつた ―― 得の内訳を数へて居らぬ★
# ════════════════════════════════════════════════════════════════════
def stage3():
    led = o0.ledger()
    a_code = {}
    for (g, k, f, ln, n, pre, post, anm, hum_ok, hum, code) in led:
        if g == "G1": a_code[(g, k)] = code
    # A4 の 得(81のうち取り且つ合ふ 15) を ―― ★A4 が其の名を 何処の窓の 何の語で取つたか★ で割る
    gain4 = []
    for (g, k, f, ln, n, pre, post, anm, hum_ok, hum, code) in led:
        if g == "G1" or not hum_ok: continue
        a3, s3 = o0.elem3(pre, post); a4, s4 = o1.elem4(pre, post)
        if a4 is None: continue
        v = None
        if (g, k) in o0.JUDGE180 and a4 == a3: v = o0.JUDGE180[(g, k)][0]
        elif (g, k) in o1.JUDGE181:            v = o1.JUDGE181[(g, k)][0]
        if v == "合ふ": gain4.append((g, k, a4, s4))
    c = {}
    for (g, k, a4, s4) in gain4: c[(a4, s4)] = c.get((a4, s4), 0) + 1
    print("\n== 第三段 (★後知恵★) ―― 器A4 の 得 15 を ★語と窓★ で割る ==")
    for (nm, sd), v in sorted(c.items(), key=lambda z: -z[1]):
        print("   %-6s %s窓 = %2d 件  %s" % (nm, sd, v, "★A5 が捨てた★" if (nm in BAN_POST and sd == "後") else ""))
    killed = sum(v for (nm, sd), v in c.items() if nm in BAN_POST and sd == "後")
    print("   ⇒ 得 15 のうち ★後窓の 行/鍵 が担つて居た = %d 件 (%.1f%%)★" % (killed, 100.0 * killed / len(gain4)))
    print("   ⇒ order181 §八 の実測『失 24 のうち 行/鍵 = 17 件(70.8%)』と ★同じ語が★ 得も担つて居た")

if __name__ == "__main__":
    stage1()
    stage2()
    stage3()

# -*- coding: utf-8 -*-
# order183 第一段 ―― 器A6(枠の★絶対の適合★で採否) と ★幅を三本 立てる★
#
# ★此の第一段は 器A6 の ★得失・分子★ を一度も数へる前★ に書き切つた★。
#   ★受入②★: ★A6 の得失は 一つも数へて居らぬ★ (紙にも書く)
#   ★自訴 (百六十三)★: 「A6 が名を取れた件 = 151」「人が新たに判ずる要 = 3 件」の二つは
#     ★家老へ申し出る前の費え★ として ★既に測つて居る★ ∴ ★見込みに非ず★・幅の比べから外す。
#     ★但し 之は「設計に要る数」であり「答の数(得/失/分子)」には ★一度も触れて居らぬ★★。
#
# 令(家老third・逐語):
#   「★order183 採る(①主・②同走の副・③次へ)★」
#   「条=百六十三(設計に要る数を先に測るは可・★但し ★答の数★ に触れて居らぬ事を明かに書け★)」
#   「★②も採る=★家老の条(百五十九)を ★また★ 検めに行く★=★条を検める弾が ★二度目★
#     (百五十八は ★落ちた★・百五十九は ★之から★)★」
#   受入 五つ:
#     ①★閾(≥3 且つ >50%／<3 は残す)は ★先に字にした通り★ ―― ★実測を見て動かすな★
#     ②★『A6 の得失は一つも数へて居らぬ』を ★紙にも★ 書け★
#     ③★五度目の差引が ★損か否か★ を三択語で・★四度の損の記録は消すな(併記)★
#     ④★②は ★百五十九が ★立つ／立たぬ★ の双方が現に出得るか★ を ★先に★ 確かめよ(百六十五)★
#     ⑤wc/split 併記
#
# 走らせる処: /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/

import importlib.util, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

def _load(nick, fn):
    sp = importlib.util.spec_from_file_location(nick, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

o9 = _load("o9", "order179_recall_and_toolfix_v1.rule.py")   # 器A2 の語彙
o0 = _load("o0", "order180_window_widen_v1.rule.py")         # 器A3 + 217台帳 + JUDGE180
o1 = _load("o1", "order181_vocab_window_both_v1.rule.py")    # 器A4 + JUDGE181 + 幅A
o2 = _load("o2", "order182_asym_and_two_bands_v1.rule.py")   # 器A5 + JUDGE182 + 幅B

CRITERION8 = """器A6 = ★枠(語×窓)の ★絶対の適合★ で採否を決める器★
 ㋐語彙=器A2(境界付き) ㋑窓=前46/後46 ㋒同距離は前 (㋐㋑㋒ は器A4 と一字も違はぬ)
 ㋓★採否の閾 ―― 先に字にする(受入①・実測を見て動かさぬ)★:
     枠の ★判定済の件★ が 3 件以上 且つ ★適合 > 50.0%★ ⇒ ★採る★
     枠の ★判定済の件★ が 3 件未満          ⇒ ★材が足らぬゆゑ 残す★ (落とさぬ)
     其の余(判定済 3 件以上 且つ 適合 ≤ 50.0%) ⇒ ★落とす★
 ㋔★適合は「器A との差」でなく「人の名との一致」で測る★
     (差で作つた台帳では 前窓の全枠が 得0失0 と出る ―― ★0 は『効かぬ』の意に非ず『器A と同じ名』の意★)
 ㋕枠の材 = 器A4 が取つた 153 件 (人が名を讀めた分)・判定は o178/o180/o181 の再利用のみ
 ㋖判ずる材は台帳の元素の字のみ ㋗迷つたら合はぬ側 ㋘頭の名詞の補ひ(主要部・o180 以来 一字も違はぬ)
 ㋙讀めなんだ 15 件は分子分母の外"""

# ―― ★閾は先に字にした通り★ (受入①) ――
MIN_JUDGED = 3
MIN_PREC   = 50.0   # ★> 50.0% を採る (= と等しきは採らぬ)★

KNOWN = {"A6 が名を取れた件": (151, "家老へ申し出る ★前★ に費えとして測つた ∴ 見込みに非ず (百六十三)"),
         "人が新たに判ずる要": (3, "同上。申し出の便に『人の新判 3 件のみ』と書いて居る")}

THREE_BANDS = """★幅を三本★ (作り方を先に字にする ―― 受入①)
  幅A = ★過去四度版★ = order181 の BANDS を import (一字も作り直さぬ)
  幅B = ★直近一度版(o181 の 6 対)★ = order182 の BANDS_B を import (同上)
  幅C = ★A5 一度版(o182 の 5 対)★ = ★本弾で新たに作る★ (材 = order182 の 点 vs 実測)
  ★何故 幅C を立てるか★ = 条百五十九 (幅の材は ★新旧★ でなく ★手の種が同じか否か★ で選ぶ) の検め。
    A6 の手の種 = ★枠を落とす★ ―― A5 (★語を落とす★) と ★同種★ / A4 (★窓を広げる★) とは ★別種★。
    ∴ 条百五十九 が立つならば ★幅C が勝つ★。
  ★勝敗の規 (先に字にする)★: ①実測を含んだ欄が多い幅が勝つ ②同数なら幅の広さの和が小さい方
    ③三本とも外した欄は「★三本とも外れた★」と書く
  ★百六十五 (受入④) ―― 立つ／立たぬ の双方が現に出得るか を ★先に★ 確かめる★:
    三本の区間が ★互ひに 重ならぬ処を持つ★ 事を stage1 で数へて示す (§下 の表)。
    重なりが全欄で完全ならば 勝敗は付かず ―― 其の時は ★『測定不能』と書く★ と先に決める。"""

# ―― 幅C の材 = order182 の 5 対 (素 → 実測) ――
PAIRS182 = [("得", "o182 得(81のうち合ふ)", 12, 1),
            ("誤", "o182 失(㋐86 替/落)",   4, 6),
            ("誤", "o182 新たな偽陽性",     6, 11),
            ("得", "o182 ㋑46→正しい名へ",  1, 1),
            ("産", "o182 適合の分子",      95, 82)]

def build_bands_c():
    """★幅A・幅B と ★同じ形★ (r_min, r_max, 材の一覧) で作る ―― o181 build_bands と同じ算★"""
    rs = {}
    for kind, nm, moto, act in PAIRS182:
        assert act > 0, "ZERO_DENOM:" + nm
        rs.setdefault(kind, []).append(((moto - act) / float(act), nm))
    out = {}
    for k, v in rs.items():
        out[k] = (min(x[0] for x in v), max(x[0] for x in v), v)
    return out

BANDS_A = o1.BANDS
BANDS_B = o2.BANDS_B
BANDS_C = build_bands_c()

def band(bands, kind, moto, cap):
    """★o181 band_for / o182 band と ★一字も違はぬ算★★"""
    if kind not in bands: return (0, cap)
    lo_r, hi_r, _ = bands[kind]
    lo = math.floor(moto / (1.0 + hi_r)); hi = math.ceil(moto / (1.0 + lo_r))
    return max(0, min(lo, cap)), max(0, min(hi, cap))

# ―― 見込み (点) ―― ★A6 の得失を一度も数へる前に書いた★
FORECAST183 = [
 ("得(81のうち取り且つ合ふ)", "得", 14, 81,
  "A4 は 15。A6 は ★行 後窓(得 14 を担ふ枠)を残す★ ゆゑ 概ね保たれると見る"),
 ("失(㋐86のうち替/落)", "誤", 6, 86,
  "A4 は 8。落とす 4 枠(値後/鍵後/定義後/file後)が 失 8 を担つて居た ∴ 幾らか減ると見る"),
 ("新たな偽陽性", "誤", 9, 81,
  "A4 は 15。同上・落とす枠の失の多くは新偽と見る"),
 ("㋑46→正しい名へ", "得", 1, 46,
  "A4 は 1・A5 も 1。動く材が無い"),
 ("適合の分子", "産", 94, 217,
  "A4 は 94。落とす 4 枠の 合ふ は 2 件のみ ∴ 繰り上がりで戻ると見る"),
]

def three_band_table():
    out = []
    for key, kind, moto, cap, why in FORECAST183:
        out.append((key, kind, moto, cap, why,
                    band(BANDS_A, kind, moto, cap),
                    band(BANDS_B, kind, moto, cap),
                    band(BANDS_C, kind, moto, cap)))
    return out

def stage1():
    print("== order183 第一段 ―― 器A6 の宣言 と ★三本の幅★ (★A6 の得失を一度も数へる前★) ==")
    print("\n-- 閾 (受入①・先に字にした通り) --")
    print("  判定済 >= %d 且つ 適合 > %.1f%% ⇒ 採る / 判定済 < %d ⇒ 残す / 其の余 ⇒ 落とす"
          % (MIN_JUDGED, MIN_PREC, MIN_JUDGED))
    print("\n-- ★自訴 (百六十三)★ 既に測つて居る数 = ★設計に要る数★ (答の数に非ず) --")
    for k, (v, why) in KNOWN.items(): print("  %-16s = %3d   %s" % (k, v, why))
    print("  ★A6 の 得/失/分子 は ★一つも数へて居らぬ★ (受入②)★")

    print("\n-- 幅C の材 (order182 の 5 対) --")
    for kind, nm, moto, act in PAIRS182:
        r = (moto - act) / float(act)
        print("  %s %-22s 素 %3d → 実測 %3d   r=%+.4f" % (kind, nm, moto, act, r))
    print("\n-- 三本の倍率 --")
    for kind in ("誤", "得", "産"):
        row = "  %s : " % kind
        for nm, b in (("幅A", BANDS_A), ("幅B", BANDS_B), ("幅C", BANDS_C)):
            if kind in b:
                lo_r, hi_r, v = b[kind]
                row += "%s(n=%d) r∈[%+.4f, %+.4f]   " % (nm, len(v), lo_r, hi_r)
            else: row += "%s(材無)   " % nm
        print(row)

    print("\n-- A6 の見込み(点) と ★三本の幅★ --")
    for key, kind, moto, cap, why, lA, lB, lC in three_band_table():
        print("  %-22s %s 点=%3d 幅A=[%3d,%3d] 幅B=[%3d,%3d] 幅C=[%3d,%3d] 上限=%3d"
              % (key, kind, moto, lA[0], lA[1], lB[0], lB[1], lC[0], lC[1], cap))
        print("      因: %s" % why)

    # ―― ★百六十五 (受入④) 立つ／立たぬ の双方が現に出得るか を ★先に★ 確かめる★ ――
    print("\n-- ★百六十五 の先の確かめ ―― 三本は ★互ひに勝ち得るか★★ --")
    solo = {"幅A": 0, "幅B": 0, "幅C": 0}
    for key, kind, moto, cap, why, lA, lB, lC in three_band_table():
        for nm, me, others in (("幅A", lA, (lB, lC)), ("幅B", lB, (lA, lC)), ("幅C", lC, (lA, lB))):
            uniq = [x for x in range(me[0], me[1] + 1)
                    if not any(o[0] <= x <= o[1] for o in others)]
            if uniq: solo[nm] += 1
    print("  ★己だけが含む数を持つ欄★ : 幅A = %d 欄 / 幅B = %d 欄 / 幅C = %d 欄 (全 %d 欄)"
          % (solo["幅A"], solo["幅B"], solo["幅C"], len(FORECAST183)))
    ok = all(v > 0 for v in solo.values())
    print("  ⇒ 三本とも ★己だけが勝ち得る処★ を持つか = ★%s★"
          % ("現に在る (∴ 百五十九 は 立つ／立たぬ の双方が出得る)" if ok
             else "★現に無い ―― 勝敗が付かぬ恐れ★"))


# ════════════════════════════════════════════════════════════════════
# 第二段 ―― ★追記のみ★ (第一段を一字も書き換へず継ぐ)
#   第一段の sha16 (器A6 の得失を一度も数へる前に刷つた物) = 9534999535717985
#   ★第一段 166 行(wc) / 167 片(split) / 10,336 B★
# ════════════════════════════════════════════════════════════════════
STAGE1_SHA16 = "9534999535717985"

def rows_and_ver():
    """器A4 迄の名と ★判定★ を作る (o178/o180/o181 の再利用のみ・新たに判じて居らぬ)"""
    led = o0.ledger()
    rows = []
    for (g, k, f, ln, n, pre, post, anm, hum_ok, hum, code) in led:
        a3, s3 = o0.elem3(pre, post)
        a4, s4 = o1.elem4(pre, post)
        rows.append((g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post))
    ver = {}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        if a4 is None: ver[(g, k)] = None
        elif not hum_ok: ver[(g, k)] = "外"
        elif (g, k) in o0.JUDGE180 and a4 == a3: ver[(g, k)] = o0.JUDGE180[(g, k)][0]
        elif g == "G1" and a4 == anm: ver[(g, k)] = "合ふ" if code == "ア" else "合はぬ"
        elif (g, k) in o1.JUDGE181: ver[(g, k)] = o1.JUDGE181[(g, k)][0]
        else: ver[(g, k)] = None
    return rows, ver

def frame_ledger(rows, ver):
    """枠(語×窓)ごとの ★絶対の適合★ (器A との差でなく 人の名との一致)"""
    fr = {}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        if not hum_ok or a4 is None: continue
        d = fr.setdefault((a4, s4), {"取": 0, "合": 0, "否": 0})
        d["取"] += 1
        if ver[(g, k)] == "合ふ": d["合"] += 1
        elif ver[(g, k)] == "合はぬ": d["否"] += 1
    return fr

def keep_set(fr):
    """★閾は第一段で先に字にした通り・実測を見て動かさぬ (受入①)★"""
    keep = set(); tab = []
    for (nm, sd), d in fr.items():
        j = d["合"] + d["否"]; p = 100.0 * d["合"] / j if j else 0.0
        if j < MIN_JUDGED: how = "材<%d ∴ 残す" % MIN_JUDGED; take = True
        elif p > MIN_PREC: how = "採る"; take = True
        else: how = "落とす"; take = False
        if take: keep.add((nm, sd))
        tab.append((nm, sd, d["取"], j, d["合"], d["否"], p, how))
    tab.sort(key=lambda z: -z[6])
    return keep, tab

def elem6(pre, post, KEEP):
    best = None
    for nm, pat in o9.A2_VOCAB:
        if (nm, "前") in KEEP:
            for m in pat.finditer(pre):
                d = len(pre) - m.end()
                if best is None or d < best[1]: best = (nm, d, "前")
        if (nm, "後") in KEEP:
            for m in pat.finditer(post):
                d = m.start()
                if best is None or d < best[1]: best = (nm, d, "後")
    return (best[0], best[2]) if best else (None, None)

# ―― 人が新たに判ずる要が生じた 3 件 ――
#   書式: 群|番号|合ふ/合はぬ|A6の名|己が讀んだ元素(台帳の逐語)
#   ★㋖判ずる材は台帳の元素の字のみ・㋗迷つたら合はぬ側・㋘主要部(「A(B)」は A ／「A の B」は B)★
JUDGE183_SRC = """
G3|8|合はぬ|呼出|出現(def と呼出)
G3|9|合はぬ|呼出|関数
G3|11|合はぬ|行|出現(def+呼出)
"""
JUDGE183 = {}
for _l in JUDGE183_SRC.strip().split("\n"):
    _g, _k, _j, _nm, _e = _l.split("|", 4)
    JUDGE183[(_g, int(_k))] = (_j, _nm, _e)

def stage2():
    rows, ver4 = rows_and_ver()
    assert len(rows) == 217, "LEDGER_DRIFT=%d" % len(rows)
    fr = frame_ledger(rows, ver4)
    KEEP, tab = keep_set(fr)

    print("\n== order183 第二段 ―― 器A6 の実測 ==")
    print("第一段 sha16 =", STAGE1_SHA16, "(★A6 の得失を数へる前に刷つた★)")

    print("\n-- ① 枠(語×窓)の ★絶対の適合★ と 採否 (閾は第一段の通り) --")
    for nm, sd, tori, j, y, n, p, how in tab:
        print("  %-10s 取%3d 判%3d 合%3d 否%3d 適合%5.1f%%  %s"
              % (nm + " " + sd + "窓", tori, j, y, n, p, how))
    print("  ★採る枠 = %d / 全 %d 枠★" % (len(KEEP), len(fr)))

    # ―― A6 の名 と 判定 ――
    a5m = {}; a6m = {}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        a5m[(g, k)] = o2.elem5(pre, post)[0]
        a6m[(g, k)] = elem6(pre, post, KEEP)

    drift = []
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        if (g, k) in JUDGE183:
            j, nm, e = JUDGE183[(g, k)]
            if nm != (a6m[(g, k)][0] or "-"): drift.append(("A6名", g, k, nm, a6m[(g, k)][0]))
            if e.strip() != hum.strip(): drift.append(("元素", g, k, e, hum))
    assert not drift, "JUDGE183_DRIFT:%s" % drift[:4]

    miss = []
    def verdict6(g, k, anm, a3, a4, hum_ok, code):
        a6 = a6m[(g, k)][0]
        if a6 is None: return None
        if not hum_ok: return "外"
        if (g, k) in o0.JUDGE180 and a6 == a3: return o0.JUDGE180[(g, k)][0]
        if g == "G1" and a6 == anm: return "合ふ" if code == "ア" else "合はぬ"
        if (g, k) in o1.JUDGE181 and a6 == a4: return o1.JUDGE181[(g, k)][0]
        if (g, k) in o2.JUDGE182 and a6 == a5m[(g, k)]: return o2.JUDGE182[(g, k)][0]
        if (g, k) in JUDGE183: return JUDGE183[(g, k)][0]
        miss.append((g, k, anm, a3, a4, a6)); return None
    ver = {}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        ver[(g, k)] = verdict6(g, k, anm, a3, a4, hum_ok, code)
    assert not miss, "JUDGE_MISS:%s" % miss[:6]

    got6 = [r for r in rows if a6m[(r[0], r[1])][0]]
    side = {}
    for r in got6:
        sd = a6m[(r[0], r[1])][1]; side[sd] = side.get(sd, 0) + 1
    print("\n-- ② 名を取れた件 と ★費えの当否★ --")
    print("  器A 136 / A2 122 / A3 170 / A4 158 / A5 139 / ★A6 %d★ (側: %s)" % (len(got6), side))
    print("  費え(申し出の前に測つた 151) ―― 実測 %d ⇒ %s"
          % (len(got6), "★一致★" if len(got6) == KNOWN["A6 が名を取れた件"][0] else "★食ひ違ふ(其の儘申す)★"))
    print("  人の新判(測つた 3) ―― 実測 %d ⇒ %s"
          % (len(JUDGE183), "★一致★" if len(JUDGE183) == KNOWN["人が新たに判ずる要"][0] else "★食ひ違ふ(其の儘申す)★"))

    # ―― ③ 得と失 (器A を基とする・両欄で) ――
    a_code = {(r[0], r[1]): r[8] for r in rows if r[0] == "G1"}
    lost = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "ア"
            and a6m[(r[0], r[1])][0] != r[2]]
    gain81 = [r for r in rows if r[0] != "G1" and ver[(r[0], r[1])] == "合ふ"]
    fp81 = [r for r in rows if r[0] != "G1" and ver[(r[0], r[1])] == "合はぬ"]
    fixed46 = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "イ"
               and ver[(r[0], r[1])] == "合ふ"]
    G = len(gain81) + len(fixed46); L = len(lost) + len(fp81); d6 = G - L
    print("\n-- ③ 得と失 --")
    print("  得 = 81 のうち取り且つ合ふ %d + ㋑46 を正しい名へ %d = ★%d★" % (len(gain81), len(fixed46), G))
    print("  失 = ㋐86 のうち替/落 %d + 新たな偽陽性 %d = ★%d★" % (len(lost), len(fp81), L))
    print("  ★受入③ 五度目の差引★ : A2 = -6 / A3 = -9 / A4 = -7 / A5 = -15 / ★A6 = %+d★"
          " (★四度の損の記録は消さぬ=併記★)" % d6)
    print("  ⇒ 『差引が損でなくなつた』は ★%s★"
          % ("現に在る" if d6 >= 0 else "現に無い(五度目も損)"))

    # ―― ④ 分子・率 ――
    num6 = sum(1 for r in rows if ver[(r[0], r[1])] == "合ふ")
    den = 202
    print("\n-- ④ 六つの器を ★同じ分母 202★ で・★別分母も併記★ --")
    for nm, num, dn in [("器A", 86, 136), ("器A2", 82, 122), ("器A3", 95, 170),
                        ("器A4", 94, 158), ("器A5", 82, 139), ("器A6", num6, len(got6))]:
        print("  %-4s 分子 %3d / 取れた %3d = 適合(★別母:取れた件は讀めなんだを含み/分子は含まぬ★) %5.1f%%   再現 %3d/202 = %5.1f%%"
              % (nm, num, dn, 100.0 * num / dn, num, 100.0 * num / den))

    # ―― ⑤ ★三本の幅★ の当否 (受入①④・百五十九の検め) ――
    act = {"得(81のうち取り且つ合ふ)": len(gain81), "失(㋐86のうち替/落)": len(lost),
           "新たな偽陽性": len(fp81), "㋑46→正しい名へ": len(fixed46), "適合の分子": num6}
    print("\n-- ⑤ 見込み(点) と ★三本の幅★ --")
    win = {"幅A": 0, "幅B": 0, "幅C": 0}; wide = {"幅A": 0, "幅B": 0, "幅C": 0}; allout = 0
    for key, kind, moto, cap, why, lA, lB, lC in three_band_table():
        a = act[key]
        oks = {}
        for nm, l in (("幅A", lA), ("幅B", lB), ("幅C", lC)):
            oks[nm] = (l[0] <= a <= l[1]); wide[nm] += l[1] - l[0]
            if oks[nm]: win[nm] += 1
        if not any(oks.values()): allout += 1
        print("  %-22s 点=%3d 実測=%3d 外れ%+4d  A=[%3d,%3d]%s B=[%3d,%3d]%s C=[%3d,%3d]%s %s"
              % (key, moto, a, a - moto, lA[0], lA[1], "内" if oks["幅A"] else "外",
                 lB[0], lB[1], "内" if oks["幅B"] else "外",
                 lC[0], lC[1], "内" if oks["幅C"] else "外",
                 "★三本とも外れた★" if not any(oks.values()) else ""))
    print("  ★含んだ欄★ 幅A=%d / 幅B=%d / ★幅C=%d★ (全 %d 欄) ／ 三本とも外れた欄=%d"
          % (win["幅A"], win["幅B"], win["幅C"], len(FORECAST183), allout))
    print("  幅の広さの和: A=%d B=%d C=%d" % (wide["幅A"], wide["幅B"], wide["幅C"]))
    best = sorted(win.items(), key=lambda z: (-z[1], wide[z[0]]))
    top = best[0][0]; tie = [n for n, v in win.items() if v == best[0][1]]
    if len(tie) > 1:
        tie.sort(key=lambda n: wide[n]); top = tie[0]
        if wide[tie[0]] == wide[tie[1]]: top = None
    print("  ★受入②④ 結び (百五十九=『幅の材は 手の種が同じか否かで選ぶ』)★:")
    if top is None:
        print("    ★測定不能 (含んだ欄も幅の広さも同じ)★")
    elif top == "幅C":
        print("    ★幅C(A5 一度版=A6 と同種の手)が勝つた ⇒ 条百五十九 は ★現に在る★★")
    else:
        print("    ★%s が勝つた ⇒ 条百五十九 は ★此の一件では 現に無い★★" % top)

    # ―― ⑥ 判定の出所 と 悉皆の外 ――
    outside = [r for r in rows if not r[6] and a6m[(r[0], r[1])][0]]
    src = {"o180": 0, "o178": 0, "o181": 0, "o182": 0, "本弾で人が判じた": 0}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        a6 = a6m[(g, k)][0]
        if a6 is None or not hum_ok: continue
        if (g, k) in o0.JUDGE180 and a6 == a3: src["o180"] += 1
        elif g == "G1" and a6 == anm: src["o178"] += 1
        elif (g, k) in o1.JUDGE181 and a6 == a4: src["o181"] += 1
        elif (g, k) in o2.JUDGE182 and a6 == a5m[(g, k)]: src["o182"] += 1
        else: src["本弾で人が判じた"] += 1
    print("\n-- ⑥ 悉皆の外 と 判定の出所 --")
    print("  人が名を讀めなんだ 15 件のうち A6 が名を取つた = %d 件 (★分子分母の外★)" % len(outside))
    print("  判定の出所 =", src, "計", sum(src.values()))


# ── 第三段 ★後知恵(実測を見た後に書き足した)・自訴する★ ──
#   問: 枠を「落とす」と 其の枠が担つて居た ★失★ は 消えるのか 移るのか
def stage3():
    rows, ver4 = rows_and_ver()
    fr = frame_ledger(rows, ver4); KEEP, _ = keep_set(fr)
    DROP = set(k for k in fr if k not in KEEP)
    print("\n== 第三段 (★後知恵★) ―― 落とした枠の件は 何処へ流れたか ==")
    print("  落とした枠 =", sorted("%s %s窓" % k for k in DROP))
    a6m = {}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        a6m[(g, k)] = elem6(pre, post, KEEP)
    to = {}; n = 0; still = 0
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code, pre, post) in rows:
        if (a4, s4) not in DROP or not hum_ok: continue
        n += 1
        nm6, sd6 = a6m[(g, k)]
        key = ("%s %s窓" % (nm6, sd6)) if nm6 else "名を取らぬ"
        to[key] = to.get(key, 0) + 1
        if nm6 is not None: still += 1
    print("  落とした枠で A4 が名を取つて居た(判定済) = %d 件" % n)
    print("  そのうち A6 が ★別の枠へ流れた★ = %d 件 / ★名を取らぬに落ちた★ = %d 件" % (still, n - still))
    for kk in sorted(to, key=lambda z: -to[z]):
        print("    → %-10s %d 件" % (kk, to[kk]))

if __name__ == "__main__":
    stage1()
    stage2()
    stage3()

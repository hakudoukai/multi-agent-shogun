# -*- coding: utf-8 -*-
# order181 第一段 ―― 器A4(語彙A2 + 窓A3)の宣言 と ★幅の作り方★
#
# ★此の第一段は 器A4 を ★一度も走らせる前★ に書き切つた★。
#   第二段(判定表・勘定)は ★追記のみ★ で継ぎ、第一段の sha を assert する。
#
# 令(家老third・逐語):
#   「order181＝①を主・②を同じ走の副(費えぬなら)・③は次へ」
#   「外れ続ける物を ★止める★ のでなく ―― ★外れ方を ★測つて 幅に畳め★」
#   受入 五つ:
#     ①幅は ★作り方を先に字にして★ 作れ(★後から広げるな★)
#     ②実測が幅に ★入つたか否か★ を三択語で・★入らねば『幅も外れた』と書け★
#     ③得失が ★足し算か★ = A2 単独／A3 単独／A4 を ★三行で★・足し算でなければ其の儘
#     ④②は同じ走で費えぬなら・費えるなら 行はず 次へ回すと申せ
#     ⑤行数は ★wc/split 併記★
#
# 走らせる処: /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/
#             (席の作法 五条目の補ひ ―― 規に『何処で走らせるか』を書き添へよ)

import importlib.util, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

def _load(nick, fn):
    sp = importlib.util.spec_from_file_location(nick, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

# ―― 器・台帳(★一字も改めず★ import する) ――
oA  = _load("oA",  "order175_ken_element_census_v1.rule.py")        # 器A  5463ac137aca2e8a
oB  = _load("oB",  "order176_ken_element_widen_v1.rule.py")        # 器B  6187690653725898
o7  = _load("o7",  "order177_ken_attribution_human_v1.rule.py")     # 44台帳 4254a3567433e66e
o8  = _load("o8",  "order178_ken_positive_audit_v1.rule.py")        # 136台帳 3cfd76e078bebaa3
o9  = _load("o9",  "order179_recall_and_toolfix_v1.rule.py")        # 37台帳+器A2 2f816583fa7b0454

# ============================================================
# 一. CRITERION6 ―― 器A4 の宣言 (★走らせる前★)
# ============================================================
CRITERION6 = """
器A4 = ★語彙は器A2(境界付き)★ + ★窓は前46字 と 後46字 の双方★

 ㋐ 語彙 : 器A2 と一字も違はぬ。即ち 器A の 11 語を ★識別子境界の明示クラス★
           [^A-Za-z0-9_] で括つた形。(器B 6187690653725898 の境界規に依る)
 ㋑ 窓   : 「N 件」の ★前 46 字★ と ★後 46 字★ の双方を見る。(器A3 と同じ幅)
 ㋒ 同距離: 前と後の双方に語彙が当たり ★字の距離が等しい★ 時は ★前を採る★。
           (此の一条は order181 の ③ へ回した ―― 本弾では ★件数だけ★ を数へ、
            向きを替へた時の効きは測らぬ)
 ㋓ 判ずる材: ★台帳の元素の字のみ★。件語の周りの字を新たに讀み直して
           判定を動かす事はせぬ。
 ㋔ 迷つたら ★合はぬ側★ へ落とす。
 ㋕ ★頭の名詞の補ひ★(order180 で讀む途中に立てた物)を ★今度は先に宣言する★:
     元素の字が「A(B)」「A の B」の形の時は ★文の頭の名詞★ で判ずる。
     例) 「continue の行」= 行 / 「continue(表の行)」= continue / 「関数(def 行)」= 関数
 ㋖ 人が名を讀めなんだ 15 件(㋒)は ★分子にも分母にも入れぬ★。
"""

# ============================================================
# 二. ★幅の作り方★ (受入① ―― 先に字にして作る・後から広げぬ)
# ============================================================
BAND_METHOD = """
★材★ = 己が過去に置いた ★素の見込み★ と ★人讀みの実測★ の対。
       即ち ★己の失敗の記録★ そのもの(家老の許し「幅の材が過去四度の外れ幅なるも良し」)。

★除く対★ = 実測が 0 の対は ★比が作れぬ★ ゆゑ名指して除く。
       ―― o177「紙の疵」素 38 → 実測 0。★此の一対のみ★ を除く。

★外れの度 r★ = (素 − 実測) / 実測。  r>0 は ★甘い(多く見た)★、r<0 は ★辛い(少なく見た)★。

★欄の種で分ける★ ―― 大小ではなく ★何を数へた欄か★ で分ける。理由 =
   過去の対を並べると r の ★向き★ が欄の種で揃つて居り、大小では揃はぬ。
     ㋐ 誤り欄 : 器が ★誤つた/取り零した★ 件を数へる欄
     ㋑ 得欄   : 直しが ★効いて改まる★ 件を数へる欄
     ㋒ 産出欄 : 器が ★名を取れた/当たつた/判じ得ぬ★ 件を数へる欄

★幅★ = 実測 = 素/(1+r) ゆゑ、その種の r の 最小・最大 を用ゐて
        幅 = [ 素/(1+r_max) , 素/(1+r_min) ]。
        下限は floor、上限は ceil。母集団の上限で切る(下限は 0 で切る)。

★点は残す★ = 素の見込み(点)も併せ書く。点が幅の外へ出る欄が生じ得るが、
        其れは ★過去の癖が点を動かして居る★ 証ゆゑ ★動かさず其の儘★ に置く。
"""

# ―― 材の対 (出所を一つ一つ名指す) ――
# (種, 名, 素, 実測, 出所)
PAIRS = [
    ("誤", "o177 窓の狭さ",              o7.MIKOMI["窓の狭さ"],            36, "order177 MIKOMI / 人讀み ㋐36"),
    ("誤", "o178 ㋑偽陽性",              o8.MIKOMI178["㋑ 別の事柄の名(偽陽性)"], 46, "order178 MIKOMI178 / 実測 46"),
    ("誤", "o179 37㋐ 名が字に在り",      o9.MIKOMI_37_RAW["㋐ 名が字に在る(取り零し)"],           28, "order179 MIKOMI_37_RAW / 実測 28"),
    ("誤", "o179 37㋑ 窓・基準の外",      o9.MIKOMI_37_RAW["㋑ 窓・基準の外"],            6, "order179 MIKOMI_37_RAW / 実測 6"),
    ("誤", "o179 A2 真の巻添へ",          o9.MIKOMI_A2_RAW["真(㋐86)のうち巻添へで落とす"], 4, "order179 MIKOMI_A2_RAW / 実測 4"),
    ("誤", "o180 失(真を刈る)",            5,                                8, "order180 §五 見込み / 実測 8"),
    ("得", "o179 A2 偽陽性の名を捨てた",   o9.MIKOMI_A2_RAW["偽陽性(㋑46)のうち解消"], 12, "order179 MIKOMI_A2_RAW / 実測 12"),
    ("得", "o180 得(新たに取れて合ふ)",    30,                               16, "order180 §五 見込み / 実測 16"),
    ("得", "o180 ㋑46→正しい名へ",         5,                                1, "order180 §五 見込み / 実測 1"),
    ("産", "o178 ㋐当たり",               o8.MIKOMI178["㋐ 器の名が当たり"], 86, "order178 MIKOMI178 / 実測 86"),
    ("産", "o178 ㋒判じ得ぬ",             o8.MIKOMI178["㋒ 判じ得ぬ"],       4, "order178 MIKOMI178 / 実測 4"),
    ("産", "o179 37㋒ 語彙に無し",         o9.MIKOMI_37_RAW["㋒ 字に無い"],            3, "order179 MIKOMI_37_RAW / 実測 3"),
    ("産", "o180 A3 名を取れた",           190,                            170, "order180 §五 見込み / 実測 170"),
    ("産", "o180 適合の分子",              116,                             95, "order180 §五 見込み / 実測 95"),
]
EXCLUDED_PAIRS = [
    ("誤", "o177 紙の疵", o7.MIKOMI["紙の疵"], 0, "★実測 0 ゆゑ 比が作れぬ ―― 名指して除く★"),
]

KIND_NAME = {"誤": "㋐ 誤り欄", "得": "㋑ 得欄", "産": "㋒ 産出欄"}

def build_bands():
    """材の対から 種ごとの r の範囲を作る。★此の関数は 素を一つも見ぬ★。"""
    rs = {}
    for kind, name, moto, jitsu, src in PAIRS:
        assert jitsu > 0, "ZERO_DENOM:" + name
        rs.setdefault(kind, []).append(((moto - jitsu) / jitsu, name))
    out = {}
    for k, v in rs.items():
        lo = min(x[0] for x in v); hi = max(x[0] for x in v)
        out[k] = (lo, hi, v)
    return out

BANDS = build_bands()

def band_for(kind, moto, cap):
    lo_r, hi_r, _ = BANDS[kind]
    lo = math.floor(moto / (1.0 + hi_r))
    hi = math.ceil(moto / (1.0 + lo_r))
    lo = max(0, min(lo, cap)); hi = max(0, min(hi, cap))
    return lo, hi

# ============================================================
# 三. A4 の見込み (点) ―― ★走らせる前★ に置く
# ============================================================
# (鍵, 種, 素の点, 母集団上限, 何の数か)
FORECAST181 = [
    ("A4が名を取れた件",      "産", 152, 217, "母 217 の件語のうち A4 が元素の名を一つ返した件数"),
    ("得(81のうち取り且つ合ふ)", "得",  15,  81, "器A が取れなんだ 81 のうち A4 が取り、人讀みと合ふ件数"),
    ("失(㋐86のうち替/落)",    "誤",  10,  86, "器A が当たつて居た 86 のうち A4 が別名へ替へた・名を落とした件数"),
    ("新たな偽陽性",           "誤",  12,  81, "81 のうち A4 が取つたが人讀みと合はぬ件数"),
    ("㋑46→正しい名へ",        "得",   2,  46, "器A の偽陽性 46 のうち A4 が ★正しい名へ★ 替へた件数"),
    ("適合の分子",             "産",  93, 217, "A4 が名を取つた件のうち 人讀みと合ふ件数"),
]

def forecast_table():
    rows = []
    for key, kind, moto, cap, what in FORECAST181:
        lo, hi = band_for(kind, moto, cap)
        rows.append((key, kind, moto, lo, hi, cap, what, (lo <= moto <= hi)))
    return rows

def stage1():
    print("== order181 第一段 ―― ★器A4 を一度も走らせる前★ ==")
    print(CRITERION6)
    print(BAND_METHOD)
    print("-- 材の対 (%d 対) --" % len(PAIRS))
    for kind, name, moto, jitsu, src in PAIRS:
        r = (moto - jitsu) / jitsu
        print("  %s %-26s 素 %3d → 実測 %3d   r=%+.4f   [%s]" % (KIND_NAME[kind][0], name, moto, jitsu, r, src))
    print("-- 除いた対 (%d 対) --" % len(EXCLUDED_PAIRS))
    for kind, name, moto, jitsu, src in EXCLUDED_PAIRS:
        print("  %s %-26s 素 %3d → 実測 %3d   %s" % (KIND_NAME[kind][0], name, moto, jitsu, src))
    print("-- 種ごとの r の範囲 と 倍率 --")
    for k in ("誤", "得", "産"):
        lo, hi, v = BANDS[k]
        print("  %s : n=%d  r∈[%+.4f, %+.4f]  ⇒ 幅 = 素×[%.3f, %.3f]"
              % (KIND_NAME[k], len(v), lo, hi, 1.0/(1.0+hi), 1.0/(1.0+lo)))
    print("-- A4 の見込み (点 と 幅) --")
    out = 0
    for key, kind, moto, lo, hi, cap, what, inside in forecast_table():
        print("  %-22s %s  点=%3d  幅=[%3d, %3d]  上限=%3d  点が幅の内=%s"
              % (key, KIND_NAME[kind][0], moto, lo, hi, cap, "現に在る" if inside else "★現に無い★"))
        if not inside: out += 1
    print("  ★点が幅の外へ出た欄 = %d / %d★  (過去の癖が点を動かして居る証)" % (out, len(FORECAST181)))

if __name__ == "__main__":
    stage1()


# ════════════════════════════════════════════════════════════════════
# 第二段 ―― ★追記のみ★ (第一段を一字も書き換へず継ぐ)
#   第一段の sha16 (器A4 を一度も走らせる前に刷つた物) = 362bd8bed85729ef
#   ★第一段 172 行(wc) / 173 片(split) / 10,902 B★
# ════════════════════════════════════════════════════════════════════
STAGE1_SHA16 = "362bd8bed85729ef"
o0 = _load("o0", "order180_window_widen_v1.rule.py")   # 器A3 + 217台帳 + JUDGE180

def elem4(pre, post):
    """器A4 = ★語彙は A2(境界付き)★ ・窓は前後 46 字。同距離なら前。無ければ (None,None)"""
    best = None
    for nm, pat in o9.A2_VOCAB:
        for m in pat.finditer(pre):
            d = len(pre) - m.end()
            if best is None or d < best[1]: best = (nm, d, "前")
        for m in pat.finditer(post):
            d = m.start()
            if best is None or d < best[1]: best = (nm, d, "後")
    return (best[0], best[2]) if best else (None, None)

# ―― 人が新たに判ずる要が生じた 7 件 ――
#   (再利用が効かなんだ = A4 の名が A とも A3 とも違ふ件のみ)
#   書式: 群|番号|合ふ/合はぬ|A4の名|己が讀んだ元素(台帳の逐語)
#   ★判ずる材は 台帳の元素の字のみ(CRITERION6 ㋓)・頭の名詞の補ひ(㋕)・迷ひは合はぬ側(㋔)★
JUDGE181_SRC = """
G1|85|合はぬ|行|ls-files の file
G1|112|合はぬ|値|continue(A系)
G1|133|合はぬ|値|"total_checks" の出現
G1|134|合はぬ|file|'total_checks' の出現
G3|9|合はぬ|file|関数
G3|14|合はぬ|枝|ルール(mandatory_fields_guard 型)
G3|15|合はぬ|枝|ルール(mandatory_fields_guard 型)
"""
JUDGE181 = {}
for _l in JUDGE181_SRC.strip().split("\n"):
    _g, _k, _j, _nm, _e = _l.split("|", 4)
    JUDGE181[(_g, int(_k))] = (_j, _nm, _e)

def stage2():
    led = o0.ledger()
    assert len(led) == 217, "LEDGER_DRIFT=%d" % len(led)

    rows = []      # (群,番号,A の名,A3 の名,A4 の名,A4 の側,人が讀めたか,元素,o178 code)
    for (g, k, f, ln, n, pre, post, anm, hum_ok, hum, code) in led:
        a3, s3 = o0.elem3(pre, post)
        a4, s4 = elem4(pre, post)
        rows.append((g, k, anm, a3, a4, s4, hum_ok, hum, code))

    # ―― 台帳の逐語との突合 (床(10)・o180 と同じ守り) ――
    miss = []; drift = []
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code) in rows:
        if (g, k) in JUDGE181:
            j, nm, e = JUDGE181[(g, k)]
            if nm != (a4 or "-"): drift.append(("A4名", g, k, nm, a4))
            if e.strip() != hum.strip(): drift.append(("元素", g, k, e, hum))
    assert not drift, "JUDGE181_DRIFT:%s" % drift[:4]

    # ―― 判定の解き (再利用 → 新判定) ――
    def verdict4(g, k, anm, a3, a4, hum_ok, code):
        if a4 is None: return None
        if not hum_ok:  return "外"          # 人が名を讀めなんだ 15 件 = 分子分母の外
        if (g, k) in o0.JUDGE180 and a4 == a3: return o0.JUDGE180[(g, k)][0]
        if g == "G1" and a4 == anm:            return "合ふ" if code == "ア" else "合はぬ"
        if (g, k) in JUDGE181:                 return JUDGE181[(g, k)][0]
        miss.append((g, k, anm, a3, a4)); return None
    ver = {}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code) in rows:
        ver[(g, k)] = verdict4(g, k, anm, a3, a4, hum_ok, code)
    assert not miss, "JUDGE_MISS:%s" % miss[:6]

    print("\n== order181 第二段 ―― 器A4 の実測 ==")
    print("第一段 sha16 =", STAGE1_SHA16, "(★A4 を走らせる前に刷つた★)")

    # ① 産出
    got4 = [r for r in rows if r[4]]
    side = {}
    for r in got4: side[r[5]] = side.get(r[5], 0) + 1
    got3 = [r for r in rows if r[3]]
    print("\n-- ① 名を取れた件 --")
    print("  器A  = 136 / 器A2 = 122 / 器A3 = %d / ★器A4 = %d★  (側: %s)"
          % (len(got3), len(got4), side))

    # ② 得と失 (器A を基とする)
    a_code = {(r[0], r[1]): r[8] for r in rows if r[0] == "G1"}
    lost = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "ア" and r[4] != r[2]]
    gain81 = [r for r in rows if r[0] != "G1" and ver[(r[0], r[1])] == "合ふ"]
    fp81   = [r for r in rows if r[0] != "G1" and ver[(r[0], r[1])] == "合はぬ"]
    fixed46 = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "イ" and ver[(r[0], r[1])] == "合ふ"]
    print("\n-- ② 得と失 (★両欄で書く・条 o179-c★) --")
    print("  得 = 81 のうち取り且つ合ふ %d + ㋑46 を正しい名へ %d = ★%d★" % (len(gain81), len(fixed46), len(gain81) + len(fixed46)))
    print("  失 = ㋐86 のうち替/落 %d + 新たな偽陽性 %d = ★%d★" % (len(lost), len(fp81), len(lost) + len(fp81)))
    d = (len(gain81) + len(fixed46)) - (len(lost) + len(fp81))
    print("  差引 = %+d  (★%s★)" % (d, "得" if d > 0 else ("損" if d < 0 else "同")))

    # ③ 分子・率 (★分母を欄ごとに書く・床⑷★)
    num4 = sum(1 for r in rows if ver[(r[0], r[1])] == "合ふ")
    den_recall = 202   # 人が名を讀めた件の総数 (217 − 讀めなんだ 15)
    print("\n-- ③ 四つの器を ★同じ分母 202★ で・★別分母も併記★ --")
    tbl = [("器A", 86, 136), ("器A2", 82, 122), ("器A3", 95, len(got3)), ("器A4", num4, len(got4))]
    for nm, num, den in tbl:
        print("  %-4s 分子 %3d / 取れた %3d = 適合(★別母:取れた件は讀めなんだを含み/分子は含まぬ★) %5.1f%%   再現 %3d/202 = %5.1f%%"
              % (nm, num, den, 100.0 * num / den, num, 100.0 * num / den_recall))

    # ④ ★得失が足し算か★ (受入③ ―― 三行で)
    print("\n-- ④ 得失は ★足し算か★ (器A を 0 とした差) --")
    print("  A2 単独(語彙のみ)   : Δ取れた %+d   Δ分子 %+d" % (122 - 136, 82 - 86))
    print("  A3 単独(窓のみ)     : Δ取れた %+d   Δ分子 %+d" % (len(got3) - 136, 95 - 86))
    print("  A4(語彙+窓)         : Δ取れた %+d   Δ分子 %+d" % (len(got4) - 136, num4 - 86))
    print("  足し算なら          : Δ取れた %+d   Δ分子 %+d"
          % ((122 - 136) + (len(got3) - 136), (82 - 86) + (95 - 86)))
    print("  食ひ違ひ            : Δ取れた %+d   Δ分子 %+d"
          % ((len(got4) - 136) - ((122 - 136) + (len(got3) - 136)),
             (num4 - 86) - ((82 - 86) + (95 - 86))))

    # ⑤ 見込み突合 ―― ★点★ と ★幅★ (受入②)
    act = {"A4が名を取れた件": len(got4), "得(81のうち取り且つ合ふ)": len(gain81),
           "失(㋐86のうち替/落)": len(lost), "新たな偽陽性": len(fp81),
           "㋑46→正しい名へ": len(fixed46), "適合の分子": num4}
    print("\n-- ⑤ 見込み(点・幅) と 実測 (★入らねば『幅も外れた』と書く★) --")
    inb = 0; outb = 0
    for key, kind, moto, lo, hi, cap, what, pin in forecast_table():
        a = act[key]
        ok = (lo <= a <= hi)
        if ok: inb += 1
        else: outb += 1
        print("  %-22s 点=%3d 幅=[%3d,%3d] 実測=%3d  点の外れ %+4d  幅の内=%s"
              % (key, moto, lo, hi, a, a - moto, "現に在る" if ok else "★現に無し=幅も外れた★"))
    print("  ★幅に入つた欄 = %d / 外れた欄 = %d (全 %d 欄)★" % (inb, outb, len(FORECAST181)))
    hi_side = sum(1 for key, kind, moto, lo, hi, cap, what, pin in forecast_table() if act[key] < moto)
    lo_side = sum(1 for key, kind, moto, lo, hi, cap, what, pin in forecast_table() if act[key] > moto)
    print("  点の向き: ★甘い(実測が下)= %d 欄 / 辛い(実測が上)= %d 欄 / 中り= %d 欄★"
          % (hi_side, lo_side, len(FORECAST181) - hi_side - lo_side))

    # ⑥ 副 ―― order180 の 失 24 を ★後窓の語彙別★ に割る (受入④ ―― 同じ走で費えぬゆゑ行ふ)
    lost3 = [r for r in rows if r[0] == "G1" and a_code[(r[0], r[1])] == "ア" and r[3] != r[2]]
    fp3   = [r for r in rows if r[0] != "G1" and r[3] and (r[0], r[1]) in o0.JUDGE180
             and o0.JUDGE180[(r[0], r[1])][0] == "合はぬ"]
    assert (len(lost3), len(fp3)) == (8, 16), "O180_LOST_DRIFT=%d/%d" % (len(lost3), len(fp3))
    print("\n-- ⑥ (副) order180 の 失 24 を ★A3 の名★ 別に割る --")
    for tag, lst in (("真を刈つた 8", lost3), ("新たな偽陽性 16", fp3)):
        c = {}
        for r in lst:
            for (g, k, f, ln, n, pre, post, anm, hum_ok, hum, code) in led:
                if (g, k) == (r[0], r[1]):
                    nm3, sd3 = o0.elem3(pre, post)
                    c[(nm3, sd3)] = c.get((nm3, sd3), 0) + 1
                    break
        print("  %s :" % tag)
        for (nm3, sd3), v in sorted(c.items(), key=lambda x: -x[1]):
            print("     %-6s %s窓 = %d 件" % (nm3, sd3, v))

    # ⑦ 悉皆の外 と 判定の出所
    outside = [r for r in rows if not r[6] and r[4]]
    print("\n-- ⑦ 悉皆の外 と 判定の出所 --")
    print("  人が名を讀めなんだ 15 件のうち A4 が名を取つた = %d 件 (★分子分母の外★)" % len(outside))
    src = {"o180 を再利用": 0, "o178 を再利用": 0, "本弾で人が判じた": 0}
    for (g, k, anm, a3, a4, s4, hum_ok, hum, code) in rows:
        if a4 is None or not hum_ok: continue
        if (g, k) in o0.JUDGE180 and a4 == a3: src["o180 を再利用"] += 1
        elif g == "G1" and a4 == anm:          src["o178 を再利用"] += 1
        else:                                   src["本弾で人が判じた"] += 1
    print("  判定の出所 =", src, "計", sum(src.values()))

if __name__ == "__main__":
    stage1(); stage2()

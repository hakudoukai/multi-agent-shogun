#!/usr/bin/env python3
# order180: ★217/217 の台帳が揃つた★ を承け、器A / 器A2 / 器A3 を ★同じ 217 を分母に★ 較べる。
# ★段★: 第一段(本 file の初版) = ★判じ方・効く範囲・見込み三本★ を宣言するのみ(判定表は空)
#        第二段(追記後)         = 己が讀んで付けた判定表 と 勘定
#        ―― 二段の sha を紙に並べる事で ★基準と見込みを先に固めた★ 証とする。
# ★走らせ方★: python3 (席dir で起こす) ―― 走らせる処 = third PC / 席dir `scratch/ashigaru-third-3-12e9d4bd/`
# ★讀取のみ★ (席dir の讀取のみ・git 0・書込 0・製品走 0・一時 file 0・DB 0)
import os, re, collections, hashlib, importlib.util as IU
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, fn):
    sp = IU.spec_from_file_location(n, os.path.join(HERE, fn))
    m = IU.module_from_spec(sp); sp.loader.exec_module(m); return m

q   = _load("o175", "order175_ken_element_census_v1.rule.py")   # 器A      ★一字も改めず★
r   = _load("o176", "order176_ken_element_widen_v1.rule.py")    # 器B      ★一字も改めず★
o7  = _load("o177", "order177_ken_attribution_human_v1.rule.py")# 44 の台帳 ★一字も改めず★
o8  = _load("o178", "order178_ken_positive_audit_v1.rule.py")   # 136 の台帳★一字も改めず★
o9  = _load("o179", "order179_recall_and_toolfix_v1.rule.py")   # 37 の台帳 + 器A2 ★一字も改めず★

# ═══════════════════════════════════════════════════════════════
# ★判じ方★ (器A3 を一度も走らせる ★前★ に宣言する。後から動かさぬ)
# ═══════════════════════════════════════════════════════════════
CRITERION5 = """
【器A3 の定めと ★動かす変数は一つだけ★】
  器A  = 語彙 11 種 ・ 窓 = 件 の ★前 46 字のみ★
  器A2 = 語彙を ★識別子の境界付き★ に改め ・ 窓は器A と同じ(前 46 字)      … ★語彙★ を動かした器
  器A3 = 語彙は ★器A の物を一字も改めず★ ・ 窓を ★前 46 字 + 後 46 字★ へ … ★窓★ を動かした器
  ∴ A→A2 の差は語彙の差・A→A3 の差は ★窓の差★ に帰する(A2 と A3 は混ぜぬ)。
  近さの定め = 件 からの字数。前と後で ★同じ距離★ なら ★前を採る★(器A と同じ向きを既定とする)。

【何を「合ふ」とするか】
  器の名(11 語彙の一つ)が、台帳に既に在る ★己が讀んだ元素★ の字と ★同じ物を指す★ 時のみ「合ふ」。
  判ずる材は ★台帳の元素の字のみ★ とし、紙を讀み直さぬ(讀み直せば台帳と器の両方が動く)。
  縛り: ①迷つたら ★合はぬ★ に落とす ②各件に元素の字を併記 ③人が讀めなんだ件(㋒15)は分子にも分母にも入れぬ

【三つの器を較べる分母 ―― ★欄ごとに書く★】
  適合率の分母 = ★其の器が名を取れた件数★ (器ごとに違ふ ―― A=136 / A2=122 / A3=本弾で測る)。★但し此の分母は 人が名を讀めなんだ件を含み、分子は含まぬ ∴ 別母である★
  再現率の分母 = ★人が名を讀めた 202★ (三器で同じ)
  ★前弾の 86/136(器A) と 82/122(器A2) は ★別分母であつた★ ―― 本紙で置き換へず ★併記して残す★
"""

# ═══════════════════════════════════════════════════════════════
# ★効く範囲の宣言★ (条 百四十一条目 ―― 癖の名が ★何処まで効くか★ を ★讀む前に★ 書く)
# ═══════════════════════════════════════════════════════════════
RANGE = """
己の癖の名 = 「★器に甘い★」(o177・o178・o179 の三度、いづれも ★器の誤りを少なく見積つた★)。
★効くと見る欄★ = 器の ★誤りを数へる欄★ ―― ㋐失(A が正しく取れて居た名を A3 が付け替へる数)
                                        ㋑A3 の偽陽性(名は取れたが合はぬ数)
  ∴ 此の二欄は補正で ★増やす★。
★効かぬと見る欄★ = 器の ★産出量を数へる欄★ ―― ㋒A3 が名を取れた件数(多く取れるか少なく取れるかは
  窓の広さの算術であつて、己の器への甘さとは別の事柄である)。∴ 此の欄は ★補正せぬ(素と同値を置く)★。
★測り方★ = 効くと見た欄で補正が実測に近づき、効かぬと見た欄で ★素と補正が同値ゆゑ差が出ぬ★ 事を確かめる。
  効かぬと宣言した欄で素が大きく外れて居れば、それは ★癖の名が其の欄にも及ぶ★ 証であり ―― 其の時は
  ★宣言が誤つて居た★ と書く(★後から『此の欄には効かぬ筈だつた』と言はぬ★)。
"""

# ═══════════════════════════════════════════════════════════════
# ★見込み 三本★ (器A3 を一度も走らせる ★前★ に置く)
#   素   = 己の癖の儘
#   補正 = 癖(器に甘い)を当てに使ふ ―― ★効くと宣言した欄のみ★ 動かす
# ═══════════════════════════════════════════════════════════════
MIKOMI180_RAW = {
  "A3 が名を取れた件(217 のうち)": 190,
  "得: 81 のうち A3 が名を取り ★かつ合ふ★":  30,
  "失: ㋐86 のうち A3 が ★別の名へ付け替へた★":  5,
  "㋑46 のうち A3 が ★正しい名へ★":  5,
}
MIKOMI180_ADJ = {
  "A3 が名を取れた件(217 のうち)": 190,   # ★効かぬと宣言した欄 ∴ 素と同値★
  "得: 81 のうち A3 が名を取り ★かつ合ふ★":  24,
  "失: ㋐86 のうち A3 が ★別の名へ付け替へた★": 11,
  "㋑46 のうち A3 が ★正しい名へ★":  3,
}
# 適合率の分子は上記から算術で出る ―― 素 = 86-5+30+5 = 116 / 補正 = 86-11+24+3 = 102
MIKOMI180_NUM = {"素": 86-5+30+5, "補正": 86-11+24+3}

# ―― 過補正の判じ (o179 と同じ物差しを一字も変へず用ゐる) ――
def verdict(raw, adj, act):
    if (raw-act)*(adj-act) < 0: return "★過補正★(実測を跨いだ)"
    if abs(adj-act) < abs(raw-act): return "補正が効いた"
    if abs(adj-act) > abs(raw-act): return "補正が外れた"
    return "補正で変らず(素と同値)"

# ═══════════════════════════════════════════════════════════════
# 器A3 ―― 語彙は器A の物 (q.VOCAB) を ★一字も改めず★ 用ゐる。窓のみ両側へ。
# ═══════════════════════════════════════════════════════════════
WIN3 = 46
def elem3(pre, post):
    """件 の前後 46 字の中で ★最も近い★ 語彙一つ。同距離なら前を採る。無ければ None"""
    best = None   # (名, 距離, 側)
    for nm, pat in q.VOCAB:
        for m in pat.finditer(pre):
            d = len(pre) - m.end()
            if best is None or d < best[1]: best = (nm, d, "前")
        for m in pat.finditer(post):
            d = m.start()
            if best is None or d < best[1]: best = (nm, d, "後")
    return (best[0], best[2]) if best else (None, None)

# ═══════════════════════════════════════════════════════════════
# 217 の台帳 ―― 三つの群を ★同じ形★ に揃へる (判じは入れず・機械の作業のみ)
#   ★直しの記★: 初版(sha 63052bee9cf7a607)は 件 の位置を ★数の値★ で引いて居た ゆゑ、
#   同じ行に同じ値の「N 件」が二つ在る件で ★前窓が入れ替はり★、器A の名が 11 件 食ひ違つた
#   (床(26) と同種の疵)。★出現の順★ で引く形へ直す。★判じ方・効く範囲・見込みの字は一字も動かして居らぬ★。
#   返り = (群, 番号, 紙, 行, 数, pre, post, A の名, 人が讀めたか, 己が讀んだ元素, 台帳の判定)
# ═══════════════════════════════════════════════════════════════
def occ_pos(f):
    """器A の occurrences と ★同じ順★ で (行, 始, 終, 行全体) を返す (紙→行→行内の順)"""
    out = []
    for i, ln in enumerate(q.read(f).decode("utf-8", "replace").splitlines(), 1):
        for m in q.KEN.finditer(ln):
            out.append((i, m.start(), m.end(), ln))
    return out

def ledger():
    g1 = []; g2 = []; g3 = []
    for f in q.P17:
        occ = q.occurrences(f); pos = occ_pos(f)
        assert len(occ) == len(pos), "OCC_LEN_DRIFT:%s" % f
        for o, (ln, a, b, cur) in zip(occ, pos):
            assert o[0] == ln and o[1] == int(q.KEN.search(cur[a:b]).group(1)), "OCC_ALIGN_DRIFT:%s" % f
            pre = cur[max(0, a-WIN3):a]; post = cur[b:b+WIN3]
            if o[2] is not None:                       # 器A が名を取れた
                g1.append((f, ln, o[1], pre, post, o[2]))
            elif not o[4] and not o[5]:                # 器B でも取れず・表の欄でもない → o177 の 44
                g2.append((f, ln, o[1], pre, post))
            else:                                      # 器B有 or 表内 → o179 の 37
                g3.append((f, ln, o[1], pre, post))
    assert (len(g1), len(g2), len(g3)) == (136, 44, 37), "GROUP_DRIFT=%d/%d/%d" % (len(g1), len(g2), len(g3))
    out = []
    for k, (f, ln, n, pre, post, nm) in enumerate(g1, 1):
        code, hum, cite = o8.JUDGE178[k]
        out.append(("G1", k, f, ln, n, pre, post, nm, code in ("ア", "イ"), hum, code))
    for k, (f, ln, n, pre, post) in enumerate(g2, 1):
        code, hum, cite = o7.JUDGE[k]
        out.append(("G2", k, f, ln, n, pre, post, None, code == "ㇰ", hum, code))
    for k, (f, ln, n, pre, post) in enumerate(g3, 1):
        code, hum, why2, cite = o9.JUDGE37[k]
        out.append(("G3", k, f, ln, n, pre, post, None, code in ("ア", "イ"), hum, code))
    return out

def sanity():
    """★器A を此処で作り直して居らぬ事★ を器自身に言はせる (G1 の 136 件で A の名が一致するか)"""
    L = ledger(); bad = 0
    it = o8.items136()
    for g, k, f, ln, n, pre, post, nm, hum_ok, hum, code in L:
        if g != "G1": continue
        if q.elem(pre) != nm: bad += 1
        if (it[k-1][0], it[k-1][1], it[k-1][2], it[k-1][3]) != (f, ln, n, nm): bad += 1
    assert bad == 0, "A_REPRODUCE_MISMATCH=%d" % bad
    return "器A の名と o178 台帳の並びを 136 件で再現 ―― 食ひ違ひ 0 件"

def stage1():
    print("== 判じ方 (器A3 を一度も走らせる ★前★ に宣言した) =="); print(CRITERION5)
    print("== 効く範囲の宣言 =="); print(RANGE)
    print("== 見込み 三本 ==")
    for k in MIKOMI180_RAW:
        print("   %-46s 素=%3d / 補正=%3d" % (k, MIKOMI180_RAW[k], MIKOMI180_ADJ[k]))
    print("   適合率の分子(算術で出る)            素=%3d / 補正=%3d" % (MIKOMI180_NUM["素"], MIKOMI180_NUM["補正"]))
    L = ledger()
    print("\n== 台帳 217 の形 ==")
    print("   件数 = %d (G1=%d / G2=%d / G3=%d)" % (len(L), sum(1 for x in L if x[0]=="G1"),
          sum(1 for x in L if x[0]=="G2"), sum(1 for x in L if x[0]=="G3")))
    print("   人が名を讀めた = %d / 讀めなんだ = %d" % (sum(1 for x in L if x[8]), sum(1 for x in L if not x[8])))
    print("   " + sanity())

if __name__ == "__main__": stage1()

# ═══════════════════════════════════════════════════════════════
# ★第二段★ ―― 己が讀んで付けた判定 (第一段の字は ★一つも改めず★ 追記のみ)
#   判ずる材 = 台帳の元素の字のみ(紙は讀み直さぬ)。迷つたら ★合はぬ★。
#   ★判じ方の補ひ(讀む途中で立てた・自訴)★:
#     元素の字が「A(B)」「A の B」の形の時、★文の頭の名詞★ で判ずる。
#     例: 「continue の行」= 行 / 「continue(表の行)」= continue / 「関数(def 行)」= 関数
#     此の補ひは ★迷ひを合はぬ側へ落とす★ のみで、合ふ側へ動かした件は ★一つも無い★
#     (第一段の縛り①と同じ向き ∴ 基準を緩めては居らぬ)。
# ═══════════════════════════════════════════════════════════════
JUDGE180_SRC = """
G1|10|合はぬ|行|it( = test ケース
G1|12|合はぬ|行|test ケース(3件目)
G1|17|合はぬ|鍵|grep -n の hit 行
G1|19|合ふ|hit|grep の一致
G1|27|合はぬ|hit|不一致(突合の結果)
G1|32|合はぬ|鍵|grep の hit 行
G1|36|合はぬ|鍵|required_fields を持つ行(型別)
G1|42|合はぬ|定義|continue(非除去)
G1|49|合はぬ|行|参照(定義を除く)
G1|61|合はぬ|鍵|file
G1|73|合はぬ|file|悉皆の def
G1|77|合はぬ|呼出|一時 file の疵
G1|80|合はぬ|行|紙+規の和(file)
G1|86|合はぬ|行|ls-files の file(今の実測)
G1|96|合はぬ|行|識別子境界形の出現(def)
G1|100|合はぬ|行|註釈中の名の言及
G1|107|合はぬ|値|object 要素
G1|113|合はぬ|行|continue(表の行)
G1|115|合はぬ|行|continue(comment 付き)
G2|4|合はぬ|file|test
G2|5|合はぬ|file|test
G2|12|合ふ|値|grep -c の集計値
G2|34|合はぬ|行|識別子の出現箇所
G3|1|合はぬ|呼出|grep の hit 行
G3|2|合ふ|行|grep の hit 行
G3|4|合ふ|鍵|鍵(field 名 2 つ)
G3|5|合はぬ|鍵|語一致の hit
G3|6|合はぬ|行|断片(required_fields の)
G3|7|合はぬ|行|疵(自訴した違反)
G3|8|合はぬ|定義|出現(def と呼出)
G3|9|合はぬ|表示|関数
G3|11|合はぬ|定義|出現(def+呼出)
G3|12|合はぬ|行|註釈中の名の言及
G3|13|合はぬ|行|識別子の出現(def)
G3|14|合はぬ|鍵|ルール(mandatory_fields_guard 型)
G3|15|合はぬ|鍵|ルール(mandatory_fields_guard 型)
G3|16|合ふ|行|continue の行
G3|17|合ふ|行|continue の行
G3|18|合ふ|行|continue の行
G3|20|合ふ|行|continue の行
G3|21|合ふ|行|continue の行
G3|22|合ふ|行|continue の行
G3|23|合ふ|行|continue の行
G3|24|合ふ|行|continue の行
G3|25|合ふ|行|continue の行
G3|26|合ふ|行|continue の行
G3|27|合ふ|行|continue の行
G3|28|合ふ|行|continue の行
G3|34|合ふ|行|continue の行
G3|36|合はぬ|行|関数
G3|37|合はぬ|行|関数(def 行)
"""
JUDGE180 = {}
for _ln in JUDGE180_SRC.strip().split("\n"):
    _g, _k, _j, _a3, _e = _ln.split("|")
    JUDGE180[(_g, int(_k))] = (_j, _a3, _e)

def stage2():
    L = ledger()
    kept = []; changed = []; new = []; a3none = []
    for g, k, f, ln, n, pre, post, nm, ok, hum, code in L:
        a3, side = elem3(pre, post)
        rec = (g, k, f, ln, n, nm, a3, side, ok, hum, code)
        if g == "G1":
            (kept if a3 == nm else changed).append(rec)
        else:
            (new if a3 is not None else a3none).append(rec)
    print("== 器A3 の産出 ==")
    print("   名を取れた = %d / 217 (G1 kept=%d + G1 変=%d + 81 側の新名=%d)"
          % (len(kept) + len(changed) + len(new), len(kept), len(changed), len(new)))
    print("   ★変つた %d 件は ★悉く後窓★ = %d 件★ (前窓で勝つた変化 = %d 件)"
          % (len(changed), sum(1 for r in changed if r[7] == "後"), sum(1 for r in changed if r[7] == "前")))
    # ―― 逐語の検め ――
    miss = 0
    for g, k, f, ln, n, nm, a3, side, ok, hum, code in changed + new:
        if not ok: continue
        j = JUDGE180.get((g, k))
        assert j is not None, "JUDGE_MISS=%s%s" % (g, k)
        if j[2] != hum: miss += 1; print("   ELEM_DRIFT %s%s 記=%s / 台帳=%s" % (g, k, j[2], hum))
        assert j[1] == a3, "A3NAME_DRIFT=%s%s 記=%s / 器=%s" % (g, k, j[1], a3)
    print("   元素の逐語 食ひ違ひ = %d 件" % miss)
    print("   人が讀めなんだ ∴ 判ぜぬ件 = %d (変=%d / 新=%d)"
          % (sum(1 for r in changed + new if not r[8]),
             sum(1 for r in changed if not r[8]), sum(1 for r in new if not r[8])))
    # ―― 得と失を ★両欄で★ ――
    lost = [r for r in changed if r[8] and r[10] == "ア"]                       # A が当たり → 名を替へた
    lost_ok = [r for r in lost if JUDGE180[(r[0], r[1])][0] == "合ふ"]
    gain_g1 = [r for r in changed if r[8] and r[10] == "イ" and JUDGE180[(r[0], r[1])][0] == "合ふ"]
    swap_g1 = [r for r in changed if r[8] and r[10] == "イ" and JUDGE180[(r[0], r[1])][0] == "合はぬ"]
    gain_new = [r for r in new if r[8] and JUDGE180[(r[0], r[1])][0] == "合ふ"]
    fp_new = [r for r in new if r[8] and JUDGE180[(r[0], r[1])][0] == "合はぬ"]
    kept_a = [r for r in kept if r[10] == "ア"]
    print("\n== ★得★ の欄 ==")
    print("   ㋑46(器A の偽陽性) のうち A3 が ★正しい名へ★  = %d 件" % len(gain_g1))
    print("   81(器A が名を取れず) のうち A3 が名を取り合ふ = %d 件" % len(gain_new))
    print("   得 合計 = %d 件" % (len(gain_g1) + len(gain_new)))
    print("== ★失★ の欄 ==")
    print("   ㋐86(器A の当たり) のうち A3 が名を替へた   = %d 件 (うち替へた先も合ふ = %d)"
          % (len(lost), len(lost_ok)))
    print("   ∴ ★真を刈つた★ = %d 件" % (len(lost) - len(lost_ok)))
    print("   81 側で A3 が名を取つたが合はぬ(新たな偽陽性) = %d 件" % len(fp_new))
    print("   失 合計(真を刈る + 新たな偽陽性) = %d 件" % (len(lost) - len(lost_ok) + len(fp_new)))
    print("   誤りの入替へ(㋑のまま別の誤名へ) = %d 件 ―― 得にも失にも数へぬ" % len(swap_g1))
    # ―― 三器の率 (★分母を欄ごとに★) ――
    num3 = len(kept_a) + len(lost_ok) + len(gain_g1) + len(gain_new)
    den3 = len(kept) + len(changed) + len(new)
    print("\n== 三器を ★同じ 217★ の台帳で並べる ==")
    print("   ┌ 器  │ 名を取れた │ 合ふ │ 適合率(分母=其の器が取れた数) │ 再現率(分母=202)  ―― ★適合の分母は讀めなんだ件を含み 分子は含まぬ=別母★")
    for nmx, den, num in (("A ", 136, 86), ("A2", 122, 82), ("A3", den3, num3)):
        print("   │ %s │ %10d │ %4d │ %5.1f%%                        │ %5.1f%%"
              % (nmx, den, num, 100.0 * num / den, 100.0 * num / 202))
    print("   ★前弾の 86/136(A) と 82/122(A2) は ★別分母であつた★ ―― 置き換へず此処に併記する★")
    # ―― 主源「窓の向き」を幾つ拾つたか ――
    w18 = [r for r in new if r[0] == "G3" and "窓の向き" in o9.JUDGE37[r[1]][2]]
    w18ok = [r for r in w18 if r[8] and JUDGE180[(r[0], r[1])][0] == "合ふ"]
    allw = [k for k in o9.JUDGE37 if "窓の向き" in o9.JUDGE37[k][2]]
    print("\n== 主源「窓の向き」(o179 で %d 件) を A3 は幾つ拾つたか ==" % len(allw))
    print("   A3 が名を取れた = %d / %d ・ うち合ふ = %d" % (len(w18), len(allw), len(w18ok)))
    # ―― 見込み突合 (四度目の向き) ――
    act = {"A3 が名を取れた件(217 のうち)": den3,
           "得: 81 のうち A3 が名を取り ★かつ合ふ★": len(gain_new),
           "失: ㋐86 のうち A3 が ★別の名へ付け替へた★": len(lost),
           "㋑46 のうち A3 が ★正しい名へ★": len(gain_g1)}
    print("\n== 見込み突合 (★讀む前に固めた四本★) ==")
    up = dn = 0
    for k in MIKOMI180_RAW:
        raw, adj, a = MIKOMI180_RAW[k], MIKOMI180_ADJ[k], act[k]
        amai = ("器に甘い" if ((raw > a) if "失" not in k else (raw < a)) else "器に辛い")
        if amai == "器に甘い": up += 1
        else: dn += 1
        print("   %-46s 素=%3d 補正=%3d 実測=%3d  %s / 素の向き=★%s★"
              % (k, raw, adj, a, verdict(raw, adj, a), amai))
    print("   %-46s 素=%3d 補正=%3d 実測=%3d  %s"
          % ("適合率の分子", MIKOMI180_NUM["素"], MIKOMI180_NUM["補正"], num3,
             verdict(MIKOMI180_NUM["素"], MIKOMI180_NUM["補正"], num3)))
    print("   ★四度目の向き★: 甘い=%d 欄 / 辛い=%d 欄" % (up, dn))
    print("\n== 効く範囲の宣言 は当たつたか ==")
    print("   ★効かぬ★ と宣言した欄(A3 が名を取れた件): 素 190 / 実測 %d ⇒ 外れ %d 件 (%.1f%%)"
          % (den3, abs(190 - den3), 100.0 * abs(190 - den3) / den3))
    return dict(kept=len(kept), changed=len(changed), new=len(new), num3=num3, den3=den3,
                gain=len(gain_g1) + len(gain_new), lost=len(lost) - len(lost_ok), fp=len(fp_new),
                swap=len(swap_g1), w18=(len(allw), len(w18), len(w18ok)))

if __name__ == "__main__":
    print("\n" + "=" * 60)
    stage2()

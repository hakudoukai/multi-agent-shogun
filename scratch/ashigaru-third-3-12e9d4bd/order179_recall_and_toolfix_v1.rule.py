#!/usr/bin/env python3
# order179 第一段 ―― ★讀む前に固める版★
#   ①器Aが名指せなんだ 81 のうち o177 で讀んだ 44 を除く ★残り(未讀)★ を悉皆人讀 ⇒ 217/217 完結
#   ②見込みを ★二本★ 先に出す (㋐素=癖の儘 / ㋑補正後) ⇒ 三度目の向きと「癖を言語化できたか」を測る
#   ③器A2 (語彙の拾ひ過ぎを直した別 file) を並走 ⇒ ★偽陽性が幾つ消え★ ★真を幾つ落とすか(巻添へ)★
# ★走らせ方★: python3 scratch/ashigaru-third-3-12e9d4bd/order179_recall_and_toolfix_v1.rule.py
#             (走らせる処 = third PC / /home/hakudoukai/multi-agent-shogun ・席 dir)
# ★讀取のみ★ (席 dir の讀取のみ・書込 0・製品走 0・一時 file 0・DB 0・commit/push 0)
import os, re, hashlib, importlib.util as IU, collections
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(nm, fn):
    sp = IU.spec_from_file_location(nm, os.path.join(HERE, fn))
    m = IU.module_from_spec(sp); sp.loader.exec_module(m); return m
q  = _load("o175", "order175_ken_element_census_v1.rule.py")   # 器A ★一字も改めず import★
r  = _load("o176", "order176_ken_element_widen_v1.rule.py")    # 器B ★一字も改めず import★
o8 = _load("o178", "order178_ken_positive_audit_v1.rule.py")   # 136 の人讀み台帳 ★改めず★

# ────────────────────────────────────────────────────────────
# 一 ★判じ方★ (未讀分・★一件も讀む前に宣言する★)
# ────────────────────────────────────────────────────────────
CRITERION3 = """
【的】器A が元素を名指せなんだ件のうち、order177 で人讀みした 44 を除く ★残り★ (=器B が名を取れた件 + 行頭が `|` の表内の件)。
【問ひ】★人が讀めば「何を一つと数へたか」が字に在るか★。器A が取れなんだのは ★字に無い★ が故か ★語彙に無い★ が故か。
【窓】当該行の全文 + ★前後各一行★ (器B と同じ広さ ∴ 器B の可否と同じ土俵で比べ得る)。表内の件は ★同じ表の見出し行★ も見る (見た事を各件に書く)。
【三択】
  ㋐ 名が字に在る（∴ 器A の ★取り零し★） ―― 逐語で名を挙げ得る
  ㋑ 名は在るが ★己の宣言した窓・基準の外★ に在る ―― 何処に在るか(前行/見出し行/前の箇条項目)を書く
  ㋒ ★字に無い★ ―― 人が讀んでも単位が定まらぬ (＝器の取り零しに非ず)
【縛り】
  ①基準を後から動かさぬ ②各件に ★逐語★ を付す ③迷つたら ㋒ (㋐へ寄せぬ)
  ④★器B の名を見る前に、先に己で「何を一つと数へたか」を讀む★ ―― 然る後に器B の名と突き合はせる
  ⑤㋐ と ㋑ の差は ★器の疵の種★ が違ふ ―― ㋐=語彙の不足、㋑=窓の狭さ。混ぜて数へぬ
"""

# ────────────────────────────────────────────────────────────
# 二 ★見込み 二本★ (★一件も讀む前に書く★・家老令: 過補正も一つの向きとして書く)
# ────────────────────────────────────────────────────────────
# 素 = 己の癖の儘に立てた見込み。補正後 = 「己は器に甘い(=器の誤りを少なく見積る)」癖を ★当てに使つた★ 見込み。
MIKOMI_37_RAW = {"㋐ 名が字に在る(取り零し)": 24, "㋑ 窓・基準の外": 6, "㋒ 字に無い": 7}
MIKOMI_37_ADJ = {"㋐ 名が字に在る(取り零し)": 29, "㋑ 窓・基準の外": 4, "㋒ 字に無い": 4}
MIKOMI_37_WHY = """
素の拠り所: 器B が名を取れた件は前後行に名が在る蓋然が高い ∴ ㋐ を多めに、表内の件は升目ゆゑ ㋒ を多めに見た。
補正の拠り所: o177(38→0) と o178(偽陽性 26→46) の ★二度とも同じ向き★ ―― 己は ★器の誤りを少なく見積る★。
  ∴ 器の誤り＝㋐(取り零し) を ★上げ★、器を庇ふ側＝㋒(字に無い) を ★下げる★ 向きに補正した (+5 / -3 / -2)。
過補正の判じ: 補正後が実測を ★跨いで★ 反対側へ出たら ★過補正★ と書く (素が下・実測が中・補正後が上、の類)。
  跨がずに近づいたら「補正が効いた」、跨がず遠ざかつたら「補正が外れた」。三つを別の語で書く。
"""
MIKOMI_A2_RAW = {"偽陽性(㋑46)のうち解消": 18, "真(㋐86)のうち巻添へで落とす": 3}
MIKOMI_A2_ADJ = {"偽陽性(㋑46)のうち解消": 12, "真(㋐86)のうち巻添へで落とす": 8}
MIKOMI_A2_WHY = """
素: ASCII 語の識別子境界を課せば `..._field_count` `total_checks` `required_fields` の類が悉く落ちる ∴ 鍵10+表示5 を主に 18 と見た。
補正: 同じ癖(器に甘い)を当てはめ、解消を ★下げ★・巻添へを ★上げる★ (18→12 / 3→8)。
  ★直しの効きを高く・直しの害を低く見るのも「器に甘い」の一形である。★
"""

# ────────────────────────────────────────────────────────────
# 三 ★器A2★ ―― 語彙の拾ひ過ぎを直した別 file 相当 (★器A は一字も改めぬ★)
# ────────────────────────────────────────────────────────────
A2_SPEC = """
直しは ★一つだけ★ 課す (二つ課せば何方が効いたか帰属が付かぬ):
  ★ASCII の語彙は ★識別子境界★ を要求する★ ―― (^|[^A-Za-z0-9_])語([^A-Za-z0-9_]|$) の明示クラス (床⒅⒇)。
  対象 = call/def/test/it/assert/file/hit/key/field/branch/commit/checks/emit_log/L\\d+ 等の ASCII 片。
  日本語の語彙(呼出/定義/紙/行/鍵/枝/表示/値 等)は ★手を触れぬ★ (∴ 「実行」の中の「行」の類は A2 でも残る = 直しの外)。
名の採り方(窓・最も近い一つを採る)は器A と同一 ∴ 差は ★語彙の当たり方だけ★ に帰属する。
測る二つ:
  ★解消★  = o178 で ㋑(偽陽性) と判じた件で、A2 の名が None に成るか ★人讀みの元素と合ふ名★ に変はつた件
  ★巻添へ★ = o178 で ㋐(当たり) と判じた件で、A2 の名が None に成るか ★別の名★ に変はつた件 (=★真を落とした数★)
"""
_ASCII = [
 ("呼出",   [r"call", r"emit_log"]),
 ("定義",   [r"def"]),
 ("test",  [r"test", r"it", r"assert"]),
 ("file",  [r"file"]),
 ("行",     [r"L\d+"]),
 ("commit", [r"commit"]),
 ("hit",   [r"hit"]),
 ("鍵",     [r"field", r"key"]),
 ("枝",     [r"branch"]),
 ("表示",   [r"checks"]),
]
_JA = [
 ("呼出",   r"呼出|を呼[ぶび]"),
 ("定義",   r"定義|関数"),
 ("test",  r"テスト|ケース"),
 ("file",  r"ファイル|紙|本紙"),
 ("行",     r"行"),
 ("commit", r"コミット"),
 ("hit",   r"一致|差分|突合"),
 ("鍵",     r"鍵|フィールド|引数|キー"),
 ("枝",     r"分岐|枝|条件"),
 ("表示",   r"表示|警告|警報|画面"),
 ("値",     r"値|要素|項目|種|set_code|カテゴリ"),
]
BND = r"(?:^|[^A-Za-z0-9_])(?:%s)(?:[^A-Za-z0-9_]|$)"
A2_VOCAB = []
for _n, _ps in _ASCII: A2_VOCAB.append((_n, re.compile(BND % "|".join(_ps))))
for _n, _p in _JA:     A2_VOCAB.append((_n, re.compile(_p)))
def elem_a2(pre):
    best = None
    for nm, pat in A2_VOCAB:
        for m in pat.finditer(pre):
            if best is None or m.end() > best[1]: best = (nm, m.end())
    return best[0] if best else None

# ────────────────────────────────────────────────────────────
# 四 ★適合率・再現率の欄と分母★ (★測る前に式を宣言する★・家老令: 分母を欄ごとに書く)
# ────────────────────────────────────────────────────────────
RATE_SPEC = """
欄①適合率 = ★器A が名を取れた件★ のうち人讀みが ㋐ の数  / ★分母 = 136 (器A が名を取れた件・★人が名を讀めなんだ件を含む★)★ ―― ★分子は ㋐ ゆゑ 讀めなんだ件を含まぬ ∴ 分子と分母は別の母である★
欄②再現率 = 同じ分子(㋐ の数)                             / ★分母 = 人が名を讀めた件の総数★
  分母の内訳を欄ごとに書く: (a)136 のうち人が元素を讀めた数 (b)o177 の 44 のうち人が名を讀めた数 (c)本弾の未讀分のうち ㋐+㋑
  ※「人が名を讀めた」= ㋒(字に無い)以外。㋑(基準の外)も ★人には讀めて居る★ ゆゑ分母に入れる ―― 之を入れねば再現率が甘くなる。
欄③器A2 の適合率 = A2 が名を取れた件のうち人讀みと合ふ数 / 分母 = ★A2 が名を取れた件数(器A とは別の数)★
  ★分母が違ふ二つの率を同じ行に並べぬ (床⑷)。★
"""

# ────────────────────────────────────────────────────────────
# 五 母集団の掃き出し
# ────────────────────────────────────────────────────────────
def census():
    tot = named = nb_b = nb_bar = base44 = 0
    unread = []
    for f in q.P17:
        for o in q.occurrences(f):
            tot += 1
            if o[2] is not None: named += 1; continue
            if o[4]:   nb_b += 1;   unread.append((f, o[0], o[1], "器Bが名を取れた", o[4]))
            elif o[5]: nb_bar += 1; unread.append((f, o[0], o[1], "行頭が|(表内)", None))
            else:      base44 += 1
    unread.sort(key=lambda x: (x[0], x[1], x[2]))
    return tot, named, nb_b, nb_bar, base44, unread

if __name__ == "__main__":
    tot, named, nb_b, nb_bar, base44, unread = census()
    print("== 母集団 ==")
    print("  件語 総 %d / 器A が名を取れた %d / 取れず %d" % (tot, named, tot - named))
    print("  取れず の内訳: o177 で人讀み済 %d / ★本弾の的(未讀) %d★ (器B有 %d + 表内 %d)"
          % (base44, nb_b + nb_bar, nb_b, nb_bar))
    print("== 見込み(讀む前) ==")
    print("  37 素 =", MIKOMI_37_RAW); print("  37 補正後 =", MIKOMI_37_ADJ)
    print("  A2 素 =", MIKOMI_A2_RAW); print("  A2 補正後 =", MIKOMI_A2_ADJ)
    print("== 的の一覧 (%d 件・逐語は第二段で付す) ==" % len(unread))
    for k, u in enumerate(unread, 1):
        print("  %3d %s L%d 数=%d %s" % (k, u[0].replace("_v1.md",""), u[1], u[2], u[3]))

# ════════════════════════════════════════════════════════════
# 第二段 ―― 人讀みの結果を収める (第一段の字は ★一字も改めて居らぬ★・以下は ★追記のみ★)
# ════════════════════════════════════════════════════════════
# 形式: 番号@@判定(ア=㋐/イ=㋑/ウ=㋒)@@己が讀んだ元素@@器Aが取れなんだ因@@逐語(当該行に現に在る字)
JUDGE37_SRC = """
1@@ア@@grep の hit 行@@窓の狭さ(46字の外)@@実測=**0件**
2@@ア@@grep の hit 行@@窓の狭さ(46字の外)@@実測=1件のみ
3@@イ@@required_fields の要素(型別)@@名は ★表の見出し行★@@object(16〜17件
4@@ア@@鍵(field 名 2 つ)@@窓の狭さ(「要素」が46字の外)@@`tray_type`の2件は
5@@ア@@語一致の hit@@窓の向き(名が ★後ろ★)@@参考14件(S4含む)
6@@ア@@断片(required_fields の)@@語彙不足(「断片」が語彙に無い)@@断片1件行)
7@@ア@@疵(自訴した違反)@@語彙不足(「疵」が語彙に無い)@@疵1件・自訴
8@@ア@@出現(def と呼出)@@窓の向き(名が ★後ろ★)@@→ **3件**(def と呼出を分離
9@@ア@@関数@@窓の向き(「呼出元」が ★後ろ★)@@4件は前弾 total_checks 紙で呼出元を
10@@ウ@@―@@★字に無い★(何を三分類したかが名指されて居らぬ)@@16件をconfirmed/negative/unmeasuredへ仕分け
11@@ア@@出現(def+呼出)@@窓の向き(名が ★後ろ★)@@(全2件=def L6376 と呼出 L12884 のみ
12@@ア@@註釈中の名の言及@@語彙不足(「言及」が語彙に無い)@@**1件現に在る**
13@@ア@@識別子の出現(def)@@語彙不足(「識別子」が語彙に無い)+向き@@= **全1件**(L12831 の def のみ)
14@@ア@@ルール(mandatory_fields_guard 型)@@窓の向き(「ルール群」が ★後ろ★)@@(16件 vs 185件)
15@@ア@@ルール(mandatory_fields_guard 型)@@窓の向き(「ルール群」が ★後ろ★)@@(16件 vs 185件)
16@@ア@@continue の行@@窓の狭さ(「continue」が46字の外)@@51件中、B系=**2件**
17@@ア@@continue の行@@窓の狭さ(「continue」が46字の外)@@51件中、B系=**2件**
18@@ア@@continue の行@@窓の向き(「行」が ★後ろ★)@@### 表1: A系49件(rule_type別・行
19@@ウ@@―@@★字に無い★(B系 は群の名・単位が無い)@@### 表2: B系2件(内側required_fieldsループ専用
20@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| **19件** | L10993
21@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| **16件** | L11010
22@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| **2件** | L11000・L11012 |
23@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| **1件** | L11335 |
24@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| **1件** | L11102 |
25@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| **9件** | L11116
26@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@**B系2件**(分母=2、別掲)
27@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@「無し」2件(L11344・L11347)
28@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| genuine pass(19件) | 現に無い(L11202の1件を除く18件)
29@@イ@@continue@@名は ★表の見出し行★@@| blocked済(16件) |
30@@イ@@continue@@名は ★表の見出し行★@@| warning済(2件) |
31@@イ@@continue@@名は ★表の見出し行★@@| unsupported_red済(1件) |
32@@イ@@continue@@名は ★表の見出し行★@@| resolved_itemsのみ(1件) |
33@@イ@@continue@@名は ★表の見出し行★@@| 混在・範囲内判明(9件) |
34@@ア@@continue の行@@窓の向き(L 番号が ★後ろ★)@@| 混在・範囲外依存(1件・L10997) |
35@@ウ@@―@@★字に無い★(「⑥の」は節の指し・単位が無い)@@⑥の27件・積む先の再掲元
36@@ア@@関数@@語彙不足(器Aの `を呼[ぶび]` は「呼ばれる」に当たらぬ)@@但し此の4件は
37@@ア@@関数(def 行)@@窓の向き(L 番号が ★後ろ★)@@系4件(L11585/11641/11741/11840)
"""
JUDGE37 = {}
for _ln in JUDGE37_SRC.strip().splitlines():
    _k, _c, _e, _w, _f = _ln.split("@@")
    JUDGE37[int(_k)] = (_c, _e, _w, _f)
KANA = {"ア": "㋐ 名が字に在る(取り零し)", "イ": "㋑ 窓・基準の外", "ウ": "㋒ 字に無い"}

# ―― ③ 器A2 の効き ―― ★第一段で宣言した定義を其の儘用ゐる★
def a2_effect():
    it = o8.items136(); J = o8.JUDGE178
    solved = collat = swap = kept = 0
    rows = []
    for k, (f, ln, n, nm, pre, cur) in enumerate(it, 1):
        a2 = elem_a2(pre); j = J[k][0]; hum = J[k][1]
        if a2 == nm: kept += 1; continue
        # ★宣言した定義★: 解消 = ㋑ の件で A2 が None か ★人讀みの元素と合ふ名★ に変つた
        if j == "イ":
            if a2 is None: solved += 1; tag = "解消(名を捨てた)"
            elif a2 in hum: solved += 1; tag = "解消(正しい名へ)"
            else:          swap  += 1; tag = "★誤りの入替へ(解消に非ず)★"
        elif j == "ア":
            collat += 1; tag = "★巻添へ(真を落とした)★"
        else:
            tag = "㋒(元より判じ得ぬ)"
        rows.append((k, f.replace("_v1.md", ""), ln, n, nm, a2, KA2[j], hum, tag))
    return solved, collat, swap, kept, rows
KA2 = {"ア": "㋐", "イ": "㋑", "ウ": "㋒"}

def stage2():
    tot, named, nb_b, nb_bar, base44, unread = census()
    it = o8.items136(); J = o8.JUDGE178
    # ―― 逐語を器自身に言はせる (床(28)の趣旨) ――
    assert sorted(JUDGE37) == list(range(1, 38)), "JUDGE37_KEY_DRIFT"
    L = lines_of = None
    for k, (f, ln, n, why, bn) in enumerate(unread, 1):
        cur = r.lines(f)[ln - 1]
        assert JUDGE37[k][3] in cur, "CITE_MISS=%d" % k
    print("== ① 未讀 37 の判定 (37/37) ==")
    import collections
    c = collections.Counter(v[0] for v in JUDGE37.values())
    for kk in ("ア", "イ", "ウ"): print("   %s = %d" % (KANA[kk], c.get(kk, 0)))
    print("   因の内訳 =", dict(collections.Counter(v[2].split("(")[0] for v in JUDGE37.values())))
    print("== ② 見込み 二本 と 実測 (37) ==")
    for kk in MIKOMI_37_RAW:
        raw, adj, act = MIKOMI_37_RAW[kk], MIKOMI_37_ADJ[kk], c.get({"㋐ 名が字に在る(取り零し)": "ア", "㋑ 窓・基準の外": "イ", "㋒ 字に無い": "ウ"}[kk], 0)
        if (raw - act) * (adj - act) < 0: verd = "★過補正★(実測を跨いだ)"
        elif abs(adj - act) < abs(raw - act): verd = "補正が効いた"
        elif abs(adj - act) > abs(raw - act): verd = "補正が外れた"
        else: verd = "補正で変らず"
        print("   %-22s 素=%2d / 補正後=%2d / ★実測=%2d★  素差=%+d 補正差=%+d ⇒ %s"
              % (kk, raw, adj, act, raw - act, adj - act, verd))
    print("== ③ 器A2 の効き ==")
    solved, collat, swap, kept, rows = a2_effect()
    for kk, raw, adj, act in (("偽陽性(㋑46)のうち解消", MIKOMI_A2_RAW["偽陽性(㋑46)のうち解消"], MIKOMI_A2_ADJ["偽陽性(㋑46)のうち解消"], solved),
                              ("真(㋐86)のうち巻添へ", MIKOMI_A2_RAW["真(㋐86)のうち巻添へで落とす"], MIKOMI_A2_ADJ["真(㋐86)のうち巻添へで落とす"], collat)):
        if (raw - act) * (adj - act) < 0: verd = "★過補正★(実測を跨いだ)"
        elif abs(adj - act) < abs(raw - act): verd = "補正が効いた"
        elif abs(adj - act) > abs(raw - act): verd = "補正が外れた"
        else: verd = "補正で変らず"
        print("   %-22s 素=%2d / 補正後=%2d / ★実測=%2d★ ⇒ %s" % (kk, raw, adj, act, verd))
    print("   名が変らなんだ=%d / ★誤りの入替へ=%d★" % (kept, swap))
    for x in rows: print("     %3d %-40s L%-4d 数=%-4d A=%-5s A2=%-5s 判=%s %s" % (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[8]))
    print("== ④ 適合率・再現率 (★分母を欄ごとに★) ==")
    a_named = 136
    hit = sum(1 for v in J.values() if v[0] == "ア")                      # 器A の名が人讀みと合つた
    hum136 = sum(1 for v in J.values() if v[0] in ("ア", "イ"))            # 136 のうち人が名を讀めた
    hum44  = 36                                                          # o177 実測 (㋐36 / ㋒8)
    hum37  = c.get("ア", 0) + c.get("イ", 0)
    hum_all = hum136 + hum44 + hum37
    print("   欄① 適合率(器A) = %d / ★分母=%d(器A が名を取れた件・讀めなんだ件を含む)★ = %.1f%% ★分子は含まぬ∴別母★" % (hit, a_named, 100.0 * hit / a_named))
    print("   欄② 再現率(器A) = %d / ★分母=%d(人が名を讀めた件の総数)★ = %.1f%%" % (hit, hum_all, 100.0 * hit / hum_all))
    print("        分母の内訳: 136 のうち %d + o177 の 44 のうち %d + 本弾 37 のうち %d" % (hum136, hum44, hum37))
    a2_named = sum(1 for k, (f, ln, n, nm, pre, cur) in enumerate(it, 1) if elem_a2(pre) is not None)
    a2_hit = hit - collat
    print("   欄③ 適合率(器A2) = %d / ★分母=%d(A2 が名を取れた件・器A とは別の数・讀めなんだ件を含む)★ = %.1f%% ★分子は含まぬ∴別母★" % (a2_hit, a2_named, 100.0 * a2_hit / a2_named))
    print("   欄④ 再現率(器A2) = %d / ★分母=%d(同上・人が名を讀めた総数)★ = %.1f%%" % (a2_hit, hum_all, 100.0 * a2_hit / hum_all))
    print("== ⑤ 悉皆の完結 ==")
    print("   217 = 136(器A が名を取れた) + 44(o177) + 37(本弾) ・★人讀み 217/217★")
    print("   人が名を讀めた = %d / ★字に無い★ = %d (136:%d + 44:8 + 37:%d)"
          % (hum_all, 217 - hum_all, 136 - hum136, c.get("ウ", 0)))

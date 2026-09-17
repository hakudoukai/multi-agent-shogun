# -*- coding: utf-8 -*-
"""㋑ ★語の衝突を解く(本札の主眼)★ ―― 「甲乙丙」の二義を、一表の★二欄★に分ける。

★衝突の姿★: 四つの紙が悉く「甲/乙/丙」の三字を使ふ。然るに数へて居る物が違ふ。

  ★軸甲 = 捨證軸(三席 a1/a2/當方)★
      問ひ「★此の枝を捨てて良い證が立つか★」。
      甲 = 立たぬ(∴ 着地させる) / 乙 = 立つ(∴ 捨てる) / 丙 = 測れぬ。
      a1 は則 R0-R4 で、a2・當方は同趣の五条で判ずる。
      ★a1 の紙は「紙のみか／器を含むか」は甲乙を分けぬ★と明記して居る(下の逐語)。

  ★軸乙 = 器軸(家老)★
      問ひ「★此の枝の自前差分が器を含むか★」。
      甲 = 器を含む / 乙 = 紙のみ / 丙 = 手許に物が無い。
      捨てて良いか否かは★問うて居らぬ★。

  ★第三の語 = 「不要」(家老 前紙 km-eda-fuyou・臺帳 17d7dbf7)★
      問ひ「★其の枝の tip が、origin に現に在る他の枝の祖先か★」。
      不要 = 祖先である(∴ ref を消しても commit は一つも失はれぬ)。
      ★「捨てて良い」でも「main に入つた」でもない★(逐語を下に引く)。

∴ 同じ「甲」でも、三席の甲は「捨てられぬ」、家老の甲は「器入り」。★別物である★。
  「不要15」も亦「捨てる15」ではない。★三つの語が三つの問ひに答へて居る。★
本器は各紙の定義を★引いて★(手で写さず) raw/41_teigi_chikugo.txt に刻み、
45 本を二欄に分けた一表 raw/42_ichihyou.tsv と、二軸の交差表 raw/43_kousa.tsv を出す。

出所(枝毎の判):
  捨證軸 a1 `an/95_shiwake.tsv` 欄 shiwake(10)・則 R(11)
         a2 `raw/40_shiwake.tsv` 欄 甲乙丙(7)
         當 km-102 `raw/81_shiwake.tsv` 欄 甲乙丙(7)
  器軸   家老 `raw/10_sokutei.tsv` 欄 jizen_kigu_files(6) ★＞0 なら甲★
         ＋ 家老 `raw/30_summary.txt` の「甲の枝=…」の★名指し★

対照(倒れたら止まる):
  ⓐ 逐語の錨が紙に★唯一命中せねば★ 止 ―― 0 命中(引けぬ)も 2 以上(どの行か決まらぬ)も止める。
     初版は錨 `| R4 |` が★枝の行 L52★にも当たり、先頭を採つて★偽の逐語★を刷つた。
     緩い錨は「引けぬ」ではなく「別の行を引いた」に成る ∴ 数へて止める。
  ⓑ 家老の二つの出所(器file数＞0 ／ 名指し 10 本)が一本でも食ひ違へば 止
  ⓒ 45 本が二軸とも悉く判を持たねば 止(欠けた儘で交差表を刷らぬ)
  ⓓ 家老の紙が宣する 甲10/乙35 と、本器の数へが合はねば 止
"""
import os, sys, importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("K", os.path.join(_d, "00_kaki.py"))
K = importlib.util.module_from_spec(_s); _s.loader.exec_module(K)
REPO = os.path.abspath(os.path.join(_d, "..", "..", "..", ".."))
EV = os.path.join(REPO, "docs/evidence")
A1 = os.path.join(EV, "ashigaru-mac-1_km-100-eda-chakuchi-shiwake-20260917")
A2 = os.path.join(EV, "a2_km-101-eda-yonjuugo-no-chakuchi-shiwake-20260917")
A3 = os.path.join(EV, "ashigaru-mac-3_km-102-eda-yonjuugo-no-chakuchi-shiwake-karo-kou-20260917")
KR = os.path.join(EV, "karo-mac-eda-chakuchi-shiwake-20260917")

# ── 逐語の錨(★軸・紙・錨★) ─────────────────────────────
IKARI = [
    ("捨證軸", "a1 README.md", A1 + "/README.md",
     ["| R0 | ㋐", "| R1 | tip", "| R2 | own", "| R3 | 祖先", "| R4 | 其れ以外",
      "は ★甲乙を分けぬ★"]),
    ("捨證軸", "a2 report.md", A2 + "/report.md",
     ["| ★甲(着地させる=PR)★ | ★13★", "| 乙(捨てる=裁を待つ) | ★0★",
      "| 丙(測れぬ) | ★0★"]),
    ("捨證軸", "當方 km-102 README.md", A3 + "/README.md",
     ["| 丙① |", "| 丙② |", "| 乙① |", "| 乙② |", "| 乙③ |",
      "| 甲 | 上の五つに悉く当たらぬ", "捨ててよい證が一つも立たなかつた本数"]),
    ("重複軸(語「不要」)", "家老 前紙 km-eda-fuyou README.md",
     os.path.join(EV, "karo-mac-eda-fuyou-20260917/README.md"),
     ["## 二 「不要」の定義", "其の枝の tip が、★origin に現に在る他の枝★の祖先である",
      "「main へ入つたから要らぬ」ではない", "残枝に保持先を持たぬ不要枝 = ★0本★"]),
    ("器軸", "家老 README.md", KR + "/README.md",
     ["| ★甲 着地させる(PR)★", "| ★乙 捨てる(理事長裁を待つ)★", "| 丙 測れぬ",
      "本紙の「乙=捨てる」は"]),
]

def tsv(path, key_col, val_cols):
    out = {}
    for i, ln in enumerate(open(path, encoding="utf-8").read().split("\n")):
        if i == 0 or not ln.strip():
            continue
        c = ln.split("\t")
        if max([key_col] + val_cols) < len(c):
            out[c[key_col].strip()] = [c[v].strip().replace("★", "") for v in val_cols]
    return out

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 40_nigi.py <束の根>\n"); return 2
    base = sys.argv[1]; raw = os.path.join(base, "raw")
    eda = [l.split("\t")[1] for i, l in
           enumerate(open(os.path.join(raw, "21_nul_jissoku.tsv"), encoding="utf-8")
                     .read().split("\n")) if i and l.strip()]

    # ── 逐語を引く(対照ⓐ) ────────────────────────────────
    chiku = ["★各紙の甲乙丙の定義 ―― 逐語(器が紙から引いた。手で写して居らぬ)★", ""]
    for jiku, kami, path, anchors in IKARI:
        chiku.append("── %s ／ %s ──" % (jiku, kami))
        gyou = open(path, encoding="utf-8").read().split("\n")
        for a in anchors:
            hit = [(i + 1, g) for i, g in enumerate(gyou) if a in g]
            if len(hit) != 1:
                sys.stderr.write("★錨 %r が %s に %d 行 命中(唯一で無い) ∴ 止まる★\n"
                                 % (a, kami, len(hit))); return 5
            n, g = hit[0]
            chiku.append("  L%-4d %s" % (n, g.strip()))
        chiku.append("")
    K.kaku(os.path.join(raw, "41_teigi_chikugo.txt"), "\n".join(chiku))

    # ── 捨證軸(三席) ────────────────────────────────────
    sha = {}
    for b, v in tsv(A1 + "/an/95_shiwake.tsv", 0, [9, 10]).items():
        sha[b] = ("a1", v[0].replace("**", ""), v[1])
    for b, v in tsv(A2 + "/raw/40_shiwake.tsv", 0, [6]).items():
        sha[b] = ("a2", v[0], "―")
    for b, v in tsv(A3 + "/raw/81_shiwake.tsv", 0, [6]).items():
        sha[b] = ("當方", v[0].split("-")[0], v[0])

    # ── 器軸(家老)・二つの出所 ────────────────────────────
    kigu = {b: v[0] for b, v in tsv(KR + "/raw/10_sokutei.tsv", 0, [5]).items()}
    nazashi = set()
    for ln in open(KR + "/raw/30_summary.txt", encoding="utf-8").read().split("\n"):
        if ln.startswith("甲の枝="):
            nazashi = set(ln[len("甲の枝="):].split())
    if not nazashi:
        sys.stderr.write("★家老の名指し「甲の枝=」が引けぬ ∴ 止まる★\n"); return 5
    for b in eda:                                    # ── 対照ⓑ
        kara_suu = (int(kigu.get(b, "0")) > 0)
        if kara_suu != (b in nazashi):
            sys.stderr.write("★家老の二出所が食ひ違ふ: %s(器file=%s / 名指し=%s) ∴ 止まる★\n"
                             % (b, kigu.get(b), b in nazashi)); return 5

    # ── 一表 ────────────────────────────────────────────
    rows, kousa = [], {}
    for b in sorted(eda):
        if b not in sha or b not in kigu:             # ── 対照ⓒ
            sys.stderr.write("★%s の判が欠く(捨證=%s 器=%s) ∴ 止まる★\n"
                             % (b, b in sha, b in kigu)); return 5
        seki, s_han, s_noru = sha[b]
        k_han = "甲" if int(kigu[b]) > 0 else "乙"
        rows.append([b.replace("karo-mac/", "K/"), seki, s_han, s_noru, k_han, kigu[b],
                     "★二軸が割れる★" if s_han != k_han else "二軸が揃ふ"])
        kousa[(s_han, k_han)] = kousa.get((s_han, k_han), 0) + 1
    K.kaku_tsv(os.path.join(raw, "42_ichihyou.tsv"), rows,
               ["枝名(K/=karo-mac/)", "測つた席",
                "★捨證軸★_三席(甲=捨てて良い證が立たぬ/乙=立つ/丙=測れぬ)", "同_則or副札",
                "★器軸★_家老(甲=自前差分に器を含む/乙=紙のみ/丙=手許に物無し)", "同_自前器file数",
                "二軸の異同"])

    K.kaku_tsv(os.path.join(raw, "43_kousa.tsv"),
               [[s, k, str(kousa.get((s, k), 0))] for s in "甲乙丙" for k in "甲乙丙"],
               ["★捨證軸★_三席", "★器軸★_家老", "枝の数"])

    s_kei = {h: sum(1 for r in rows if r[2] == h) for h in "甲乙丙"}
    k_kei = {h: sum(1 for r in rows if r[4] == h) for h in "甲乙丙"}
    if (k_kei["甲"], k_kei["乙"]) != (10, 35):        # ── 対照ⓓ
        sys.stderr.write("★器軸の数へ %s が家老の宣 甲10/乙35 と合はぬ ∴ 止まる★\n" % k_kei); return 5

    ware = sum(1 for r in rows if r[6].startswith("★"))
    K.kaku(os.path.join(raw, "44_nigi_matome.txt"), "\n".join([
        "母數 45 本・二軸を別欄に分けた(raw/42_ichihyou.tsv)",
        "",
        "★捨證軸★(三席・問ひ=捨てて良い證が立つか): 甲 %d / 乙 %d / 丙 %d"
        % (s_kei["甲"], s_kei["乙"], s_kei["丙"]),
        "★器軸★(家老・問ひ=自前差分が器を含むか):   甲 %d / 乙 %d / 丙 %d"
        % (k_kei["甲"], k_kei["乙"], k_kei["丙"]),
        "",
        "★二軸が割れる枝 = %d 本 / 45★ ―― 同じ字「乙」が %d 本で別の物を指して居る。"
        % (ware, ware),
        "交差表 raw/43_kousa.tsv: " +
        " / ".join("捨證%s×器%s=%d" % (s, k, kousa[(s, k)]) for s, k in sorted(kousa)),
        "",
        "★此の表が意味せぬ事★:",
        "  ・「二軸が割れる」は★どちらかが誤り★の意ではない。二つは別の問ひに答へて居る。",
        "  ・捨證軸の甲は「PR を起こせ」の證ではない(是非の判は軍師mac ―― 裁 325884)。",
        "  ・器軸の乙は「捨てて良い」の證ではない。家老紙の逐語は",
        "    「紙のみの枝ゆゑ main に入れずとも器は揃ふ」であり、捨證を論じて居らぬ。",
        "  ・丙 0 は「測れぬ枝が無い」であり「測りが正しい」ではない。",
        "  ・★「不要15」は「捨てる15」ではない★ ―― 逐語は「他の枝の祖先ゆゑ消しても",
        "    commit は失はれぬ」。45 本が不要15 を担ぐのは★定義の裏返し★であつて疵ではない。",
    ]))
    sys.stderr.write("二義 解了 捨證 甲%d乙%d丙%d / 器 甲%d乙%d丙%d / 割れ %d\n"
                     % (s_kei["甲"], s_kei["乙"], s_kei["丙"],
                        k_kei["甲"], k_kei["乙"], k_kei["丙"], ware))
    return 0

sys.exit(main())

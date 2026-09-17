# -*- coding: utf-8 -*-
"""㋒ ★出所欄★ ＋ ㋐追補 ★名の揺れ★ ―― ⑴ を六つの出所から引き、當器の実測と一本づつ突合す。

★出所(紙=散文の表／実=器の出した TSV)★:
  當実  本束 `raw/21_nul_jissoku.tsv` 欄「甲NUL実測」       ← ★本表の拠り所(基準)★
  a1紙  a1 `README.md` 冠 `| # | 枝 | sha12 | ⑴3dot |…` の表 欄「⑴3dot」
  a1実  a1 `an/95_shiwake.tsv` 欄 `d1_3dot_files`
  a2紙  a2 `report.md` 冠 `| 枝(karo-mac/ を略す) | ⑴対main |…` の表 欄「⑴対main」
  a2実  a2 `raw/40_shiwake.tsv` 欄「⑴file数」
  家老  家老 `raw/10_sokutei.tsv` 欄 `tai_main_files`(45本・三席の割当を跨ぐ)

★表は冠行の逐語で名指す★。紙には表が二つ以上在り(a2 は 42 行目と 117 行目)、
「markdown の表を悉く読む」実装では★後の表が前の表を上書きして別の数を刷る★(初版で現に起きた)。

★名の揺れ(㋐「名の揺れを名指せ」への答)★ ―― 紙の名を枝の名へ戻す規、四つ:
  規0 其の儘          例 `ashigaru-mac-1/a1-jishu-…-20260917`
  規1 冠 `karo-mac/` を補ふ          例 `a1-r56`            → `karo-mac/a1-r56`
  規2 末尾 `-20260917` を補ふ
  規3 規1+規2 を併せ補ふ             例 `km-52-shikii-…-seyo` → `karo-mac/km-52-…-seyo-20260917`
  規4 ★前方一致が唯一一本★の時のみ戻す   例 `km-77-…-de-kakutei`(`-seyo-20260917` まで落ちて居る)
     ―― 二本以上に前方一致したら★戻さず★「曖昧」と刷る(推して当てぬ)。
規は★上から順に当て、最初に当つた一つを採る★。当らねば「戻せず」と名指して刷る(黙つて捨てぬ)。

★枝に非ざる行(宣して除く)★: `★総和★` = 紙の表の締め行。枝名ではない ∴ 名の揺れに数へぬ。

対照(倒れたら止まる):
  ⓐ 六つの出所が一つでも一本も命中せねば 止(空の表を「一致」と書かぬ)
  ⓑ 規を当てずに突合したら a2紙 の命中は 0 に成る筈 ―― 成らねば 止(規の検めに成らぬ)
  ⓒ 二つの紙名が同じ枝へ戻つたら 止(規が名を潰して居る)
  ⓓ 二本以上へ前方一致する名(`karo-mac/km-5`)を規4 が戻したら 止(曖昧を推して当てて居る)
"""
import os, sys, re, importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("K", os.path.join(_d, "00_kaki.py"))
K = importlib.util.module_from_spec(_s); _s.loader.exec_module(K)
REPO = os.path.abspath(os.path.join(_d, "..", "..", "..", ".."))
A1 = os.path.join(REPO, "docs/evidence/ashigaru-mac-1_km-100-eda-chakuchi-shiwake-20260917")
A2 = os.path.join(REPO, "docs/evidence/a2_km-101-eda-yonjuugo-no-chakuchi-shiwake-20260917")
KR = os.path.join(REPO, "docs/evidence/karo-mac-eda-chakuchi-shiwake-20260917")

def tsv(path, key_col, val_col):
    out = {}
    for i, ln in enumerate(open(path, encoding="utf-8").read().split("\n")):
        if i == 0 or not ln.strip():
            continue
        c = ln.split("\t")
        if max(key_col, val_col) < len(c):
            out[c[key_col].strip()] = c[val_col].strip().replace("★", "")
    return out

def md_table(path, kanmuri, name_col, val_col):
    """冠行(kanmuri を含む `|` 行)で表を名指し、其の表★のみ★を読む。"""
    out, naka = {}, False
    for ln in open(path, encoding="utf-8").read().split("\n"):
        if not ln.startswith("|"):
            if naka:
                break          # 表は空行で終る
            continue
        if not naka:
            naka = kanmuri in ln
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if max(name_col, val_col) >= len(c) or set(c[0]) <= set("-: "):
            continue
        nm = c[name_col].strip("`* ")
        v = c[val_col].strip("`*★ ")
        if re.fullmatch(r"\d+", v):
            out[nm] = v
    if not out:
        raise SystemExit("★冠 %r の表が読めぬ★: %s" % (kanmuri, path))
    return out

KI = ["規0 其の儘", "規1 冠karo-mac/", "規2 末尾-20260917", "規3 冠+末尾"]
SHIME = ("★総和★",)          # 枝に非ざる締め行(宣して除く)
def modosu(nm, eda):
    """紙名 → (枝名, 用ゐた規)。戻せねば (None, 理由)。"""
    if nm in SHIME:
        return None, "―― 締め行(枝に非ず)"
    for i, c in enumerate([nm, "karo-mac/" + nm, nm + "-20260917",
                           "karo-mac/" + nm + "-20260917"]):
        if c in eda:
            return c, KI[i]
    for kanmuri in ("", "karo-mac/"):       # 規4 前方一致(唯一のみ)
        hit = [e for e in eda if e.startswith(kanmuri + nm)]
        if len(hit) == 1:
            return hit[0], "規4 前方一致(唯一)"
        if len(hit) > 1:
            return None, "★曖昧(前方一致 %d 本)★" % len(hit)
    return None, "★戻せず★"

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 30_shussho.py <束の根>\n"); return 2
    base = sys.argv[1]; raw = os.path.join(base, "raw")
    jissoku = tsv(os.path.join(raw, "21_nul_jissoku.tsv"), 1, 3)

    kami = {
        "a1紙": md_table(os.path.join(A1, "README.md"), "⑴3dot", 1, 3),
        "a2紙": md_table(os.path.join(A2, "report.md"), "⑴対main", 0, 1),
    }
    jitsu = {
        "a1実": tsv(os.path.join(A1, "an/95_shiwake.tsv"), 0, 2),
        "a2実": tsv(os.path.join(A2, "raw/40_shiwake.tsv"), 0, 2),
        "家老": tsv(os.path.join(KR, "raw/10_sokutei.tsv"), 0, 3),
    }
    # ── 名を規で戻し、揺れを臺帳に取る ───────────────────
    yure, src = [], {}
    for k in list(kami) + list(jitsu):
        moto = kami.get(k) or jitsu[k]; naoshi = {}
        for nm, v in moto.items():
            eda, ki = modosu(nm, jissoku)
            if eda is None:
                # ★modosu の返した理由を其の儘刷る★(呼び手が字面を書くと、
                #  締め行・曖昧・戻せず の三つが一語に潰れる ―― 現に潰れた)
                yure.append([k, nm, "-", ki]); continue
            if ki != KI[0]:
                yure.append([k, nm, eda.replace("karo-mac/", "K/"), ki])
            if eda in naoshi:                      # ── 対照ⓒ
                sys.stderr.write("★%s の二名が同じ枝 %s へ潰れた ∴ 止まる★\n" % (k, eda)); return 5
            naoshi[eda] = v
        src[k] = naoshi
    # ── 対照ⓓ: 曖昧な名を規4 が戻さぬ事 ───────────────────
    aimai, riyuu = modosu("karo-mac/km-5", jissoku)
    if aimai is not None:
        sys.stderr.write("★曖昧な名 karo-mac/km-5 を %s へ戻した ∴ 止まる★\n" % aimai); return 5

    # ── 対照ⓐ ────────────────────────────────────────────
    for k, v in src.items():
        if not v:
            sys.stderr.write("★出所 %s が一本も命中せぬ ∴ 止まる★\n" % k); return 5
    # ── 対照ⓑ: 規を当てねば a2紙 は 0 命中 ────────────────
    if sum(1 for nm in kami["a2紙"] if nm in jissoku):
        sys.stderr.write("★規を当てずとも a2紙 が命中した ∴ 規の検めに成らぬ ∴ 止まる★\n"); return 5

    RAN = ["a1紙", "a1実", "a2紙", "a2実", "家老"]
    rows, chigai = [], {k: 0 for k in RAN}
    for br in sorted(jissoku):
        j = jissoku[br]; r = [br.replace("karo-mac/", "K/"), j]
        for k in RAN:
            v = src[k].get(br, "-")
            r.append(v)
            if v not in ("-", j):
                chigai[k] += 1
        sa = [k for k in RAN if src[k].get(br, "-") not in ("-", j)]
        r.append("★違ふ:%s★" % ",".join(sa) if sa else "一致")
        rows.append(r)
    K.kaku_tsv(os.path.join(raw, "31_shussho.tsv"), rows,
               ["枝名(K/=karo-mac/)", "當実NUL", "a1紙", "a1実", "a2紙", "a2実", "家老", "判"])
    K.kaku_tsv(os.path.join(raw, "33_na_no_yure.tsv"), yure,
               ["出所", "紙に載る名", "戻した枝名", "用ゐた規"])

    arihu = {k: sum(1 for br in jissoku if br in src[k]) for k in RAN}
    # a1紙 の +1 か否かを名指す
    a1sa = sorted({int(src["a1紙"][b]) - int(jissoku[b]) for b in src["a1紙"]})
    K.kaku(os.path.join(raw, "32_shussho_matome.txt"), "\n".join(
        ["基準 = 當実NUL(本束 raw/21_nul_jissoku.tsv・母數 45 本)", ""] +
        ["%s: 載る %2d 本 / ★當実と違ふ %2d 本★" % (k, arihu[k], chigai[k]) for k in RAN] +
        ["",
         "a1紙 − 當実 の差の種類 = %s(★悉く +1 なら値は [1] の一つのみ★)" % a1sa,
         "名の揺れ = %d 件(raw/33_na_no_yure.tsv)・★戻せず = %d 件★・締め行(枝に非ず) = %d 件"
         % (len(yure), sum(1 for y in yure if y[3].startswith("★")),
            sum(1 for y in yure if y[3].startswith("――"))),
         "",
         "★此の表が意味せぬ事★:",
         "  ・「違ふ」は「誤り」ではない。各紙は各々の刻に各々の器で測つた。",
         "    枝(sha)は動かぬが★器は直る★ ―― a1 は走の途中で splitlines を -z へ直して居る。",
         "  ・「一致」も「其の紙の器が正しい」の證ではない。同じ疵を二つの器が共に持てば揃つて誤る。",
         "  ・「載る N 本」は其の席の割当本数であり、測れた本数ではない。",
         "  ・本表は ⑴(対 main)のみ。⑵(自前差分)の出所は別に測る要が在る。",
         ]))
    sys.stderr.write("突合了 " + " / ".join("%s 違%d(載%d)" % (k, chigai[k], arihu[k]) for k in RAN)
                     + " / 揺れ%d\n" % len(yure))
    return 0

sys.exit(main())

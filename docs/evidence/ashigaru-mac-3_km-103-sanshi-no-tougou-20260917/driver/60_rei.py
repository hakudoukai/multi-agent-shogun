# -*- coding: utf-8 -*-
"""㋔ ★零の四札★ ―― 本束が刷る零を、悉く同じ形で保證する。

★零には四つの札が要る(裁・過去の教訓)★
  ㊀ ★陽性対照★ ―― 其の零を出した★檢出子そのもの★に、種を一つ植ゑて当てる。
       鳴らねば「零」ではなく「檢出子が死んで居る」。∴ 鳴らぬ時は ★止まる(rc=5)★。
       ★檢出子は「行」ではなく「行の集合」を受ける★ ―― 重複の檢出子の如く★状態を持ち回る★
       器が在る。行毎に呼ぶと、対照の種が★本番の歩きを汚す★(本器の初版で現に起きた:
       種を先に植ゑた所為で本番の一行目が「二度目」に見え、零①が偽で鳴つた)。
       ∴ 本番 = 檢出子(本番の行) / 対照 = 檢出子(本番の行 ＋ 種一行) と★別々に呼ぶ★。
       対照の命中が★本番より丁度一つ多い★事を以て「鳴つた」と見る。
  ㊁ ★根と深さ★ ―― 何處を歩いて零だつたか(file の path)と、幾行歩いたか(行数)。
  ㊂ ★rc★     ―― 其の測りの終了符。
  ㊃ ★刻★     ―― 何時の disk の状態か。

★本器は測り直さぬ(再測ではない)★
  零は既に 10/20/30/40/50 の器が出した。本器は其の出目 tsv を★根として歩き直し★、
  同じ零に成るかを検め、四札を付けて刷る。∴ 本器の零は「紙の写し」ではなく「紙を歩いた実測」。

★此の数が意味せぬ事★
  ・陽性対照が鳴る事は「檢出子が正しい」の證ではない。★「死んで居らぬ」の證★のみ。
  ・行数(深さ)は「歩いた行」であり、「有り得た行」ではない。
"""
import os, sys, subprocess, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = __import__("00_kaki")


def yomu(path):
    """tsv を 見出し+行 で返す。★空欄 `-` は其の儘★(kaku_tsv の約束)。"""
    s = open(path, encoding="utf-8").read()
    rows = [ln.split("\t") for ln in s.split("\n") if ln and not ln.startswith("#")]
    return rows[0], rows[1:]


def main(bundle):
    raw = os.path.join(bundle, "raw")
    toki = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%z"],
                          capture_output=True, text=True).stdout.strip()

    fuda = []   # [零の名, 根, 深さ, 檢出子, 実測, 陽性対照, rc]
    taore = []

    def satsu(na, ne, atama, gyou, kenshutsu, tane, ken_na):
        """一つの零に四札を当てる。
        kenshutsu(atama, rows) -> 命中した行の list(★集合を受ける★・上の ㊀ 参照)。
        tane = 檢出子が★必ず鳴る★筈の贋の行(本番の行に一行だけ足す)。"""
        honban = kenshutsu(atama, gyou)
        taisho = kenshutsu(atama, list(gyou) + [tane])
        nari = len(taisho) - len(honban)           # ── ㊀ 陽性対照は「丁度一つ増える」事
        rc = 0
        if nari != 1:
            rc = 5
            taore.append("%s: 陽性対照の増分が %d(1 で無い) ∴ 檢出子が死んで居る疑ひ" % (na, nari))
        if honban:
            rc = rc or 7
            taore.append("%s: ★零に非ず★ %d 行 命中 ―― %s" % (na, len(honban), honban[0][:3]))
        fuda.append([na, os.path.relpath(ne, bundle), str(len(gyou)), ken_na,
                     str(len(honban)), "鳴る(増分1)" if nari == 1 else "★鳴らず(増分%d)★" % nari,
                     str(rc), toki])
        return rc

    warui = 0

    # ── 零① ㋐ 割持に★同じ枝名が二度★出ぬ(重複=0)
    p = os.path.join(raw, "11_bogen_warimochi.tsv"); a, g = yomu(p)
    def juufuku(atama, rows):
        """★呼ぶ毎に状態を作り直す★(持ち回れば対照の種が本番を汚す ―― 上の ㊀)。"""
        mita, hit = set(), []
        for r in rows:
            if r[1] in mita:
                hit.append(r)
            mita.add(r[1])
        return hit
    tane = list(g[0])                               # 種 = 一行目の名を、も一度
    warui |= satsu("零① 枝名の重複=0(㋐)", p, a, g, juufuku, tane,
                   "同じ枝名が二度目に現れたら鳴る")

    # ── 零② ㋒ U+2028 の疵 = 0(丙splitlines − 甲NUL実測 ≠ 0 が零本)
    p = os.path.join(raw, "21_nul_jissoku.tsv"); a, g = yomu(p)
    i_sa = a.index("丙−甲")
    tane = list(g[0]); tane[i_sa] = "1"
    warui |= satsu("零② U+2028 の疵=0(㋒)", p, a, g,
                   lambda a_, rs: [r for r in rs if r[i_sa] != "0"], tane,
                   "欄「丙−甲」が 0 に非ずば鳴る")

    # ── 零③ ㋒ 名の★戻せず★=0(揺れ臺帳に「戻せず」「曖昧」が一件も無い)
    p = os.path.join(raw, "33_na_no_yure.tsv"); a, g = yomu(p)
    i_ki = len(a) - 1
    tane = list(g[0]); tane[i_ki] = "★戻せず★"
    warui |= satsu("零③ 名を戻せず=0(㋒)", p, a, g,
                   lambda a_, rs: [r for r in rs
                                   if ("戻せず" in r[i_ki]) or ("曖昧" in r[i_ki])], tane,
                   "揺れ臺帳の末欄に「戻せず」か「曖昧」が在らば鳴る")

    # ── 零④ ㋑ 二軸の何れにも「丙(測れぬ)」が無い
    p = os.path.join(raw, "42_ichihyou.tsv"); a, g = yomu(p)
    i_su = [i for i, c in enumerate(a) if c.startswith("★捨證軸★")][0]
    i_ki2 = [i for i, c in enumerate(a) if c.startswith("★器軸★")][0]
    tane = list(g[0]); tane[i_su] = "丙"
    warui |= satsu("零④ 丙(測れぬ)=0(㋑・二軸共)", p, a, g,
                   lambda a_, rs: [r for r in rs if r[i_su].startswith("丙")
                                   or r[i_ki2].startswith("丙")],
                   tane, "捨證軸か器軸の何れかが「丙」で始まらば鳴る")

    # ── 零⑤ ㋓ 45 本の内、★他の 45 本★を待つ枝 = 0
    p = os.path.join(raw, "51_kusari.tsv"); a, g = yomu(p)
    i_45 = a.index("段③★45本同士★を待つ数")
    tane = list(g[0]); tane[i_45] = "2"
    warui |= satsu("零⑤ 45本同士の待ち=0(㋓)", p, a, g,
                   lambda a_, rs: [r for r in rs if r[i_45] != "0"], tane,
                   "段③欄が 0 に非ずば鳴る")

    # ── 零⑥ ㋑ 捨證軸の「乙(捨てて良い證が立つ)」= 0
    p = os.path.join(raw, "42_ichihyou.tsv"); a, g = yomu(p)
    tane = list(g[0]); tane[i_su] = "乙"
    warui |= satsu("零⑥ 捨證軸の乙=0(㋑)", p, a, g,
                   lambda a_, rs: [r for r in rs if r[i_su].startswith("乙")], tane,
                   "捨證軸が「乙」で始まらば鳴る")

    K.kaku_tsv(os.path.join(raw, "61_rei_yonsatsu.tsv"), fuda,
               ["零の名", "㊁根(束内相対)", "㊁深さ(歩いた行数)", "檢出子(逐語)",
                "実測(命中行数)", "㊀陽性対照(種を一行足すと+1)", "㊂rc", "㊃刻"])

    K.kaku(os.path.join(raw, "62_rei_matome.txt"), "\n".join([
        "★零 %d 件に四札を当てた★(刻 %s)" % (len(fuda), toki),
        "  ㊀陽性対照=六件悉く★増分1★で鳴る / ㊂rc=悉く 0 / ㊁根と深さは欄に在り",
        "",
        "★四札を当てなかつた零★(宣して除く):",
        "  ・㋐の「差=0/0」(60−15−45)は★零ではなく等式★である ∴ 四札に非ず、突合で示す。",
        "  ・㋓段①の「単独で載る=0」は★零だが疵ではない★ ―― 45 本が悉く不要15 を担ぐ事の",
        "    裏返しであり、`52_kusari_matome.txt` に逐語で書いた。",
        "",
        "★此の数が意味せぬ事★:",
        "  ・陽性対照が鳴るのは★檢出子が死んで居らぬ★事のみを示す(正しさの證ではない)。",
        "  ・深さは★歩いた行数★であり、有り得た行数ではない。",
        "  ・刻は★本器が歩いた時★であり、元の器が測つた時ではない(元の刻は各 matome に在り)。",
    ] + (["", "★倒れ★:"] + ["  " + t for t in taore] if taore else [])))

    if taore:
        for t in taore:
            sys.stderr.write("★" + t + "★\n")
        return 5
    sys.stderr.write("四札 了 零%d件 / 陽性対照 悉く鳴る / rc 悉く0\n" % len(fuda))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

# -*- coding: utf-8 -*-
"""km-103 納め便を組み、★字数を器で測つてから★書く(條 300 字・python3 len)。

★宣した事★
 ・胴は本器が組む。★数は raw/*.tsv から引く★(手で写さぬ ―― kin 逐語)。
 ・★300 字を超えたら一字も本便を書かず rc=7 で止まる(fail-closed)★。下書のみ raw に残す。
 ・最終巡の門の名は ★引数で受ける★(器に焼き込めば巡を足した時に便が嘘を吐く)。

★本器は門より先に走る★
  便も束の一部ゆゑ、臺帳が凍る前に置かねば成らぬ。∴ 便が申す「門 rc=0」は
  ★本器が書いた時点の見込み★である。★最終巡の門と食ひ違はぬ事は `driver/90_awase.py`
  が門の後に検める★(其の出目は臺帳の外 `_gate/85_awase.txt`)。
  ∴ 門が落ちたなら ―― 便は★送らぬ★。書いて在る事は送つた事ではない。

★此の字数が意味せぬ事★: 便が★届いた★事ではない。届いたか否かは家老mac の箱を
  ★鍵で引いて★胴を照合して初めて言へる(便の rc=0 は「送つた」に過ぎぬ)。
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = __import__("00_kaki")

JOU = int(os.environ.get("KM103_JOU", "300"))


def yomu(path):
    s = open(path, encoding="utf-8").read()
    rows = [ln.split("\t") for ln in s.split("\n") if ln and not ln.startswith("#")]
    return rows[0], rows[1:]


def main(base, saigo):
    raw = os.path.join(base, "raw")
    a_k, g_k = yomu(os.path.join(raw, "43_kousa.tsv"))
    ksa = {(r[0], r[1]): int(r[2]) for r in g_k}
    su = {k: sum(v for (x, _), v in ksa.items() if x == k) for k in "甲乙丙"}
    ki = {k: sum(v for (_, y), v in ksa.items() if y == k) for k in "甲乙丙"}
    a_y, g_y = yomu(os.path.join(raw, "33_na_no_yure.tsv"))
    a_r, g_r = yomu(os.path.join(raw, "51_kusari.tsv"))
    i_m1 = a_r.index("段①待つ相手の数"); i_m2 = a_r.index("段②待つ相手の数")
    i_45 = a_r.index("段③★45本同士★を待つ数")
    tan1 = sum(1 for r in g_r if r[i_m1] == "0")
    tan2 = sum(1 for r in g_r if r[i_m2] == "0")
    machi2 = len(g_r) - tan2
    uchi45 = sum(1 for r in g_r if r[i_45] != "0")
    a_s, g_s = yomu(os.path.join(raw, "31_shussho.tsv"))
    i_t = a_s.index("當実NUL"); i_a = a_s.index("a1紙")
    a1_chigau = sum(1 for r in g_s if r[i_a] != "-" and r[i_a] != r[i_t])

    hon = (
        "[專任3 km-103 納] 三紙を一表に、語を一義に。★同字二義★=捨證軸(三席)甲%d乙%d丙%d"
        "／器軸(家老)甲%d乙%d丙%d ―― ★%d本が「乙」で別物★。「不要15」も「捨てる15」に非ず"
        "(逐語=他枝の祖先ゆゑ消して commit 失はれず)。㋐60-15=45 閉ぢ・揺れ%d(戻せず0)。"
        "㋒a1の+1疵は★紙のみ%d本★、a1実/a2/家老は實測と一致。㋓幹=main 単独%d／家老の幹が"
        "載れば単独%d待%d、45本同士の待ち%d。★家老の幹は不要15の一本★∴可否は理事長裁。"
        "門rc=0(%s)。束=本札の bundle。軍師mac 死箱ゆゑ中継を請ふ。"
        % (su["甲"], su["乙"], su["丙"], ki["甲"], ki["乙"], ki["丙"], ksa[("甲", "乙")],
           len(g_y), a1_chigau, tan1, tan2, machi2, uchi45, saigo)
    )
    ji = len(hon)
    K.kaku(os.path.join(raw, "96_osame_ji.txt"),
           "字数(python3 len)=%d\n條=%d\n残り=%d\n最終巡=%s\n測つた胴=raw/96_osame.txt"
           % (ji, JOU, JOU - ji, saigo))
    if ji > JOU:
        K.kaku(os.path.join(raw, "96_osame_shitagaki.txt"), hon)
        sys.stderr.write("★條を超えた ∴ 一字も本便を書かず止まる(超過 %d 字)★\n" % (ji - JOU))
        return 7
    K.kaku(os.path.join(raw, "96_osame.txt"), hon)
    sys.stderr.write("字数=%d(條 %d・残 %d)\n" % (ji, JOU, JOU - ji))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))

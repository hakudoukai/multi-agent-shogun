# -*- coding: utf-8 -*-
"""㋓ 仕分け ―― ★判ずる拠り所を先に宣し、然る後に機械で当てる★。

  usage: python3 driver/80_shiwake.py <raw dir> <札 yaml>

★拠り所(此の docstring が宣言である ―― 出目を見てから足したり曲げたりして居らぬ)★
順に当て、★先に当たつた一つ★で決める(排他・順序有り)。

  丙① 物が手許に無い        : 11_bogen の cat_file_e_rc ≠ 0
  丙② ⑵ が測れぬ            : 31 の (2)kiten_eda = 測れぬ(真の祖先 tip が 60 本の内に一本も無い)
  乙① 末端が運ぶ            : 42 の「60本中の子孫tip数」≧1 ―― 此の tip を含む枝が別に在る
                              ∴ 其の末端を着地させれば此の枝の中身も運ばれる ∴ 単独 PR は要らぬ
  乙② 齎す物が無い          : 31 の (2)file_gyou = 0 ―― 自前の差分が空
  乙③ 既に main に在る      : 51 の「★mainへ齎す★」= 0 ―― 自前 path の悉くが main と同一 blob
  甲  着地させる            : 上の五つに悉く当たらぬ

★甲の副札★(着地の★順序★を付ける為の物であつて、甲乙の別ではない):
  甲-器-要調停 : ⑵領域に器(scripts / .claude / config)を含み、且つ 62 の「重なる枝の数」≧1
  甲-器        : 器を含み、重なり 0
  甲-紙        : 器を含まず(docs / queue のみ)

★此の拠り所が★測れぬ★物★(=甲乙丙では答へられぬ・判定は軍師mac の職):
  ・「此の中身が★正しい★か」 ―― 拠り所は悉く ★在る/無い・同一/相違★ の話であり、是非を問うて居らぬ。
  ・「PR に通るか」 ―― 其れは ㋔ の受入条件を実際に通して初めて判る。
出目: 81_shiwake.tsv(札の求める逐語の列) / 82_shiwake_riyuu.tsv(拠り所の当たり方を一本づつ)
"""
import sys
from importlib import import_module

sys.path.insert(0, __file__.rsplit("/", 1)[0])
K = import_module("00_kaki")

UTSUWA = ("scripts", ".claude", "config")


def load(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        head = None
        for ln in fh:
            c = ln.rstrip("\n").split("\t")
            if head is None:
                head = c
                continue
            if c and c[0]:
                rows.append(dict(zip(head, c)))
    return rows


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    raw, fuda = sys.argv[1], sys.argv[2]

    order = []
    for ln in open(fuda, encoding="utf-8"):
        s = ln.strip()
        if len(s) > 41 and s[:40].isalnum() and "karo-mac/" in s:
            sha, name = s.split()[0], s.split()[1]
            order.append((sha, name))
    if len(order) != 14:
        sys.stderr.write("★札から枝が %d 本しか引けぬ(14 を期す)★ ―― 一行も書かず止まる\n" % len(order))
        return 5

    bogen = {r["branch"]: r for r in load(raw + "/11_bogen.tsv")}
    soku = {r["branch"]: r for r in load(raw + "/31_sokutei.tsv")}
    shison = {r["branch"]: r for r in load(raw + "/42_shison.tsv")}
    shitsu = {r["branch"]: r for r in load(raw + "/51_shitsu.tsv")}
    kasa = {r["branch"]: r for r in load(raw + "/62_kasanari_matome.tsv")}
    for nm, d in (("11", bogen), ("31", soku), ("42", shison), ("51", shitsu), ("62", kasa)):
        if len(d) != 14:
            sys.stderr.write("★%s の行が %d(14 を期す)★ ―― 一行も書かず止まる\n" % (nm, len(d)))
            return 5

    rows, riyuu = [], []
    tally = {}
    for sha, br in order:
        b, s, sh, q, ka = bogen[br], soku[br], shison[br], shitsu[br], kasa[br]
        rc = b["cat_file_e_rc"]
        kiten = s["(2)kiten_eda"]
        shison_n = int(sh["60本中の子孫tip数"])
        jimae = int(s["(2)file_gyou"])
        motarasu = int(q["★mainへ齎す★"])
        kasanari = int(ka["重なる枝の数"])
        ryouiki2 = s["(2)ryouiki"]
        utsuwa = [u for u in UTSUWA if u in ryouiki2.split()]

        hit = []
        hit.append(("丙①物が手許に無い", rc != "0", "cat_file_e rc=%s" % rc))
        hit.append(("丙②⑵測れぬ", kiten == "測れぬ", "基点=%s" % kiten))
        hit.append(("乙①末端が運ぶ", shison_n >= 1, "子孫tip=%d" % shison_n))
        hit.append(("乙②齎す物無し", jimae == 0, "⑵=%d" % jimae))
        hit.append(("乙③既にmainに在り", motarasu == 0, "mainへ齎す=%d" % motarasu))
        atari = [h for h in hit if h[1]]
        if atari:
            nm = atari[0][0]
            fuda_c = nm[0]
            riyuu_s = "%s(%s)" % (nm, atari[0][2])
            fuda_full = nm
        else:
            fuda_c = "甲"
            if utsuwa and kasanari >= 1:
                fuda_full = "甲-器-要調停"
                riyuu_s = ("子孫0・⑵=%d・mainへ齎す=%d ∴着地要。器(%s)を触り、同じ file を%d本が触る ∴版の先後を糺してから出せ"
                           % (jimae, motarasu, "/".join(utsuwa), kasanari))
            elif utsuwa:
                fuda_full = "甲-器"
                riyuu_s = ("子孫0・⑵=%d・mainへ齎す=%d ∴着地要。器(%s)を据ゑ、同 file を触る他枝0 ∴単独で出せる"
                           % (jimae, motarasu, "/".join(utsuwa)))
            else:
                fuda_full = "甲-紙"
                riyuu_s = ("子孫0・⑵=%d・mainへ齎す=%d ∴着地要。紙/箱のみ(%s)・衝突0 ∴記録として単独で出せる"
                           % (jimae, motarasu, ryouiki2))
        tally[fuda_c] = tally.get(fuda_c, 0) + 1
        rows.append([br, sha, s["(1)file_gyou"], jimae, s["(1)commit_main"],
                     s["(1)ryouiki"], fuda_full, riyuu_s])
        riyuu.append([br, fuda_full] + ["○" if h[1] else "×" for h in hit] + [h[2] for h in hit])

    K.kaku_tsv(raw + "/81_shiwake.tsv", rows,
               header=["枝", "sha40", "⑴(対main file数)", "⑵(自前 file数)", "commit(対main)",
                       "領域(対main)", "甲乙丙", "理由"])
    K.kaku_tsv(raw + "/82_shiwake_riyuu.tsv", riyuu,
               header=["枝", "札", "丙①", "丙②", "乙①", "乙②", "乙③",
                       "丙①の値", "丙②の値", "乙①の値", "乙②の値", "乙③の値"])
    sys.stderr.write("母數=%d / %s\n" % (len(rows), " ".join("%s=%d" % kv for kv in sorted(tally.items()))))
    return 0


sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒ 囮(をとり)の区 ―― 「臺帳の主張する path が不在で、'/' を含む別の語が実在する」区。

家老の問: ★v5 の第二の for(tok.split() で '/' を含む語を候補へ足す)★ が ★偽の通★ を作るか。
之は 10_menseki の十区では測れぬ(十区の行には '/' を含む余分な語が無い)。∴ 二区を新たに建てる。

  区壬  臺帳 path=nai/mono.txt(★不在★) / 同じ行の末に裸の語 aru/mono.txt(★実在★)
        宣sha = sha(囮の中身)                          期待=★鳴る★
        ―― 第二の for が囮を候補に足し、其れが disk に在り sha も合へば ★偽の通★ に成る
  区癸  同上・但し 宣sha = ★囮と違ふ中身★ の sha       期待=★鳴る★
        ―― 囮を拾つても sha で落ちる筈。拾ふ事自体は「鳴る理由」を実体無→相違へ挿げ替へる

方言は 10_menseki と同じ三形(甲=隣接 / 乙=間に他欄 / 丙=sha が先)。
器は 10_menseki の KI(十一本)を其の儘引く(★同じ器列で測る★)。

出目: raw/13_otori.tsv(全 66 行 = 2区 × 3方言 × 11器) / raw/13_otori.txt(要約) /
      raw/13_otori_tateta.txt(建てる手順)

★此の区は「臺帳の形として普通か」を問うて居らぬ★ ―― 問うて居るのは
  「行に '/' を含む余分な語が混じつた時、器が其れを path へ昇格させるか」だけである。
"""
import hashlib
import importlib.util
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

_spec = importlib.util.spec_from_file_location("menseki", os.path.join(HERE, "10_menseki.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
KI = _m.KI
hakaru = _m.hakaru

OTORI = "otori no naka\n"     # 囮 file `aru/mono.txt` の中身
BETSU = "betsu no naka\n"     # 区癸 の宣 sha が指す、★何処にも無い★ 中身
NAI = "nai/mono.txt"
ARU = "aru/mono.txt"


def sha(b):
    return hashlib.sha256(b.encode()).hexdigest()


KU = [
    ("壬", "囮と同じ", "鳴る"),
    ("癸", "囮と違ふ", "鳴る"),
]
HOUGEN = ["甲", "乙", "丙"]


def gyou(hougen, want, nbytes):
    """★末に裸の語(囮の path)を置く★ ―― 之が第二の for の餌である。"""
    if hougen == "甲":
        return f"path={NAI} sha256={want} bytes={nbytes} lines=1 {ARU}"
    if hougen == "乙":
        return f"path={NAI} bytes={nbytes} lines=1 sha256={want} {ARU}"
    return f"sha256={want} path={NAI} bytes={nbytes} lines=1 {ARU}"


def tateru(root, kuname, shakind, hougen, tejun):
    d = os.path.join(root, f"{kuname}_{hougen}")
    os.makedirs(os.path.join(d, "aru"))
    tejun.append(f"mkdir -p {d}/aru")
    with open(os.path.join(d, ARU), "w", newline="\n") as fh:
        fh.write(OTORI)
    tejun.append(f"printf '%s' {OTORI!r} > {d}/{ARU}   # ★囮(実在・'/' を含む)★")
    tejun.append(f"# {d}/{NAI} は ★建てぬ★(臺帳の主張する path は不在)")
    body = OTORI if shakind == "囮と同じ" else BETSU
    want = sha(body)
    man = os.path.join(d, "manifest.txt")
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# km-117 ㋒ 囮の見本(器の外・束の外)\n")
        fh.write(gyou(hougen, want, len(OTORI.encode())) + "\n")
    tejun.append(f"# 臺帳 {man} の一行 = {gyou(hougen, want[:8] + '…', len(OTORI.encode()))}")
    return d, man


def main():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    root = f"/private/tmp/km117_otori_{stamp}_{os.getpid()}"
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    tejun = [f"# ★建てる手順★(走る毎に建て直す・{stamp} の走りの逐語)",
             f"# 根 = {root}  ―― ★束の外★(札 kinshi 順守)",
             f"rm -rf {root}; mkdir -p {root}",
             f"# 囮の中身 sha256 = {sha(OTORI)}",
             f"# 区癸 の宣 sha(何処にも無い中身) = {sha(BETSU)}"]
    rows = []
    for kuname, shakind, kitai in KU:
        for hougen in HOUGEN:
            d, man = tateru(root, kuname, shakind, hougen, tejun)
            for kiname, kipath in KI:
                rc, n, nazashi, out, err = hakaru(kipath, man, d)
                kekka = ("正" if (kitai == "通る") == (rc == 0)
                         else ("★偽の通★" if kitai == "鳴る" else "★偽の赤★"))
                rows.append([hougen, kuname, shakind, kitai, kiname, rc,
                             n["一致"], n["相違"], n["実体無"], n["読めぬ行"],
                             n["曖昧"], kekka, nazashi])
    kaku_tsv(os.path.join(BUNDLE, "raw", "13_otori.tsv"), rows,
             header=["方言", "区", "宣sha", "期待", "器", "rc", "一致", "相違",
                     "実体無", "読めぬ行", "曖昧", "判定", "名指し"])
    kaku(os.path.join(BUNDLE, "raw", "13_otori_tateta.txt"), "\n".join(tejun))

    ki_names = [k for k, _ in KI]
    yo = ["# ㋒ 囮の区 ―― 器 × (区 × 方言) の rc / 判定",
          "# 期待は悉く ★鳴る★(臺帳の主張する path は不在なのだから)。",
          "# rc0 = ★偽の通★ = 第二の for が囮を path へ昇格させた印。",
          "\t".join(["器"] + [f"{k}{h}" for k, _, _ in KU for h in HOUGEN] + ["偽の通", "母數"])]
    for kiname in ki_names:
        line = [kiname]
        t = 0
        for kuname, _, _ in KU:
            for hougen in HOUGEN:
                r = [x for x in rows if x[0] == hougen and x[1] == kuname and x[4] == kiname][0]
                line.append(f"rc{r[5]}/{r[11]}")
                if r[11] == "★偽の通★":
                    t += 1
        line += [str(t), str(len(KU) * len(HOUGEN))]
        yo.append("\t".join(line))
    yo.append("")
    yo.append("# ★鳴る理由★(名指し) ―― 同じ rc でも理由が違ふ事が在る")
    for r in rows:
        yo.append("\t".join([r[0], r[1], r[4], f"rc{r[5]}",
                             f"一致{r[6]}/相違{r[7]}/実体無{r[8]}", r[12]]))
    kaku(os.path.join(BUNDLE, "raw", "13_otori.txt"), "\n".join(yo))
    print("\n".join(yo[:4 + len(ki_names)]))
    print(f"\n見本の根 = {root}(★束の外★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

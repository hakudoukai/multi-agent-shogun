# -*- coding: utf-8 -*-
"""40_narasu.py ―― raw の★末尾空白のみ★を剥ぎ、前後の sha256 を記す。

★何故要るか★ ―― km-105 の臺帳には ★末尾に空白一字を持つ行★ が現に在り、
照合器 karo_mac_manifest_verify.py は其の行を ★逐語で echo★ する。
∴ 其の出目を `>` で生捕りした raw は ★己の條②(末尾空白禁)に鳴る★。
之は此の束が論じてゐる疵と ★同族の自己参照★ である
(記録済: gate_log_burner_breaks_jou1_self_reference)。

★均すのは末尾の空白のみ。刷られた語は一字も変へぬ。★
★意味せぬ事★ ―― 均しは「元の行に空白が無かつた」の意ではない。
    在つた事は本 file の「均す前」欄の sha256 と「末尾空白=N行」が證す。

用: 40_narasu.py <raw dir>
"""
import hashlib
import pathlib
import sys


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def matsubi(b):
    return sum(1 for l in b.split(b"\n") if l.endswith(b" ") or l.endswith(b"\t"))


def main():
    raw = pathlib.Path(sys.argv[1])
    mae, ato = [], []
    for p in sorted(raw.glob("31_*.out")):
        b = p.read_bytes()
        n = matsubi(b)
        if n == 0:
            continue
        mae.append((p.name, sha16(b), n))
        nb = b"\n".join(l.rstrip(b" \t") for l in b.split(b"\n"))
        p.write_bytes(nb)
        ato.append((p.name, sha16(nb), matsubi(nb)))
    out = ["★均す前の sha256(記録)★"]
    for n, s, c in mae:
        out.append("  raw/%-40s %s  末尾空白=%d行" % (n, s, c))
    out.append("★均した後の sha256★")
    for n, s, c in ato:
        out.append("  raw/%-40s %s  末尾空白=%d行" % (n, s, c))
    out.append("  ★均したのは末尾空白のみ。刷られた語は一字も変へて居らぬ★")
    out.append("  ★均した本数 = %d / 31_*.out の母數 = %d★"
               % (len(mae), len(list(raw.glob("31_*.out")))))
    (raw / "40_seikika_no_mae_to_ato.txt").write_text("\n".join(out) + "\n",
                                                      encoding="utf-8")
    print("均した=%d本" % len(mae))


main()

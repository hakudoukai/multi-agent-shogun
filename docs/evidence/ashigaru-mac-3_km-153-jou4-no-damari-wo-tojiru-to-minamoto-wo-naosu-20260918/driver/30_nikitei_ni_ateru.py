# -*- coding: utf-8 -*-
"""七本の fx を ★二つの基底★ へ当て、鳴りと rc を並べる。
旧基底=共用樹 disk(未commit・321行) / 新基底=origin/main の blob 04672e15(339行)。
★rc は subprocess の returncode ―― 管を通さぬ★。門の出目は stderr にも stdout にも出る故 両方読む。
★新基底は兄弟器 karo_mac_fukashiji.py を `$(dirname $0)` から呼ぶ★ ∴ 同じ dir へ origin/main の blob を置いた
(km-159 の己の疵①=兄弟器無しで走らせ濡れ衣 rc=1 を出した件の治め)。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from importlib import import_module

K = import_module("00_kaki")
TABA = os.path.abspath(os.path.join(HERE, ".."))
FX = os.path.join(TABA, "raw", "fx")
KYUU = os.path.join(TABA, "_fx", "base_kyuu_disk.sh")
SHIN = os.path.join(TABA, "_fx", "base_shin_origin_main.sh")

NARI = [
    ("は空file(0byte)", "條④(0byte の口)"),
    ("EOF改行が無い(0)", "條④(改行無の口)"),
    ("EOF改行が複数(末尾に空行)", "條④(旧・末尾2字 0a0a の口)"),
    ("末尾行が不可視のみ", "條④(新・裁 seq330497 の口)"),
    ("CR混入", "條③"),
    ("末尾不可視字", "條②(新・類 Zs/Zl/Zp/Cc/Cf)"),
    ("末尾空白", "條②(旧・ASCII 空白と TAB のみ)"),
    ("測れぬ", "★測れぬ(default-deny)★"),
]


def hashiru(base, fxpath):
    p = subprocess.run(["bash", base, "--", fxpath],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    return out, err, p.returncode


def natta(out, err, fxname):
    """★其の fx の名を含む ★行★ のみを拾ふ★ ―― 他の行(結語・條①の刷り)を鳴りに数へぬ。"""
    hits = []
    for ln in (out + "\n" + err).split("\n"):
        if "★" not in ln:
            continue
        if fxname not in ln:
            continue
        for kotoba, jou in NARI:
            if kotoba in ln:
                hits.append((jou, ln.strip()))
                break
    return hits


def main():
    rows = []
    kuwashiku = []
    for na in sorted(os.listdir(FX)):
        fxp = os.path.join(FX, na)
        if not os.path.isfile(fxp):
            continue
        for kitei, base in (("旧(disk 321行)", KYUU), ("新(origin/main 339行)", SHIN)):
            out, err, rc = hashiru(base, fxp)
            hits = natta(out, err, na)
            jou = " / ".join(sorted(set(h[0] for h in hits))) if hits else "★一つも鳴らず★"
            rows.append((na, kitei, str(rc), str(len(hits)), jou))
            kuwashiku.append("== %s / 基底=%s / rc=%d ==" % (na, kitei, rc))
            for _j, ln in hits:
                kuwashiku.append("  鳴 " + ln)
            if not hits:
                kuwashiku.append("  ★此の紙に付いては一行も鳴らず★")
            K.kaku(os.path.join(TABA, "raw", "31_run", "%s.%s.err" % (na, "kyuu" if base is KYUU else "shin")), err)
            K.kaku(os.path.join(TABA, "raw", "31_run", "%s.%s.out" % (na, "kyuu" if base is KYUU else "shin")), out)
            K.kaku(os.path.join(TABA, "raw", "31_run", "%s.%s.rc" % (na, "kyuu" if base is KYUU else "shin")), str(rc))
    K.kaku_tsv(os.path.join(TABA, "raw", "30_nikitei_no_nari.tsv"), rows,
               header=("fx 名", "基底", "門の rc", "其の紙に鳴つた行数", "鳴つた條"))
    K.kaku(os.path.join(TABA, "raw", "30_kuwashiku.txt"), "\n".join(kuwashiku))
    K.kaku_tsv(os.path.join(TABA, "raw", "30_nari_no_goi.tsv"),
               [(k, v) for k, v in NARI], header=("逐語の鍵", "當席が当てた條"))
    print("測つた=%d 走" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())

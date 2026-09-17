#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋔-2 ★据ゑ試し★ ―― raw/40_naoshi.diff が ★本当に当たるか★ を仮の木で確かめる器。

紙に diff を書くだけでは「当たる」の證に成らぬ ∴ 仮の木を立てて実際に当て、
出来た物の sha256 が _an/v5_daini_nashi.py と★一致する★事を以て證とする。

★scripts/ には一指も触れぬ★ ―― 仮の木は /private/tmp の下に立て、終ひに毀す。
出 = raw/41_sue_dameshi.txt
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

MOTO = os.path.join(BUNDLE, "_ki", "v5_pr23.py")
SAKI = os.path.join(BUNDLE, "_an", "v5_daini_nashi.py")
DIFF = os.path.join(BUNDLE, "raw", "40_naoshi.diff")
SAKI_PATH = "scripts/checks/karo_mac_manifest_verify.py"
DST = os.path.join(BUNDLE, "raw", "41_sue_dameshi.txt")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    o = ["# ㋔-2 ★据ゑ試し★ ―― raw/40_naoshi.diff を仮の木へ当てる",
         "# 刻 = " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
         "# ★之が言はぬ事★: 当たる事は「直しが正しい」の意ではない。",
         "#   正しさは盤(raw/10_menseki.tsv)と囮(raw/13_otori.tsv)と現物(raw/31_genbutsu.txt)が言ふ。",
         "#   此処で言ふのは『家老が此の diff を git apply -p1 すれば、拙者が測つた物と同じ物が出来る』の一事のみ。",
         ""]
    for nm, p in (("元(PR#23 head の v5)", MOTO), ("先(第二の for を除いた版)", SAKI), ("直し(diff)", DIFF)):
        b = open(p, "rb").read()
        o.append("%s\t%s\tbytes=%d\t行(LF数)=%d\t%s"
                 % (nm, sha(p), len(b), b.count(b"\n"), os.path.relpath(p, BUNDLE)))
    o.append("")

    t = tempfile.mkdtemp(prefix="km117_sue_", dir="/private/tmp")
    try:
        os.makedirs(os.path.join(t, os.path.dirname(SAKI_PATH)))
        shutil.copyfile(MOTO, os.path.join(t, SAKI_PATH))
        rcs = []
        for kotoba in (["git", "init", "-q", "."],
                       ["git", "apply", "--check", "-p1", DIFF],
                       ["git", "apply", "-p1", DIFF]):
            p = subprocess.run(kotoba, cwd=t, capture_output=True, text=True)
            rcs.append((" ".join(kotoba), p.returncode, (p.stderr or "").strip().replace("\n", " / ")))
        o.append("# 仮の木で打つた手 ―― rc は悉く刷る(0 でない物も刷る)")
        for k, rc, err in rcs:
            o.append("  %s\trc=%d\t%s" % (k, rc, err or "-"))
        deta = os.path.join(t, SAKI_PATH)
        a, b = sha(deta), sha(SAKI)
        o += ["",
              "出来た物 = " + a,
              "案(第二無) = " + b,
              "★一致★" if a == b else "★不一致 ―― 紙の diff を信ずるな★"]
        rc = 0 if (a == b and all(r == 0 for _, r, _ in rcs)) else 3
    finally:
        shutil.rmtree(t, ignore_errors=True)
        o += ["", "仮の木 = %s (毀した ―― 残つて居らぬ: %s)" % (t, not os.path.exists(t))]
    kaku(DST, "\n".join(o))
    sys.stdout.write("\n".join(o) + "\n")
    return rc


sys.exit(main())

# -*- coding: utf-8 -*-
"""一行目を焼く ―― ★數は門の出目から抜く(手で打たぬ)★。

  usage: python3 -B driver/99_yaki.py <束の根> <抜く巡> <紙に書く巡>
     例: ... . 01 02   = 01 巡の出目を抜き、「最終巡は 02」と名指して焼く

★焼けば紙の sha が変る ∴ 臺帳を建て直し、02 巡を通し、
  02 の數が焼いた數と一致する事を `driver/98_awase.py` で検める★ ―― 一致せねば焼き直す。
★母數は二つ在る★: 枝の母數(札の割当)と 臺帳の母數(束の file)。混ぜぬ為に両方書く。
"""
import os
import re
import sys


def main():
    root, kara, made = sys.argv[1], sys.argv[2], sys.argv[3]
    g = os.path.join(root, "_gate")
    rc = open(os.path.join(g, kara + "_gate.rc"), encoding="utf-8").read().strip()
    out = open(os.path.join(g, kara + "_gate.out"), encoding="utf-8").read()
    err = open(os.path.join(g, kara + "_gate.err"), encoding="utf-8").read()

    m = re.search(r"一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)", out)
    if not m:
        sys.stderr.write("★條①の行が讀めぬ★ ―― 一字も焼かず止まる\n")
        return 5
    icchi, soui, jittai, yomenu, bogen_taba = m.groups()
    vr = re.search(r"manifest_verify\.py rc=(\d+)", err)
    if not vr:
        sys.stderr.write("★verify の rc が讀めぬ★ ―― 一字も焼かず止まる\n")
        return 5

    eda = sum(1 for i, ln in enumerate(open(os.path.join(root, "raw", "11_bogen.tsv"),
                                            encoding="utf-8")) if i > 0 and ln.strip())

    line = ("門 rc=%s ／ 母數=★本席の割当 枝 %d 本★・★臺帳 %s 行★ ／ "
            "條①=一致 %s(相違 %s・実体無 %s・讀めぬ行 %s・manifest_verify.py rc=%s) ―― "
            "出す前門を `KM_GATE_MANIFEST_BASE=.` 付きで★束の中から★通した(裁 seq322699)。"
            "★最終巡=本行を焼いた後★の出目(`_gate/%s_gate.*`)。"
            % (rc, eda, bogen_taba, icchi, soui, jittai, yomenu, vr.group(1), made))

    p = os.path.join(root, "README.md")
    body = open(p, encoding="utf-8").read().split("\n")
    if "未焼" not in body[0] and not body[0].startswith("門 rc="):
        sys.stderr.write("★一行目が焼き場でない: %s★ ―― 止まる\n" % body[0][:60])
        return 5
    body[0] = line
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(body))
    sys.stderr.write("焼いた: %s\n" % line)
    return 0


sys.exit(main())

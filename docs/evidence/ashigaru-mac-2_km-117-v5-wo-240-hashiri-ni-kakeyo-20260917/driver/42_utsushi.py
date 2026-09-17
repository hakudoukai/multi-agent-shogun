#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""紙の條件⑶ ★写しと其の出所★ ―― 何処から写し、写した後に★己が書き換へた物★は何か。

「km-114 の器を写した」だけでは足らぬ。写した物を弄れば、もはや同じ器ではない。
∴ ①出所の束 ②写した刻の sha(raw/00_utsushi_moto_sha.txt) ③今の sha ④出所に今在る物の sha
  の四つを並べ、★動いた物を名指す★。

出 = raw/42_utsushi.txt
"""
import hashlib
import io
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

MOTO_TABA = os.path.join(os.path.dirname(BUNDLE),
                         "ashigaru-mac-2_km-114-nori-no-jun-wo-kazu-de-kimeyo-20260917")
SHA_HYOU = os.path.join(BUNDLE, "raw", "00_utsushi_moto_sha.txt")
DST = os.path.join(BUNDLE, "raw", "42_utsushi.txt")


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        return "-"


def main():
    utsu = {}
    if os.path.exists(SHA_HYOU):
        for ln in io.open(SHA_HYOU, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if "  " in ln:
                h, p = ln.split("  ", 1)
                utsu[p.strip()] = h.strip()

    o = ["# 紙の條件⑶ ★写しと其の出所★ / 刻 = " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
         "# 出所の束 = " + os.path.relpath(MOTO_TABA, os.path.dirname(BUNDLE)),
         "#   (在る = %s)" % os.path.isdir(MOTO_TABA),
         "# 写した刻の sha = raw/00_utsushi_moto_sha.txt(写した其の場で取つた物)",
         "",
         "\t".join(["器(束内相対)", "出自", "写した刻の sha", "今の sha", "出所に今在る物の sha", "判"])]

    doui = ugoita = jibun = 0
    for nm in sorted(os.listdir(os.path.join(BUNDLE, "driver"))):
        if not nm.endswith(".py"):
            continue
        rel = "driver/" + nm
        ima = sha(os.path.join(BUNDLE, rel))
        moto_ima = sha(os.path.join(MOTO_TABA, rel))
        if rel in utsu:
            shussi = "km-114 からの写し"
            mukashi = utsu[rel]
            if ima == mukashi:
                han = "写しの儘"
                doui += 1
            else:
                han = "★写した後に己が書き換へた★"
                ugoita += 1
        else:
            shussi = "★km-117 で己が書いた★" if moto_ima == "-" else "★km-114 にも同名在り(写し表に無し)★"
            mukashi = "-"
            han = "-"
            jibun += 1
        o.append("\t".join([rel, shussi, mukashi, ima, moto_ima, han]))

    o += ["",
          "写しの儘 = %d 本 / ★写した後に書き換へた★ = %d 本 / km-117 で己が書いた = %d 本 / 計 = %d 本"
          % (doui, ugoita, jibun, doui + ugoita + jibun),
          "",
          "# ★此の数が言はぬ事★",
          "#  ・『写しの儘』は ★中身が同じ★ の意であり、★出所の器が今も正しい★ の意ではない。",
          "#  ・『出所に今在る物の sha』が写した刻と違ふ事も在り得る(km-114 の束は己の物ゆゑ今は動かぬ筈だが、測つて刷る)。",
          "#  ・写し表(00_utsushi_moto_sha.txt)に無い器は ★km-117 で書いた物★ と見做したが、",
          "#    其れは『出所の束に同名が無い』事で確かめて居る(右から二列目が '-' なら真に新規)。"]
    kaku(DST, "\n".join(o))
    sys.stdout.write("\n".join(o) + "\n")
    return 0


sys.exit(main())

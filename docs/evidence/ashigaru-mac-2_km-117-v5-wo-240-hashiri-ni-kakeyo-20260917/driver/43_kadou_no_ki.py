#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★今 門が現に呼ぶ器は何者か★ ―― 盤上の十二本と突き合はせて身元を割る。

的は PR#23 head の v5 だが、★稼働木に据ゑて在る器は別物であり得る★。
「v5 を可とするか」の断は、★今何が走つて居るか★を知らねば据ゑ所を誤る。
∴ scripts/checks/karo_mac_manifest_verify.py の sha256 を取り、盤の十二本＋
   PR#23 blob と ★字面で★ 突き合はせる(讀んで似て居ると言はぬ)。

★scripts/ は讀むだけ★ ―― 一指も書かぬ。
出 = raw/43_kadou_no_ki.txt
"""
import hashlib
import importlib.util
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

KADOU = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_verify.py")
PR23 = "571f338756775acd3e2d73dab5e423e9492d24a2"
DST = os.path.join(BUNDLE, "raw", "43_kadou_no_ki.txt")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    sp = importlib.util.spec_from_file_location("ban", os.path.join(HERE, "10_menseki.py"))
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except SystemExit:
        pass

    o = ["# ★今 門が現に呼ぶ器は何者か★ / 刻 = " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
         "# repo 根 = " + REPO,
         "# 見た物 = scripts/checks/karo_mac_manifest_verify.py(★讀むだけ★)",
         ""]

    kb = open(KADOU, "rb").read()
    kh = sha_bytes(kb)
    o.append("稼働木の器\t%s\tbytes=%d\t行(LF数)=%d" % (kh, len(kb), kb.count(b"\n")))

    p = subprocess.run(["git", "cat-file", "blob",
                        PR23 + ":scripts/checks/karo_mac_manifest_verify.py"],
                       cwd=REPO, capture_output=True)
    o.append("PR#23 head の blob\t%s\tbytes=%d\t行(LF数)=%d\t(git rc=%d)"
             % (sha_bytes(p.stdout), len(p.stdout), p.stdout.count(b"\n"), p.returncode))
    o += ["", "# 盤の十二本との突き合はせ(★sha256 の字面★・讀んだ印象では無い)",
          "\t".join(["盤の名", "sha256", "稼働木と同じか"])]
    atari = []
    for nm, path in m.KI:
        h = sha_bytes(open(path, "rb").read())
        onaji = (h == kh)
        if onaji:
            atari.append(nm)
        o.append("\t".join([nm, h, "★同じ★" if onaji else "-"]))

    o += ["",
          "★稼働木の器の身元★ = " + (" / ".join(atari) if atari else "★盤の十二本の何れとも違ふ(未知の版)★"),
          "★PR#23 の v5 が稼働木に据ゑて在るか★ = %s"
          % ("在る" if kh == sha_bytes(p.stdout) else "★据ゑて居らぬ★"),
          "",
          "# ★此の数が言はぬ事★",
          "#  ・『稼働木の器 = v2_originmain』は ★此の席の此の木★ の話である。",
          "#    他席の木・他の枝・PR の枝が何を持つかは、此処では測つて居らぬ。",
          "#  ・『据ゑて居らぬ』は「据ゑるべきだ」の意ではない ―― 据ゑ所の断は ㋔ に在る。",
          "#  ・刻は上に在る。版は走る間にも動く(拙者は一指も書いて居らぬが、他席は書き得る)。"]
    kaku(DST, "\n".join(o))
    sys.stdout.write("\n".join(o) + "\n")
    return 0


sys.exit(main())

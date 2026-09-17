#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""70_daichou.py ―― 束の臺帳を ★束内相対★ で建て直す(裁 seq322699)。

行を足すのは scripts/checks/karo_mac_manifest_append.py のみ ―― 本器は
⑴歩いて ⑵除く物を宣して ⑶append を呼ぶ、丈である(己で行を書かぬ)。

臺帳の外に置く物(宣):
  ・MANIFEST.txt 己自身(臺帳は己を数へられぬ)
  ・_gate/ 配下の一切(門の控 ―― 下命「門の控は臺帳へ入れるな」)
  ・__pycache__(python が後から生む ―― 歩きを二つに割る)
usage: 70_daichou.py <束の絶対path> <repo根>
"""
import os
import subprocess
import sys

NOZOKU_DIR = ("_gate", "__pycache__")


def main(argv):
    bundle, repo = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    append = os.path.join(repo, "scripts", "checks", "karo_mac_manifest_append.py")
    man = os.path.join(bundle, "MANIFEST.txt")

    noseru, nozoita = [], []
    for root, dirs, files in os.walk(bundle):
        dirs[:] = sorted(d for d in dirs if d not in NOZOKU_DIR)
        for d in sorted(set(os.listdir(root)) - set(dirs) - set(files)):
            pass
        for f in sorted(files):
            p = os.path.relpath(os.path.join(root, f), bundle)
            if p == "MANIFEST.txt":
                nozoita.append(p)
                continue
            noseru.append("./" + p)
    # ★除いた物は歩いて居らぬのではない★ ―― 別歩きで数へて宣する
    gate_n = sum(len(fs) for _, _, fs in os.walk(os.path.join(bundle, "_gate")))

    if os.path.exists(man):
        os.remove(man)                      # 建て直し(追記器ゆゑ古い行が残る)
    rc = subprocess.call([sys.executable, append, "MANIFEST.txt"] + noseru, cwd=bundle)
    gyou = sum(1 for _ in open(man, encoding="utf-8")) if os.path.isfile(man) else -1
    honnbun = sum(1 for l in open(man, encoding="utf-8")
                  if l.strip() and not l.startswith("#")) if os.path.isfile(man) else -1
    print("append rc=%d" % rc)
    print("臺帳 行=%d (内 註=%d / 本文=%d)" % (gyou, gyou - honnbun, honnbun))
    print("載せた=%d 本 / 臺帳自身=%d 本 / _gate 配下=%d 本(★臺帳の外★)" %
          (len(noseru), len(nozoita), gate_n))
    print("束の全 file=%d 本(和の検め: %d + %d + %d)" %
          (len(noseru) + len(nozoita) + gate_n, len(noseru), len(nozoita), gate_n))
    return 0 if (rc == 0 and honnbun == len(noseru)) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

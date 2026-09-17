#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑の★陽性対照★ ―― 「②a = 0 行」が『器が数へられぬ』ではない事を示す。

★束の外★(/private/tmp)に、五方言を一行づつ持つ臺帳を建て、20_hougen.py を★同じ路★で走らせる。
(禁「束に空白を含む名の実体を置くな」順守 ―― 実体は束の外に建て、★建て方★を刻んで再現を保つ)
出目は 束/raw/21_taishou*.txt へ落とす。
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku  # noqa: E402

SHA = "0" * 64
ROWS = [
    ("①隣接", 'path=ichi.txt sha256=%s bytes=3 lines=1' % SHA),
    ("②a食ひ過ぎ", 'path=nia.txt bytes=3 lines=1 sha256=%s' % SHA),
    ("②b空白名", 'path=nib kuuhaku.txt sha256=%s bytes=3 lines=1' % SHA),
    ("③sha無し", 'path=san.txt bytes=3 lines=1'),
    ("④sha先", 'sha256=%s path=yon.txt bytes=3 lines=1' % SHA),
]


def main():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    root = "/private/tmp/km114_taishou_%s_%d" % (stamp, os.getpid())
    os.makedirs(root)
    man = os.path.join(root, "manifest.txt")
    with open(man, "w", encoding="utf-8") as fh:
        fh.write("\n".join(r[1] for r in ROWS) + "\n")
    # ②b の實体も一つ建てる(束の★外★ゆゑ門は鳴らぬ)
    with open(os.path.join(root, "nib kuuhaku.txt"), "w", encoding="utf-8") as fh:
        fh.write("abc\n")
    ki = os.path.join(HERE, "20_hougen.py")
    cp = subprocess.run([sys.executable, "-B", ki, root,
                         os.path.join(BUNDLE, "raw"), "21_taishou"],
                        capture_output=True, text=True)
    tate = ["# ㋑陽性対照 ―― ★建て方★(此れを踏めば何時でも同じ盤が建つ)",
            "# 刻 " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "# 根(★束の外★) = " + root,
            "# mkdir -p <根> ; 下の五行を <根>/manifest.txt へ書き、'nib kuuhaku.txt' を建てる",
            ""]
    for k, r in ROWS:
        tate.append("%s\t%s" % (k, r))
    tate += ["",
             "# 然る後 20_hougen.py <根> <出目dir> 21_taishou を走らす",
             "# 走らせた rc = %d" % cp.returncode,
             "",
             "--- 器の出目(stdout) ---"] + cp.stdout.rstrip("\n").split("\n")
    if cp.stderr.strip():
        tate += ["--- stderr ---"] + cp.stderr.rstrip("\n").split("\n")
    kaku(os.path.join(BUNDLE, "raw", "21_taishou_tateta.txt"), "\n".join(tate))
    print("\n".join(tate))
    return cp.returncode


if __name__ == "__main__":
    sys.exit(main())

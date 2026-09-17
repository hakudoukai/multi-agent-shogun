#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐の前段 ―― ★走る前の姿を控へる★(器は幹束の紙を上書きする作りゆゑ)。

50_ref_toutatsu.py は末尾で己の出目を ★幹束の raw/51_toutatsu.txt へ上書き★ する。
∴ 再走すれば 幹束の当該 file は 頭 0bb92e2 の blob と ★異なる★ 状態に成る。
之は器の仕様であつて當席の逸脱ではないが、★證として前後の sha を残す★。
使ひ方: 10_zenshu.py <頭>
"""
import hashlib
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
kaki = import_module('00_kaki').kaki

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()
TABA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIKI = 'docs/evidence/karo-mac-miki-push-negai-20260917'
MATO = MIKI + '/raw/51_toutatsu.txt'


def g(*a):
    p = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return p.returncode, p.stdout.decode('utf-8', 'surrogateescape')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '根 = ' + ROOT,
         '當席の束 = ' + os.path.relpath(TABA, ROOT),
         '測る先(幹束) = ' + MIKI, '']

    rc_h, s = g('rev-parse', '--verify', sys.argv[1] + '^{commit}')
    if rc_h:
        L.append('★頭が引けぬ★ rc=%d 引数=%s' % (rc_h, sys.argv[1]))
        kaki(os.path.join(TABA, 'raw/10_zenshu.txt'), L)
        return 3
    head = s.strip()
    L += ['頭 = %s (引数=%s・rc=%d)' % (head, sys.argv[1], rc_h), '']

    p = os.path.join(ROOT, MATO)
    body = open(p, 'rb').read()
    rc_b, blob_txt = 0, None
    pb = subprocess.run(['git', '-C', ROOT, 'cat-file', '-p', '%s:%s' % (head, MATO)],
                        capture_output=True)
    rc_b, blob = pb.returncode, pb.stdout

    L += ['★走る前★ %s' % MATO,
          '  disk  sha256=%s bytes=%d' % (sha(body), len(body)),
          '  頭の blob sha256=%s bytes=%d (cat-file rc=%d)' % (sha(blob), len(blob), rc_b),
          '  disk と頭の blob は %s' % ('★同じ★' if body == blob else '★異なる★')]

    # 走る前の本文を當席の束へ控へる(幹束は一指も触れぬ ―― 讀むだけ)
    kaki(os.path.join(TABA, 'raw/11_51toutatsu_zen.txt'),
         body.decode('utf-8', 'surrogateescape'))
    L.append('  控 = raw/11_51toutatsu_zen.txt(正規化を通した写し ∴ sha は原本と一致せぬ)')

    # 幹束が今 disk に何本持つか(器の母數に成る本数を先に知る)
    n = 0
    for dp, dn, fn in os.walk(os.path.join(ROOT, MIKI)):
        dn[:] = [d for d in dn if d != '__pycache__']
        for f in fn:
            fp = os.path.join(dp, f)
            if os.path.isfile(fp) and not os.path.islink(fp):
                n += 1
    L += ['', '走る前の幹束 disk 本数(file・__pycache__除・symlink除) = %d' % n,
          '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/10_zenshu.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

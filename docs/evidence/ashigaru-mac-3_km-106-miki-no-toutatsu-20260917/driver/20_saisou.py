#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐ ―― ★既存の器 50_ref_toutatsu.py を其の儘★ 固定頭で再走し、出目を控へる。

★器は書換へぬ・己の束へ写さぬ★(写せば ROOT/taba_rel の約束が狂ふ)。
本器は ⑴走らせ ⑵stdout/stderr/rc を別々に控へ ⑶走つた後の幹束 raw/51 の sha を測る のみ。
使ひ方: 20_saisou.py <頭>
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
KI = MIKI + '/driver/50_ref_toutatsu.py'
MATO = MIKI + '/raw/51_toutatsu.txt'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    head = sys.argv[1]
    kip = os.path.join(ROOT, KI)
    ki_sha = sha(open(kip, 'rb').read())
    t0 = time.strftime('%Y-%m-%dT%H:%M:%S%z')

    # ★-B で走らす★: 幹束の driver に __pycache__ を生やさぬ(他席の束を汚さぬ)
    p = subprocess.run([sys.executable, '-B', kip, head],
                       capture_output=True, cwd=ROOT)
    t1 = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    out = p.stdout.decode('utf-8', 'surrogateescape')
    err = p.stderr.decode('utf-8', 'surrogateescape')

    kaki(os.path.join(TABA, 'raw/20_saisou.stdout.txt'), out)
    kaki(os.path.join(TABA, 'raw/21_saisou.stderr.txt'), err)
    kaki(os.path.join(TABA, 'raw/22_saisou.rc.txt'),
         ['器 = ' + KI,
          '器の sha256 = ' + ki_sha + ' (★走らせる前後で書換へて居らぬ★)',
          '引数 = ' + head,
          'cwd = ' + ROOT,
          '走り出し = ' + t0, '走り終り = ' + t1,
          'rc = %d' % p.returncode,
          'stdout = %d byte / %d 行' % (len(p.stdout), out.count('\n')),
          'stderr = %d byte / %d 行' % (len(p.stderr), err.count('\n'))])

    # 走つた後 ―― 器が己の出目で上書きした筈
    after = open(os.path.join(ROOT, MATO), 'rb').read()
    pb = subprocess.run(['git', '-C', ROOT, 'cat-file', '-p', '%s:%s' % (head, MATO)],
                        capture_output=True)
    blob = pb.stdout
    ki_sha2 = sha(open(kip, 'rb').read())
    L = ['刻 = ' + t1,
         '★走つた後★ ' + MATO,
         '  disk  sha256=%s bytes=%d' % (sha(after), len(after)),
         '  頭の blob sha256=%s bytes=%d' % (sha(blob), len(blob)),
         '  disk と頭の blob は %s' % ('★同じ★' if after == blob else '★異なる(器が上書きした)★'),
         '',
         '器 %s の sha256' % KI,
         '  走る前 = ' + ki_sha,
         '  走つた後 = ' + ki_sha2,
         '  → %s' % ('★一指も触れて居らぬ★' if ki_sha == ki_sha2 else '★変つた=禁を破つた★'),
         '',
         '★此の上書きが意味する事★',
         '  ・器は末尾 kaki() で己の出目を幹束へ書く作り(50_ref_toutatsu.py L116)。',
         '  ・∴ 再走すれば幹束の当該 file は必ず頭の blob と別に成る ―― ★器の仕様★。',
         '  ・當席は幹束へ commit も restore もせぬ。家老の裁を仰ぐ。']
    kaki(os.path.join(TABA, 'raw/23_gosho.txt'), L)
    print('\n'.join(L))
    print('--- 器の rc = %d ---' % p.returncode)
    return 0


sys.exit(main())

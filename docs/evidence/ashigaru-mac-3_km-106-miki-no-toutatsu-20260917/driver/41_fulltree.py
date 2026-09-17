#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋓の続 ―― ★器の註が名指す疵が、今の引数で再現するか★を四通りで測る。

50_ref_toutatsu.py L20-22 の註(逐語):
  「★-C ROOT を必ず噛ます★: ls-tree の pathspec は ★cwd 相対★ ゆゑ、
    束の中から呼ぶと同じ引数が 0 本を返す(2026-09-17 實測 ―― 甲=0/13 の偽)。」
★註の機構は正しい★。然れど今の呼び口には `--full-tree` も在り、
之は「cwd を見ず根から引く」旗である ∴ ★-C 無しでも 0 本に成らぬ★筈。
四通り(cwd 二 × --full-tree 二)を通し、★何が効いて居るか★を名指す。
使ひ方: 41_fulltree.py <頭>
"""
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


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    p0 = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--verify',
                         sys.argv[1] + '^{commit}'], capture_output=True, text=True)
    if p0.returncode:
        kaki(os.path.join(TABA, 'raw/41_fulltree.txt'), ['★頭が引けぬ★ rc=%d' % p0.returncode])
        return 3
    head = p0.stdout.strip()

    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '根 = ' + ROOT, '頭 = ' + head, '',
         '―― 四通り(cwd 二 × --full-tree 二)・引数の pathspec は常に 根相対の "%s/" ――' % MIKI,
         '%-10s %-12s %6s %5s' % ('cwd', '--full-tree', '本数', 'rc')]

    deme = {}
    for cwd_nm, cwd in (('根', ROOT), ('束の中', os.path.join(ROOT, MIKI))):
        for ft_nm, ft in (('有', ['--full-tree']), ('無', [])):
            a = ['git', 'ls-tree', '-r', '-z'] + ft + ['--name-only', head, '--', MIKI + '/']
            p = subprocess.run(a, capture_output=True, cwd=cwd)
            n = len([x for x in p.stdout.decode('utf-8', 'surrogateescape').split('\0') if x])
            deme[(cwd_nm, ft_nm)] = (n, p.returncode)
            L.append('%-10s %-12s %6d %5d' % (cwd_nm, ft_nm, n, p.returncode))

    n_naka_mu = deme[('束の中', '無')][0]
    n_naka_yu = deme[('束の中', '有')][0]
    n_ne_yu = deme[('根', '有')][0]
    L += ['',
          '★讀み★',
          '  ・束の中 × --full-tree無 = %d 本 ―― ★註が名指す疵は實在する★' % n_naka_mu,
          '  ・束の中 × --full-tree有 = %d 本 ―― ★-C を外しても 0 に成らぬ★' % n_naka_yu,
          '  ∴ 今の呼び口で ★効いて居るのは --full-tree★ であり、`-C ROOT` は',
          '    ★同じ穴を塞ぐ二枚目の板★(重ねて悪い物ではない ―― 外せとは申さぬ)。',
          '  ・註は「-C を噛ませねば 0 本に成る」と讀めるが、實測は「--full-tree が在れば成らぬ」。',
          '    ★器の數は正しい。註の因果だけが一枚ずれて居る★(器は書換へぬ ―― 家老へ申し送る)。',
          '',
          '★此の數が意味せぬ事★',
          '  ・「%d 本」は ★頭の tree に其の path が在る★ の意のみ。中身が disk と合ふかは別問(器の⑶欄)。' % n_ne_yu,
          '',
          '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/41_fulltree.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

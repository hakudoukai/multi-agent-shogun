#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋓ ―― ★己の器への対照★(陽性・陰性を同じ路に乗せ、rc と數を並べて刷る)。

何故要るか: `--contains` は ★在らぬ commit に rc=129 で空を返す★。
∴ 「0 本」を見た時、其れが「含む ref が無い」のか「頭が引けなんだ」のか、
數だけでは ★見分けられぬ★。rc を並べて初めて數が名乗れる。
併せて ls-tree の pathspec が cwd 相対である疵(束の中から呼ぶと 0 本)を、
`-C <根>` を噛ませた上で ★既知の一本が丁度一度出る★ 事で検める。
使ひ方: 40_taisho.py <頭>
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
NAI = 'dead' * 10          # 40字 hex ―― ★在らぬ筈の頭★(使ふ前に不在を證する)


def g(*a):
    p = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return p.returncode, p.stdout.decode('utf-8', 'surrogateescape')


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    rc_h, s = g('rev-parse', '--verify', sys.argv[1] + '^{commit}')
    if rc_h:
        kaki(os.path.join(TABA, 'raw/40_taisho.txt'),
             ['★頭が引けぬ★ rc=%d' % rc_h])
        return 3
    head = s.strip()
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '根 = ' + ROOT, '',
         '―― 甲 --contains の二対照(★數と rc を並べる★) ――',
         '  註 %d 字 hex を陰性に使ふ: %s' % (len(NAI), NAI)]

    # ★使ふ前に「在らぬ」を證する★(陰性対照が実は在つたら対照に成らぬ)
    rc_e, _ = g('cat-file', '-e', NAI)
    rc_rv, _ = g('rev-parse', '--verify', NAI + '^{commit}')
    L.append('  陰性の不在の證: cat-file -e rc=%d / rev-parse --verify rc=%d → %s'
             % (rc_e, rc_rv,
                '★在らぬ(対照に使へる)★' if (rc_e != 0 and rc_rv != 0)
                else '★在つた=陰性対照に成らぬ★'))
    if rc_e == 0 or rc_rv == 0:
        kaki(os.path.join(TABA, 'raw/40_taisho.txt'), L)
        return 4

    for nm, h in (('陽性(在る頭 %s)' % head[:12], head), ('陰性(在らぬ頭)', NAI)):
        for pat in ('refs/heads', 'refs/remotes'):
            rc_r, out = g('for-each-ref', '--format=%(refname)', '--contains', h, pat)
            n = len([x for x in out.split('\n') if x])
            L.append('  %-26s %-13s = %d 本 (rc=%d) %s'
                     % (nm, pat, n, rc_r,
                        '' if rc_r == 0 else '★rc≠0 ∴ 此の 0 は「無い」ではなく「測れぬ」★'))

    L += ['',
          '  ★此の二行が示す事★: 陽性 refs/heads=1(rc=0) と 陰性 refs/heads=0(rc=129) は',
          '    ★共に「0 か 1」の數を出すが、rc が別★である。rc を落として數だけ読めば、',
          '    「在らぬ頭を問うた」を「含む ref が無い」と読み違へる。',
          '',
          '―― 乙 ls-tree の根の対照(pathspec は cwd 相対) ――']

    # 既知の一本が丁度一度出るか
    shirushi = 'MANIFEST.txt'
    rc_t, tree = g('ls-tree', '-r', '-z', '--full-tree', '--name-only', head, '--', MIKI + '/')
    names = [x for x in tree.split('\0') if x]
    kazu = names.count(MIKI + '/' + shirushi)
    L += ['  `git -C <根> ls-tree -r -z --full-tree --name-only <頭> -- %s/`' % MIKI,
          '    出目 = %d 本 (rc=%d) ―― 既知の一本 %s の出現回数 = %d 回 → %s'
          % (len(names), rc_t, shirushi, kazu,
             '★丁度一度=器は生きて居る★' if kazu == 1 else '★一度でない=根を外して居る★')]

    # 根を外した時どう見えるか(束の中から呼ぶ ―― ★禁を破らぬ形で疵を実演★)
    p = subprocess.run(['git', 'ls-tree', '-r', '-z', '--full-tree', '--name-only',
                        head, '--', MIKI + '/'],
                       capture_output=True, cwd=os.path.join(ROOT, MIKI))
    n2 = len([x for x in p.stdout.decode('utf-8', 'surrogateescape').split('\0') if x])
    L += ['  同じ引数を ★束の中(cwd=%s)★ から呼ぶと = %d 本 (rc=%d)' % (MIKI, n2, p.returncode),
          '    → %s' % ('★0 本=疵が再現した(∴ -C <根> は飾りではない)★' if n2 == 0
                        else '★0 本に成らなんだ(%d 本)★' % n2)]

    L += ['', '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/40_taisho.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

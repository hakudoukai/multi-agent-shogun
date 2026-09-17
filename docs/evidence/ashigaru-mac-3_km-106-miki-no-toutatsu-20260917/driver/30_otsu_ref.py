#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑ ―― ★乙(ref の到達)を二欄で測る★。

★二つは別物である★:
  A欄 for-each-ref refs/remotes --contains <頭>
      = ★手許の refs/remotes を見るだけ★。fetch せねば古びる。
        ∴ 「0 本」は「上流に無い」ではなく「★手許が知らぬ★」の意でしかない。
  B欄 git ls-remote origin
      = ★上流へ問ひ合はせる★。今 上流が何を持つかの實測。
        ∴ sha の一致までは見るが、「merge された」までは言はぬ。
註: --contains は在らぬ commit に rc=129 で空を返す ∴ 數と rc を必ず並べる(㋓で対照)。
使ひ方: 30_otsu_ref.py <頭>
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
EDA = 'karo-mac/km-gate-kou-otsu-20260917'


def g(*a):
    p = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return p.returncode, p.stdout.decode('utf-8', 'surrogateescape')


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    rc_h, s = g('rev-parse', '--verify', sys.argv[1] + '^{commit}')
    if rc_h:
        kaki(os.path.join(TABA, 'raw/30_otsu.txt'),
             ['★頭が引けぬ★ rc=%d 引数=%s' % (rc_h, sys.argv[1])])
        return 3
    head = s.strip()
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '根 = ' + ROOT,
         '頭 = %s' % head,
         '本札の枝 = ' + EDA + ' (PR#20)',
         '', '―― A欄 手許 for-each-ref(★fetch せねば古びる★) ――']

    for nm, pat in (('refs/heads', 'refs/heads'), ('refs/remotes', 'refs/remotes')):
        rc_r, out = g('for-each-ref', '--format=%(refname)', '--contains', head, pat)
        names = [x for x in out.split('\n') if x]
        L.append('  A %-14s --contains 頭 = %d 本 (rc=%d) %s'
                 % (nm, len(names), rc_r, ' '.join(names) or '―'))

    rc_f, fh = 1, ''
    p = os.path.join(ROOT, '.git/FETCH_HEAD')
    if os.path.exists(p):
        rc_f = 0
        fh = time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(os.path.getmtime(p)))
    L.append('  A 手許が最後に上流を聞いた刻(.git/FETCH_HEAD の mtime) = %s (在=%s)'
             % (fh or '―', 'rc=0' if rc_f == 0 else '無'))

    L += ['', '―― B欄 上流 ls-remote(★今 上流へ問ふ★) ――']
    rc_l, out = g('ls-remote', 'origin')
    rows = [x for x in out.split('\n') if x]
    L.append('  B ls-remote origin 全 ref = %d 本 (rc=%d)' % (len(rows), rc_l))
    if rc_l != 0:
        L.append('  ★上流へ問へなんだ ―― 數を名乗る資格無★')
        kaki(os.path.join(TABA, 'raw/30_otsu.txt'), L)
        return 4

    atari = [r for r in rows if r.split('\t')[-1] == 'refs/heads/' + EDA]
    L.append('  B 本札の枝 refs/heads/%s = %d 本' % (EDA, len(atari)))
    for r in atari:
        sh = r.split('\t')[0]
        L.append('     上流の sha = %s ―― 頭と %s'
                 % (sh, '★一致★' if sh == head else '★不一致(上流=' + sh[:12] + ')★'))

    # 上流の ref の内、頭を含む物は幾つか ―― ls-remote は含有を答へぬ ∴ 手許に在る物のみ照合
    L += ['',
          '  ★B欄が答へられぬ事★: ls-remote は ref 名と sha を返すのみで、',
          '    「其の ref が頭を★含む★か」は答へぬ(含有は手許の object を辿らねば判らぬ)。',
          '    ∴ A欄=含有の數 / B欄=上流の存否 ―― ★同じ「到達」の語で別の物を数へて居る★。']

    L += ['', '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/30_otsu.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

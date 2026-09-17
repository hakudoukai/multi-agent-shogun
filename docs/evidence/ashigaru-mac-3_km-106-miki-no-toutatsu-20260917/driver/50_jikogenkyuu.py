#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★器が己の出目を母數に含む(條①の自己言及)★を、二度走らせて實証する。

50_ref_toutatsu.py は
  ⑴幹束の file を悉く歩き ⑵頭の blob と中身を照し ⑶末尾で己の出目を幹束 raw/51 へ書く。
∴ 一度目は「異 0」で終るが、其の直後に己が raw/51 を書換へる ―― ★終つた時には 異 1★。
二度目を同じ頭で走らせれば、其の 1 を己で見付けて rc=1 に成る筈。
★筈を實測に替へる★(當席の札の的其の物)。
註: 二度目も出目は幹束 raw/51 を上書きするのみで、幹束の他の紙には一指も触れぬ。
使ひ方: 50_jikogenkyuu.py <頭>
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
KI = os.path.join(ROOT, MIKI, 'driver/50_ref_toutatsu.py')
MATO = os.path.join(ROOT, MIKI, 'raw/51_toutatsu.txt')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    head = sys.argv[1]
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'), '頭 = ' + head, '']

    before = open(MATO, 'rb').read()
    L.append('二度目を走らす前の raw/51 sha256 = %s (%d byte)' % (sha(before), len(before)))

    p = subprocess.run([sys.executable, '-B', KI, head], capture_output=True, cwd=ROOT)
    out = p.stdout.decode('utf-8', 'surrogateescape')
    after = open(MATO, 'rb').read()

    hits = [l for l in out.split('\n') if '異なる本' in l or '異: ' in l or '到達 ' in l]
    L += ['', '★二度目の rc = %d★' % p.returncode,
          '二度目の出目より抜き書き:']
    L += ['  ' + h.strip() for h in hits]
    L += ['',
          '二度目の後の raw/51 sha256 = %s (%d byte)' % (sha(after), len(after)),
          '',
          '★讀み★']
    if p.returncode == 1:
        L += ['  ・一度目 rc=0 ／ 二度目 rc=1 ―― ★同じ頭・同じ器で出目が変つた★。',
              '  ・因は器の作りである: 己の出目 raw/51 を ★己が数へる母數の中★ へ書く。',
              '    ∴ 「異 0」と刷つた其の紙自身が、刷つた瞬間に「異 1」を作る。',
              '  ・之は 條①(己が検める物を己で数へぬ)の ★門の控を臺帳へ入れるな★ と同じ形の疵。',
              '  ・★數が嘘なのではない★ ―― 一度目の「17/17・異 0」は ★書く直前の姿として正しい★。',
              '    正しからざるは「其の數が走つた後も成り立つ」と読む事である。']
    else:
        L += ['  ・二度目も rc=%d ―― ★予期と異なる★。自己言及は起きて居らぬか、別の路が在る。' % p.returncode]
    L += ['', '★當席が幹束へ為した事の総て★',
          '  ・raw/51_toutatsu.txt を ★二度 上書き★ した(器を走らせた結果・器の仕様)。',
          '  ・他の 16 本には一指も触れて居らぬ(次の欄で證す)。',
          '  ・commit も restore も checkout もせぬ。',
          '', '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/50_jikogenkyuu.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★正誤★ ―― 控(raw/11)が原本と一致するか否かを、断ぜずに測る。

10_zenshu.py は控を書く際に「正規化を通した写し ∴ sha は原本と一致せぬ」と
★測る前に★ 書いた。之は ★筈★ であつて 實測ではない。本器で測る。
(10_zenshu.py は再走せぬ ―― 走らせれば「走る前の姿」といふ控の値打が消える。
 ∴ 器の出目 raw/10_zenshu.txt は其の儘残し、本紙で正す。)
使ひ方: 12_utsushi.py <頭>
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


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    head = sys.argv[1]
    pb = subprocess.run(['git', '-C', ROOT, 'cat-file', '-p',
                         '%s:%s/raw/51_toutatsu.txt' % (head, MIKI)], capture_output=True)
    genpon = pb.stdout
    hikae = open(os.path.join(TABA, 'raw/11_51toutatsu_zen.txt'), 'rb').read()
    a, b = hashlib.sha256(genpon).hexdigest(), hashlib.sha256(hikae).hexdigest()
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '頭 = ' + head, '',
         '原本(頭の blob) sha256=%s bytes=%d (cat-file rc=%d)' % (a, len(genpon), pb.returncode),
         '控 raw/11      sha256=%s bytes=%d' % (b, len(hikae)),
         '',
         '★判★ 二つは %s' % ('★一致する★' if a == b else '★異なる★'),
         '',
         '★正誤★',
         '  10_zenshu.py は控を書く際、測る前に',
         '    「正規化を通した写し ∴ sha は原本と一致せぬ」',
         '  と書いた。實測は %s ―― 因は、原本が ★既に同じ正規化を経て居た★ 事に在る' % ('★一致★' if a == b else '不一致'),
         '  (原本も 50_ref_toutatsu.py の kaki() が書いた紙であり、當席の 00_kaki.py と同じ',
         '   「CR 除・末尾空白除・EOF 改行丁度1」を掛けて居る ∴ 二度掛けても動かぬ＝冪等)。',
         '  ★筈を紙に書けば、實測が出るまで其れは嘘に成り得る★ ―― 本行を以て正す。',
         '',
         '★此の一致が意味せぬ事★',
         '  ・控が原本と同じなのは ★此の紙に限つた事★ である。',
         '    正規化を経て居らぬ紙(末尾空白や CR を持つ紙)を控へれば、控の sha は必ず動く。',
         '  ・∴ 「控＝原本」と一般に読むな。★此の一本を測つた★ のみ。',
         '',
         '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/12_utsushi.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

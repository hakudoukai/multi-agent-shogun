#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★母數が 16 から 17 へ増えた事を、名で説明する★。

札の期待は「16/16」であつたが、實測の母數は 17 であつた。
★期待に寄せず★、⑴前走(15:52・頭 68b6e07b)の 16 本 ⑵今(頭 0bb92e2)の 17 本 を
名で並べ、増えた一本と、不到達 4 本が到達へ転じた事を ★名指しで★ 示す。
前走の 16 本は、當席が控へた raw/11_51toutatsu_zen.txt からは ★全名が取れぬ★
(其の紙は不到達 4 本の名しか列べて居らぬ) ∴ 前走の頭 68b6e07b の tree と
今の tree の差で語る ―― ★紙に無い物は紙から取らぬ★。
使ひ方: 70_uchiwake.py <今の頭> <前走の頭>
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
# 前走の紙が己で列べた不到達 4 本(逐語)
ZEN_FUTODATSU = ['driver/50_ref_toutatsu.py', 'raw/50_atama_head68b6e07b.txt',
                 'raw/51_toutatsu.txt', 'tsuiroku_saiso_20260917.md']


def tree(head):
    p = subprocess.run(['git', '-C', ROOT, 'ls-tree', '-r', '-z', '--full-tree',
                        '--name-only', head, '--', MIKI + '/'], capture_output=True)
    return p.returncode, sorted(x[len(MIKI) + 1:] for x in
                                p.stdout.decode('utf-8', 'surrogateescape').split('\0') if x)


def main():
    if len(sys.argv) != 3:
        sys.stderr.write(__doc__)
        return 2
    ima_arg, zen_arg = sys.argv[1], sys.argv[2]
    rcs = []
    heads = []
    for a in (ima_arg, zen_arg):
        p = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--verify', a + '^{commit}'],
                           capture_output=True, text=True)
        rcs.append(p.returncode)
        heads.append(p.stdout.strip())
    if any(rcs):
        kaki(os.path.join(TABA, 'raw/70_uchiwake.txt'),
             ['★頭が引けぬ★ rc=%s' % rcs])
        return 3
    ima, zen = heads
    rc_i, ti = tree(ima)
    rc_z, tz = tree(zen)

    disk = []
    for dp, dn, fn in os.walk(os.path.join(ROOT, MIKI)):
        dn[:] = [d for d in dn if d != '__pycache__']
        for f in sorted(fn):
            fp = os.path.join(dp, f)
            if os.path.isfile(fp) and not os.path.islink(fp):
                disk.append(os.path.relpath(fp, os.path.join(ROOT, MIKI)))
    disk.sort()

    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '今の頭 = %s (tree %d 本・rc=%d)' % (ima, len(ti), rc_i),
         '前走の頭 = %s (tree %d 本・rc=%d)' % (zen, len(tz), rc_z),
         'disk(今) = %d 本' % len(disk), '',
         '―― 甲 今の tree 17 本の全名(★前走の tree に在つたか★を併記) ――']
    for i, n in enumerate(ti, 1):
        sirushi = '' if n in set(tz) else '  ★前走の tree に無し★'
        zf = '  ←前走の紙が「不到達」と名指した一本' if n in ZEN_FUTODATSU else ''
        L.append('  %2d %s%s%s' % (i, n, sirushi, zf))

    fueta = [n for n in ti if n not in set(tz)]
    L += ['', '―― 乙 増減 ――',
          '  前走 tree = %d 本 / 今 tree = %d 本 ―― ★増 %d 本★' % (len(tz), len(ti), len(ti) - len(tz))]
    for n in fueta:
        L.append('    増: ' + n)
    kieta = [n for n in tz if n not in set(ti)]
    L.append('  ★消えた本 = %d★' % len(kieta))
    for n in kieta:
        L.append('    消: ' + n)

    L += ['', '―― 丙 前走の紙が名指した「不到達 4 本」は今どうか ――']
    for n in ZEN_FUTODATSU:
        L.append('  %-34s 今の tree に %s / disk に %s'
                 % (n, '在' if n in set(ti) else '★無★',
                    '在' if n in set(disk) else '★無★'))

    L += ['', '―― 丁 札の期待 16/16 と實測 17/17 の差 ――',
          '  ★母數が違ふ★: 札は前走の disk 16 本を念頭に「16/16」と書かれた。',
          '  然れど前走(15:52)の後・commit(15:54)の前に 門の控が一本生れ、',
          '  其れも 0bb92e2 に収められた ∴ 今の母數は 17 である。',
          '  ★到達率は 16/16 でも 17/17 でも「悉く」である ―― 分母が動いただけで、穴は塞がつて居る。★',
          '  ★然れど「16/16 であつた」とは書かぬ。實測は 17/17 である。★',
          '', '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/70_uchiwake.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())

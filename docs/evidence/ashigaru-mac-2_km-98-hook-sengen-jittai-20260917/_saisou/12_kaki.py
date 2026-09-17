#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_kaki.py <歩き根> ―― 生捕りの出目の末尾を揃へる(門 條②③④ の前捌き)。
  ・各行末尾の 空白/TAB/CR を落とす ・EOF の改行は丁度一つ ・0byte は作らぬ
★歩き根は argv から取り、且つ `_saisou/` の下に在る事を assert する★ ―― 提出済の `_raw/` を
一字も触らぬ為である(裁: 出した紙は直さぬ)。己(12_kaki.py)と `.first` と __pycache__ は歩かぬ。
"""
import os, sys

def main():
    if len(sys.argv) != 2:
        sys.stderr.write('usage: 12_kaki.py <歩き根>\n'); return 2
    root = os.path.abspath(sys.argv[1])
    if os.path.basename(root) != '_saisou':
        sys.stderr.write('★歩き根が _saisou に非ず(拒む)★ %s\n' % root); return 3
    SELF = os.path.abspath(__file__)
    tgt = []
    for d, ds, fs in os.walk(root):
        ds[:] = sorted(x for x in ds if x != '__pycache__')
        for f in sorted(fs):
            p = os.path.join(d, f)
            if p == SELF or f.endswith('.first'):
                continue
            tgt.append(p)
    naoshi = zero = 0
    for p in sorted(tgt):
        b = open(p, 'rb').read()
        if not b:
            print('★0byte★(觸らぬ):', os.path.relpath(p, root)); zero += 1; continue
        lines = [ln.rstrip(' \t\r') for ln in b.decode('utf-8').split('\n')]
        while lines and lines[-1] == '':
            lines.pop()
        out = ('\n'.join(lines) + '\n').encode('utf-8')
        if out != b:
            fst = p + '.first'
            if not os.path.exists(fst):
                open(fst, 'wb').write(b)
            open(p, 'wb').write(out)
            naoshi += 1
            print('直し:', os.path.relpath(p, root), len(b), '->', len(out))
    print('歩いた file 数=%d / 直した=%d / 0byte=%d' % (len(tgt), naoshi, zero))
    print('★直し 0 は「歩かなかつた」の意に非ず ―― 歩いた上で疵が無かつたの意である。★')
    return 0

sys.exit(main())

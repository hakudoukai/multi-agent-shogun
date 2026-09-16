# -*- coding: utf-8 -*-
"""15 shell の `>` で直取りした 10_kuumoji.{stdout,err,rc} を kaki に通す(作法⑸ 空は「空である旨の一行」・0byte を残さぬ)。前後の bytes を記す。"""
import os, sys, time
B = sys.argv[1]; RAW = B + '/raw'; sys.path.insert(0, RAW); import kaki as K
out = [f'# 15 kaki 通し / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
for n in ('10_kuumoji.stdout', '10_kuumoji.err', '10_kuumoji.rc'):
    p = f'{RAW}/{n}'; b0 = os.path.getsize(p); K.kaku(p, open(p, encoding='utf-8').read()); b1 = os.path.getsize(p)
    out.append(f'{n}: {b0} → {b1} bytes' + (' (0byte → 空である旨の一行)' if b0 == 0 else ''))
K.kaku(RAW + '/15_normalize.txt', '\n'.join(out)); print('\n'.join(out))

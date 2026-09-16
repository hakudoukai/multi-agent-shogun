# -*- coding: utf-8 -*-
"""15 shell の `>` で直取りした raw/05_run.stdout を kaki に通す(59 が EOF 改行 2 で鳴つた ―― raw 取りは正規化を素通りする)。前後の bytes を記す。"""
import os, sys, time
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
out = [f'# 15 kaki 通し / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
for n in ('05_run.stdout',):
    p = f'{RAW}/{n}'; b0 = os.path.getsize(p); K.kaku(p, open(p, encoding='utf-8').read()); out.append(f'{n}: {b0} → {os.path.getsize(p)} bytes(59 の鳴り: EOF 改行が丁度 1 でない → 直した)')
K.kaku(RAW + '/15_normalize.txt', '\n'.join(out)); print('\n'.join(out))

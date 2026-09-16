# -*- coding: utf-8 -*-
"""raw の text を門の條②③④に合はせて整へる(各行の末空白を落とし・EOF 改行を丁度1本)。
倒れた走(.first)は ★触れぬ★(作法⑺ ―― 其の儘が證である)。原本は <名>.first へ退避する。
"""
import os, sys, shutil
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
n = 0
for r, ds, ns in os.walk('raw'):
    for x in sorted(ns):
        p = os.path.join(r, x)
        if p.endswith('.first'):
            print('触れぬ(⑺ 倒れた走の控): ' + p); continue
        s = open(p, encoding='utf-8').read()
        t = chr(10).join(l.rstrip() for l in s.split(chr(10))).rstrip(chr(10)) + chr(10)
        if t != s:
            if not os.path.exists(p + '.first'):
                shutil.copyfile(p, p + '.first')
            open(p, 'w', encoding='utf-8').write(t); n += 1
            print('整へた(原本→.first): ' + p)
        else:
            print('元より整ふ: ' + p)
print('整へた紙=%d' % n)

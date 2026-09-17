# -*- coding: utf-8 -*-
"""raw の text を門の條②③④に合はせて整へる(各行の末空白を落とし・EOF 改行を丁度1本)。
★空は 0byte でなく「空である旨の一行」★(裁 seq310228⑶) ―― 0byte の紙は一行を書き入れる。
倒れた走(.first/.second/.third)は ★触れぬ★(作法⑺ ―― 其の儘が證である)。原本は <名>.first へ退避。
"""
import os, shutil
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOMERU = ('.first', '.second', '.third')
n = k = 0
for r, ds, ns in os.walk('raw'):
    for x in sorted(ns):
        p = os.path.join(r, x)
        if p.endswith(TOMERU):
            print('触れぬ(⑺ 倒れた走の控): ' + p); continue
        if os.path.getsize(p) == 0:
            open(p, 'w', encoding='utf-8').write('★空である旨★ 本紙に一字も無し(裁 seq310228⑶)\n')
            k += 1; print('★0byte → 空である旨の一行★: ' + p); continue
        s = open(p, encoding='utf-8').read()
        t = chr(10).join(l.rstrip() for l in s.split(chr(10))).rstrip(chr(10)) + chr(10)
        if t != s:
            if not os.path.exists(p + '.first'):
                shutil.copyfile(p, p + '.first')
            open(p, 'w', encoding='utf-8').write(t); n += 1
            print('整へた(原本→.first): ' + p)
        else:
            print('元より整ふ: ' + p)
print('整へた紙=%d / 空を一行にした紙=%d' % (n, k))

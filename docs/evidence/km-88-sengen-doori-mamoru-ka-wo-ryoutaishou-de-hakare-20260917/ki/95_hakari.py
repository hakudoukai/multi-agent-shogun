# -*- coding: utf-8 -*-
"""便の字を ★送る前に★ 測る(300字の條)。字は python の len(=符号位置)で数へる。
   macOS の awk length() は byte を返す ―― 用ゐぬ。"""
import io, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read().rstrip('\n')
n = len(s)
print('字=%d / byte=%d / 條=300 / %s' % (n, len(s.encode('utf-8')),
      '★通(送つてよい)★' if n <= 300 else '★超 %d 字 ―― 送るな★' % (n - 300)))
sys.exit(0 if n <= 300 else 1)

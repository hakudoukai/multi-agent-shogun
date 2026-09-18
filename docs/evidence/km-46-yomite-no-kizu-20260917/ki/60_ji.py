#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60_ji.py -- ★便の胴の字数を測る器★。使ひ方: 60_ji.py <file>  (無ければ stdin)
# 數ふ形: ⑴字(codepoint 総数・改行を含む) ⑵字(改行を除く) ⑶行 ⑷bytes(utf-8)
# ★單位を名に焼く★(裁: burn the unit into the column name)
import sys, io
if len(sys.argv) > 1:
    s = io.open(sys.argv[1], encoding='utf-8', errors='strict').read()
    src = sys.argv[1]
else:
    s = io.open(sys.stdin.fileno(), encoding='utf-8', errors='strict').read()
    src = '(stdin)'
cp_all = len(s)
cp_nonl = len(s.replace(u'\n', u''))
gyou = s.count(u'\n') + (0 if (s == u'' or s.endswith(u'\n')) else 1)
by = len(s.encode('utf-8'))
sys.stdout.write(u'%s 字(改行込)=%d 字(改行除)=%d 行=%d bytes=%d\n'
                 % (src, cp_all, cp_nonl, gyou, by))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 59_kaki.py -- ★紙・生の一切を此の器を通して書く★(門 條②③④ を書く側で先に潰す)。
# 使ひ方: 59_kaki.py <出し先>   (本文は stdin)
# 為す事: ⑴各行の末の空白(全角空白/NBSP/TAB 含む)を削る ⑵CR を削る ⑶EOF の改行を ★丁度一つ★ にする
#         ⑷空の流れも ★一行★ として書かぬ(0byte のまま)―― 裁 seq320321 の空の形に合はせる
import sys, io
if len(sys.argv) < 2:
    sys.stderr.write(u'★測れぬ: 出し先を argv で渡せ★\n'); sys.exit(2)
s = io.open(sys.stdin.fileno(), encoding='utf-8', errors='strict').read()
s = s.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
MATSUBI = u' \t　 ​  \x0c\x7f'
ls = [l.rstrip(MATSUBI) for l in s.split(u'\n')]
while ls and ls[-1] == u'':
    ls.pop()
body = u'\n'.join(ls)
if body:
    body += u'\n'
with io.open(sys.argv[1], 'w', encoding='utf-8', newline='') as fh:
    fh.write(body)
b = body.encode('utf-8')
sys.stderr.write(u'★書いた %s bytes=%d 行=%d 末尾改行=%d★\n'
                 % (sys.argv[1], len(b), body.count(u'\n'), 1 if body.endswith(u'\n') else 0))

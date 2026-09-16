#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 10_kaki.py(第49弾 90_kaki.py の写し ―― ★頭の一行の名のみ改めた。他は一字も変へて居らぬ★) -- 本弾の紙・生の一切を此の器を通して書く。
#
# ★第46弾の 59_kaki.py との違ひ(本弾の主題其の物)★
#   59_kaki.py L12-16 は ★空の流れを 0byte のまま書いた★ ―― 頭註に
#   「裁 seq320321 の空の形に合はせる」と書いて居たが、★seq320321 に其の條は無い★。
#   實在する條は ★裁 seq310228⑶★ ―― 逐語「空を空のまま残せ」と「0byte は條④で鳴る」は
#   併存する。★空の結果は 0byte の file ではなく『空であつた』と述べる一行である★。
#   ∴ 本器は空の流れへ ★『空である旨の一行』★ を書く(器名・刻・何が空か を含む)。
#
# 使ひ方: 70_kaki.py <出し先> [--nushi <器名>]   (本文は stdin)
# 為す事: ⑴各行末の空白(全角空白/NBSP/TAB 等)を削る ⑵CR を削る
#         ⑶EOF の改行を ★丁度一つ★ にする ⑷★空なら一行を書く(0byte にせぬ)★
import sys, io, os, time

if len(sys.argv) < 2:
    sys.stderr.write(u'★測れぬ: 出し先を argv で渡せ★\n'); sys.exit(2)
dest = sys.argv[1]
nushi = u'(名乗り無し)'
if '--nushi' in sys.argv:
    i = sys.argv.index('--nushi')
    if i + 1 < len(sys.argv):
        nushi = sys.argv[i + 1].decode('utf-8') if isinstance(sys.argv[i + 1], bytes) else sys.argv[i + 1]

s = io.open(sys.stdin.fileno(), encoding='utf-8', errors='strict').read()
s = s.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
MATSUBI = u' \t　 ​  \x0c\x7f'
ls = [l.rstrip(MATSUBI) for l in s.split(u'\n')]
while ls and ls[-1] == u'':
    ls.pop()
body = u'\n'.join(ls)
kara = 0
if body:
    body += u'\n'
else:
    # ★裁 seq310228⑶★ 空は 0byte にせず「空である旨の一行」を書く。
    kara = 1
    body = (u'★空であつた★ 器=%s 出し先=%s 刻=%s ―― '
            u'流れが一字も無かつた事を述べる一行である(0byte にせぬ・裁 seq310228⑶)。\n'
            % (nushi, os.path.basename(dest),
               time.strftime('%Y-%m-%dT%H:%M:%S%z')))

with io.open(dest, 'w', encoding='utf-8', newline='') as fh:
    fh.write(body)
b = body.encode('utf-8')
sys.stderr.write(u'★書いた %s bytes=%d 行=%d 末尾改行=%d 空=%d★\n'
                 % (dest, len(b), body.count(u'\n'),
                    1 if body.endswith(u'\n') else 0, kara))

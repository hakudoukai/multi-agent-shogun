#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""書き器 ―― 捕へた流れを束の作法へ揃へる。
(a) 行末の空白/TAB/CR を剥ぐ (b) 末尾の改行を丁度一つ (c) LF のみ
(d) ★空(0byte)は「空であつた」の一行を書く★
★正規化の前の寸法を必ず記す★(事後に導出せず実測)
使ひ方: 10_kaki.py <出先>   (胴は stdin)
"""
import sys, os
def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: 10_kaki.py <out>\n"); return 2
    b = sys.stdin.buffer.read()
    pre_bytes = len(b)
    s = b.decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
    lines = [ln.rstrip(' \t') for ln in s.split('\n')]
    while lines and lines[-1] == '': lines.pop()
    body = ('\n'.join(lines) + '\n') if lines else '★空であつた(0byte)★\n'
    with open(sys.argv[1], 'w', encoding='utf-8', newline='\n') as f: f.write(body)
    sys.stderr.write("kaki out=%s 正規化前=%dbyte 後=%dbyte 行=%d\n"
                     % (sys.argv[1], pre_bytes, os.path.getsize(sys.argv[1]), len(lines) if lines else 1))
    return 0
sys.exit(main())

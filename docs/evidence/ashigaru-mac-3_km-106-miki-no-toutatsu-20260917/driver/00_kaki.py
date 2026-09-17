#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生の出目を紙へ落とす唯一の口(正規化を通す)。

★何故 器を挟むか★: `>` で受けた生は 末尾空白・CR・EOF 改行の数 が器任せに成り、
出す前門の 條②③④ で鳴る。∴ 書く口を一本にし、其處で悉く正した上で置く。
  ・CR(\r) を除く / 各行の末尾空白を除く / EOF 改行を ★丁度1本★ に
  ・★空の流れも一行として書く★(0 byte の紙は 條④ で鳴る ―― km 既知)
使ひ方: from kaki import kaki  /  00_kaki.py <紙> <<< "本文"
"""
import sys


def kaki(path, body):
    """body は str か str の list。正規化して path へ書く。返り値=書いた byte 数。"""
    if isinstance(body, (list, tuple)):
        lines = list(body)
    else:
        lines = body.split('\n')
    lines = [l.replace('\r', '').rstrip() for l in lines]
    while lines and lines[-1] == '':
        lines.pop()
    if not lines:                      # ★空の流れも一行★(0 byte を作らぬ)
        lines = ['(空 ―― 出目 0 行)']
    s = '\n'.join(lines) + '\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    return len(s.encode('utf-8'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        sys.exit(2)
    n = kaki(sys.argv[1], sys.stdin.read())
    sys.stderr.write('書いた = %s (%d byte)\n' % (sys.argv[1], n))

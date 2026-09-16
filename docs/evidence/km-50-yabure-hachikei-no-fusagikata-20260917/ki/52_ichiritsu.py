#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 52_ichiritsu.py ―― ★位置律の前提を測る。★
#   51_taisho.py の chuunyuu は「末の非空行は門自身の結語である」を前提に、
#   ★字面でなく位置で★ 己の結語を除く。其の前提が全門票で成つて居るかを此処で測る。
#   ―― 前提を測らぬ器は、前提を騙られる。
import glob, io, sys

KETSU = (u'★出す前 門 通。出してよい。★', u'★出す前 門が落ちた。出すな。★',
         u'★門 五條 通。押してよい。★', u'★門 が落ちた。押すな。★')

def main():
    w = sys.stdout.write
    w(u'★位置律の前提★ ―― 「末の非空行 = 門自身の結語」を 生器/単/合 の全門票で測る\n')
    w(u'(此の數が 51_taisho.py の chuunyuu が字面でなく位置で除く根拠である)\n\n')
    ps = sorted(glob.glob('.nama/hyou51_*.txt'))
    n = sue = ichi = 0; hazure = []
    for p in ps:
        ls = [l for l in io.open(p, encoding='utf-8').read().split(u'\n') if l.strip()]
        if not ls or ls[0].startswith(u'★空であつた★'):
            continue                      # 案を当てぬ走(陰性の「単」)は門票を持たぬ
        n += 1
        a = ls[-1].strip() in KETSU
        b = sum(1 for l in ls if l.strip() in KETSU) == 1
        sue += 1 if a else 0; ichi += 1 if b else 0
        if not (a and b): hazure.append((p, a, b))
    w(u'母數(門票 file)      = %d\n' % n)
    w(u'末の非空行が結語      = %d  ★之が位置律の前提★\n' % sue)
    w(u'結語が ちやうど一度   = %d\n' % ichi)
    w(u'両方満つ              = %d\n\n' % (n - len(hazure)))
    if hazure:
        w(u'★外れ★ ―― 結語が二度。之は ★前提の破れでは無く 注入の検出★ である\n')
        w(u'  (gate4 の門票へ dasumae の結語が現れた = 其の門が刷る筈の無い句)\n')
        for p, a, b in hazure:
            w(u'  %s  末=結語:%s / 一度:%s\n' % (p, u'○' if a else u'×', u'○' if b else u'×'))
    else:
        w(u'★外れは無い(空である旨の一行)★\n')
    return 0 if sue == n else 1           # ★前提が崩れたら鳴る★

if __name__ == '__main__':
    sys.exit(main())

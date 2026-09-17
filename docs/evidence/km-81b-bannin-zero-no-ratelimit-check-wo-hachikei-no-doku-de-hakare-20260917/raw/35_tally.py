# -*- coding: utf-8 -*-
"""35 集計(第77弾 km-81b)―― 30_doku.tsv を口×倒れ先で数へ(紙の數は此処から引く・手で写さぬ)、両対照の○×を口ごとに器が言ふ。
八形(未設定/空文字/空白半/空白全/20桁/負数/域外2/01/+1/先頭改行)= 10 値を「八形」の母數とし、補(abc/None/?/101/1e3/xx/EN/LC_ALL=C)は別に数へる。"""
import sys, time, re
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
rows = [l.split('\t') for l in open(D + '/raw/30_doku.tsv', encoding='utf-8').read().split('\n')[1:] if l.strip()]
HACHI = ('未設定', '空文字', '空白(半角)', '空白(全角 U+3000)', '20桁(2^63超)', '負数 -5', '域外の十進 2', '域外の十進 01', '域外の十進 +1', '先頭改行付き ␊1')
def kind(f):
    s = f[8]
    if '陰性対照' in s: return '陰性'
    if '陽性対照' in s: return '陽性'
    if '鳴つて止まる' in s: return '鳴つて止まる(rc≠0・stderr 有)'
    if '黙つて止まる' in s: return '黙つて止まる(rc≠0・stderr 0)'
    if '黙つて別枝' in s: return '黙つて別枝(rc0・stderr 0・枝≠正常)'
    if '刷つて別枝' in s: return '刷つて別枝(rc0・stderr 有・枝≠正常)'
    if '毒が見えぬ' in s: return '黙つて通る(rc0・stderr 0・枝=正常)'
    if '黙つて通る' in s: return '刷つて通る(rc0・stderr 有・枝=正常)'
    return '其の他'
out = [f'# 35 集計 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 30_doku.tsv の行 {len(rows)}(見出し除く)']
tbl = ['口\t八形の母數\t黙つて通る(枝=正常・毒が見えぬ)\t刷つて通る(stderr 有・枝=正常)\t黙つて別枝\t刷つて別枝\t鳴つて止まる\t黙つて止まる\t陽性対照 ○×\t陰性対照 ○×\t補の走\t補の内 止まる']
grand = {}
for k in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'):
    rs = [r for r in rows if r[0] == k]; hachi = [r for r in rs if r[1] in HACHI]; ho = [r for r in rs if r[1].startswith('補') or (k == 'P7' and not r[1].startswith(('正常', '陽性')))]
    c = {}
    for r in hachi: c[kind(r)] = c.get(kind(r), 0) + 1; grand[kind(r)] = grand.get(kind(r), 0) + 1
    pos = [r for r in rs if r[1].startswith('陽性')]; neg = [r for r in rs if r[1].startswith('正常')]
    pos_ok = pos and all('陽性対照・枝が変はる' in r[8] for r in pos); neg_ok = neg and all('陰性対照' in r[8] for r in neg)
    g = lambda s: c.get(s, 0)
    tbl.append('\t'.join([k, str(len(hachi)), str(g('黙つて通る(rc0・stderr 0・枝=正常)')), str(g('刷つて通る(rc0・stderr 有・枝=正常)')), str(g('黙つて別枝(rc0・stderr 0・枝≠正常)')), str(g('刷つて別枝(rc0・stderr 有・枝≠正常)')), str(g('鳴つて止まる(rc≠0・stderr 有)')), str(g('黙つて止まる(rc≠0・stderr 0)')), ('○' if pos_ok else '★×★') + f'({len(pos)})', ('○' if neg_ok else '★×★') + f'({len(neg)})', str(len(ho)), str(sum(1 for r in ho if r[3] != '0'))]))
    assert sum(c.values()) == len(hachi), k
out.append(f'八形(10 値)× P1-P6 の 6 口= {sum(1 for r in rows if r[1] in HACHI)} 走(P7 は argv ゆゑ八形の外・8 走)。全口の八形 合計: ' + ' / '.join(f'{kk} {vv}' for kk, vv in sorted(grand.items())))
q = [r for r in rows if r[0] in ('P3', 'P4') and r[1] in HACHI]; qs = {}
for r in q: qs[kind(r)] = qs.get(kind(r), 0) + 1
out.append(f'★枠の口(P3 5h + P4 7d)の八形 {len(q)} 走★: ' + ' / '.join(f'{kk} {vv}' for kk, vv in sorted(qs.items())))
out.append('八形の定義(母數 10 値): ' + ' / '.join(HACHI) + '。補は八形に数へぬ(abc・None・?・101・1e3・xx・EN・LC_ALL=C・argv の形)。')
out.append('此の表が意味せぬ事: 「黙つて通る」は害の有無を言はぬ(P1 空文字→? は宣どおり、P2 の 0 倒しは番人 L419-420 の設計)。害の向きは紙で口ごとに讀む。')
K.kaku(D + '/raw/35_tally.txt', '\n'.join(out)); K.kaku(D + '/raw/35_tally.tsv', '\n'.join(tbl)); print('\n'.join(out)); print('\n'.join(tbl))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""87_hikaku.py ―― 提出済 raw/(前) と 再走 raw2/(後) の數を並べる。手で数へぬ・器の出目を讀む。
用法: python3 -B 87_hikaku.py <raw(前)dir> <raw2(後)dir>   → stdout に TSV(項 前 後 差)。讀めぬ物は 測れぬ と書く。
註: 差 = 後−前。差の符号は「後で増えた」であつて「此の枝が変へた」では★ない★(歩くのは disk・他席の束も混じる)。"""
import os, re, sys

mae, ato = sys.argv[1], sys.argv[2]


def yomu(d, name):
    p = os.path.join(d, name)
    if not os.path.isfile(p):
        return None
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()


def hiku(text, pat):
    if text is None:
        return None
    m = re.search(pat, text)
    return int(m.group(1)) if m else None


rows = []


def kumu(label, a, b):
    if a is None or b is None:
        rows.append((label, '測れぬ' if a is None else a, '測れぬ' if b is None else b, '測れぬ'))
    else:
        rows.append((label, a, b, b - a))


# 10: R1-R4
for r in ('R1', 'R2', 'R3', 'R4'):
    t1, t2 = yomu(mae, '10_aruki_summary.txt'), yomu(ato, '10_aruki_summary.txt')
    kumu(f'10 {r} files', hiku(t1, rf'{r} hits=\d+ of files=(\d+)'), hiku(t2, rf'{r} hits=\d+ of files=(\d+)'))
    kumu(f'10 {r} hits', hiku(t1, rf'{r} hits=(\d+)'), hiku(t2, rf'{r} hits=(\d+)'))
    r1, r2 = yomu(mae, '10_aruki_rc.txt'), yomu(ato, '10_aruki_rc.txt')
    kumu(f'10 {r} grep_rc', hiku(r1, rf'{r}_grep_rc=(\d+)'), hiku(r2, rf'{r}_grep_rc=(\d+)'))
kumu('10 R1 陽性対照(門 自身 行)', hiku(yomu(mae, '10_R1_positive_control.txt'), r'(\d+)'), hiku(yomu(ato, '10_R1_positive_control.txt'), r'(\d+)'))
# 15: R5
t1, t2 = yomu(mae, '15_aruki_R5_summary.txt'), yomu(ato, '15_aruki_R5_summary.txt')
kumu('15 R5 files', hiku(t1, r'files=(\d+)'), hiku(t2, r'files=(\d+)'))
kumu('15 R5 hits', hiku(t1, r'hits=(\d+)'), hiku(t2, r'hits=(\d+)'))
# 20: ps
t1, t2 = yomu(mae, '20_ps_hits.txt'), yomu(ato, '20_ps_hits.txt')
kumu('20 ps 母數', hiku(t1, r'母數=(\d+)'), hiku(t2, r'母數=(\d+)'))
kumu('20 ps hits', hiku(t1, r'hits=(\d+)'), hiku(t2, r'hits=(\d+)'))
# 30: 逐語行
t1, t2 = yomu(mae, '30_gyou_all.txt'), yomu(ato, '30_gyou_all.txt')
kumu('30 gyou files(###)', None if t1 is None else t1.count('\n### ') + t1.startswith('### '), None if t2 is None else t2.count('\n### ') + t2.startswith('### '))
kumu('30 gyou lines', None if t1 is None else t1.count('\n'), None if t2 is None else t2.count('\n'))
kumu('30 gyou ★実体無★', None if t1 is None else t1.count('★実体無★'), None if t2 is None else t2.count('★実体無★'))
# 35: 第二歩き
t1, t2 = yomu(mae, '35_summary.txt'), yomu(ato, '35_summary.txt')
for k in ('files', 'any', 'first', 'tei_kouho'):
    kumu(f'35 {k}', hiku(t1, rf'{k}=(\d+)'), hiku(t2, rf'{k}=(\d+)'))
# 40: 箱の人口
t1, t2 = yomu(mae, '40_hako_jinkou.tsv'), yomu(ato, '40_hako_jinkou.tsv')
kumu('40 箱数', hiku(t1, r'箱数=(\d+)'), hiku(t2, r'箱数=(\d+)'))
kumu('40 生pane数', hiku(t1, r'生pane数=(\d+)'), hiku(t2, r'生pane数=(\d+)'))
for kind in ('正名(pane有)', '異名:未知(pane無)', '異名:読点/空白'):
    kumu(f'40 {kind}', None if t1 is None else sum(1 for l in t1.splitlines() if l.startswith(kind + '\t')),
         None if t2 is None else sum(1 for l in t2.splitlines() if l.startswith(kind + '\t')))
# 50: 門の実走
t1, t2 = yomu(mae, '50_summary.txt'), yomu(ato, '50_summary.txt')
for tag in ('1_touten', '2_kuuhaku', '3_michi', '4_pane', '5_hako_nomi', '6_allow', '7_shibako'):
    kumu(f'50 {tag} rc', hiku(t1, rf'(?m)^{tag}\trc=(\d+)'), hiku(t2, rf'(?m)^{tag}\trc=(\d+)'))
kumu('50 箱の名列 本数(前)', hiku(t1, r'前=[0-9a-f]+\((\d+)本\)'), hiku(t2, r'前=[0-9a-f]+\((\d+)本\)'))
def ji(text, pat):
    m = re.search(pat, text) if text is not None else None
    return m.group(1) if m else '測れぬ'


rows.append(('50 箱の名列 同(前後)', ji(t1, r'同=(\w+)'), ji(t2, r'同=(\w+)'), '-'))
rows.append(('50 門sha16', ji(t1, r'門sha=([0-9a-f]+)'), ji(t2, r'門sha=([0-9a-f]+)'), '-'))
# 60: 分類
for r in ('R1', 'R2', 'R3', 'R4', 'R5'):
    t1, t2 = yomu(mae, f'60_bunrui_{r}.txt'), yomu(ato, f'60_bunrui_{r}.txt')
    for k in ('合計', '器', '控', '紙', '試'):
        kumu(f'60 {r} {k}', hiku(t1, rf'{k}=(\d+)'), hiku(t2, rf'{k}=(\d+)'))

print('項\t前(raw)\t後(raw2)\t差(後−前)')
for r in rows:
    print('\t'.join(str(x) for x in r))
n_mez = sum(1 for r in rows if '測れぬ' in (str(r[1]), str(r[2])))
print(f'# 行={len(rows)} 測れぬ={n_mez} 前={mae} 後={ato}')

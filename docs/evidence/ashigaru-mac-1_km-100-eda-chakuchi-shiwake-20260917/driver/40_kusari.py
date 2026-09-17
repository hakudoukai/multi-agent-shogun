#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""40_kusari.py ―― ㋕ 鎖: 割当 X ごとに、60 tip の内の真の祖先を rev-list --count の小さい順に列べる(=鎖)。
用法: python3 -B driver/40_kusari.py <REPO> raw/40_hakari.tsv raw/20_anc_pairs_60x59.tsv raw/03_karo_fuyou15_utsushi.tsv <out.tsv>
"""
import sys, subprocess, collections
REPO, HAKARI, ANC, FUYOU, OUT = sys.argv[1:6]
def git(*a):
    p = subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True); return p.stdout.strip()
fuyou = {l.split('\t')[1] for l in open(FUYOU, encoding='utf-8').read().split('\n')[1:] if l}
anc = collections.defaultdict(list)
for l in open(ANC, encoding='utf-8').read().split('\n')[1:]:
    if not l: continue
    b, bs, x, xs, rc, same = l.split('\t')
    if same == '0': anc[x].append((b, bs))
hdr = open(HAKARI, encoding='utf-8').readline().rstrip('\n').split('\t')
rows = ['X_branch\tanc_n\tkusari(祖先を近い順・count=rev-list B..X・†=家老の不要15)']
for line in open(HAKARI, encoding='utf-8').read().split('\n')[1:]:
    if not line: continue
    c = dict(zip(hdr, line.split('\t')))
    lst = []
    for b, bs in anc.get(c['branch'], []):
        lst.append((int(git('rev-list', '--count', f'{bs}..{c["sha40"]}')), b))
    lst.sort()
    rows.append('\t'.join([c['branch'], str(len(lst)), ' → '.join(f'{b}{"†" if b in fuyou else ""}({n})' for n, b in lst)]))
open(OUT, 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print(f'rows={len(rows)-1}')

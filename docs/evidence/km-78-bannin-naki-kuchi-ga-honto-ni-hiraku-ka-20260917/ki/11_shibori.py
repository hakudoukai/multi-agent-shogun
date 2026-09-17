# -*- coding: utf-8 -*-
"""11 母數の絞り(第56弾 km-78)―― 廣(398口/68file)から ★生きて走る器★ へ落とす。
★除外は数へて刷る★(memory 76「declared exclusion still counts in the 母數」)。
絞① .bak* / .new.* / .orig / .pre* の控 file
絞② .claude/worktrees/**(他席の worktree の写し ―― 走らぬ)
絞③ scripts/archive/**(退役)
絞④ tests/**(試験具)
絞⑤ 非 .sh(.md 等 ―― 走らぬ)
残り= ★生器★。之を本弾の母數とする。"""
import os, re, sys, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
rows = [l.split('\t') for l in open(D + '/raw/10_census.tsv', encoding='utf-8').read().splitlines()[1:]]

def why(f):
    b = os.path.basename(f)
    if re.search(r'\.(bak|orig|pre)[^/]*$', b) or '.new.' in b: return '絞①控'
    if f.startswith('.claude/worktrees/'): return '絞②worktree'
    if '/archive/' in f: return '絞③退役'
    if f.startswith('tests/') or '/tests/' in f: return '絞④試験具'
    if not f.endswith('.sh'): return '絞⑤非sh'
    return ''

cnt = collections.Counter(); live = []
for r in rows:
    w = why(r[0])
    cnt[w or '★生器★'] += 1
    (live if not w else []).append(r) if not w else None
live = [r for r in rows if not why(r[0])]
K.kaku_tsv(D + '/raw/11_live.tsv', live, header=['file', 'line', 'name', 'default', 'bannin', 'genbun'])
lf = sorted({r[0] for r in live})
out = ['# 11 母數の絞り / 廣= %d 口 / %d file' % (len(rows), len({r[0] for r in rows}))]
for k in ['絞①控', '絞②worktree', '絞③退役', '絞④試験具', '絞⑤非sh']:
    out.append('  %s で落ちた口= %d' % (k, cnt[k]))
out.append('★生器の口= %d 口 / %d file★' % (len(live), len(lf)))
out.append('  番人在= %d / ★番人無= %d★' % (sum(1 for r in live if r[4] == '番人在'), sum(1 for r in live if r[4] != '番人在')))
for f in lf:
    sub = [r for r in live if r[0] == f]
    ng = [r for r in sub if r[4] != '番人在']
    out.append('  %-58s 口%2d 番人無%2d  %s' % (f, len(sub), len(ng), ' '.join(sorted({r[2] for r in ng}))))
out.append('# ★之は家老の 22口/8file(定義丁)と一致せぬ。定義丁の本文を當席は持たぬゆゑ、当てに行かず★')
out.append('# ★己の定義を宣して己の數を出す。丁との差は 20 の kawashimo(比較器)で埋める。★')
K.kaku(D + '/raw/11_shibori.txt', '\n'.join(out))
print('\n'.join(out))

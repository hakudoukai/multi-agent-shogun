#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-180 census: 根 <tree>/docs/evidence 直下(深さ1)の束ごとに
   disk(find -type f 相当・os.walk・symlink は辿らぬ)/ tracked(git ls-files)/ 差 /
   porcelain 行数 / others / others+ignored / deleted を数へる。読むのみ・書かぬ。
   usage: 01_census.py <tree_root> <out_tsv>"""
import os, subprocess, sys, time
tree, out = sys.argv[1], sys.argv[2]
root = os.path.join(tree, 'docs', 'evidence')
def git(*a):
    p = subprocess.run(['git', '-C', tree] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout
def nlines(s): return 0 if s == '' else s.count('\n') + (0 if s.endswith('\n') else 1)
rows = []; t0 = time.strftime('%Y-%m-%dT%H:%M:%S%z')
bundles = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and not os.path.islink(os.path.join(root, d)))
for b in bundles:
    rel = os.path.join('docs', 'evidence', b)
    disk = 0; maxdepth = 0
    for dp, dn, fn in os.walk(os.path.join(root, b)):
        depth = os.path.relpath(dp, os.path.join(root, b)).count(os.sep) + 1
        maxdepth = max(maxdepth, depth); disk += len(fn)
    rc1, o1 = git('ls-files', '--', rel); tracked = nlines(o1)
    rc2, o2 = git('status', '--porcelain', '--', rel); porc = nlines(o2)
    rc3, o3 = git('ls-files', '--others', '--exclude-standard', '--', rel); others = nlines(o3)
    rc4, o4 = git('ls-files', '--others', '--ignored', '--exclude-standard', '--', rel); ignored = nlines(o4)
    rc5, o5 = git('ls-files', '--deleted', '--', rel); deleted = nlines(o5)
    rows.append((b, disk, tracked, disk - tracked, porc, others, ignored, deleted, maxdepth, f'{rc1}{rc2}{rc3}{rc4}{rc5}'))
with open(out, 'w', encoding='utf-8') as f:
    f.write(f'# koku={t0} tree={tree} root=docs/evidence depth=1(束)・束内は全深さ walk・symlink 不辿・bundles={len(bundles)}\n')
    f.write('bundle\tdisk\ttracked\tdiff\tporcelain\tothers\tothers_ignored\tdeleted\tmaxdepth\trcs\n')
    for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
    pos = [r for r in rows if r[3] > 0]; neg = [r for r in rows if r[3] < 0]; zero = [r for r in rows if r[3] == 0]
    f.write(f'# 束数={len(rows)} 差>0={len(pos)} 束(本数計 {sum(r[3] for r in pos)}) 差<0={len(neg)} 束(本数計 {sum(r[3] for r in neg)}) 差=0={len(zero)} 束\n')
    f.write(f'# porcelain>0 の束={sum(1 for r in rows if r[4]>0)} / 差>0 且つ porcelain==0(盲)={sum(1 for r in pos if r[4]==0)} 束\n')
    f.write(f'# 代器 (others+others_ignored)==diff の束={sum(1 for r in rows if r[5]+r[6]==r[3])} / ≠ の束={sum(1 for r in rows if r[5]+r[6]!=r[3])}\n')
    f.write(f'# rc: 全 git 呼びの rc 連結が 00000 でない束={sum(1 for r in rows if r[9]!="00000")}\n')
print(open(out, encoding='utf-8').read().splitlines()[0]); print('\n'.join(open(out, encoding='utf-8').read().splitlines()[-4:]))

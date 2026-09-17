#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30_naiyou_kasanari.py ―― 乙の拠り所: X の own diff(B_min..X)の file が、60 の他 tip Y の樹に ★同一 blob★ で在るか。
commit の祖先関係とは別の「内容の重なり」。ls-tree のみ(読取)。
用法: python3 -B driver/30_naiyou_kasanari.py <REPO> raw/40_hakari.tsv raw/02_karo_60tips_utsushi.tsv raw/ <out.tsv>
"""
import sys, subprocess, os
REPO, HAKARI, TIPS, RAW, OUT = sys.argv[1:6]
def git(*a):
    p = subprocess.run(['git', '-c', 'core.quotePath=false', '-C', REPO, *a], capture_output=True, text=True); return p.returncode, p.stdout
tips = [l.split('\t') for l in open(TIPS, encoding='utf-8').read().split('\n')[1:] if l]
def blobs(sha, paths):
    if not paths: return {}
    _, out = git('ls-tree', '-r', '-z', sha, '--', *paths)   # -z: splitlines は U+2028 を割る
    m = {}
    for l in [x for x in out.split('\0') if x]:
        meta, path = l.split('\t', 1); m[path] = meta.split()[2]
    return m
hdr = open(HAKARI, encoding='utf-8').readline().rstrip('\n').split('\t')
rows = ['X_branch\town_n\tY_max_branch\tY_max_sha12\tsame_blob_n\tY_full_n(全fileを同一blobで抱へるY数)\tY_full_list']
for line in open(HAKARI, encoding='utf-8').read().split('\n')[1:]:
    if not line: continue
    c = dict(zip(hdr, line.split('\t')))
    f = os.path.join(RAW, f'31_d2_own_{c["branch"].replace("/","__")}.txt')
    own = [x for x in open(f, encoding='utf-8').read().split('\n') if x] if os.path.exists(f) else []   # split('\n'): 控は -z 由来の生の名
    bx = blobs(c['sha40'], own)
    best = (None, None, -1); full = []
    for sy, ny in tips:
        if ny == c['branch']: continue
        by = blobs(sy, own)
        same = sum(1 for p in own if p in by and by[p] == bx.get(p))
        if same > best[2]: best = (ny, sy, same)
        if own and same == len(own): full.append(ny)
    rows.append('\t'.join([c['branch'], str(len(own)), best[0] or '-', (best[1] or '-')[:12], str(best[2]), str(len(full)), ','.join(full)]))
open(OUT, 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print(f'rows={len(rows)-1}')

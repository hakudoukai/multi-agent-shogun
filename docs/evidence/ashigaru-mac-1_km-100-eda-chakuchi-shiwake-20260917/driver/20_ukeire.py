#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_ukeire.py ―― ㋔ 受入条件の材料を tip の樹から ★ls-tree/show のみ★ で読む(checkout せず)。
紙=dir 直下の *.md(README.md 又は <席>_<名>.md) / 臺帳=名に manifest を含む file / 門控=名に gate|mon を含む *.rc|*.txt|*.log
用法: python3 -B driver/20_ukeire.py <REPO> raw/40_hakari.tsv raw/71_ukeire.tsv
"""
import sys, subprocess, os, re
REPO, HAKARI, OUT = sys.argv[1:4]
def git(*a):
    p = subprocess.run(['git', '-c', 'core.quotePath=false', '-C', REPO, *a], capture_output=True, text=True); return p.returncode, p.stdout
rows = ['branch\tsha12\tevidence_dir\tkami_n\tkami\tdaichou_n\tdaichou\tdaichou_hougen\tmon_rc_files_n\tmon_rc\tfile_n']
hdr = open(HAKARI, encoding='utf-8').readline().rstrip('\n').split('\t')
for line in open(HAKARI, encoding='utf-8').read().split('\n')[1:]:
    if not line: continue
    c = dict(zip(hdr, line.split('\t')))
    for d in [x for x in c['d2_evidence_dirs'].split(',') if x]:
        base = f'docs/evidence/{d}'
        _, lt = git('ls-tree', '-r', '-z', '--name-only', c['sha40'], '--', base); files = [x for x in lt.split('\0') if x]  # -z: splitlines は U+2028 を割る
        rel = [f[len(base)+1:] for f in files]
        kami = [f for f in rel if f.endswith('.md') and '/' not in f]
        dai = [f for f in rel if 'manifest' in f.lower() and '/' not in f]
        hou = []
        for m in dai:
            _, t = git('show', f'{c["sha40"]}:{base}/{m}')
            ps = [l.split()[0][5:] for l in t.split('\n') if l.startswith('path=')]
            if not ps: hou.append(f'{m}:path行無'); continue
            hou.append(f'{m}:' + ('束外(docs/ 又は / 始まり)' if any(p.startswith(('docs/', '/')) for p in ps) else '束内相対') + f'({len(ps)}行)')
        mon = [f for f in rel if re.search(r'(gate|mon|hashiri)', f, re.I) and f.endswith('.rc')]
        rcs = []
        for f in mon:
            _, v = git('show', f'{c["sha40"]}:{base}/{f}'); rcs.append(f'{f}={v.strip()}')
        rows.append('\t'.join([c['branch'], c['sha40'][:12], d, str(len(kami)), ';'.join(kami), str(len(dai)), ';'.join(dai), ';'.join(hou), str(len(mon)), ';'.join(rcs), str(len(files))]))
open(OUT, 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print(f'rows={len(rows)-1}')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-182: repo 中で `git status --porcelain` / `git status -s` / `--short` を呼ぶ行を歩き出す。
   根 = 樹の頂(argv1)。除外 dir = .git node_modules .venv __pycache__ queue(13.2GB) docs/evidence(束)。
   python の os.walk(ugrep/.gitignore に依らぬ)。読むのみ。
   出力(TSV): kind  path  line  ignored_flag  verbatim
   kind = sh(.sh/.bash/.bats/拡張子無しで shebang bash)/ py / md / yaml / other"""
import os, re, sys, time
root = sys.argv[1]; out = sys.argv[2]
SKIP = {'.git', 'node_modules', '.venv', '__pycache__', 'queue', 'evidence'}
rx = re.compile(r'git\s+(?:-C\s+\S+\s+)?status\b[^\n|;&]*?(--porcelain(?:=v[12])?|(?<![\w-])-s(?![\w-])|--short)')
# 第二の網(km-182 疵⑵で足す): python/list 形 ―― "status", "--porcelain" が引用符で並ぶ形(git status の字面を持たぬ)
rx2 = re.compile(r'[\'"]status[\'"]\s*,\s*[\'"](--porcelain(?:=v[12])?|-s|--short)[\'"]')
def kind(p, first):
    e = os.path.splitext(p)[1].lower()
    if e in ('.sh', '.bash', '.bats'): return 'sh'
    if e == '.py': return 'py'
    if e == '.md': return 'md'
    if e in ('.yaml', '.yml'): return 'yaml'
    if e == '' and first.startswith('#!') and ('bash' in first or 'sh' in first): return 'sh'
    if e == '' and first.startswith('#!') and 'python' in first: return 'py'
    return 'other'
files = 0; maxdepth = 0; rows = []
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in SKIP]
    depth = os.path.relpath(dp, root).count(os.sep) + (0 if dp == root else 1)
    maxdepth = max(maxdepth, depth)
    for f in fn:
        p = os.path.join(dp, f); files += 1
        try:
            b = open(p, 'rb').read()
        except Exception as e:
            print('UNREADABLE', p, e, file=sys.stderr); continue
        if b'\x00' in b[:4096]: continue
        s = b.decode('utf-8', 'replace'); lines = s.split('\n')
        k = kind(p, lines[0] if lines else '')
        for i, l in enumerate(lines, 1):
            if 'status' in l and (rx.search(l) or rx2.search(l)):
                rows.append((k, os.path.relpath(p, root), i, 'ignored' if '--ignored' in l else '-', l.strip()[:200]))
with open(out, 'w', encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} root={root} skip={sorted(SKIP)} files_walked={files} max_depth={maxdepth} rc=0\n")
    f.write('kind\tpath\tline\tignored\tverbatim\n')
    for r in sorted(rows): f.write('\t'.join(str(x) for x in r) + '\n')
from collections import Counter
c = Counter(r[0] for r in rows); cf = Counter((r[0], r[1]) for r in rows)
print(f'files_walked={files} max_depth={maxdepth} hits={len(rows)} rows / {len(cf)} files')
for k in ('sh', 'py', 'md', 'yaml', 'other'): print(f'  {k}: {c.get(k,0)} 行 / {len([1 for kk,_ in cf if kk==k])} file')
print('  --ignored 併記の行:', sum(1 for r in rows if r[3]=='ignored'))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-187: `2>&1` を「数を取る流れ」へ繋ぐ箇所を歩き出す。読むのみ。
   数を取る流れ = 同じ行(pipe 鎖)の後ろに grep -c / wc -l / wc -c / sort -u / 変数代入 $( … 2>&1 … ) が在る。
   usage: 01_walk_stderr_into_count.py <root> <out_tsv> [skip_dirs...]"""
import os,re,sys,time
root,out=sys.argv[1],sys.argv[2]
SKIP=set(sys.argv[3:]) or {'.git','node_modules','.venv','__pycache__','queue','evidence'}
R_COUNT=re.compile(r'2>&1[^\n]*\|\s*(grep\s+-[a-zA-Z]*c|wc\s+-[lc]|sort\s+-u|uniq\s+-c|awk[^|]*END|tail\s+-n?\s*1|head)')
R_VAR=re.compile(r'(\w+)=\s*"?\$\((?:[^()]|\([^()]*\))*2>&1(?:[^()]|\([^()]*\))*\)')
R_PY=re.compile(r'stderr\s*=\s*subprocess\.STDOUT|2>&1')
def kind(p,first):
    e=os.path.splitext(p)[1].lower()
    if e=='.bats': return 'bats'
    if e in('.sh','.bash') or (e=='' and first.startswith('#!') and 'sh' in first): return 'sh'
    if e=='.py' or (e=='' and first.startswith('#!') and 'python' in first): return 'py'
    if e=='.md': return 'md'
    return 'other'
rows=[];files=0;maxd=0
for dp,dn,fn in os.walk(root):
    dn[:]=[d for d in dn if d not in SKIP]
    depth=0 if dp==root else os.path.relpath(dp,root).count(os.sep)+1; maxd=max(maxd,depth)
    for f in fn:
        p=os.path.join(dp,f); files+=1
        if '.bak' in f: continue
        try: b=open(p,'rb').read()
        except Exception: continue
        if b'\x00' in b[:4096]: continue
        ls=b.decode('utf-8','replace').split('\n'); k=kind(p,ls[0] if ls else '')
        if k in('md','other'): continue
        for i,l in enumerate(ls,1):
            if '2>&1' not in l and 'subprocess.STDOUT' not in l: continue
            form=[]
            if R_COUNT.search(l): form.append('count_pipe')
            if R_VAR.search(l): form.append('var_capture')
            if k=='py' and 'subprocess.STDOUT' in l: form.append('py_stderr_merged')
            rows.append((k,os.path.relpath(p,root),i,'+'.join(form) or 'other_2>&1',l.strip()[:180]))
with open(out,'w',encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} root={root} skip={sorted(SKIP)} files={files} max_depth={maxd} rc=0\n")
    f.write('kind\tpath\tline\tform\tverbatim\n')
    for r in sorted(rows): f.write('\t'.join(map(str,r))+'\n')
from collections import Counter
c=Counter(r[3] for r in rows); ck=Counter((r[0]) for r in rows if r[3]!='other_2>&1')
print(f'files={files} depth={maxd} 2>&1 行={len(rows)} / 数へる流れ(count_pipe/var_capture/py_merged)={sum(1 for r in rows if r[3]!="other_2>&1")}')
print('  形:', dict(c)); print('  kind(数へる流れ):', dict(ck), '/ file:', len(set(r[1] for r in rows if r[3]!='other_2>&1')))

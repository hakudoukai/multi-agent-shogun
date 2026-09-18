#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-195: 文法を検める器の呼出(bash -n / sh -n / zsh -n / shellcheck / py_compile / python -m compileall)を歩き、
 甲=対象の shebang を読んで器を選ぶ(同じ file の前後 5 行に head -1|shebang|#! の読みが在る) / 乙=器を固定して呼ぶ(冠を見ぬ) / 丙=器が env・引数で可変($SHELL/$SH/${...}/argv)
 二形の判: A=同じ行に shebang 読みの字面 / B=前後 5 行に在る。A≠B は「測れぬ(判が割れる)」で別勘定。和=母數。
 usage: 01_walk_syntax_checkers.py <out_tsv> <root> [<root>...]"""
import os,re,sys,time
out=sys.argv[1]; roots=sys.argv[2:]
SKIP={'.git','node_modules','.venv','__pycache__','queue'}
R_CALL=re.compile(r'\b(bash|sh|zsh|dash|ksh)\s+-n\b|\bshellcheck\b|py_compile|compileall|\bbash\s+-[a-z]*n[a-z]*\b')
R_SHEBANG=re.compile(r'shebang|#!|head\s+-n?\s*1|sed\s+-n\s+1p|read\s+-r\s+first|interpreter|冠')
R_VAR=re.compile(r'\$\{?(SHELL|SH|INTERP|CHECKER|BASH|RUNNER)\b|\$1\b|argv|getenv')
def kind(p,first):
    e=os.path.splitext(p)[1].lower()
    if e in('.sh','.bash','.bats') or (e=='' and first.startswith('#!') and 'sh' in first): return 'sh'
    if e=='.py' or (e=='' and first.startswith('#!') and 'python' in first): return 'py'
    if e in('.yml','.yaml'): return 'yaml'
    if e in('.md','.txt','.json'): return 'paper'
    return None
rows=[];files=0;maxd=0
for root in roots:
    for dp,dn,fn in os.walk(root):
        dn[:]=[d for d in dn if d not in SKIP]
        depth=os.path.relpath(dp,root).count(os.sep)+(0 if dp==root else 1); maxd=max(maxd,depth)
        for f in fn:
            p=os.path.join(dp,f); files+=1
            if '.bak' in f: continue
            try: b=open(p,'rb').read()
            except Exception: continue
            if b'\x00' in b[:4096]: continue
            ls=b.decode('utf-8','replace').split('\n'); k=kind(p,ls[0] if ls else '')
            if not k: continue
            for i,l in enumerate(ls,1):
                m=R_CALL.search(l)
                if not m: continue
                # 疵⑴の直し: `# shellcheck disable=/source=` の指示行と註行(先頭 #)は呼出でない → 別勘定 '註' として数へる
                st=l.strip()
                if re.match(r'#\s*shellcheck\s+(disable|source|shell)=',st) or (st.startswith('#') and k in ('sh','py')):
                    rows.append((k,root,os.path.relpath(p,root),i,m.group(0).split()[0],'-','-','註(呼出でない・指示行/註)',st[:150])); continue
                tool=m.group(0).split()[0]
                A=bool(R_SHEBANG.search(l)); ctx='\n'.join(ls[max(0,i-6):i+5]); Bv=bool(R_SHEBANG.search(ctx))
                var=bool(R_VAR.search(l))
                if A!=Bv: v='測れぬ(判が割れる A≠B)'
                elif A: v='甲(冠を読む)'
                elif var: v='丙(器が可変)'
                else: v='乙(器を固定)'
                rows.append((k,root,os.path.relpath(p,root),i,tool,'A' if A else '-','B' if Bv else '-',v,l.strip()[:150]))
with open(out,'w',encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} roots={roots} skip={sorted(SKIP)} files={files} max_depth={maxd} rc=0\n")
    f.write('kind\troot\tpath\tline\ttool\tA\tB\tverdict\tverbatim\n')
    for r in sorted(rows): f.write('\t'.join(map(str,r))+'\n')
from collections import Counter
def summ(rr,label):
    c=Counter(r[7].split('(')[0] for r in rr)
    print(f'{label}: 行 {len(rr)} / file {len(set((r[1],r[2]) for r in rr))} / 甲 {c["甲"]} 乙 {c["乙"]} 丙 {c["丙"]} 測れぬ {c["測れぬ"]} 註 {c["註"]} / 和={sum(c.values())} ({"=" if sum(c.values())==len(rr) else "≠"}母數) / 器別 {dict(Counter(r[4] for r in rr))}')
summ(rows,'全体')
for k in ('sh','py','yaml','paper'): summ([r for r in rows if r[0]==k],'  '+k)
for root in roots: summ([r for r in rows if r[1]==root],'  根 '+root)

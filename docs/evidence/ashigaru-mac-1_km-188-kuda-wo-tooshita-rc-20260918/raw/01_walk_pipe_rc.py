#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-188: 管の左の失敗が rc に出ぬ形を数へる(読むのみ)。
 形① count_pipe   : `cmd | wc -l` / `cmd | grep -c` の類(左の rc が落ちる)
 形② subst_pipe   : `$( cmd | … )` の中の管(左が失敗しても空が「0」として通る)
 形③ head_pipe    : `cmd | head -N`(SIGPIPE が rc を汚す)
 形④ pipefail     : file 単位で `set -o pipefail` / `set -euo pipefail` の有無
 形⑤ rc_after_pipe: 管の行の直後行で `$?` を読む
 排他: 一行は 形①〜③・⑤ の複数に当たり得る(併記)ゆゑ、行数の和は行の数と一致せぬ事を刷る。
 重なり: 同じ行に 2>/dev/null(km-184)や 2>&1(km-187)が在れば overlap 欄に印(母數から外す時に数へる)。
 usage: 01_walk_pipe_rc.py <root> <out_tsv> [skip...]"""
import os,re,sys,time
root,out=sys.argv[1],sys.argv[2]
SKIP=set(sys.argv[3:]) or {'.git','node_modules','.venv','__pycache__','queue','evidence'}
R_PIPE=re.compile(r'(?<![|>])\|(?!\|)')
R_COUNT=re.compile(r'\|\s*(wc\s+-[lcw]|grep\s+-[a-zA-Z]*c\b|uniq\s+-c|sort\s+-u|awk[^|]*NR|tr\s+-cd)')
R_HEAD=re.compile(r'\|\s*(head|tail)\s+(-n\s*)?-?\d')
R_SUBST=re.compile(r'\$\([^()]*\|[^()]*\)')
R_RC=re.compile(r'\$\?|\$\{PIPESTATUS|\$\{pipestatus|\$pipestatus')
def kind(p,first):
    e=os.path.splitext(p)[1].lower()
    if e=='.bats': return 'bats'
    if e in('.sh','.bash') or (e=='' and first.startswith('#!') and 'sh' in first): return 'sh'
    if e=='.py' or (e=='' and first.startswith('#!') and 'python' in first): return 'py'
    return None
rows=[]; files=0; maxd=0; pf={}; scanned=[]
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
        if not k or k=='py': continue   # 管は shell の物。py は pipe を持たぬ(subprocess の shell=True は測れぬ・紙に書く)
        rel=os.path.relpath(p,root); scanned.append(rel)
        pf[rel]=any(re.search(r'set\s+-[a-zA-Z]*o\s+pipefail|set\s+-o\s+pipefail|pipefail',l) for l in ls)
        for i,l in enumerate(ls,1):
            s=l.split('#')[0] if not l.strip().startswith('#') else ''
            if '|' not in s: continue
            if not R_PIPE.search(s): continue
            forms=[]
            if R_COUNT.search(s): forms.append('①count')
            if R_SUBST.search(s): forms.append('②subst')
            if R_HEAD.search(s): forms.append('③head')
            nxt=ls[i] if i<len(ls) else ''
            if R_RC.search(nxt) and 'PIPESTATUS' not in nxt and 'pipestatus' not in nxt: forms.append('⑤rc_after')
            if not forms: continue
            ov=[]
            if '2>/dev/null' in s or '2> /dev/null' in s: ov.append('km184')
            if '2>&1' in s: ov.append('km187')
            rows.append((k,rel,i,'+'.join(forms),'pipefail' if pf[rel] else 'no_pipefail','+'.join(ov) or '-',l.strip()[:170]))
with open(out,'w',encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} root={root} skip={sorted(SKIP)} files={files} sh/bats_scanned={len(scanned)} max_depth={maxd} rc=0\n")
    f.write('kind\tpath\tline\tforms\tfile_pipefail\toverlap\tverbatim\n')
    for r in sorted(rows): f.write('\t'.join(map(str,r))+'\n')
from collections import Counter
print(f'files={files} sh/bats={len(scanned)} depth={maxd} hit_lines={len(rows)} files_with_hits={len(set(r[1] for r in rows))}')
c=Counter(); [c.update(r[3].split('+')) for r in rows]; print('  形の延べ:', dict(c), '(和', sum(c.values()), '≠ 行', len(rows), '= 排他でない)')
print('  多重形の行:', sum(1 for r in rows if '+' in r[3]))
print('  ④ file pipefail 有:', sum(1 for v in pf.values() if v), '/ 無:', sum(1 for v in pf.values() if not v), '(走査 sh/bats', len(pf), ')')
print('  ④ hit 行の内 pipefail 無 file の行:', sum(1 for r in rows if r[4]=='no_pipefail'))
print('  重なり: km184', sum(1 for r in rows if 'km184' in r[5]), '/ km187', sum(1 for r in rows if 'km187' in r[5]), '/ 双方', sum(1 for r in rows if r[5]=='km184+km187'))

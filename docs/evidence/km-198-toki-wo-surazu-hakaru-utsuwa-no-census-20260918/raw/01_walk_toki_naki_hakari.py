#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-198: 動く物を測る器が、測つた値と同じ息で刻を刷るか。
 母數 = argv の根(file 単位)。検出子(動く物を測る字面) = git rev-parse|rev-list|for-each-ref|ls-remote|reflog / date / stat / wc / du / sb read / tmux capture-pane。
 刻の字面 = date(+%|"+|-I|`)・strftime・koku=|刻=|as_of|timestamp|%Y-%m|isoformat|now()。
 判(file 単位・㋒): 甲 = 検出子の行と同じ行(又は其の出目を刷る同じ echo/printf)に刻の字面 / 乙 = file の別の行に刻 / 丙 = file に刻の字面無し。
 ㋓ 固定: ref 名(HEAD|origin/main|refs/heads/…|main\b)を 2 度以上使ふ file で、`$(git rev-parse …)` を変数に受ける行(固定)が在るか。
 己を除く: 此の file 自身は数へぬ(名で除き、除いた事を刷る)。
 usage: 01_walk_toki_naki_hakari.py <out_tsv> <label:root> [...]"""
import os,re,sys,time,stat
out=sys.argv[1]; roots=[a.split(':',1) for a in sys.argv[2:]]
SELF=os.path.basename(__file__)
R_DET=re.compile(r'git\s+(rev-parse|rev-list|for-each-ref|ls-remote|reflog)\b|(?<![\w-])date\b|(?<![\w-])stat\s+-|(?<![\w-])wc\s+-|(?<![\w-])du\s+-|sb\s+read\b|tmux\s+capture-pane')
R_TOKI=re.compile(r'date\s+["\']?[+-]|strftime|koku=|刻=|as_of|timestamp|%Y-%m|isoformat|now\(\)|\bkoku\b')
R_REF=re.compile(r'\bHEAD\b|origin/main|refs/heads/|(?<![\w/-])main\b')
R_FIX=re.compile(r'=\s*"?\$\(\s*git\s+rev-parse|=\s*\$\(git rev-parse|rev-parse\s+--verify')
rows=[];files=0
for label,root in roots:
    cands=[]
    if os.path.isdir(root):
        for dp,dn,fn in os.walk(root):
            dn[:]=[d for d in dn if d not in ('.git','node_modules','.venv','__pycache__','seed_repo','seed_hyg','seed_build','seed_ctrl')]
            for f in fn: cands.append(os.path.join(dp,f))
    for p in sorted(cands):
        if label=='bin' and not (os.access(p,os.X_OK) and os.path.isfile(p)): continue
        if label=='raw' and not p.endswith('.txt'): continue
        if label=='checks' and not p.endswith('.sh'): continue
        if os.path.basename(p)==SELF: continue
        files+=1
        try: b=open(p,'rb').read()
        except Exception: continue
        if b'\x00' in b[:4096]: rows.append((label,os.path.join(root,os.path.basename(root)) if False else os.path.relpath(p,os.path.dirname(os.path.dirname(root))) if label=="raw" else os.path.relpath(p,root),'測れぬ(binary)','-','-','-','-')); continue
        ls=b.decode('utf-8','replace').split('\n')
        det=[(i,l) for i,l in enumerate(ls,1) if R_DET.search(l.split('#',1)[0] if not l.strip().startswith('#') else '')]
        if not det: rows.append((label,os.path.join(root,os.path.basename(root)) if False else os.path.relpath(p,os.path.dirname(os.path.dirname(root))) if label=="raw" else os.path.relpath(p,root),'動かぬ物のみ/検出子無し','-','-','-','-')); continue
        same=sum(1 for i,l in det if R_TOKI.search(l)); anyt=any(R_TOKI.search(l) for l in ls)
        v='甲(同じ行に刻)' if same==len(det) else ('乙(刻は別の行)' if anyt else '丙(刻無し)')
        if 0<same<len(det): v='乙(刻は別の行・一部の行のみ同行)'
        refs=sum(1 for l in ls if R_REF.search(l.split('#',1)[0])); fix=any(R_FIX.search(l) for l in ls)
        kotei='-' if refs<2 else ('固定(rev-parse を変数へ)' if fix else '★毎度 ref 名で引き直す★')
        rows.append((label,os.path.join(root,os.path.basename(root)) if False else os.path.relpath(p,os.path.dirname(os.path.dirname(root))) if label=="raw" else os.path.relpath(p,root),v,str(len(det)),str(same),str(refs),kotei))
with open(out,'w',encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} roots={roots} files={files} self_excluded={SELF} rc=0\n")
    f.write('root\tpath\tverdict\tdetector_lines\tsame_line_toki\tref_lines\tkotei\n')
    for r in rows: f.write('\t'.join(r)+'\n')
from collections import Counter
for label in dict.fromkeys(l for l,_ in roots):
    rr=[r for r in rows if r[0]==label]; hk=[r for r in rr if r[2].startswith(('甲','乙','丙'))]
    c=Counter(r[2].split('(')[0] for r in hk)
    print(f'{label}: 母數 file={len(rr)} / 動く物を測る器={len(hk)} / 甲 {c["甲"]} 乙 {c["乙"]} 丙 {c["丙"]} (和 {sum(c.values())}) / 検出子無し={sum(1 for r in rr if r[2].startswith("動かぬ"))} / 測れぬ={sum(1 for r in rr if r[2].startswith("測れぬ"))}')
    k=Counter(r[6] for r in hk); print('   固定の別(ref 名 2 度以上の器):', {x:y for x,y in k.items() if x!="-"})

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-191: shell の `$名` の直後に多byte 文字が続く形を数へる(読むのみ)。
 甲 = `${名}` と括る(安全) / 乙 = 裸の `$名` + 多byte(疵) / 丙 = `"$名"` の様に引用符で閉ぢる(安全)
 併せて file 単位の set -u(-u / -eu / -euo / set -o nounset)の有無、行が註か heredoc かを印す。
 重なり: 同じ行に 2>/dev/null(km-184)・2>&1(km-187)・数へる管(km-188)。
 usage: 01_walk_dollar_multibyte.py <root> <out_tsv> [skip...]"""
import os,re,sys,time
root,out=sys.argv[1],sys.argv[2]
SKIP=set(sys.argv[3:]) or {'.git','node_modules','.venv','__pycache__','queue','evidence'}
NAME=r'[A-Za-z_][A-Za-z0-9_]*'
R_OTSU=re.compile(r'(?<![\\$])\$('+NAME+r')(?=[^\x00-\x7f])')          # 裸 $名 の直後が非ASCII
R_KOU=re.compile(r'\$\{'+NAME+r'[^}]*\}(?=[^\x00-\x7f])')               # ${名} の直後が非ASCII
R_HEI=re.compile(r'"\$'+NAME+r'"(?=[^\x00-\x7f])')                      # "$名" の直後が非ASCII
R_SETU=re.compile(r'^\s*set\s+-[a-zA-Z]*u|set\s+-o\s+nounset|^\s*set\s+-[a-zA-Z]*e[a-zA-Z]*u',re.M)
R_OV=[('km184',re.compile(r'2>\s*/dev/null')),('km187',re.compile(r'2>&1')),('km188',re.compile(r'\|\s*(wc\s+-[lcw]|grep\s+-[a-zA-Z]*c\b)'))]
def kind(p,first):
    e=os.path.splitext(p)[1].lower()
    if e=='.bats': return 'bats'
    if e in('.sh','.bash') or (e=='' and first.startswith('#!') and 'sh' in first): return 'sh'
    return None
rows=[];files=0;maxd=0;scanned=0;setu={}
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
        if not k: continue
        rel=os.path.relpath(p,root); scanned+=1; su=bool(R_SETU.search('\n'.join(ls))); setu[rel]=su
        inhere=False; hd=None
        for i,l in enumerate(ls,1):
            st=l.strip()
            # heredoc の粗い追跡(<<'EOF' は展開せぬ・<<EOF は展開する)
            m=re.search(r"<<-?\s*(['\"]?)(\w+)\1",l)
            if inhere and st==hd: inhere=False; hd=None; continue
            if m and not inhere: inhere=True; hd=m.group(2); quoted=bool(m.group(1)); continue
            comment = st.startswith('#')
            for tag,rx in (('乙',R_OTSU),('甲',R_KOU),('丙',R_HEI)):
                for mm in rx.finditer(l):
                    nxt=l[mm.end():mm.end()+1]
                    ctx='註' if comment else ('heredoc(展開無)' if (inhere and quoted) else ('heredoc(展開有)' if inhere else 'code'))
                    ov='+'.join(t for t,r in R_OV if r.search(l)) or '-'
                    rows.append((k,rel,i,tag,mm.group(0)[:30],nxt,ctx,'set-u' if su else 'no-set-u',ov,l.strip()[:150]))
with open(out,'w',encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} root={root} skip={sorted(SKIP)} files={files} sh/bats_scanned={scanned} max_depth={maxd} rc=0\n")
    f.write('kind\tpath\tline\tform\tmatch\tnext_char\tctx\tset_u\toverlap\tverbatim\n')
    for r in sorted(rows): f.write('\t'.join(map(str,r))+'\n')
from collections import Counter
c=Counter(r[3] for r in rows); print(f'files={files} sh/bats={scanned} depth={maxd} hits={len(rows)} 甲={c["甲"]} 乙={c["乙"]} 丙={c["丙"]}')
otsu=[r for r in rows if r[3]=='乙']
print('  乙 の ctx:', dict(Counter(r[6] for r in otsu)), '/ set-u:', dict(Counter(r[7] for r in otsu)), '/ 重なり:', sum(1 for r in otsu if r[8]!='-'))
print('  乙 の直後の字 上位:', Counter(r[5] for r in otsu).most_common(8))
print('  乙 code の file:', sorted(set(r[1] for r in otsu if r[6]=='code'))[:20])

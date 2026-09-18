#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-192: 位置引数を取る helper の呼出を歩き、旗が位置引数より前に在る形(乙)を数へる(読むのみ)。
 器 = sb / sb-karo-mac / sb-ashigaru-mac-N / sb-gunshi-mac / sb-gakushu-bucho / agent_letter.py / inbox_write.sh / board_write.py / inbox_mark_read.py
 甲 = 正しい語順(位置引数の後に旗) / 乙 = 旗(--to/--parent-seq/--urgent/--requires-response/--dry-run)が最初の位置引数(胴)より前 / 丙 = 判じ得ぬ(変数展開・多行・pipe で胴を渡す)
 勘定: 器(sh/py/bats)と紙(md/yaml/txt の例文)を別欄。usage 行(器自身の説明)は例文として数へる。
 usage: 01_walk_helper_calls.py <root> <out_tsv> [skip...]"""
import os,re,sys,time
root,out=sys.argv[1],sys.argv[2]
SKIP=set(sys.argv[3:]) or {'.git','node_modules','.venv','__pycache__','queue','evidence'}
HELPER=re.compile(r'(?:^|[\s;&|(`"\'])((?:~/bin/|\$HOME/bin/|/Users/momizimac/bin/)?(?:sb-[a-z0-9-]+|sb|agent_letter\.py|inbox_write\.sh|board_write\.py|inbox_mark_read\.py))\s+([^\n]*)')
FLAG=re.compile(r'--(to|parent-seq|urgent|requires-response|dry-run|deferral)\b')
def kind(p,first):
    e=os.path.splitext(p)[1].lower()
    if e in('.sh','.bash','.bats') or (e=='' and first.startswith('#!') and 'sh' in first): return 'sh'
    if e=='.py' or (e=='' and first.startswith('#!') and 'python' in first): return 'py'
    if e in('.md','.yaml','.yml','.txt'): return 'paper'
    return None
def judge(helper,rest):
    toks=rest.strip()
    if helper.endswith('inbox_write.sh') or helper.endswith('board_write.py') or helper.endswith('inbox_mark_read.py'):
        return '甲(旗を持たぬ器)' if not FLAG.search(toks) else '丙(旗を持たぬ器に旗)'
    # sb 系 / agent_letter: 期待 = [read|write] letter "<胴>" [--to X] [--parent-seq N]
    m=re.match(r'(read|write)\s+(\S+)\s*(.*)$',toks)
    if not m: return '丙(語順を読めぬ)'
    if m.group(1)=='read': return '甲(read)'
    after=m.group(3)
    fm=FLAG.search(after)
    if not fm: return '丙(胴も旗も無い/多行)'
    before=after[:fm.start()].strip()
    if before=='' : return '★乙(旗が胴より前)★'
    if before.startswith(('"',"'",'$','"$','$(')) or len(before)>0: return '甲'
    return '丙'
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
        if not k: continue
        rel=os.path.relpath(p,root)
        for i,l in enumerate(ls,1):
            for m in HELPER.finditer(l):
                helper=m.group(1).split('/')[-1]; rest=m.group(2)
                if helper=='sb' and not re.match(r'\s*(read|write)\b',rest): continue
                ctx='usage/例文' if ('usage' in l.lower() or l.strip().startswith('#') or k=='paper') else 'code'
                rows.append((k,ctx,rel,i,helper,judge(helper,rest),l.strip()[:170]))
with open(out,'w',encoding='utf-8') as f:
    f.write(f"# koku={time.strftime('%Y-%m-%dT%H:%M:%S%z')} root={root} skip={sorted(SKIP)} files={files} max_depth={maxd} rc=0\n")
    f.write('kind\tctx\tpath\tline\thelper\tverdict\tverbatim\n')
    for r in sorted(rows): f.write('\t'.join(map(str,r))+'\n')
from collections import Counter
print(f'files={files} depth={maxd} calls={len(rows)}')
for ctx in ('code','usage/例文'):
    rr=[r for r in rows if r[1]==ctx]; print(f'  {ctx}: {len(rr)} 件 / verdict', dict(Counter(r[5] for r in rr)), '/ helper', dict(Counter(r[4] for r in rr)))

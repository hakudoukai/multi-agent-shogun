# -*- coding: utf-8 -*-
"""全走の出目を一枚へ。★0 でも一行出す★。"""
import os, glob, re
rows=[]
for f in sorted(glob.glob('_after/20_*.verdict')):
    d={}
    for L in open(f,encoding='utf-8'):
        if '=' in L:
            k,v=L.split('=',1); d[k.strip()]=v.strip()
    case=d.get('case','?')
    errf='_after/20_%s.err'%case
    errtxt=''
    if os.path.exists(errf):
        t=open(errf,encoding='utf-8',errors='replace').read().strip()
        errtxt=t.split('\n')[0][:60] if t else '(0行)'
    rows.append((case,d.get('rc','?'),d.get('秒','?'),d.get('stdout','?'),d.get('stderr 行','?'),d.get('判定','?'),errtxt))
print('%-12s %-4s %-4s %-10s %-6s %-26s %s'%('case','rc','秒','stdout','err行','判定','stderr の初行'))
print('-'*130)
for r in rows:
    print('%-12s %-4s %-4s %-10s %-6s %-26s %s'%r)
print('-'*130)
print('走 = %d 件'%len(rows))

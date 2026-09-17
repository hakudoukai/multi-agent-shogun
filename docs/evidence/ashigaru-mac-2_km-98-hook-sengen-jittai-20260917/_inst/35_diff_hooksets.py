#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""35_diff_hooksets.py <A.tsv> <nameA> <B.tsv> <nameB> ―― 二つの hook 集合を
(event, 展開後path) の鍵で突き合はせ、増/減/形だけ変つた物を ★名で★ 出す。"""
import sys, os, shlex
INTERP={'bash','sh','zsh','python3','python','env','node','ruby','perl'}
def expand(t):
    o,i=[],0
    while i<len(t):
        if t.startswith('${',i):
            j=t.find('}',i)
            if j<0: return None
            inn=t[i+2:j]
            nm,df=(inn.split(':-',1)+[None])[:2] if ':-' in inn else (inn,None)
            o.append(os.environ.get(nm, df if df is not None else '${%s}'%nm)); i=j+1
        else: o.append(t[i]); i+=1
    return ''.join(o)
def key(cmd):
    try: toks=shlex.split(cmd)
    except ValueError: return None
    for t in toks:
        if t in INTERP or t.startswith('-'): continue
        if '/' in t:
            p=expand(t)
            return os.path.normpath(p) if p else None
    return None
def load(f):
    d={}
    for l in open(f,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l or l.startswith('#'): continue
        fl=l.split('\t')
        if len(fl)<7: continue
        cmd=fl[6].replace('␊','\n').replace('␍','\r').replace('␉','\t')
        d[(fl[1], key(cmd))]=cmd
    return d
def main():
    if len(sys.argv)!=5:
        sys.stderr.write('usage: 35_diff_hooksets.py <A.tsv> <nameA> <B.tsv> <nameB>\n'); return 2
    A,na,Bf,nb=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
    a,b=load(A),load(Bf)
    only_a=sorted(set(a)-set(b)); only_b=sorted(set(b)-set(a)); both=sorted(set(a)&set(b))
    print('# %s = %d 本 / %s = %d 本' % (na,len(a),nb,len(b)))
    print('# %s のみ = %d / %s のみ = %d / 両方 = %d' % (na,len(only_a),nb,len(only_b),len(both)))
    for k in only_a: print('%s のみ\t%s\t%s\t%s' % (na,k[0],k[1],a[k]))
    for k in only_b: print('★%s で増えた★\t%s\t%s\t%s' % (nb,k[0],k[1],b[k]))
    same=diff=0
    for k in both:
        if a[k]==b[k]: same+=1
        else:
            diff+=1
            print('形のみ変つた\t%s\t%s\t%s ⇒ %s' % (k[0],k[1],a[k],b[k]))
    print('# 両方に在り 字面同一=%d / 字面違ふ=%d' % (same,diff))
    return 0
sys.exit(main())

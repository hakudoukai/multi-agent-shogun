#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""幹の在処と PR の形を測る(読取のみ)。裁 seq326093 ①「main へ rebase 不要・merge commit 方式」の裏取り。"""
import subprocess, os, sys, datetime
MIKI='363d5fb06084'; MAIN='4be3ee19e1c5'; EDA='refs/heads/karo-mac/km-gate-kou-otsu-20260917'
ROOT=subprocess.run(['git','rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip()
def g(*a):
    r=subprocess.run(['git']+list(a),capture_output=True,text=True); return r.returncode,r.stdout.strip()
def kaki(p,ls): open(p,'w',encoding='utf-8').write('\n'.join(l.replace('\r','').rstrip() for l in ls)+'\n')
R=['刻=%s'%datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'根=%s'%ROOT,'']
rc,eda=g('rev-parse',EDA); rc2,mn=g('rev-parse','refs/heads/main'); rc3,om=g('rev-parse','origin/main')
R+=['一 版',
    '  枝 karo-mac/km-gate-kou-otsu-20260917 = %s (rc=%d)'%(eda[:12],rc),
    '  手許 refs/heads/main                  = %s (rc=%d)'%(mn[:12],rc2),
    '  origin/main                           = %s (rc=%d)'%(om[:12],rc3),
    '  ★枝==手許main★ = %s   ★枝==紙の宣 363d5fb06084★ = %s'%(eda==mn, eda.startswith('363d5fb06084')),'']
rcA,_=g('merge-base','--is-ancestor',om,eda)
rcB,_=g('merge-base','--is-ancestor',eda,om)
_,mb=g('merge-base',om,eda)
_,ah=g('rev-list','--count','%s..%s'%(om,eda)); _,bh=g('rev-list','--count','%s..%s'%(eda,om))
_,fl=g('diff','--name-only','%s...%s'%(MAIN,MIKI))
R+=['二 PR の形',
    '  origin/main は幹の祖先か(早送り可か) = %s (is-ancestor rc=%d)'%('可' if rcA==0 else '★否★',rcA),
    '  幹は origin/main の祖先か            = %s (rc=%d)'%('然り' if rcB==0 else '否',rcB),
    '  分岐点(merge-base) = %s'%mb[:12],
    '  幹が進んだ = %s commit / origin/main が進んだ = %s commit'%(ah,bh),
    '  ★両者が別々に進んで居る ∴ 早送りは効かず merge commit が要る(裁326093①と合ふ)★' if (rcA!=0 and int(bh)>0)
      else ('  ★origin/main は幹の祖先 ∴ 早送りでも merge でも入る★' if rcA==0 else '  ★要検分★'),
    '  三点 diff の file = %d 本'%len([x for x in fl.split('\n') if x]),'']
_,c16=g('rev-list','--count','%s...%s'%(MAIN,MIKI))
_,c1=g('rev-list','--count','%s..%s'%(MAIN,MIKI))
R+=['三 數の意味',
    '  「16 commit」= rev-list --count %s..%s = %s ―― ★幹の側だけ★'%(MAIN[:8],MIKI[:8],c1),
    '  対称差(両側の和) = %s ―― ★之を16と混ぜるな★'%c16,
    '  「464 file」= diff --name-only ★三点(...)★ ―― 二点(..)なら 475 と出る(分岐後の基の動きを混ぜる故)',
    '','★數が意味せぬ事★: 464 は「幹が変へた file 数」であつて、PR が世に出す file の総数(tree 967本)ではない。']
kaki(os.path.join(ROOT,'docs/evidence/karo-mac-miki-push-negai-20260917/raw/30_arika.txt'),R)
print('\n'.join(R))
sys.exit(0)

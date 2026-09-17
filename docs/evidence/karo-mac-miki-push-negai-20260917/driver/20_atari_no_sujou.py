#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""甲の当り6件の★素性★を焼く(読取のみ)。問は二つ:
  ㋐其の file は★幹が触れたか★/ blob は origin/main と同じか ―― 同じなら PR は之を足して居らぬ
  ㋑其の値は★本物の鍵の形★か ―― 厳密形(sk-ant/jwt/gh_pat/aws/slack/pem)と緩形(鍵名=長い字)を分けて数へる
値は一字も刷らぬ。字種の内訳のみ刷る(桁数・英大/小・数字・記号の別)。
"""
import re, subprocess, os, sys, datetime
MIKI='363d5fb06084'; MAIN='4be3ee19e1c5'
ROOT=subprocess.run(['git','rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip()
ATARI=[('SECURITY.md',[47]),('tests/test_karo_second_send_iincho.bats',[123,138,162,231]),('tests/unit/test_ntfy_auth.bats',[50])]
STRICT=[('sk_ant',re.compile(r'sk-ant-[A-Za-z0-9_\-]{20,}')),('jwt',re.compile(r'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}')),
        ('gh_pat',re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}')),('aws_akid',re.compile(r'AKIA[0-9A-Z]{16}')),
        ('slack',re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}')),('pem',re.compile(r'[-]{5}BEGIN [A-Z ]*PRIVATE KEY[-]{5}'))]
LOOSE=re.compile(r'(?i)(service_role_key|api_key|apikey|secret|password|passwd|token)\s*[=:]\s*["\']?([A-Za-z0-9_\-/+=]{20,})')
def kaki(p,ls): open(p,'w',encoding='utf-8').write('\n'.join(l.replace('\r','').rstrip() for l in ls)+'\n')
def g(*a):
    r=subprocess.run(['git']+list(a),capture_output=True,text=True); return r.returncode,r.stdout
fs=set(g('diff','--name-only','%s...%s'%(MAIN,MIKI))[1].split('\n'))
rep=['刻=%s'%datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'根=%s'%ROOT,
     '幹=%s 基=%s'%(MIKI,MAIN),'','㋐ file の素性 ―― 幹が触れたか / blob は基と同じか','']
kizu=0
for f,_ in ATARI:
    rca,a=g('rev-parse','%s:%s'%(MIKI,f)); rcb,b=g('rev-parse','%s:%s'%(MAIN,f))
    same = rca==0 and rcb==0 and a.strip()==b.strip()
    rep.append('  %-46s 幹が触れた=%-5s blob 幹==基=%s (rc %d/%d)'%(f,f in fs,'★同★' if same else '★異★',rca,rcb))
    if (f in fs) or not same: kizu+=1
rep+=['','  ★幹が触れた file は 0 本・blob は悉く基と同一 ∴ 当り6件は PR が足す物に非ず★' if kizu==0
      else '  ★疵 %d 本 ―― PR が足す側に当りが在る★'%kizu,'','㋑ 値の素性 ―― 厳密形は幾つ鳴つたか','']
S=L=0
for f,lns in ATARI:
    src=g('cat-file','-p','%s:%s'%(MIKI,f))[1].split('\n')
    for n in lns:
        line=src[n-1]
        st=[t for t,rx in STRICT if rx.search(line)]
        m=LOOSE.search(line); v=m.group(2) if m else ''
        S+=len(st); L+=1 if m else 0
        pro='桁%d 英大%d 英小%d 数%d 記号%d'%(len(v),sum(c.isupper() for c in v),sum(c.islower() for c in v),
                                              sum(c.isdigit() for c in v),sum(not c.isalnum() for c in v))
        rep.append('  %s:%d 鍵=%s 厳密形=%s 値=<伏:%d字>(%s)'%(f,n,m.group(1) if m else '-', '・'.join(st) or '★無★',len(v),pro))
rep+=['','  ★厳密形の当り = %d 件 / 緩形 = %d 件★'%(S,L),
      '  緩形は「鍵名 = 20字以上の字」に当たるだけで、本物の鍵の形には当たらぬ。',
      '  ∴ 6件は悉く「鍵名を書いた行」であつて、鍵の形をした値では無い。',
      '','★數が意味せぬ事★: 之は「6件が贋である」の証明に非ず。',
      '  示したのは⑴幹が之を足して居らぬ事(blob 同一)と⑵値が既知の鍵の形に当たらぬ事の二つのみ。',
      '  基 origin/main に既に在る物の是非は★別件★であり、本 PR の可否とは切り離して上申する。']
kaki(os.path.join(ROOT,'docs/evidence/karo-mac-miki-push-negai-20260917/raw/20_atari.txt'),rep)
print('\n'.join(rep))
sys.exit(1 if (kizu or S) else 0)

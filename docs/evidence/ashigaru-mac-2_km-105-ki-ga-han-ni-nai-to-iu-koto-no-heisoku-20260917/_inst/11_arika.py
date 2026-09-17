# -*- coding: utf-8 -*-
"""11_arika.py ―― ★覆し★の裏取り。km-104 で「object すら無し(rc=1)」と裁かれた blob が
今 rc=0 で在る。★因は当てず★、在り処だけを歩く(疎/詰・刻・到達する ref)。
併せて 家老の母數(scripts/checks の16本)を ★己の器で★ 測り直す。
"""
import os, sys, subprocess, hashlib, time, re
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
APP='b56d6576c82212c155980968d4ec1e0a8c5c7427'
L=[]
def w(s): L.append(s); print(s)
def g(*a):
    p=subprocess.run(['git','-C',NE]+list(a),capture_output=True,text=True)
    return p.returncode,p.stdout,p.stderr
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w('')
w('【一】km-104 の裁「object すら無し」の再検 ―― blob %s' % APP)
rc,out,err=g('cat-file','-e',APP); w('  cat-file -e rc=%d ★(km-104 の刻は rc=1 であつた)★' % rc)
rc2,out2,_=g('cat-file','-s',APP); w('  cat-file -s = %s byte (rc=%d)' % (out2.strip(),rc2))
loose=os.path.join(NE,'.git/objects',APP[:2],APP[2:])
if os.path.isfile(loose):
    st=os.stat(loose)
    w('  ★疎(loose)★ = %s' % loose)
    w('  其の file の mtime = %s / ctime = %s / %d byte'
      % (time.strftime('%Y-%m-%dT%H:%M:%S%z',time.localtime(st.st_mtime)),
         time.strftime('%Y-%m-%dT%H:%M:%S%z',time.localtime(st.st_ctime)),st.st_size))
else:
    w('  疎では無い ∴ 詰(pack)の中か、別の在り処')
    rc3,out3,_=g('cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize:disk)','--batch-all-objects')
    w('  (詰の照会 rc=%d)' % rc3)
w('  ★到達する ref★(blob は for-each-ref --contains で問へぬ ∴ rev-list --objects で歩く):')
rc4,out4,_=g('rev-list','--objects','--all')
hit=[l for l in out4.split('\n') if l.startswith(APP)]
w('    rev-list --objects --all の出目に在るか = %s (rc=%d / 出目 %d 行)'
  % ('★在り★' if hit else '★無し★',rc4,len(out4.split(chr(10)))))
for h in hit: w('      %s' % h)
w('  ∴ ★どの ref からも到達せぬ疎 object★ = 「書かれたが、木に入つて居らぬ」' if not hit
  else '  ∴ 何處かの木が運んで居る')
w('  ★因は当てぬ★。此処で言へるは「★在る★」と「★到達せぬ★」の二つのみ。')

w('')
w('【二】家老の母數(scripts/checks の16本)を己の器で測り直す')
d=os.path.join(NE,'scripts/checks')
gen=sorted(f for f in os.listdir(d)
           if os.path.isfile(os.path.join(d,f)) and (f.endswith('.py') or f.endswith('.sh')))
w('  面1 disk .py/.sh = ★%d本★ (家老=16) %s' % (len(gen),'一致' if len(gen)==16 else '★相違★'))
rc_i,out_i,_=g('ls-files','-s','--','scripts/checks/')
idx={}
for line in out_i.split('\n'):
    if not line.strip(): continue
    m,p=line.split('\t',1); idx[p]=m.split()[1]
idxgen=[f for f in gen if 'scripts/checks/'+f in idx]
w('  面2 index に在る = ★%d本★ (家老=15) %s' % (len(idxgen),'一致' if len(idxgen)==15 else '★相違★'))
w('     index 外 = %s' % ' '.join(f for f in gen if f not in idxgen))
rc,out,_=g('ls-tree','-r','--full-tree','origin/main','--','scripts/checks/')
ori={}
for line in out.split('\n'):
    if not line.strip(): continue
    m,p=line.split('\t',1); ori[p]=m.split()[2]
ctl='scripts/checks/pane_identity.sh'
assert g('cat-file','-e','origin/main:'+ctl)[0]==0 and ctl in ori, '★対照落ち ∴ 止まる★'
w('  面4 origin/main 行 = %d (対照 %s 在り rc=%d)' % (len(ori),ctl,rc))
nashi,koto=[],[]
for f in gen:
    rel='scripts/checks/'+f
    b=open(os.path.join(d,f),'rb').read()
    blob=hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()
    if rel not in ori: nashi.append(f)
    elif ori[rel]!=blob: koto.append((f,ori[rel],blob))
w('  ★食ひ違ひ = %d本★ (家老=5) %s' % (len(nashi)+len(koto),
                                    '一致' if len(nashi)+len(koto)==5 else '★相違★'))
w('    path 無 = %d本 (家老=3): %s' % (len(nashi),' '.join(nashi)))
w('    中身 異 = %d本 (家老=2):' % len(koto))
for f,o,m in koto: w('      %s 遠隔=%s / 手許=%s' % (f,o[:8],m[:8]))
open(os.path.join(B,'_raw/11_arika.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))

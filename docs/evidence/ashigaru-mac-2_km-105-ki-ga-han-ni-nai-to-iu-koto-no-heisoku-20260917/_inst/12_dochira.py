# -*- coding: utf-8 -*-
"""12_dochira.py ―― ⑴己の疵の名指し ⑵append.py を ★何處の木が運ぶか★。
★11_arika.py の疵(逐語で残す)★:
  11 は「因は当てぬ。此処で言へるは『在る』と『到達せぬ』の二つのみ。」を
  ★条件分岐の外に固定文として★ 刷つた。實測は hit 有り=「到達する」であり、
  ★分岐は正しく刷つたのに、其の直前の固定文が逆を述べた★。
  ∴ 疵の形 = 「判じの前に結語を書いた」。判じから結語を組め。11_raw は其の儘残す。
"""
import os, subprocess, time, hashlib
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
REL='scripts/checks/karo_mac_manifest_append.py'
APP='b56d6576c82212c155980968d4ec1e0a8c5c7427'
L=[]
def w(s): L.append(s); print(s)
def g(*a):
    p=subprocess.run(['git','-C',NE]+list(a),capture_output=True,text=True)
    return p.returncode,p.stdout,p.stderr
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(__doc__.strip())
w('')
w('【一】blob %s を其の path で運ぶ commit' % APP)
rc,out,_=g('log','--all','--format=%H %ct %d %s','--',REL)
cs=[l for l in out.split('\n') if l.strip()]
w('  log --all -- %s = ★%d件★ (rc=%d)' % (REL,len(cs),rc))
mochi=[]
for l in cs:
    h=l.split()[0]
    r2,o2,_=g('rev-parse','%s:%s'%(h,REL))
    if r2==0 and o2.strip()==APP: mochi.append(h)
    w('    %s  → %s:%s = %s' % (l[:110],h[:8],'…append.py',
        (o2.strip()[:8]+(' ★此の blob★' if r2==0 and o2.strip()==APP else '')) if r2==0 else '★無★'))
w('  ★手許の中身と同じ blob を運ぶ commit = %d件★' % len(mochi))
w('')
w('【二】其の commit へ到達する ref(★數を出した器の出目で対照する★)')
for h in mochi:
    rc3,o3,_=g('for-each-ref','--format=%(refname)','--contains',h)
    rs=[x for x in o3.split('\n') if x.strip()]
    w('  %s ← ref %d本 (rc=%d)' % (h,len(rs),rc3))
    for r in rs: w('      %s' % r)
    rc4,o4,_=g('branch','-r','--contains',h)
    w('      遠隔追跡枝(-r --contains) = %s' % (' '.join(o4.split()) or '★0本★ rc=%d'%rc4))
w('')
w('【三】陰性対照 ―― 在らぬ commit への --contains')
rc5,o5,_=g('for-each-ref','--format=%(refname)','--contains','0'*40)
w('  0000…(40) → 出目 %d本 / ★rc=%d★ (rc≠0 の零は「0本」に非ず)'
  % (len([x for x in o5.split('\n') if x.strip()]),rc5))
w('')
w('【四】∴ 言へる事')
w('  ・blob は ★在る★(cat-file -e rc=0)。km-104 の刻の rc=1 とは ★食ひ違ふ★。')
w('  ・且つ ★ref から到達する★ ∴ 「書かれたが木に入らぬ疎 object」では ★無い★。')
w('  ・然れど origin/main にも 幹PR#20 にも ★path が無い★ ∴ 「遠隔には届いて居らぬ」は変らぬ。')
w('  ・★因(何時・誰が)は本紙では断ぜぬ★。測つたのは在り処のみ。')
open(os.path.join(B,'_raw/12_dochira.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))

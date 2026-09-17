# -*- coding: utf-8 -*-
"""21_shizuka.py ―― 「在るのに違ふ」に ★出目の差が實際に出るか★。
幹の verify.py は127行・手許は198行。差が ★判じに出ぬ★ なら「違ふ」は紙の上の話に留まる。
出るなら ★静かな欠★ である。判じの分かれ易い試料で突く:
  試料A 空白を含む path (裁 seq321353⑵ の回帰域)
  試料B 引用符で括つた既存行 (裁 seq321127⑵/321353⑴ の旧形)
★同じ臺帳・同じ file を、二つの verify.py に食はせ、rc と出目を並べる★。
"""
import os, subprocess, time, shutil
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
MI=os.path.join(B,'_inst/miki'); TE=os.path.join(NE,'scripts/checks')
L=[]
def w(s): L.append(s); print(s)
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z')); w(__doc__.strip()); w('')

import hashlib
def sha(p):
    b=open(p,'rb').read(); return hashlib.sha256(b).hexdigest(), len(b), b.count(b'\n')

for tag,fname,quote in [('A 空白を含む path','c d.txt',False),
                        ('B 引用符で括つた行','e.txt',True)]:
    d=os.path.join(B,'_fixture/s_'+('A' if 'A' in tag else 'B')); shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    open(os.path.join(d,fname),'w',encoding='utf-8').write('丙\n')
    s,by,ln=sha(os.path.join(d,fname))
    p = ('"%s"'%fname) if quote else fname
    man=os.path.join(d,'MANIFEST.txt')
    open(man,'w',encoding='utf-8').write(
        '# dialect: path= sha256= bytes= lines=\n'
        'path=%s sha256=%s bytes=%d lines=%d\n' % (p,s,by,ln))
    w('■ 試料%s  臺帳の行: path=%s …' % (tag,p))
    for nm,v in [('幹PR#20 127行',os.path.join(MI,'karo_mac_manifest_verify.py')),
                 ('手許   198行',os.path.join(TE,'karo_mac_manifest_verify.py'))]:
        r=subprocess.run(['python3','-B',v,'MANIFEST.txt','.'],cwd=d,capture_output=True,text=True)
        o=(r.stdout+r.stderr).rstrip('\n')
        w('   %s → ★rc=%d★' % (nm,r.returncode))
        for l in [x for x in o.split('\n') if x.strip()][:5]: w('        | %s' % l[:140])
    w('')
open(os.path.join(B,'_raw/21_shizuka.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))

# -*- coding: utf-8 -*-
"""usage: 91_daichou.py  ―― ★束の中で走らせよ★(cwd=束の根)。裁 seq322699 の束内相対で臺帳を建てる。
karo_mac_manifest_append.py の usage 逐語: <manifest> <path...>(root=os.getcwd() で相対を取る)。
0byte の紙は入れぬ(raw/96_kuu.txt に宣す)。己(_manifest.txt)は入れぬ。
"""
import os, sys, subprocess
root=os.getcwd()
assert os.path.basename(root).startswith('km-53'), '★束の中で走らせよ★ cwd=%s' % root
fs=[]
for d,dn,fn in os.walk('.'):
    dn[:] = [x for x in dn if x != '__pycache__']
    for f in fn:
        p=os.path.relpath(os.path.join(d,f),'.')
        if p=='_manifest.txt': continue
        st=os.stat(p)
        if st.st_size==0: continue
        fs.append(p)
fs.sort()
print('積む紙=%d' % len(fs))
if os.path.exists('_manifest.txt'): os.remove('_manifest.txt')
r=subprocess.run(['/opt/homebrew/bin/python3',
  '/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_manifest_append.py','_manifest.txt']+fs)
print('append rc=%d' % r.returncode)
L=open('_manifest.txt',encoding='utf-8').read().split(chr(10))
kan=[l for l in L if l.startswith('#')]; gyo=[l for l in L if l.startswith('path=')]
print('臺帳 全行=%d(冠%d + path行%d)' % (len([l for l in L if l]),len(kan),len(gyo)))
assert len(gyo)==len(fs), '★行数が合はぬ★ %d vs %d' % (len(gyo),len(fs))
print('★合★ path行 == 積んだ紙')

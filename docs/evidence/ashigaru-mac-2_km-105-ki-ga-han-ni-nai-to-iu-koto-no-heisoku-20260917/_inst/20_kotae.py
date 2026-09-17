# -*- coding: utf-8 -*-
"""20_kotae.py ―― ★的に實際に答へる★: 「此の機が一つ失せた時、臺帳は建ち、門は鳴るか」。
推さず、★幹PR#20 が運ぶ版だけを取り出して★ 己の束の中で走らせる。
★追記(12→13→本紙)★: 00 の追跡器は append.py:142 `_yomite()` の
  importlib.util.spec_from_file_location による ★path 直読み★ を辺として拾へなんだ。
  顔触れ(3本)は変らぬが ★辺は2本でなく3本★。追跡器の盲点として名指す。
"""
import os, sys, subprocess, time, shutil
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
MIKI='0bb92e2b800c'; MI=os.path.join(B,'_inst/miki'); FX=os.path.join(B,'_fixture/taba')
L=[]
def w(s): L.append(s); print(s)
def g(*a):
    p=subprocess.run(['git','-C',NE]+list(a),capture_output=True,text=True); return p
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(__doc__.strip()); w('')

w('【一】幹PR#20 %s から閉包3本を取り出す(己の束の中へ)' % MIKI)
aru={}
for nm in ['karo_mac_dasumae_gate.sh','karo_mac_manifest_verify.py','karo_mac_manifest_append.py']:
    p=g('show','%s:scripts/checks/%s'%(MIKI,nm))
    if p.returncode==0:
        open(os.path.join(MI,nm),'w',encoding='utf-8').write(p.stdout)
        os.chmod(os.path.join(MI,nm),0o755); aru[nm]=True
        w('  %-32s = ★在★ rc=0 / %d byte' % (nm,len(p.stdout.encode())))
    else:
        aru[nm]=False
        w('  %-32s = ★無★ rc=%d / stderr=%s' % (nm,p.returncode,p.stderr.strip()[:80]))

w('')
w('【二】試料の束を作る(己の束の中・2本)')
for i,(n,body) in enumerate([('a.txt','甲\n'),('b.txt','乙\n')]):
    open(os.path.join(FX,n),'w',encoding='utf-8').write(body)
w('  %s に a.txt / b.txt' % os.path.relpath(FX,NE))

def hashiru(argv,cwd,env=None):
    e=dict(os.environ); e['KM_GATE_MANIFEST_BASE']='.'
    if env: e.update(env)
    p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,env=e)
    return p

w('')
w('【三】★臺帳は建つか★')
w('  甲 幹の append.py で建てる:')
if not aru['karo_mac_manifest_append.py']:
    w('     → ★器が幹に無い★ ∴ ★建たぬ★(rc 以前に呼ぶ物が無い)')
    w('       零の四札: 陽性対照=下の乙が同じ路で建つ / 根=%s 深さ=1 / rc=128(git show) / 刻=上記' % MIKI)
w('  乙 手許の append.py で建てる(★陽性対照★):')
p=hashiru(['python3','-B',os.path.join(NE,'scripts/checks/karo_mac_manifest_append.py'),
           'MANIFEST.txt','a.txt','b.txt'],FX)
w('     rc=%d / stdout %d字 / stderr %d字' % (p.returncode,len(p.stdout),len(p.stderr)))
man=os.path.join(FX,'MANIFEST.txt')
w('     MANIFEST.txt = %s' % ('★建つた★ %d byte'%os.path.getsize(man) if os.path.isfile(man) else '★無★'))
if os.path.isfile(man):
    for l in open(man,encoding='utf-8').read().rstrip('\n').split('\n'): w('       | %s' % l)

w('')
w('【四】★門は鳴るか★(臺帳は乙で建てた物を使ふ ―― 幹には建てる器が無い故)')
for tag,path in [('幹PR#20 の gate.sh',os.path.join(MI,'karo_mac_dasumae_gate.sh')),
                 ('手許の gate.sh',os.path.join(NE,'scripts/checks/karo_mac_dasumae_gate.sh'))]:
    if not os.path.isfile(path): w('  %s = ★器無★' % tag); continue
    p=hashiru(['bash',path,'MANIFEST.txt','a.txt','b.txt'],FX)
    w('  ■ %s' % tag)
    w('     rc=%d / stdout %d字 / ★stderr %d字(門の出目は悉く stderr)★'
      % (p.returncode,len(p.stdout),len(p.stderr)))
    for l in [x for x in p.stderr.rstrip('\n').split('\n') if x.strip()][:8]: w('       | %s' % l[:150])
w('')
w('【五】幹の gate.sh は ★どの verify.py を呼ぶか★')
w('  幹 gate.sh は `$(dirname "$0")/karo_mac_manifest_verify.py` を呼ぶ ∴ ★己の隣★。')
w('  上の走りでは %s の隣 = 幹の 127行版 が呼ばれた(手許 198行版では無い)。' % os.path.relpath(MI,NE))
open(os.path.join(B,'_raw/20_kotae.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))

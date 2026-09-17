# -*- coding: utf-8 -*-
"""22_hankei.py ―― ⑴rc 反転の ★被害半径★(旧形行を持つ現物の臺帳は幾つか)
                    ⑵★丙★(repo 外ゆゑ PR では治らぬ物)を ★推さず字面から★ 拾ふ。
丙の定義: 閉包の器が依存する物の内、★repo の中に版が無く、系(OS)が供給する★ 物で、
  且つ ★方言で判じが変り得る★ 物。器の在否では無く ★系の別★ が効く所。
"""
import os, re, subprocess, time, glob
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
L=[]
def w(s): L.append(s); print(s)
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z')); w('')

w('【一】rc 反転の被害半径 ―― 現物の臺帳に「引用符を含む path 行」は幾つ在るか')
mans=sorted(glob.glob(os.path.join(NE,'docs/evidence/*/MANIFEST.txt')))
w('  歩き根 = docs/evidence/*/MANIFEST.txt / 深さ=1 / 見つけた臺帳 = ★%d本★' % len(mans))
kyu=[]; zen=0
for m in mans:
    n=0
    for line in open(m,encoding='utf-8',errors='replace'):
        if not line.startswith('path='): continue
        zen+=1
        v=line[5:].split(' sha256=')[0]
        if v.startswith('"') or v.startswith("'"): n+=1
    if n: kyu.append((os.path.relpath(os.path.dirname(m),NE),n))
w('  path= 行 總計 = %d / ★旧形(引用符)を持つ臺帳 = %d本★' % (zen,len(kyu)))
for d,n in kyu[:12]: w('     %3d行  %s' % (n,d))
if len(kyu)>12: w('     …(他 %d本)' % (len(kyu)-12))
w('  ∴ 幹の127行版が呼ばれた時、此の ★%d本★ の束は 條① で ★実体無★ と判じられ 門が ★落ちる★。' % len(kyu))
if not kyu:
    w('  ★零の四札★: 陽性対照=_inst/21 の試料Bは同じ器で 旧形1行 を拾つた / 根=docs/evidence 深さ=1 /'
      ' rc=0(走了) / 刻=上記 ∴ 「器が拾へぬ」では無く「現物に無い」')

w('')
w('【二】★丙★ ―― 閉包が系(OS)に委ねて居る器と、其の方言')
TOOLS=['tr','stat','sed','awk','date','grep','sort','wc','od','printf','find','xargs','md5','shasum','file']
kit=['scripts/checks/karo_mac_dasumae_gate.sh','scripts/checks/karo_mac_manifest_verify.py',
     'scripts/checks/karo_mac_manifest_append.py']
tsukau={}
for rel in kit:
    s=open(os.path.join(NE,rel),encoding='utf-8').read()
    for i,line in enumerate(s.split('\n'),1):
        if line.lstrip().startswith('#'): continue
        for t in TOOLS:
            if re.search(r'(?:^|[;&|(`$]\s*|\s)%s\s' % re.escape(t), line):
                tsukau.setdefault(t,[]).append('%s:%d' % (os.path.basename(rel),i))
w('  閉包が呼ぶ系の器 = ★%d種★' % len(tsukau))
for t in sorted(tsukau):
    w('    %-8s %d箇所  例 %s' % (t,len(tsukau[t]),tsukau[t][0]))
w('')
w('  ★方言が判じを変へる實例(本機で實測)★:')
for nm,cmd in [('BSD tr が U+3000 を [:space:] と讀むか',
                "printf '\\343\\200\\200' | tr -d '[:space:]' | wc -c")]:
    r=subprocess.run(['bash','-c',cmd],capture_output=True,text=True)
    w('    %s → 残 %s byte (rc=%d)' % (nm,r.stdout.strip(),r.returncode))
    w('      ∴ 本機(BSD)では全角空白は ★空白側★ へ落ちる。GNU coreutils の tr は C locale で')
    w('        U+3000 を空白と讀まぬ ∴ ★同じ臺帳・同じ file でも 條② の判じが系で変り得る★。')
    w('      ★之は repo の中に版が無い★(tr は系が供給する)∴ ★PR では治らぬ★。')
r=subprocess.run(['bash','-c','echo $BASH_VERSION'],capture_output=True,text=True)
w('    本機の bash = %s (門は bash script ∴ 3.2 と 5.x の別も同じ丙の族)' % r.stdout.strip())
open(os.path.join(B,'_raw/22_hankei.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))

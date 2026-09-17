# -*- coding: utf-8 -*-
"""01_uraura.py ―― 00 の閉包を ★別の規★ で裏から検める。
00 は「呼出の形」で拾つた。此方は ★字面に現れる .py/.sh の basename を悉く★ 拾ひ、
scripts/checks に実在する物へ写す。★00 より広く出る筈★(註・usage・bak も拾ふ)。
広い側が狭い側を ★含む★ 事を検め、含まぬ物が在れば 00 の漏れである。
併せて 陽性対照 _fixture/09_taisho.sh を 00 の規で走らせ、★4件拾ひ・註の1件は拾はぬ★を確かめる。
"""
import os, re, sys, subprocess
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
KIT=['scripts/checks/karo_mac_manifest_append.py','scripts/checks/karo_mac_dasumae_gate.sh',
     'scripts/checks/karo_mac_manifest_verify.py']
L=[]
def w(s): L.append(s); print(s)

w('★裏の規★ 字面の basename を悉く拾ふ(註も usage も含む)')
hiroi=set()
for rel in KIT:
    s=open(os.path.join(NE,rel),encoding='utf-8',errors='replace').read()
    for m in re.finditer(r'[A-Za-z0-9_.\-]+\.(?:py|sh)', s):
        b=m.group(0)
        if os.path.exists(os.path.join(NE,'scripts/checks',b)):
            hiroi.add('scripts/checks/'+b)
semai=set(KIT)
w('  裏(字面)=%d本 / 表(呼出)=%d本' % (len(hiroi),len(semai)))
w('  裏のみ(=00 が拾はなんだ物):')
for x in sorted(hiroi-semai): w('    %s' % x)
w('  表のみ(=裏が拾はなんだ物 ★0 が正★):')
for x in sorted(semai-hiroi): w('    %s' % x)
w('  ★判じ★ 表 ⊆ 裏 = %s' % ('★是★' if not (semai-hiroi) else '★非★'))

w('')
w('★陽性対照★ _fixture/09_taisho.sh を 00 と同じ規で走らせる')
SH=[(r'\$\(dirname\s+"?\$0"?\)/([A-Za-z0-9_.\-]+)','dirname相対'),
    (r'(?:^|[;&|(]\s*|\s)(?:python3|python|bash|sh)\s+"?([A-Za-z0-9_./\-${}"]*[A-Za-z0-9_.\-]+\.(?:py|sh))"?','直呼び'),
    (r'(?:^|\s)(?:source|\.)\s+"?([A-Za-z0-9_./\-${}"]*[A-Za-z0-9_.\-]+\.(?:sh|bash))"?','読込み')]
s=open(os.path.join(B,'_fixture/09_taisho.sh'),encoding='utf-8').read()
hit=[]
for i,line in enumerate(s.split('\n'),1):
    if line.lstrip().startswith('#'): continue
    for pat,kind in SH:
        for m in re.finditer(pat,line,re.M): hit.append((i,kind,m.group(1)))
for h in hit: w('   拾つた: %d行 [%s] %s' % h)
w('  拾つた数 = ★%d★ (期待 4)' % len(hit))
w('  註の中の gate7 を拾つたか = %s (★拾はぬ★が正)'
  % ('★拾つた★' if any('gate7' in h[2] for h in hit) else '拾はず'))
ok = (len(hit)==4) and not any('gate7' in h[2] for h in hit) and not (semai-hiroi)
w('')
w('★対照の結★ = %s' % ('★通★' if ok else '★落★'))
open(os.path.join(B,'_raw/03_uraura.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))
sys.exit(0 if ok else 1)

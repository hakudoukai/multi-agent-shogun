# -*- coding: utf-8 -*-
"""usage: 92_mon.py  ―― 束の中で走らせ、出す前 門 を掛ける。
門の usage 逐語: karo_mac_dasumae_gate.sh <manifest> <path...>。
★束内相対の臺帳は KM_GATE_MANIFEST_BASE に束の根(絶対)を与へねば條①が悉く落ちる★(實測・記憶)。
出目は悉く stderr。rc は pipe を通さず取る。
"""
import os, subprocess
root=os.getcwd(); assert os.path.basename(root).startswith('km-54'), root
fs=[l.split(' ',1)[0][5:] for l in open('_manifest.txt',encoding='utf-8') if l.startswith('path=')]
NOZOKU=[x for x in fs if x.endswith(('.first','.second','.third'))]
watasu=[x for x in fs if x not in NOZOKU]
print('臺帳の紙=%d / ★門の argv から除く=%d★' % (len(fs),len(NOZOKU)))
for x in NOZOKU: print('  除く: %s ―― 倒れた走の控(作法⑺・其の儘が證)' % x)
print('門へ渡す紙=%d' % len(watasu))
e=dict(os.environ); e['KM_GATE_MANIFEST_BASE']=root
r=subprocess.run(['bash','/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_dasumae_gate.sh',
                  '_manifest.txt']+watasu, capture_output=True, env=e)
open('_gate/92_gate.err','w',encoding='utf-8').write(r.stderr.decode('utf-8','replace') or '★空である旨★ stderr に一字も無し\n')
open('_gate/92_gate.out','w',encoding='utf-8').write(r.stdout.decode('utf-8','replace') or '★空である旨★ stdout に一字も無し\n')
open('_gate/92_gate.rc','w',encoding='utf-8').write('%d\n' % r.returncode)
print(r.stderr.decode('utf-8','replace'))
print('★門 rc=%d★' % r.returncode)

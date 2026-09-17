# -*- coding: utf-8 -*-
"""92b_taishou.py ―― ★陽性対照★ 「門は本当に鳴るか」を己の疵で確かめる。
  本器は 92_mon.py が一度踏んだ疵 ―― 臺帳の行を `ln[5:]` で切り、
  「raw/foo.tsv sha256=… bytes=… lines=…」を丸ごと file 名として門へ渡す ―― を
  ★態と★ 再現し、門が rc≠0 で落ちる事を示す。
  ★之は元の落ちた控の復元では無い。★ 元の控(15:07:08)は本器が臺帳を建てる前に
  己が消したゆゑ物として残つて居らぬ ―― 其の事も紙に書く。
"""
import os, subprocess, time

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
assert os.path.basename(ROOT).startswith('a2_km-101-'), ROOT
os.chdir(ROOT)
GATE = '/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_dasumae_gate.sh'
MAN = '_manifest.txt'

argv = [ln.rstrip('\n')[len('path='):] for ln in open(MAN, encoding='utf-8') if ln.startswith('path=')]
stamp = time.strftime('%Y%m%dT%H%M%S')
base = os.path.join('_gate', '92b_taishou_%s' % stamp)
e = dict(os.environ); e['KM_GATE_MANIFEST_BASE'] = '.'
with open(base + '.out', 'wb') as o, open(base + '.err', 'wb') as r:
    p = subprocess.run(['bash', GATE, MAN] + argv, stdout=o, stderr=r, env=e)
open(base + '.rc', 'w').write('%d\n' % p.returncode)
err = open(base + '.err', encoding='utf-8').read()
nari = err.count('★條⑤ 測れぬ')
print('陽性対照 rc=%d(★0 なら器が鳴らぬ＝器を疑へ★) / 條⑤「測れぬ」の鳴り=%d 本' % (p.returncode, nari))
print('控=%s.{out,err,rc}' % base)
assert p.returncode != 0, '★対照が鳴らぬ。門を信じるな。★'
print('★對照 鳴る ―― ∴ 本番 rc=0 は「測つた上で疵が無い」の意である。★')

# -*- coding: utf-8 -*-
"""92_mon.py ―― 出す前門を ★KM_GATE_MANIFEST_BASE 付き★ で通す。
  ★臺帳が束内相対ゆゑ base を渡さねば條①が悉く落ちる。★
  控の名は run ごとに一意(刻を入れる) ―― 前の run の控を上書きして「通つた」に見せぬ為。
"""
import os, re, subprocess, sys, time

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
assert os.path.basename(ROOT).startswith('a2_km-101-'), ROOT
os.chdir(ROOT)
GATE = '/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_dasumae_gate.sh'
MAN = '_manifest.txt'
os.makedirs('_gate', exist_ok=True)

# ★臺帳の行は四欄(path= sha256= bytes= lines=)★ ―― path だけを切り出す。
# ★`ln[5:]` の如く行の残り悉くを path と見做せば、門は「sha256=… を名に持つ file」を
#   探して悉く★測れぬ★で落ちる(本器で一度踏んだ疵。逐語で残す)。★
ROW = re.compile(r'^path=(.*) sha256=[0-9a-f]{64} bytes=[0-9]+ lines=[0-9]+$')
argv, kake = [], 0
for ln in open(MAN, encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.startswith('path='): continue
    m = ROW.match(ln)
    if not m:
        print('★四欄に当たらぬ行(渡さぬ)★:', ln); kake += 1; continue
    q = m.group(1)
    if len(q) >= 2 and q[0] == '"' and q[-1] == '"':   # 空白名は括られて居る
        q = q[1:-1]
    argv.append(q)
argv.sort()
print('門へ渡す file 数=%d / 四欄に当たらぬ行=%d' % (len(argv), kake))
assert kake == 0, kake

stamp = time.strftime('%Y%m%dT%H%M%S')
base = os.path.join('_gate', '92_gate_%s' % stamp)
e = dict(os.environ)
e['KM_GATE_MANIFEST_BASE'] = '.'          # ★束内相対★
with open(base + '.out', 'wb') as o, open(base + '.err', 'wb') as r:
    p = subprocess.run(['bash', GATE, MAN] + argv, stdout=o, stderr=r, env=e)
open(base + '.rc', 'w').write('%d\n' % p.returncode)
print('控=%s.{out,err,rc} / rc=%d' % (base, p.returncode))
print('★rc は pipe を通さず subprocess の returncode を直に書いた。★')

err = open(base + '.err', encoding='utf-8').read()
import re
j1 = len(re.findall(r'條①', err))
print('---- 控(err)の尾 ----')
print('\n'.join(err.rstrip('\n').split('\n')[-14:]))
print('---- 條①の語が出た行数=%d ----' % j1)

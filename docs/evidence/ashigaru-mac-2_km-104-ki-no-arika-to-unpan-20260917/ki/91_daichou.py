# -*- coding: utf-8 -*-
"""91_daichou.py ―― ★束内相対★の臺帳を建てる(總監督裁 seq322699)。
  cd <束> してから karo_mac_manifest_append.py を呼ぶゆゑ path= は束の根起し。
  ★己(91_daichou.py)も臺帳に載る★。0byte(條④)と _manifest.txt 自身と __pycache__ は除く。
"""
import os, subprocess, sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
assert os.path.basename(ROOT).startswith('ashigaru-mac-2_km-104-'), ROOT
os.chdir(ROOT)                      # ★束内相対の肝★
MAN = '_manifest.txt'
APP = '/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_manifest_append.py'

files = []
for d, ds, fs in os.walk('.'):
    # ★_gate は臺帳の外に置く★ ―― 門控は★臺帳を建てた後★に生まれる物ゆゑ、
    # 臺帳へ入れれば「己を照合する」輪に成り條①が必ず崩れる。除いた事は紙に書く。
    ds[:] = [x for x in ds if x not in ('__pycache__', '_gate')]
    for f in fs:
        p = os.path.normpath(os.path.join(d, f))
        if p == MAN: continue
        if os.path.getsize(p) == 0:
            print('★0byte ゆゑ臺帳から除く(條④)★:', p); continue
        files.append(p)
files.sort()
print('臺帳に載せる file 数=%d' % len(files))

if os.path.exists(MAN): os.remove(MAN)
r = subprocess.run(['/opt/homebrew/bin/python3', '-B', APP, MAN] + files)
print('append rc=%d' % r.returncode)
assert r.returncode == 0, r.returncode

rows = sum(1 for ln in open(MAN, encoding='utf-8') if ln.startswith('path='))
print('臺帳の path= 行数=%d / 載せた file 数=%d' % (rows, len(files)))
assert rows == len(files), (rows, len(files))
print('★一致★')

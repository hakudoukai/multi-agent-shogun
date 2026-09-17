# -*- coding: utf-8 -*-
"""臺帳を建てる。★新法・總監督裁 seq322699★ ―― cwd を本束に置いてから呼ぶ ∴ path は束内相対。
usage: (cd <本束> && python3 -B ki/91_daichou.py)
"""
import os, subprocess, sys
assert os.path.basename(os.getcwd()).startswith('km-54'), '★本束の中で走らせよ★: ' + os.getcwd()
fs = []
for r, ds, ns in os.walk('.'):
    ds[:] = [d for d in ds if d != '__pycache__']
    for n in ns:
        p = os.path.relpath(os.path.join(r, n), '.')
        if p == '_manifest.txt':
            continue
        if os.path.getsize(p) == 0:
            print('★0byte ゆゑ臺帳から除く(條④)★ ' + p); continue
        fs.append(p)
fs.sort()
if os.path.exists('_manifest.txt'):
    os.remove('_manifest.txt')
r = subprocess.run(['/opt/homebrew/bin/python3',
    '/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_manifest_append.py',
    '_manifest.txt'] + fs, capture_output=True, text=True)
sys.stdout.write(r.stdout); sys.stderr.write(r.stderr)
assert r.returncode == 0, '★append rc=%d★' % r.returncode
L = open('_manifest.txt', encoding='utf-8').read().split(chr(10))
kan = [l for l in L if l.startswith('#')]
gyo = [l for l in L if l.startswith('path=')]
assert len(gyo) == len(fs), '★行 %d ≠ 紙 %d★' % (len(gyo), len(fs))
print('冠=%d 行=%d 紙=%d' % (len(kan), len(gyo), len(fs)))

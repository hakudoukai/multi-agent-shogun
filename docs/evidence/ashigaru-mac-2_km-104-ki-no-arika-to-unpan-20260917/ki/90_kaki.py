# -*- coding: utf-8 -*-
"""90_kaki.py ―― raw/紙/器 の末尾を揃へる(條②③④の前捌き)。
  ・各行の末尾の空白・TAB・CR を落とす
  ・EOF の改行は★丁度一つ★
  ・0byte は作らぬ(元が 0byte なら其の旨を刷る)
  ★変はつた時のみ★ 元を <name>.first に残す(既に .first が在れば上書きせぬ)。
  ★己(90_kaki.py)と .first と __pycache__ は歩かぬ。★
"""
import io, os, sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SELF = os.path.abspath(__file__)
assert os.path.basename(ROOT).startswith('ashigaru-mac-2_km-104-'), ROOT
os.chdir(ROOT)

tgt = []
for d, ds, fs in os.walk('.'):
    ds[:] = [x for x in ds if x not in ('__pycache__', '_gate')]
    for f in fs:
        p = os.path.join(d, f)
        if os.path.abspath(p) == SELF: continue
        if f.endswith('.first'): continue
        if f == '_manifest.txt': continue
        tgt.append(p)
tgt.sort()

naoshi = zero = 0
for p in tgt:
    b = open(p, 'rb').read()
    if not b:
        print('★0byte★(觸らぬ):', p); zero += 1; continue
    t = b.decode('utf-8')
    lines = [ln.rstrip(' \t\r') for ln in t.split('\n')]
    while lines and lines[-1] == '': lines.pop()
    out = ('\n'.join(lines) + '\n').encode('utf-8')
    if out != b:
        fst = p + '.first'
        if not os.path.exists(fst):
            open(fst, 'wb').write(b)
        open(p, 'wb').write(out)
        naoshi += 1
        print('直し:', p, len(b), '->', len(out))

print('歩いた file 数=%d / 直した=%d / 0byte=%d' % (len(tgt), naoshi, zero))
print('★直し 0 は「歩かなかつた」の意に非ず ―― 歩いた上で疵が無かつたの意である。★')

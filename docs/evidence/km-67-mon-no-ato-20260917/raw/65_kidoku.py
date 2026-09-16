# -*- coding: utf-8 -*-
"""己の箱の既讀化 65(第67弾・66 §8-1 の疵を直す = 手でなく器で)。札の便 id を引き、其の entry の '  read: false' 一つだけを '  read: true' に替へる(己の箱のみ・他は 0 字)。前後の状態と箱の bytes を raw/65_kidoku.txt に。"""
import sys, os, time
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ID = sys.argv[1]; p = M + '/queue/inbox/ashigaru-mac-1.yaml'; s = open(p, encoding='utf-8').read(); n0 = len(s.encode())
i = s.find(f'  id: {ID}\n'); assert i >= 0, 'id 無'; j = s.rfind('\n- content:', 0, i); k = s.find('\n- content:', i); seg = s[j:k if k >= 0 else len(s)]
before = 'true' if '\n  read: true\n' in seg else ('false' if '\n  read: false\n' in seg else '?')
if before == 'false':
    seg2 = seg.replace('\n  read: false\n', '\n  read: true\n', 1); s2 = s[:j] + seg2 + s[k if k >= 0 else len(s):]
    with open(p, 'w', encoding='utf-8', newline='') as fh: fh.write(s2)
s3 = open(p, encoding='utf-8').read(); i3 = s3.find(f'  id: {ID}\n'); j3 = s3.rfind('\n- content:', 0, i3); k3 = s3.find('\n- content:', i3); seg3 = s3[j3:k3 if k3 >= 0 else len(s3)]
after = 'true' if '\n  read: true\n' in seg3 else ('false' if '\n  read: false\n' in seg3 else '?')
K.kaku(E + '/65_kidoku.txt', f'{time.strftime("%Y-%m-%dT%H:%M:%S%z")}\n箱 queue/inbox/ashigaru-mac-1.yaml / id {ID} / read: {before} → {after}(器 65 が替へた・己の箱のみ)/ 箱の bytes {n0} → {len(s3.encode())}(差 {len(s3.encode()) - n0} = "false"→"true" の 1 byte 減 が期待)/ read: false の entry(鍵で数へた) {s.count(chr(10) + "  read: false" + chr(10))} → {s3.count(chr(10) + "  read: false" + chr(10))}')
print(open(E + '/65_kidoku.txt', encoding='utf-8').read()); sys.exit(0 if after == 'true' else 7)

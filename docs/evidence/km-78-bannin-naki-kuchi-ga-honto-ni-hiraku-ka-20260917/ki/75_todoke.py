# -*- coding: utf-8 -*-
"""75 届けの覚 ―― ★送出の rc ではなく、受手の箱の胴で検める★"""
import io, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = io.open('/Users/momizimac/multi-agent-shogun/queue/inbox/karo-mac.yaml', encoding='utf-8').read().split('\n')
ko = [i for i, l in enumerate(L) if l.startswith('- content:')]
hit = []
for n, j in enumerate(ko):
    e = ko[n + 1] if n + 1 < len(ko) else len(L)
    blob = '\n'.join(L[j:e])
    fr = re.search(r'^  from: (\S+)', blob, re.M)
    if not fr or fr.group(1) != 'ashigaru-mac-2':
        continue
    m = re.search(r'納め(\d+)/(\d+)', blob)
    ts = re.search(r"^  timestamp: '([^']+)'", blob, re.M)
    if m:
        hit.append((int(m.group(1)), m.group(2), ts.group(1) if ts else '?', j))
o = ['# 75 届け ―― ★受手(karo-mac)の箱の胴で検めた★(送出 rc は届けの証に非ず)', '']
o.append('家老箱の項 = %d' % len(ko))
o.append('from=ashigaru-mac-2 の 納め = %d通' % len(hit))
for a, b, ts, j in sorted(hit):
    o.append('    納め%d/%s  %s  (箱の行 %d)' % (a, b, ts, j))
o.append('')
o.append('番の重複 = %s / 欠番 = %s'
         % (len(hit) != len(set(x[0] for x in hit)),
            sorted(set(range(1, len(hit) + 1)) - set(x[0] for x in hit)) or '無'))
o.append('')
o.append('★断り★ 箱は追記して回転する ∴ ★尾は時順に非ず★。')
o.append('        現に尾の 納め5/6・6/6 は ★專任3 の便★(07:02)であつて當席の物ではない。')
o.append('        ∴ 「尾を見て着いた」と書いてはならぬ ―― from と刻で引くべきである。')
K.kaku(B + '/raw/75_todoke.txt', '\n'.join(o))
print('納め %d通 / 重複=%s' % (len(hit), len(hit) != len(set(x[0] for x in hit))))

# -*- coding: utf-8 -*-
"""05 着手便の控(第74弾)―― 08:5x に bash で出した着手便を家老の箱から引き、id・刻・胴の字数を記す(★便は既に出て居る・再送せぬ★)。"""
import sys, time, re
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
raw = open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8').read() + open(M + '/queue/inbox/_archive/karo-mac_pruned.yaml', encoding='utf-8').read(); ps = raw.split('\n- content: ')[1:]  # 箱は 08:58:26 に回転し着手便は archive へ落ちた ―― 両方を引く  # 箱は鍵で数へる: 項は「- content:」起し
ms = [{'content': q.split('\n  expires_at:')[0], 'from': (re.search(r'\n  from: (\S+)', q) or [None, ''])[1], 'id': (re.search(r'\n  id: (\S+)', q) or [None, ''])[1], 'timestamp': (re.search(r"\n  timestamp: '([^']+)'", q) or [None, ''])[1], 'type': (re.search(r'\n  type: (\S+)', q) or [None, ''])[1]} for q in ps]
hit = [m for m in ms if m['from'] == 'ashigaru-mac-1' and '第74弾 着手報' in m['content']]
out = [f'# 05 着手便の控 / 刻(此の控を書いた) {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 家老箱+archive の便 母數 {len(ms)} / 己の第74弾着手便 {len(hit)} 本']
for m in hit: out.append(f'  id {m.get("id")} timestamp {m.get("timestamp")} type {m.get("type")} 字数 {len(str(m.get("content","")))}(★300 字の條を越えて居る= {"是・疵" if len(str(m.get("content",""))) > 300 else "否"}★)')
out.append('宣ETA= 11:00:00(起点= 着手便の timestamp・端点= 納め最終便の timestamp) ―― 根= 第73弾 實 29.52 分(宣 4 分)・第72弾も過小ゆゑ本弾は 2 時間を宣した')
K.kaku(D + '/raw/05_chakushu.txt', '\n'.join(out)); print('\n'.join(out))

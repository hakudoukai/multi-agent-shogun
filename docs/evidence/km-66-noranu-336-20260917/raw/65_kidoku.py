# -*- coding: utf-8 -*-
"""己の箱の既讀化の記録 65(第66弾)―― 本弾の auto-recovery 便(id msg_auto_recovery_20260917_023817_df8c9e7f・type task_assigned)は束を建てる前(02:38)に手(python 一行)で read: true にした ∴ 此の器は書かず id で引いて状態を讀み返すのみ(己の箱にも 0 字)。手で替へた事は紙の ㋕ に疵として書く。"""
import sys, os, time
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ID = 'msg_auto_recovery_20260917_023817_df8c9e7f'; p = M + '/queue/inbox/ashigaru-mac-1.yaml'; s = open(p, encoding='utf-8').read()
i = s.find(f'  id: {ID}\n'); assert i >= 0, 'id 無'; k = s.find('\n- content:', i); seg = s[i:k if k >= 0 else len(s)]
state = 'true' if '  read: true\n' in seg else ('false' if '  read: false\n' in seg else '?')
K.kaku(E + '/65_kidoku.txt', f'{time.strftime("%Y-%m-%dT%H:%M:%S%z")}\n箱 queue/inbox/ashigaru-mac-1.yaml / id {ID} / read: {state}(讀み返しのみ・此の器は 0 字書かぬ)/ 既讀化は 02:38 に手で行つた(束の前・器 65 の外 = 疵)/ 箱の bytes {len(s.encode())} / read: false の entry(鍵で数へた) {s.count(chr(10) + "  read: false" + chr(10))}')
print(open(E + '/65_kidoku.txt', encoding='utf-8').read())

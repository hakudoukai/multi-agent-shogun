# -*- coding: utf-8 -*-
"""01 着手便(第76弾 km-80)―― 胴を組み、★字数を二器(python len / wc -m)で測り★、先送り語の門を通してから inbox_write。送出後に箱から id と timestamp を讀み返す(第八の番人)。宣ETA の起点= 此の便の timestamp。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'
body = ("[第76弾 km-80 着手] 札 cc538102168bd323 48行 受。的= scripts/inbox_watcher.sh 一本(ASW_PROCESS_TIMEOUT 受L224/比L1599・守る表L173-175 ―― 行番号は己の器で引き直す)。"
        "稼働watcher 3本(inode 20564860/74274B)≠disk(22062559/80724B)を既に測つた。毒六形は束内の写し器へ当てる(repo 0字・watcher不觸)。"
        "宣ETA 12分(新規器5×0.5+写し5×0.1+紙5+便門3・切上)・起点= 本便 timestamp。")
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
old = open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8').read(); m = re.search(r'msg_20260917_093253_d7b0fb48.*?\n  type: (\S+)', old, re.S); typ = m.group(1) if m else 'report_received'
naru = []
if not (40 <= n1 <= 300): naru.append(f'字数 {n1}')
if str(n1) != n2: naru.append(f'二器不一致 len {n1} / wc -m {n2}')
if q.returncode == 10: naru.append('先送り語 rc10 ' + q.stdout.decode('utf-8', 'replace')[:200])
print('字数 len', n1, '/ wc -m', n2, '/ deferral rc', q.returncode, '/ 前弾着手便の type', typ, '/ 門', naru or '通')
if naru: K.kaku(D + '/raw/01_letter.txt', '★門が鳴つた・送らず★ ' + str(naru) + '\n' + body); sys.exit(1)
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, typ, ME], capture_output=True, text=True, cwd=M)
box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
hits = [(re.search(r'\n  id: (\S+)', s), re.search(r"\n  timestamp: '([^']+)'", s)) for s in box.split('\n- content: ')[1:] if body[:40] in s]
ids = [(a.group(1), b.group(1)) for a, b in hits if a and b]
out = [f'# 01 着手便 / 送出刻(date) {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 {TO} / type {typ} / 字数 len {n1} = wc -m {n2} / deferral rc {q.returncode} / inbox_write rc {p.returncode}', f'第八の番人(箱 {TO}.yaml の胴の頭 40 字で引く)= {len(ids)} 本 {ids}', '★宣ETA 12 分・起点= 上の timestamp(箱の値)・端点= 納め最終便の timestamp★', body]
K.kaku(D + '/raw/01_letter.txt', '\n'.join(out)); print('\n'.join(out))

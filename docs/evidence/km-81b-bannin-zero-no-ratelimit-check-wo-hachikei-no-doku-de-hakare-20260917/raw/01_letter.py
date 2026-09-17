# -*- coding: utf-8 -*-
"""01 着手便(第77弾 km-81b)―― 胴を組み、★字数を二器(python len / wc -m)で測り★、先送り語の門を通してから inbox_write。送出後に箱から id と timestamp を讀み返す(第八の番人)。宣ETA の起点= 此の便の timestamp。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; TYP = 'task_started'
body = ("[第77弾 km-81b 着手] 札 2b8df2e59c8d4465 52行 受。的= scripts/ratelimit_check.sh 一本(disk=HEAD=main sha16 7f1e0311・582行)。"
        "起で既に測つた: 此のMacの bash は /bin/bash 3.2 のみ(的の declare -A L64 は通らず)・source する scripts/lib 三本が disk に無し ∴ 此の checkout では的は L28 で止まる。"
        "毒八形は束内の写し器へ(repo 0字・据ゑず)。宣ETA 30分・起点= 本便 timestamp。")
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
naru = []
if not (40 <= n1 <= 300): naru.append(f'字数 {n1}')
if str(n1) != n2: naru.append(f'二器不一致 len {n1} / wc -m {n2}')
if q.returncode == 10: naru.append('先送り語 rc10 ' + q.stdout.decode('utf-8', 'replace')[:200])
print('字数 len', n1, '/ wc -m', n2, '/ deferral rc', q.returncode, '/ 門', naru or '通')
if naru: K.kaku(D + '/raw/01_letter.txt', '★門が鳴つた・送らず★ ' + str(naru) + '\n' + body); sys.exit(1)
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, TYP, ME], capture_output=True, text=True, cwd=M)
box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
hits = [(re.search(r'\n  id: (\S+)', s), re.search(r"\n  timestamp: '([^']+)'", s)) for s in box.split('\n- content: ')[1:] if body[:40] in s]
ids = [(a.group(1), b.group(1)) for a, b in hits if a and b]
out = [f'# 01 着手便 / 送出刻(date) {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 {TO} / type {TYP} / 字数 len {n1} = wc -m {n2} / deferral rc {q.returncode} / inbox_write rc {p.returncode}', f'第八の番人(箱 {TO}.yaml の胴の頭 40 字で引く)= {len(ids)} 本 {ids}', '★宣ETA 30 分・起点= 上の timestamp(箱の値)・端点= 納め最終便の timestamp★', body]
K.kaku(D + '/raw/01_letter.txt', '\n'.join(out)); print('\n'.join(out))

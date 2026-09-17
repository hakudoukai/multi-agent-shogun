# -*- coding: utf-8 -*-
"""01 着手便(第82弾 km-95)―― 胴を組み、字数を二器(python len / wc -m)で測り、先送り語の門を通してから inbox_write。送出後に箱から id と timestamp を讀み返す(第八の番人)。宣ETA は ★幅★・起点= 此の便の timestamp(箱の値)。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; TYP = 'task_started'
S = open(D + '/raw/00_start.txt', encoding='utf-8').read(); fs, fl = re.search(r'札 \S+ sha16 (\S+) (\d+)行', S).groups()
body = (f"[第82弾 km-95 着手] 札 {fs} {fl}行 受。ls-remote main=4be3ee19(写しと一致)・local 363d5fb0・家老紙 585eea9f 一致。先に測れた事: 分岐点 6e9d4060(=skills-tools 枝の tip)/ rev-list local16・origin21(内 merge11)/ cherry +14−2・+8−2 ∴ 14/8 は非merge patch-id の数。"
        "㋐〜㋔ を一本づつ名指しで測る(直さぬ・fetch/ref書換 0)。宣ETA 60〜150分(幅)・起点=本便 timestamp。")
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
naru = []
if not (40 <= n1 <= 300): naru.append(f'字数 {n1}')
if str(n1) != n2: naru.append(f'二器不一致 len {n1} / wc -m {n2}')
if q.returncode == 10: naru.append('先送り語 rc10 ' + q.stdout.decode('utf-8', 'replace')[:200])
print('字数 len', n1, '/ wc -m', n2, '/ deferral rc', q.returncode, '/ 門', naru or '通')
if naru or '--dry' in sys.argv: K.kaku(D + '/raw/01_letter.txt', ('★門が鳴つた・送らず★ ' + str(naru) if naru else '# dry') + '\n' + body); sys.exit(1 if naru else 0)
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, TYP, ME], capture_output=True, text=True, cwd=M)
box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
hits = [(re.search(r'\n  id: (\S+)', s), re.search(r"\n  timestamp: '([^']+)'", s)) for s in box.split('\n- content: ')[1:] if body[:40] in s]
ids = [(a.group(1), b.group(1)) for a, b in hits if a and b]
out = [f'# 01 着手便 / 送出刻(date) {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 {TO} / type {TYP} / 字数 len {n1} = wc -m {n2} / deferral rc {q.returncode} / inbox_write rc {p.returncode}', f'第八の番人(箱 {TO}.yaml の胴の頭 40 字で引く)= {len(ids)} 本 {ids}', '★宣ETA 60〜150 分(幅)・起点= 上の timestamp(箱の値)・端点= 納め最終便の timestamp★', body]
K.kaku(D + '/raw/01_letter.txt', '\n'.join(out)); print('\n'.join(out))

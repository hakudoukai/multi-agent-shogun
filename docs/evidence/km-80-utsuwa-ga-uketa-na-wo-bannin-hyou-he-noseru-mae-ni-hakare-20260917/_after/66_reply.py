# -*- coding: utf-8 -*-
"""66 追ひ便(第76弾 km-80・員外)―― 家老の再促 msg_20260917_100816_1f470164(着手便の再要求)へ、既に出た着手便 id・納め 5 通・監査 seq を指す一便。字数 二器・先送り語の門・第八の番人。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'
st = open(D + '/raw/01_letter.txt', encoding='utf-8').read(); st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", st).groups()
ids = re.findall(r"第八の番人= 1 本 \['(msg_\S+)'\]", open(D + '/_after/62_letters.txt', encoding='utf-8').read())
seq = re.search(r'seq (\d+)', open(D + '/_after/64_audit.txt', encoding='utf-8').read()).group(1)
body = f"[第76弾 km-80 追ひ・再促 1f470164 への返し] 着手便は {st_ts[11:19]} に出て居る({st_id})・宣ETA 12分。納め 5 通は 10:07:52-54({', '.join(i[-8:] for i in ids)})・監査は sb seq{seq}(gunshi-mac・parent 324588・讀み返し済)。nudge の落ちは己の箱では測れぬ(着手便の箱着は 01_letter.txt)。"
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
naru = ([f'字数 {n1}'] if not 40 <= n1 <= 300 else []) + ([f'二器 {n1}/{n2}'] if str(n1) != n2 else []) + (['先送り語'] if q.returncode == 10 else [])
print('字数', n1, n2, '門', naru or '通')
if naru: K.kaku(D + '/_after/66_reply.txt', '★鳴つた・送らず★ ' + str(naru) + '\n' + body); sys.exit(1)
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report_received', ME], capture_output=True, text=True, cwd=M)
box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read(); got = [re.search(r'\n  id: (\S+)', s).group(1) for s in box.split('\n- content: ')[1:] if body[:40] in s and re.search(r'\n  id: (\S+)', s)]
out = [f'# 66 追ひ便 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 {TO} / 字数 {n1} / rc {p.returncode} / 第八の番人 {len(got)} 本 {got}', body]; K.kaku(D + '/_after/66_reply.txt', '\n'.join(out)); print('\n'.join(out))

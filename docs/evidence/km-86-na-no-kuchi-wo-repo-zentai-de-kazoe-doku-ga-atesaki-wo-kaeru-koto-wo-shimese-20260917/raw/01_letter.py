# -*- coding: utf-8 -*-
"""01 着手便(第79弾 km-86)―― 胴を組み、字数を二器(python len / wc -m)で測り、先送り語の門を通してから inbox_write。送出後に箱から id と timestamp を讀み返す(第八の番人)。宣ETA は ★幅★・起点= 此の便の timestamp。數は 00 の出目から抽く。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; TYP = 'task_started'
S = open(D + '/raw/00_start.txt', encoding='utf-8').read(); g = lambda pat: re.search(pat, S).group(1)
fs, fl = g(r'sha16 (\S+) \d+行'), g(r'sha16 \S+ (\d+)行'); nA = g(r'を除き ★(\d+) 本★'); nB = g(r'rc 0\)= ★(\d+) 本★'); both = g(r'両方に在る (\d+) 本'); oA = g(r'根A にのみ在る (\d+) 本'); oB = g(r'根B にのみ在る (\d+) 本')
body = (f"[第79弾 km-86 着手] 札 {fs} {fl}行 受。二根を並べた: 根A=km-84 の根(追跡 sh/bash/py+shebang・docs/evidence/除く)={nA}本 / 根B=家老の根 `git ls-files -- '*.sh' '*.py'`={nB}本。"
        f"差=両方{both}・A のみ{oA}(.bash4+gradlew)・B のみ{oB}(悉く docs/evidence/)。主=根A で 493口を閾/旗/名/他へ排他に分け、名の口を写し器(tmux は echo stub)へ毒十形。"
        "宣ETA 90〜240分(幅)・起点=本便 timestamp。")
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
out = [f'# 01 着手便 / 送出刻(date) {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 {TO} / type {TYP} / 字数 len {n1} = wc -m {n2} / deferral rc {q.returncode} / inbox_write rc {p.returncode}', f'第八の番人(箱 {TO}.yaml の胴の頭 40 字で引く)= {len(ids)} 本 {ids}', '★宣ETA 90〜240 分(幅)・起点= 上の timestamp(箱の値)・端点= 納め最終便の timestamp★', body]
K.kaku(D + '/raw/01_letter.txt', '\n'.join(out)); print('\n'.join(out))

# -*- coding: utf-8 -*-
"""63 訂正便(第78弾 km-84・員外)―― 納め便 3/5(msg_20260917_111213_b2478899)の「file169本」は 62 の regex `file (\\d+) 本\\(shell` が 10_kuchi.txt の「歩いた file 169 本(shell 114 …」を先に拾つた誤り。正は「file 6 本(shell 15 名 …」。送つた便は直さず、元 id を名指して訂正便を出す。數は器の出目から抽く(同じ過ちを繰り返さぬ regex)。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'
T10 = open(D + '/raw/10_kuchi.txt', encoding='utf-8').read()
fl = re.search(r'旗 (\d+) 本\(file×名\) / file (\d+) 本\(shell (\d+) 名・python (\d+) 名\)', T10); wk = re.search(r'歩いた file (\d+) 本', T10)
body = (f"[第78弾 訂正・納め3/5 msg_20260917_111213_b2478899] 「file169本」は誤り(便の器の regex が『歩いた file {wk.group(1)} 本』を先に拾つた)。正= ★旗 {fl.group(1)} 本は file {fl.group(2)} 本(shell {fl.group(3)} 名・python {fl.group(4)} 名)に在る★。"
        f"母數の file 數 {wk.group(1)} は変はらぬ。紙(README ㊀-1)と 10_kuchi.txt は元より正。疵は _after/63_teisei.txt に残す(紙は門で凍結ゆゑ書き足さぬ)。")
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
naru = [x for x in ((f'字数 {n1}' if not 40 <= n1 <= 300 else ''), (f'二器 {n1}/{n2}' if str(n1) != n2 else ''), ('先送り語' if q.returncode == 10 else '')) if x]
print('字数', n1, n2, '門', naru or '通')
if naru: K.kaku(D + '/_after/63_teisei.txt', '★門が鳴つた・送らず★ ' + str(naru) + '\n' + body); sys.exit(1)
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report_received', ME], capture_output=True, text=True, cwd=M)
box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
ids = [re.search(r'\n  id: (\S+)', s).group(1) for s in box.split('\n- content: ')[1:] if body[:40] in s and re.search(r'\n  id: (\S+)', s)]
out = [f'# 63 訂正便 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 {TO} / 字数 {n1} / inbox_write rc {p.returncode} / 第八の番人 {len(ids)} 本 {ids}', '疵⑬(62): 便3 の「file169本」は regex `file (\\d+) 本\\(shell` の緩さ(10_kuchi.txt の先の行「歩いた file 169 本(shell 114 / python 55)」に当たる)。紙の數は 70 が検めたが ★便の數は 70 の外★ であつた ―― 便の數も同じ照合に乗せるべきであつた。', body]
K.kaku(D + '/_after/63_teisei.txt', '\n'.join(out)); print('\n'.join(out))

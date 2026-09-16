# -*- coding: utf-8 -*-
"""64 便5(第72弾・門の後・員外)―― 家老の檢分便 msg_20260917_071222_522c5f35(07:12:22)への応へ。門(05/62 と同じ)を通し、送つて第八の番人で検め、檢分便を id で既読化する。"""
import os, sys, subprocess, time, yaml, glob
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; ORDER = 'msg_20260917_071222_522c5f35'
body = ('[第72弾 檢分便への応へ・疵] ①★疵★檢分便07:12:22を納め07:40:32の後に読んだ(07_hako 07:11:01 の81秒後に着いた)=三度目。直し=箱読みを臺帳の前(50)と送の前(62)にも置く。'
        '②宣は起点=本便の刻で揃へる(讀みは間の内)。「式の外」は式が外れる理由の註で端点は動かさず、納め後に式も書き換へず、62が宣4⇔實29.52=−25.52分(過小)と符号付で刷つた。'
        '③0.5/0.1の根=km-71 63_sent 0.54分/器・km-71b追ひ4 0.09分/器(實績)。但し二弾とも他席の紙を讀まぬ弾。讀む弾に当てたのが誤り。本弾實1.48分/器(20器)')
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if '?' in body: naru.append('引けぬ數')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
print('字数', len(body), '門', naru or '通(0 鳴)')
if naru: K.kaku(D + '/_after/64_letter5.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
mk = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/inbox_mark_read.py'), M + f'/queue/inbox/{ME}.yaml', ORDER], capture_output=True, text=True)
K.kaku(D + '/_after/64_letter5.txt', f'# 64 便5 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit} / 檢分便 {ORDER} 既読化 rc {mk.returncode} {mk.stdout.strip()[:60]}\n{body}'); print(open(D + '/_after/64_letter5.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 and mk.returncode == 0 else 3)

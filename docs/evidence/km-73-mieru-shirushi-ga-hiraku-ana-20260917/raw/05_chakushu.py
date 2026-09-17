# -*- coding: utf-8 -*-
"""05 着手便(第73弾・札 msg_20260917_075540_aad045fe への応へ・km-72 の写し)。宣 = 器 16 本(新規 6: 10/20/30/40/45/70 + 写し 10: 00/05/07/kaki/50/59/60/62/67/96)× 己の第72弾實績 1.48 分/器(讀みの刻を含む) = 23.68 → 24 分。端点 = 納め最終便を inbox_write.sh へ渡す直前の date 刻。"""
import os, sys, subprocess, time, yaml, glob, datetime as dt
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); SEN = 24; eta = (dt.datetime.strptime(koku[:19], '%Y-%m-%dT%H:%M:%S') + dt.timedelta(minutes=SEN)).strftime('%H:%M:%S')
body = (f'★着手★ 第73弾 km-73(可視印が開ける穴)work_started={koku[:16]} 宣ETA={eta}(起点=本便の刻・端点=納め最終便を inbox_write.sh へ渡す直前の date 刻・宣=器16本(新規6+写し10)×己の第72弾實績1.48分/器=23.68→24分)。'
        f'的=專任2 km-53b 案乙 ${{v//$\'\\n\'/␊}} を八問(再現/残る制御字/sh可否/桁/曖昧/三案表/意味せぬ/宣)で破る。生器・彼の束へ0字。在處=docs/evidence/km-73-mieru-shirushi-ga-hiraku-ana-20260917/')
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if '?' in body: naru.append('引けぬ數')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
print('字数', len(body), '門', naru or '通(0 鳴)')
if naru: K.kaku(RAW + '/05_chakushu.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
K.kaku(RAW + '/05_chakushu_koku.txt', koku); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
K.kaku(RAW + '/05_chakushu.txt', f'# 05 着手便 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit} / 札 msg_20260917_075540_aad045fe は復帰時 07:57 に inbox_mark_read.py で既読化済(07 が箱で検める)\n{body}'); print(open(RAW + '/05_chakushu.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)

# -*- coding: utf-8 -*-
"""05 着手便(第71弾 補・改め便 msg_20260917_064406_177f8cee への応へ)。宣 = 新規の器 2(05/70)× 1.2 分 + 写し 6(50/59/60/62/67/96)× 0.2 分 = 3.6 → 4 分(追ひ6 で宣した式・係数 1.5 無し)。端点 = 納め最終便を inbox_write.sh へ渡す直前の date 刻。改め便を送出後に既読化(id 名指し)。三走目(一走目 351 字 → .first・二走目 304 字 → .second)。"""
import os, sys, re, subprocess, time, yaml, glob, datetime as dt
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}; ORDER = 'msg_20260917_064406_177f8cee'
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); SEN = 4; eta = (dt.datetime.strptime(koku[:19], '%Y-%m-%dT%H:%M:%S') + dt.timedelta(minutes=SEN)).strftime('%H:%M:%S')
body = (f'★着手★ 第71弾 補 km-71b(改め便 06:44 応へ)work_started={koku[:16]} 宣ETA={eta}(起点=本便の刻・端点=納め最終便を inbox_write.sh へ渡す直前の date 刻・宣=新規2器×1.2+写し6×0.2→4分)。'
        f'★疵★改め便を納め(06:49)の後 06:50 に読んだ(箱を弾の途中で読まなんだ・二度目)。改め㋑㋒は km-71 で納め済。欠=案ロ∴案イ/ロをdiff・戻し方・塞がぬ物で並べる(据ゑず)。在處=docs/evidence/km-71b-fusagikata-ni-an-20260917/')
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
mk = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/inbox_mark_read.py'), M + f'/queue/inbox/{ME}.yaml', ORDER], capture_output=True, text=True)
K.kaku(RAW + '/05_chakushu.txt', f'# 05 着手便 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit} / 改め便 {ORDER} 既読化 rc {mk.returncode} {mk.stdout.strip()[:60]}\n{body}'); print(open(RAW + '/05_chakushu.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)

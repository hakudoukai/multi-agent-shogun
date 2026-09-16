# -*- coding: utf-8 -*-
"""05 着手便(第71弾)。宣 ETA = 起 + 25 分(器 11 本 × km-70 の實 1.20 分/器 = 13.2 分 × 1.5 → 20 分 → 切上げ 25)。端点 = 納め最終便を inbox_write.sh へ渡す直前の date 刻。起 = 本便の刻。門は 05_seikyu と同じ。第八の番人付。二走目(一走目 315 字で鳴つた → .first)。発注便 idx42 を送出後に既読にする(id 名指し)。"""
import os, sys, re, subprocess, time, yaml, glob, datetime as dt
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}; ORDER = 'msg_20260917_064022_8608761c'
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); SEN = 25; eta = (dt.datetime.strptime(koku[:19], '%Y-%m-%dT%H:%M:%S') + dt.timedelta(minutes=SEN)).strftime('%H:%M:%S')
body = (f'★着手★ 第71弾 km-71 ★空文字は値として振舞ふ★ work_started={koku[:16]} 宣ETA={eta}(起点=本便の刻・端点=納め最終便を inbox_write.sh へ渡す直前の date 刻・宣=11器×1.2分×1.5→25分)。'
        f'㋐母數(AST 檢出子+fixture 対照)→㋑門 unset/""/"."  四臺帳×cwd二所(据ゑず)→㋒形≥3→㋓対照→㋔紙のみ。自主束は動かさず紙で親子を宣す。在處=main樹 docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917/')
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
K.kaku(RAW + '/05_chakushu.txt', f'# 05 着手便 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit} / 発注便 {ORDER} 既読化 rc {mk.returncode} {mk.stdout.strip()[:60]}\n{body}'); print(open(RAW + '/05_chakushu.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)

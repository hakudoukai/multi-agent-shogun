# -*- coding: utf-8 -*-
"""追ひ便 6 の器 64(第71弾・_after/)―― 63 の宣⇔實(數は 63_sent.txt から regex で引く)と、納め便の後に判つた己の疵を一通で。門は 05/62 と同じ。第八の番人付。二走目(一走目 302 字 → .first)。"""
import os, sys, re, subprocess, time, yaml, glob
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}
t = open(AFT + '/63_sent.txt', encoding='utf-8').read()
def num(pat, alt='?'): m = re.search(pat, t); return m.group(1) if m else alt
jitsu = num(r'= 實 ([\d.]+) 分'); sen = num(r'⇔ 宣 (\d+) 分'); sa = num(r'宣−實 ([+\-][\d.]+) 分'); per = num(r'實 ÷ 器 = ([\d.]+) 分/器'); ki = num(r'起 (\S+)\(着手便'); end = num(r'端点[^=]*= (\S+)★'); fugo = num(r'= (＋過大|−過小)')
bai = f'{float(sen) / float(jitsu):.1f}' if jitsu != '?' and float(jitsu) > 0 else '?'
body = (f'[第71弾 追ひ 6・宣⇔實] 起 {ki[11:19]}(着手便)→ 端点 {end[11:19]}(納め5/5 直前)= 實 {jitsu} 分 ⇔ 宣 {sen} 分 → 宣−實 {sa} 分 = {fugo}(宣は實の {bai} 倍)。實÷器(11本)= {per} 分/器 ―― 宣に使つた 1.20 分/器(km-70 實)の半分以下。'
        f'知らなんだ事: 器の大半が既成の写し(50/59/60/62/67 は自主束の物)で、写しは書く時間が零に近い。次弾の數: 新規の器 × 1.2 分 + 写し × 0.2 分、係数 1.5 は外す。疵: 便1・着手便とも一走目が 300 字を超え己の門で鳴つた(.first)')
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if '?' in body: naru.append('引けぬ數')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
print('字数', len(body), '門', naru or '通(0 鳴)')
if naru: K.kaku(AFT + '/64_letter6.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
K.kaku(AFT + '/64_letter6.txt', f'# 64 追ひ便 6 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit}\n{body}'); print(open(AFT + '/64_letter6.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)

# -*- coding: utf-8 -*-
"""追ひ便 7 の器 64(第70弾・_after/)―― 63 の宣⇔實(數は 63_sent.txt から regex で引く)と、納め便の後に判つた己の疵三つを一通で。門は 05/62 と同じ(宛先・字数・役職名の形・先送り語)。第八の番人付。"""
import os, sys, re, subprocess, time, yaml, glob
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; sys.path.insert(0, AFT); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}
t = open(AFT + '/63_sent.txt', encoding='utf-8').read()
def num(pat, alt='?'): m = re.search(pat, t); return m.group(1) if m else alt
seki = num(r'席基準[^\n]*= 實 ([\d.]+) 分'); dseki = num(r'席基準[^\n]*宣−實 ([+\-][\d.]+) 分'); karo = num(r'家老基準[^\n]*= 實 ([\d.]+) 分'); dkaro = num(r'家老基準[^\n]*宣−實 ([+\-][\d.]+) 分'); senk = num(r'家老基準[^\n]*⇔ 宣 ([\d.]+) 分'); per = num(r'實 ÷ 器 10 = ([\d.]+) 分/器'); fugo = num(r'★符號は (\S+)★')
body = (f'[第70弾 追ひ 7] 宣⇔實(63・刻は 63_sent.txt): 席 實{seki}分 宣42 → {dseki}(過大) / 家老 實{karo}分 宣{senk} → {dkaro}(過大) 符號{fugo}・實÷器={per}分/器。'  # 二走目(.second)322 字
        '疵: ①62 の DRY 落ち(313/320字)を鎖で止めず 50 へ進み臺帳が 62 を凍結→写し _after/62b が出した ②96 が 50/59 の自產物 9 を疵と札し rc1→96b が歩哨 mtime で割り門の後 0 ③63 の札 status が正規表現の ^ で疑問符に成つた(実は km-69 done)。staged 189')  # 一走目(.first)329 字+胴の疑問符で己の門が鳴つた
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if re.fullmatch(r'[a-z0-9_-]+', body): naru.append('役職名の形')
if '?' in body: naru.append('引けぬ數')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
print('字数', len(body), '門', naru or '通(0 鳴)')
if naru: K.kaku(AFT + '/64_letter7.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
K.kaku(AFT + '/64_letter7.txt', f'# 64 追ひ便 7 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit}\n{body}'); print(open(AFT + '/64_letter7.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)

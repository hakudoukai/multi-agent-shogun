# -*- coding: utf-8 -*-
"""追ひ便 4 の器 64(第71弾 補・_after/)―― 63 の宣⇔實を★器数を数へて★割り直す(62 の写しは「器 11 本」を焼き込んで居た=疵⑤)。器 = raw/ 直下の *.py(S_ISREG・fixture 無し・kaki.py を含む)。數は 63_sent.txt から regex で引く。門は 05 と同じ。第八の番人付。"""
import os, sys, re, subprocess, time, yaml, glob, stat
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}
t = open(AFT + '/63_sent.txt', encoding='utf-8').read()
def num(pat, alt='?'): m = re.search(pat, t); return m.group(1) if m else alt
jitsu = num(r'= 實 ([\d.]+) 分'); sen = num(r'⇔ 宣 (\d+) 分'); sa = num(r'宣−實 ([+\-][\d.]+) 分'); ki = num(r'起 (\S+)\(着手便'); end = num(r'端点[^=]*= (\S+)★'); yaki = num(r'器 (\d+) 本 → 實 ÷ 器')
utsuwa = sorted(f for f in os.listdir(RAW) if f.endswith('.py') and stat.S_ISREG(os.lstat(os.path.join(RAW, f)).st_mode)); n = len(utsuwa); per = f'{float(jitsu) / n:.2f}'; bai = f'{float(sen) / float(jitsu):.1f}'
body = (f'[第71弾 補 追ひ 4・宣⇔實の割り直し] 起 {ki[11:19]}→ 端点 {end[11:19]} = 實 {jitsu} 分 ⇔ 宣 {sen} 分 → {sa} 分 過大(宣は實の {bai} 倍)。★疵⑤★ 63 は「器 {yaki} 本」を写し(62)の焼き込みの儘で割つた=誤り。'
        f'数へ直し: 器 = raw/*.py(S_ISREG・fixture 無)= {n} 本 → 實÷器 = {per} 分/器。宣の式(新規 1.2・写し 0.2)は尚 {bai} 倍過大 ∴ 次弾は 新規 0.5・写し 0.1 で建てる。器の数は焼き込まず数へる')
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if '?' in body: naru.append('引けぬ數')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
print('字数', len(body), '門', naru or '通(0 鳴)', '器', utsuwa)
if naru: K.kaku(AFT + '/64_letter4.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
K.kaku(AFT + '/64_letter4.txt', f'# 64 追ひ便 4 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit} / 器 {n} 本 {utsuwa}\n{body}'); print(open(AFT + '/64_letter4.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)

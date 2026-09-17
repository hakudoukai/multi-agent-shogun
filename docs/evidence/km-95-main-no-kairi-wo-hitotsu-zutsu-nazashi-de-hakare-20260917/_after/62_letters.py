# -*- coding: utf-8 -*-
"""納め便の器 62(第82弾 km-95・km-92 の写し・員外)―― 四便・各 300 字の條・門(宛先/未讀/字数 二器/?/先送り語)を通してから inbox_write。id は箱の胴の頭 40 字で引く(第八の番人)。宣⇔實は着手便の timestamp(箱の値)を起点に測る。數は器の出目(raw/*.txt・_after/60_gate_rcs.txt・_after/61_ingai.txt)から regex で抽く。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); g = {k: re.search(k + r'.*rc (\d+)', rcs).group(1) for k in ('selftest', 'main', 'nobase')}; LOG = re.search(r'門控 main (\S+)', rcs).group(1)
P_, MN, G = sha16(D + '/README.md'), sha16(D + '/MANIFEST.txt'), sha16(D + '/' + LOG); PL = open(D + '/README.md', encoding='utf-8').read().count('\n'); NI = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path='))
me = open(OUT + '/60_gate_main.err', encoding='utf-8').read(); bs = re.search(r'byte和[ =]*(\d+)', me); bs = bs.group(1) if bs else '?'; mo = open(OUT + '/60_gate_main.out', encoding='utf-8').read(); j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)  \(母數 (\d+)\)', mo); j1 = f'一致{j1.group(1)}/母數{j1.group(5)}・相違{j1.group(2)}・実体無{j1.group(3)}・読めぬ{j1.group(4)}' if j1 else '?'
st = open(E + '/01_letter.txt', encoding='utf-8').read(); st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", st).groups()
ing = open(OUT + '/61_ingai.txt', encoding='utf-8').read(); NG = re.search(r'員外\(臺帳に載らぬ通常 file\)= ★(\d+)★', ing).group(1)
T = {n: open(E + f'/{n}.txt', encoding='utf-8').read() for n in ('10_bunki', '20_local_side', '30_origin_side', '40_eda9', '45_an3', '46_gitignore_3way', '70_kami_awase')}
def g1(n, pat): return re.search(pat, T[n], re.S).group(1)
KZ = sum(1 for l in open(D + '/README.md', encoding='utf-8') if re.match(r'^- ★疵', l))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); t0 = time.mktime(time.strptime(st_ts, '%Y-%m-%dT%H:%M:%S')); jitsu = (time.time() - t0) / 60
bl = g1('45_an3', r'python len ★(\d+)★')
letters = [
 f"[第82弾 km-95 納め 1/4・束] docs/evidence/{KM}/ 紙 README.md {P_}({PL}行)/ 臺帳 {MN}({NI}項)/ 門控 {LOG.split('/')[-1][:-4]} {G}。git 読取のみ(fetch/merge/ref書換/commit 0回・束は未commit=禁の字義)。着手便 {st_id[-8:]}({st_ts[11:19]})。照合器 ○{g1('70_kami_awase', r'判 ○ (\d+) /')}/{g1('70_kami_awase', r'母數 (\d+)')}。",
 f"[第82弾 納め 2/4・門と員外] selftest rc{g['selftest']}・main rc{g['main']}({NI}本・byte和{bs}・條① {j1})・nobase rc{g['nobase']}(落ちて正)。★宣⇔實: 條①の母數を紙で 32 と宣し、宣の後に 70 照合器 2本を足して臺帳 34(隠さぬ)★。員外 {NG}本+自産1(名指しは _after/61_ingai.txt)。",
 f"[第82弾 納め 3/4・㋐㋑㋒] 分岐点 6e9d4060(=skills-tools tip)。母數三つ: rev-list 16/21(merge 0/11)・非merge 16/10→相手に無い patch-id ★14/8★=家老の数。local16=甲2(f2bfa26a≡af0dacfc・f0d59a3b≡26e23590=PR#15 作り直し)/乙14/丙0。origin21=object 21在・手元heads 0が含む・merge11=GitHub web。理由=local main は 08-07 ff 以来 origin 未取込(reflog)。誰が押したかは測れぬ。",
 f"[第82弾 納め 4/4・㋓㋔] 9枝: 紙sha=ls-remote 9/9・基点local +0 9/9・基点origin +0 は skills-tools 1本(宣と一致)。出所= 9 tip 悉く local main の祖先ゆゑ乙14本が写る。三案=甲寄せる/乙出す/丙基点のみ。★推す=乙★: 363d5fb0 は origin 枝 karo-mac/km-gate-kou-otsu-20260917 他46本に既に在り push 不要・.gitignore 3-way 衝突0。一文 {bl}字(raw/45)。疵{KZ}+1(61)。宣60〜150分⇔實{jitsu:.0f}分。",
]
raw = open(M + f'/queue/inbox/{ME}.yaml', encoding='utf-8').read(); un = raw.count('\n  read: false')
ROSTER = sorted(os.path.basename(p)[:-5] for p in os.listdir(M + '/queue/inbox') if p.endswith('.yaml') and not p.startswith('_')); naru = []
if TO not in ROSTER or TO == ME: naru.append('宛先')
if un: naru.append(f'己の箱に未読 {un}')
for i, b in enumerate(letters, 1):
    n2 = subprocess.run(['wc', '-m'], input=b.encode('utf-8'), capture_output=True).stdout.decode().strip()
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if str(len(b)) != n2: naru.append(f'便{i} 二器不一致 {len(b)}/{n2}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if naru or '--dry' in sys.argv: K.kaku(OUT + '/62_dry.txt', ('★門が鳴つた ' + str(naru) + '★\n' if naru else '# dry\n') + '\n---\n'.join(letters)); sys.exit(1 if naru else 0)
out = [f'# 62 納め便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]} / 宛 {TO} / 着手便 {st_id} {st_ts} / 實 {jitsu:.2f} 分(起点= 着手便 timestamp・端点= 此の刻)/ 宣 60〜150 分(幅)']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/62_letters.txt', '\n'.join(out)); print('\n'.join(out)[:2600])

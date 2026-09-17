# -*- coding: utf-8 -*-
"""納め便の器 62(第79弾 km-86・km-84 の写し・_after= 臺帳の後の器・員外)―― 五便・各 300 字の條・門(宛先/未讀/字数 二器/?/先送り語)を通してから inbox_write。id は箱の胴の頭 40 字で引く(第八の番人)。宣⇔實は着手便の timestamp(箱の値)を起点に測る。數は悉く器の出目(raw/*.txt・_after/60_gate_rcs.txt)から regex で抽く(km-84 疵⑬= 便の regex の緩さ・本弾は錨を行頭の★や固有語に置く)。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); g = {k: re.search(k + r'.*rc (\d+)', rcs).group(1) for k in ('selftest', 'main', 'nobase')}; LOG = re.search(r'門控 main (\S+)', rcs).group(1)
P_, MN, G = sha16(D + '/README.md'), sha16(D + '/MANIFEST.txt'), sha16(D + '/' + LOG); PB = os.path.getsize(D + '/README.md'); PL = open(D + '/README.md', encoding='utf-8').read().count('\n'); NI = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path='))
me = open(OUT + '/60_gate_main.err', encoding='utf-8').read(); bs = re.search(r'byte和[ =]*(\d+)', me); bs = bs.group(1) if bs else '?'
st = open(E + '/01_letter.txt', encoding='utf-8').read(); st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", st).groups()
T = {n: open(E + f'/{n}.txt', encoding='utf-8').read() for n in ('00_start', '10_kuchi', '20_shimo', '30_tally', '40_taishou', '35_naoshi', '70_kami_awase')}
def g1(n, pat): return re.search(pat, T[n]).group(1)
KZ = sum(1 for l in open(D + '/README.md', encoding='utf-8') if re.match(r'^- ★?疵', l))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); t0 = time.mktime(time.strptime(st_ts, '%Y-%m-%dT%H:%M:%S')); jitsu = (time.time() - t0) / 60
letters = [
 f"[第79弾 納め 1/5・束] docs/evidence/{KM}/ 紙 README.md {P_}({PL}行)/ 臺帳 {MN}/ 門控 {LOG.split('/')[-1][:-4]} {G}。repo 0字・tmux 実打ち0(stub)。着手便 {st_id[-8:]}({st_ts[11:19]})。照合器 ○{g1('70_kami_awase', r'○ (\d+)')}/{g1('70_kami_awase', r'母數 (\d+)')} ×{g1('70_kami_awase', r'× (\d+)')} rc{g1('70_kami_awase', r'rc (\d+)')}。",
 f"[第79弾 納め 2/5・門] selftest rc{g['selftest']}・main rc{g['main']}({NI}本・byte和{bs}・條①一致)・nobase rc{g['nobase']}(基点無し・落ちて正)。員外=MANIFEST.txt・_gate/*・_after/*・raw/50_build_manifest.*・raw/50_sengen.txt。.first は員内(倒れた走を残す)。",
 f"[第79弾 納め 3/5・㋐㋓] 根A={g1('00_start', r'を除き ★(\d+) 本★')}本(km-84の根)/根B={g1('00_start', r'rc 0\)= ★(\d+) 本★')}本(家老)・差=両方{g1('00_start', r'両方に在る (\d+) 本')}+Aのみ{g1('00_start', r'根A にのみ在る (\d+) 本')}+Bのみ{g1('00_start', r'根B にのみ在る (\d+) 本')}(悉くdocs/evidence)。口{g1('10_kuchi', r'★母數= 口 (\d+)')}=閾{g1('10_kuchi', r'閾 (\d+) / 旗')}旗{g1('10_kuchi', r'旗 (\d+) / 名')}名{g1('10_kuchi', r'名 (\d+) / 其の他')}他{g1('10_kuchi', r'其の他 (\d+) / 不能')}不能{g1('10_kuchi', r'不能 (\d+) ＝')}。甲:-{g1('10_kuchi', r'甲 `\$\{N:-d\}` (\d+)')}/乙{g1('10_kuchi', r'乙 `\$\{N-d\}` (\d+)')}(根A・零の四札)/py get{g1('10_kuchi', r'python get (\d+)')}=空を素通し。",
 f"[第79弾 納め 4/5・㋑㋒] 名{g1('10_kuchi', r'名 (\d+) / 其の他')}口の讀手: 同file害{g1('20_shimo', r'＝ 害の行 (\d+)★')}行(⑶{g1('20_shimo', r'path・dir・file (\d+)')}⑷{g1('20_shimo', r'role (\d+)')}⑸{g1('20_shimo', r'比較 (\d+) ＝')}⑴{g1('20_shimo', r'tmux target (\d+)')})+他file{g1('20_shimo', r'/ 數 0 ＝ (\d+)★')}行(⑴{g1('20_shimo', r'他file・行\): ⑴ (\d+)')})・讀まれぬ{g1('20_shimo', r'讀まれぬ口\(宣のみ・同 file にも他 file にも参照 0\)= (\d+) 組')}組。毒10×写し器{g1('30_tally', r'写し器 (\d+) = ')}={g1('30_tally', r'= (\d+) 走')}走: 報せ{g1('30_tally', r'器の報せ>0 (\d+)')}声{g1('30_tally', r'外の声>0 (\d+)')}★黙つて向先が変はる{g1('30_tally', r'素通し or 別形\)(\d+)★')}★既定へ{g1('30_tally', r'黙つて既定へ落ちた (\d+)')}。",
 f"[第79弾 納め 5/5・㋔㋕㋖] 対照{g1('40_taishou', r'○=(\d+)/')}/{g1('40_taishou', r'○=\d+/(\d+)')}(向先が変はる/stub/実行検出/声)。案5つ紙のみ: 反例=正規化+根の内・字類の禁・存在往復(許容集合に非ず)。偽陽性=A {g1('35_naoshi', r'扱ふ口 ★(\d+)★')}/B {g1('35_naoshi', r'指す口 ★(\d+)★')}/C {g1('35_naoshi', r'含む口 ★(\d+)★')}/E 死箱{g1('35_naoshi', r'在らぬ ★(\d+)/')}。疵{KZ}(紙㊈)。宣90〜240分⇔實{jitsu:.0f}分。監査sb→gunshi-mac(PASS待たず)。",
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
out = [f'# 62 納め便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]} / 宛 {TO} / 着手便 {st_id} {st_ts} / 實 {jitsu:.2f} 分(起点= 着手便 timestamp・端点= 此の刻)/ 宣 90〜240 分(幅)']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/62_letters.txt', '\n'.join(out)); print('\n'.join(out)[:2600])

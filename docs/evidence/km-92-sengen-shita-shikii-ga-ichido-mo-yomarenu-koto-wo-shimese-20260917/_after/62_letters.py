# -*- coding: utf-8 -*-
"""納め便の器 62(第81弾 km-92・km-86 の写し・_after= 臺帳の後の器・員外)―― 五便・各 300 字の條・門(宛先/未讀/字数 二器/?/先送り語)を通してから inbox_write。id は箱の胴の頭 40 字で引く(第八の番人)。宣⇔實は着手便の timestamp(箱の値)を起点に測る。數は悉く器の出目(raw/*.txt・_after/60_gate_rcs.txt)から regex で抽く。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); g = {k: re.search(k + r'.*rc (\d+)', rcs).group(1) for k in ('selftest', 'main', 'nobase')}; LOG = re.search(r'門控 main (\S+)', rcs).group(1)
P_, MN, G = sha16(D + '/README.md'), sha16(D + '/MANIFEST.txt'), sha16(D + '/' + LOG); PL = open(D + '/README.md', encoding='utf-8').read().count('\n'); NI = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path='))
me = open(OUT + '/60_gate_main.err', encoding='utf-8').read(); bs = re.search(r'byte和[ =]*(\d+)', me); bs = bs.group(1) if bs else '?'
st = open(E + '/01_letter.txt', encoding='utf-8').read(); st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", st).groups()
T = {n: open(E + f'/{n}.txt', encoding='utf-8').read() for n in ('10_meisho', '20_date', '30_kansu', '31_tests', '40_naoshi', '41_kansu_after', '42_tests', '45_commit', '70_kami_awase')}
def g1(n, pat): return re.search(pat, T[n], re.S).group(1)
KZ = sum(1 for l in open(D + '/README.md', encoding='utf-8') if re.match(r'^- ★疵', l))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); t0 = time.mktime(time.strptime(st_ts, '%Y-%m-%dT%H:%M:%S')); jitsu = (time.time() - t0) / 60
csha = g1('45_commit', r'full sha (\S+) /'); br = g1('45_commit', r'枝 (\S+) / full sha'); nsha = g1('40_naoshi', r'後: \S+ sha16 (\S+) sha256')
letters = [
 f"[第81弾 納め 1/5・束] docs/evidence/{KM}/ 紙 README.md {P_}({PL}行)+追紙 TSUIGAMI_km86.md/ 臺帳 {MN}/ 門控 {LOG.split('/')[-1][:-4]} {G}。生器 0字・watcher 不觸。着手便 {st_id[-8:]}({st_ts[11:19]})。照合器 ○{g1('70_kami_awase', r'○ (\d+) /')}/{g1('70_kami_awase', r'母數 (\d+)')} ×{g1('70_kami_awase', r'× (\d+)')}。",
 f"[第81弾 納め 2/5・門] selftest rc{g['selftest']}・main rc{g['main']}({NI}本・byte和{bs}・條①一致)・nobase rc{g['nobase']}(基点無し・落ちて正)。員外=MANIFEST.txt・_gate/*・_after/*・raw/50 の出目三つ(50 の .py 其の物は載せた= km-86 追紙2)。",
 f"[第81弾 納め 3/5・㋐㋑] 閾 DETECT_STALE_STALE_SEC=口{g1('10_meisho', r'口\(代入 `DETECT_STALE_STALE_SEC=`\) (\d+) 行')}讀手{g1('10_meisho', r'DETECT_STALE_STALE_SEC=`\) \d+ 行 / 讀手\(展開[^)]*\) (\d+) 行')}(器A {g1('10_meisho', r'歩いた通常 file (\d+) 本')}file/git grep 生1+束8/陽性 LOG 口3讀手7/陰性0 rc1/刻 {g1('10_meisho', r'刻 (\S+) /')[11:19]})・閾999999/abc でも now-1s が STALE=死。/bin/date -d は12/12 rc1→verbatim 行は悉く[0]・gdate は正(空文字を今日0時に読む)。",
 f"[第81弾 納め 4/5・㋒] 姿B(当機)= 正しい時刻2件が悉く ANOMALY。姿S= 非數8形(abc/空/-5/0/2^63/1e3/改行/出力+rc1)の内 ★6 が STALE→CLI enqueued=1★(-5・0 のみ ANOMALY)。家老表の空・2^63 行は zsh の出目・bash3.2 は共に rc2→2^63 は永久FRESHでなく auto-poke。既存test 姿B 単体6落/CLI1落・姿G PASS。",
 f"[第81弾 納め 5/5・㋓付] 直し= 閾を讀ませ(同演算子・名指し)+fromisoformat+數字のみ&[-gt 0]&[-le 253402300799]。捨てた側=宣を消す(承認値を消す形)。両対照{g1('41_kansu_after', r'判 ○ (\d+) /')}/{g1('41_kansu_after', r'母數 (\d+)')}○・test BF/G PASS。自枝 {br.split('/')[0]}/km-92-… full {csha}・的1本・porcelain不変。追紙=50/60 は臺帳を建て検める器ゆゑ前生は必然。疵{KZ}。宣120〜300分⇔實{jitsu:.0f}分。",
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
out = [f'# 62 納め便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]} / 宛 {TO} / 着手便 {st_id} {st_ts} / 實 {jitsu:.2f} 分(起点= 着手便 timestamp・端点= 此の刻)/ 宣 120〜300 分(幅)']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/62_letters.txt', '\n'.join(out)); print('\n'.join(out)[:2600])
